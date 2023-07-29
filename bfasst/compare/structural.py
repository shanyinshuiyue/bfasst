""" Structural Comparison and Mapping tool """

from collections import defaultdict
import time
from bidict import bidict
import pickle
import spydrnet as sdn
from bfasst import jpype_jvm
from bfasst.compare.base import CompareTool, CompareException
from bfasst.utils import convert_verilog_literal_to_int, error, properties_are_equal
import bfasst.rw_helpers as rw

GND_NAMES = set()
VCC_NAMES = set()
GND_PIN = None


class StructuralCompareTool(CompareTool):
    """Structural compare and map"""

    TOOL_WORK_DIR = "struct_cmp"

    def __init__(
        self, cwd, design, gold_netlist, rev_netlist, log_prefix="", flow_args="", rm_net=False
    ) -> None:
        super().__init__(cwd, design, gold_netlist, rev_netlist, flow_args)
        self.log_path = self.work_dir / f"{log_prefix}log.txt"
        self.remove_logs()
        self.rm_net = rm_net

        self.named_netlist = None
        self.reversed_netlist = None

        self.block_mapping = bidict()
        self.net_mapping = bidict()

        init_only = (
            "LUT6_2",
            "FDSE",
            "FDRE",
            "FDCE",
            "FDPE",
            "RAM32X1S",
            "RAM32X1D",
            "RAM32X1S_1",
            "RAM32X1D_1",
            "RAM256X1S",
            "SRL16E",
            "SRLC32E",
            "LDCE",
        )
        no_props = ("IBUF", "OBUF", "OBUFT", "MUXF7", "MUXF8", "CARRY4", "IOBUF")

        _cell_props = {x: ("INIT",) for x in init_only}
        _cell_props.update({x: () for x in no_props})
        _cell_props["RAM32M"] = ("INIT_A", "INIT_B", "INIT_C", "INIT_D")
        _cell_props["RAM64M"] = ("INIT_A", "INIT_B", "INIT_C", "INIT_D")
        _cell_props["RAMB36E1"] = tuple(
            [f"INIT_{i:02X}" for i in range(int("0x80", base=16))]
            + ["DOA_REG", "DOB_REG", "RAM_MODE"]
        )
        # TODO add INIT_A, INIT_B, INITP_00 - INITP_0F
        _cell_props["RAMB18E1"] = tuple(
            f"INIT_{i:02X}" for i in range(int("0x40", base=16))
        )  # TODO add INIT_A, INIT_B, INITP_00 - INITP_07
        _cell_props["BUFGCTRL"] = (
            "INIT_OUT",
            "IS_CE0_INVERTED",
            "IS_CE1_INVERTED",
            "IS_IGNORE0_INVERTED",
            "IS_IGNORE1_INVERTED",
            "IS_S0_INVERTED",
            "IS_S1_INVERTED",
            "PRESELECT_I0",
            "PRESELECT_I1",
        )

        self._cell_props = _cell_props

        self.run_num = None
        self.possible_matches = {}
        self.gnd_mappings = set()
        self.vcc_mappings = set()

        jpype_jvm.start()

    def reset_mappings(self):
        self.block_mapping = bidict()
        self.net_mapping = bidict()

    def load_mappings(self):
        """Init mapping data structures from pkl files"""
        with open(self.work_dir / "block_mapping.pkl", "rb") as f:
            block_map = pickle.load(f)
        with open(self.work_dir / "net_mapping.pkl", "rb") as f:
            net_map = pickle.load(f)

        self.map_ports()
        for lh, rh in block_map.items():
            lh_instance = [i for i in self.named_netlist.instances if i.name == lh][0]
            rh_instance = [i for i in self.reversed_netlist.instances if i.name == rh][0]
            self.block_mapping[lh_instance] = rh_instance
        for lh, rh in net_map.items():
            # Sometimes multiple net objects have the same name, like gnd nets,
            # so this is not guaranteed to recreate the exact same data
            # structure.  But, as far as I know, only this only occurs with
            # const nets, so result should be functionally the same.
            # Also, manually added pin.ignore_net_equivalency for brams are
            # not updated here, so it will trigger failures in equivalence
            # checking that must be manually reviewed.
            lh_net = [n for n in self.named_netlist.nets if n.name == lh][0]
            rh_net = [n for n in self.reversed_netlist.nets if n.name == rh][0]
            self.net_mapping[lh_net] = rh_net

    def init_netlists(self):
        """Load both netlists from spydrnet and build wrapper objects"""
        self.launch()
        impl_netlist = self.gold_netlist
        netlist_b = self.rev_netlist

        self.check_log_path()

        self.log_title("Building netlist A", impl_netlist)

        # Loads the first netlist as intermediate representation (ir1)
        ir_a = sdn.parse(str(impl_netlist))
        library_a = ir_a.libraries[0]
        netlist_a = self.get_netlist(library_a)
        self.log(f"Golden netlist size: {len(netlist_a.instances)}")

        self.log_title("Building netlist B", netlist_b)

        # Loads the second netlist as intermediate representation (ir2)
        ir_b = sdn.parse(str(netlist_b))
        library_b = ir_b.libraries[0]
        netlist_b = self.get_netlist(library_b)
        self.log(f"Reversed netlist size: {len(netlist_b.instances)}")

        # golden_netlist = [i for i in golden_netlist if i.name not in ("GND")]

        self.named_netlist = netlist_a
        self.reversed_netlist = netlist_b

    def check_log_path(self):
        if self.run_num is not None:
            self.log_path = self.work_dir / f"compare_log_{self.run_num}.txt"

    def compare_netlists(self):
        """Map the golden and reversed netlists through automated block mapping"""
        self.start_time = time.time()

        t_begin = time.perf_counter()
        self.init_netlists()

        self.log("Time after init_netlists:".ljust(35), time.perf_counter() - t_begin)

        # self.load_mappings()
        # Structurally map the rest of the netlists
        self.perform_mapping()
        t_end = time.perf_counter()

        self.log_title("Mapping (Instances)")
        block_map = {k.name: v.name for k, v in self.block_mapping.items()}
        for key, val in self.block_mapping.items():
            self.log(f"{key.name} -> {val.name}")
        self.log()
        # self.log_title("Mapping (Nets)")
        net_map = {k.name: v.name for k, v in self.net_mapping.items()}
        for key, val in self.net_mapping.items():
            self.log(f"{key.name} -> {val.name}")

        self.log_title("Finalizing")
        self.named_netlist.instances_to_map = {
            i for i in self.named_netlist.instances if i.cell_type not in ("GND", "VCC")
        }
        self.log(
            "Number of mapped blocks: ",
            f"{len(self.block_mapping)} of {len(self.named_netlist.instances_to_map)}",
        )
        self.log("  Unmapped blocks:")
        for block in [
            block
            for block in self.named_netlist.instances_to_map
            if block not in self.block_mapping
        ]:
            self.log(f"    {block.name}")

        num_mapped_nets = (
            len([net for net in self.net_mapping if net.is_connected])
            + len(self.vcc_mappings)
            + len(self.gnd_mappings)
        )
        num_total_nets = len(self.named_netlist.get_connected_nets())
        self.log("Number of mapped nets:", num_mapped_nets, "of", num_total_nets)

        self.log("  Unmapped nets:")
        for net in [
            net
            for net in self.named_netlist.get_connected_nets()
            if net not in self.net_mapping
            and net.name not in self.vcc_mappings
            and net.name not in self.gnd_mappings
        ]:
            # if net.is_vdd or net.is_gnd:
            #     num_total_nets -= 1
            #     continue
            self.log(f"    {net.name}")

        if len(self.block_mapping) != len(self.named_netlist.instances_to_map):
            raise CompareException("Could not map all blocks")
        if num_mapped_nets != num_total_nets:
            raise CompareException("Could not map all nets")

        with open(self.work_dir / "block_mapping.pkl", "wb") as f:
            self.log(f"Dumping pkl to {self.work_dir / 'block_mapping.pkl'}")
            pickle.dump(block_map, f)

        with open(self.work_dir / "net_mapping.pkl", "wb") as f:
            pickle.dump(net_map, f)

        mtime = round(t_end - t_begin, 1)
        self.log(f"Mapping time: {mtime} seconds")

        # After establishing mapping, verify equivalence
        t_begin = time.perf_counter()
        self.verify_equivalence()
        t_end = time.perf_counter()
        vtime = round(t_end - t_begin, 1)
        self.log(f"Equivalence verification time: {vtime} seconds")
        self.log(f"Total time: {mtime + vtime} seconds")
        if self.rm_net:
            self.rev_netlist.unlink()
        self.cleanup()

        self.end_time = time.time()
        self.log("Total time:".ljust(35), self.end_time - self.start_time)
        with open(self.work_dir / "comparison_time.txt", "w") as f:
            f.write(f"{self.end_time - self.start_time}\n")

    def map_ports(self):
        """Map top-level ports"""
        self.log_title("Mapping top-level ports")
        for pin in self.named_netlist.pins:
            assert isinstance(pin, Pin)
            self.log(
                "Mapping port",
                f"{pin.name}[{pin.index}] to",
                f"{pin.name}[{pin.index}]",
            )
            try:
                self.add_net_mapping(
                    pin.net,
                    self.reversed_netlist.get_pin(pin.name, pin.index).net,
                )
            except KeyError as e:
                raise CompareException("KeyError during port mapping") from e

    def init_matching_instances(self):
        """Init possible_matches dict with all instances that match by cell type and properties"""
        all_instances = [
            i for i in self.reversed_netlist.instances if not i.cell_type.startswith("SDN_VERILOG")
        ]

        grouped_by_cell_type = defaultdict(list)
        for instance in all_instances:
            properties = {}
            for prop in self.get_properties_for_type(instance.cell_type):
                properties[prop] = convert_verilog_literal_to_int(instance.properties[prop])

            grouped_by_cell_type[(instance.cell_type, hash(frozenset(properties)))].append(instance)
            if len(grouped_by_cell_type) > 10:
                break

        for named_instance in self.named_netlist.instances_to_map:
            ###############################################################
            # First find all instances of the same type and same properties
            ###############################################################

            # Compute a hash of this instance's properties
            properties = {}
            for prop in self.get_properties_for_type(named_instance.cell_type):
                properties[prop] = convert_verilog_literal_to_int(named_instance.properties[prop])
            my_hash = hash(frozenset(properties))

            instances_matching = grouped_by_cell_type[(named_instance.cell_type, my_hash)]

            if not instances_matching:
                self.log(
                    "No instances of type", named_instance.cell_type, "with properties", properties
                )
                raise CompareException(
                    f"Not equivalent. {named_instance.name} has no possible match in the netlist."
                )

            self.possible_matches[named_instance] = instances_matching.copy()

    def potential_mapping_wrapper(self, instance):
        """Wrap check_for_potential_mapping some inital checks/postprocessing"""

        # Skip assign statements (named netlist shouldn't have them)
        # Update: just let the code break if this happens
        # assert not instance.cell_type.startswith("SDN_VERILOG_ASSIGNMENT")

        self.log(f"Considering {instance.name} ({instance.cell_type})")

        # Get the implemented potential instance to map
        instances_matching = self.check_for_potential_mapping(instance)

        # self.log(f"  {instances_matching} matches")

        if not instances_matching:
            raise CompareException(
                f"Not equivalent. {instance.name} has no possible match in the netlist."
            )

        if len(instances_matching) > 1:
            self.log(f"  {len(instances_matching)} matches, skipping for now:")
            if len(instances_matching) < 10:
                for matched_instance in instances_matching:
                    self.log(f"    {matched_instance.name}")
            return False

        assert len(instances_matching) == 1
        matched_instance = instances_matching[0]

        self.log(f"  Mapped to {matched_instance.name}")

        self.add_block_mapping(instance, matched_instance)
        return True

    def perform_mapping(self):
        """Maps netlists based on their cells and nets"""

        # First map top-level nets
        self.map_ports()

        # Init possible_matches dict with all instances that match by cell type and properties
        self.init_matching_instances()
        self.log("Time after initial cache:".ljust(35), time.time() - self.start_time)

        self.log_title("Starting mapping iterations")

        # Loop until all blocks have been mapped or there is no more progress
        overall_progress = True
        iteration = 0
        while self.named_netlist.instances_to_map:
            if not overall_progress:
                num_mapped_nets = (
                    len([net for net in self.net_mapping if net.is_connected()])
                    + len(self.vcc_mappings)
                    + len(self.gnd_mappings)
                )
                num_total_nets = len(self.named_netlist.get_connected_nets())
                cell_type = {i.cell_type for i in self.named_netlist.instances_to_map}
                if len(cell_type) == 1 and num_mapped_nets == num_total_nets:
                    reversed_remaining = [
                        self.possible_matches[i] for i in self.named_netlist.instances_to_map
                    ]
                    remaining = set()
                    for i in reversed_remaining:
                        for j in i:
                            remaining.add(j.name)
                    if len(remaining) == len(reversed_remaining[0]):
                        for named, rev in zip(
                            self.named_netlist.instances_to_map, reversed_remaining[0]
                        ):
                            self.add_block_mapping(named, rev)
                        break

                self.log(f"No more progress can be made. Failed at iteration {iteration}.")
                break
            overall_progress = False

            self.log(f"===== Mapping Iteration {iteration} =====")

            # Loop through reversed netlist blocks
            instance_iter = iter(set(self.named_netlist.instances_to_map))
            try:
                while not overall_progress:
                    overall_progress = self.potential_mapping_wrapper(next(instance_iter))
                while True:
                    self.potential_mapping_wrapper(next(instance_iter))
            except StopIteration:
                pass
            iteration += 1

    def verify_equivalence(self):
        """Verify equivalence by looping through all mapped instances and
        checking that for each pin, the connected nets are also mapped
        to each other."""

        # Loop through all instances and check for equivalence
        self.log_title("Verifying equivalence")
        warnings = False
        for i, instance in enumerate(self.named_netlist.instances_to_map):
            # self.log(
            #     f"  {i+1}/{len(self.named_netlist.instances_to_map)} Instance {instance.name}:",
            #     f"verifying net mapping of {len(instance.pins)} pins",
            # )
            mapped_instance = self.block_mapping.get(instance)
            if mapped_instance is None:
                raise CompareException(
                    f"Not equivalent. Instance {instance.name} is not mapped to anything."
                )

            # Loop through all pins on instance and compare nets
            for pin_a in instance.pins:
                if pin_a.ignore_net_equivalency:
                    continue
                pin_b = mapped_instance.get_pin(pin_a.name, pin_a.index)

                net_a = pin_a.net
                net_b = pin_b.net
                net_a_empty = net_a is None or not net_a.is_connected
                net_b_empty = net_b is None or not net_b.is_connected
                try:
                    if net_a_empty and not net_b_empty:
                        raise CompareException(
                            (
                                f"Not equivalent. Pin {pin_b.name_with_index} of {mapped_instance.name}"
                                f" is connected to net {net_b.name},"
                                f" but no connection on mapped instance {instance.name}."
                            )
                        )

                    if net_b_empty and not net_a_empty:
                        raise CompareException(
                            (
                                f"Not equivalent. Pin {pin_a.name_with_index} of {instance.name}"
                                f" is connected to net {net_a.name},"
                                f" but no connection on mapped instance {mapped_instance.name}."
                            )
                        )

                    if not net_a_empty:
                        if net_a.name in self.vcc_mappings and net_b.is_vdd:
                            continue
                        elif net_a.name in self.gnd_mappings and net_b.is_gnd:
                            continue
                        if self.net_mapping[net_a] != net_b:
                            if self.net_mapping[net_a].is_gnd and net_b.is_gnd:
                                continue
                            raise CompareException(
                                (
                                    f"Not equivalent. Net {net_a.name} on {pin_a.name}[{pin_a.index}] is mapped to "
                                    f"{self.net_mapping[net_a].name} but should be {net_b.name}"
                                )
                            )
                except CompareException as e:
                    self.log(f"Warning: {type(e).__name__}: {e}\n")
                    warnings = True
        if not warnings:
            self.log("Equivalence verified")
        else:
            self.log("Equivalence questionable")
            raise CompareException("Warnings during equivalence verification")

    def add_block_mapping(self, instance, matched_instance):
        """Add mapping point between two Instances"""
        # assert isinstance(instance, Instance)
        # assert isinstance(matched_instance, Instance)

        self.block_mapping[instance] = matched_instance
        self.named_netlist.instances_to_map.remove(instance)

        for pin in instance.pins:
            # Some pins should not be used to establish net mapping
            if pin.ignore_net_equivalency:
                continue

            net_a = pin.net

            if net_a is None:
                # Disconnected pin
                continue

            assert isinstance(net_a, Net)
            if net_a in self.net_mapping:
                continue

            if instance.cell_type != "RAM32M" or not pin.name.startswith("D"):
                # for some reason RW sets DI* to the wrong bit, and SDN reads
                # DO* from the wrong bit for f2b netlist
                idx = pin.index
            else:
                idx = 0 if pin.index == 1 else 1

            net_b = matched_instance.get_pin(pin.name, idx).net
            if net_b is None and net_a.is_gnd:
                continue
            assert isinstance(net_b, Net)

            if net_a in self.net_mapping:
                assert net_b == self.net_mapping[net_a]
                continue

            if instance.cell_type == "RAM32M" and pin.name.startswith("DI"):
                # DI* doesn't matter if the corresponding output bit is not used
                out_net = matched_instance.get_pin(f"DO{pin.name[2]}", idx).net
                if out_net is None or out_net.is_gnd or len(out_net.wire.pins) <= 1:
                    continue

            self.log(
                "    Net",
                net_a.name.strip(),
                "mapped to",
                net_b.name,
                f"(from {pin.name})",
            )
            # self.log(pin.ignore_net_equivalency)
            # self.log(pin.net.is_gnd)
            # self.log(pin.net.driver_pin)
            self.add_net_mapping(net_a, net_b)

    def add_net_mapping(self, net1, net2):
        """Add mapping point between two Nets"""
        assert net1 not in self.net_mapping
        if net2 in self.net_mapping.inverse:
            if net2.is_gnd:
                assert net1.name not in self.vcc_mappings
                self.gnd_mappings.add(net1.name)
            elif net2.is_vdd:
                assert net1.name not in self.gnd_mappings
                self.vcc_mappings.add(net1.name)
            else:
                raise AssertionError(
                    f"{net2.name} in net_mapping.inverse already. net1: {net1.name}"
                )
            return

        self.net_mapping[net1] = net2

    def check_for_potential_mapping(self, named_instance):
        """Returns cells that could map to the named_instance"""

        ###############################################################
        # Now look at connections
        ###############################################################

        instances_matching_connections = [
            i for i in self.possible_matches[named_instance] if i not in self.block_mapping.inverse
        ]

        bram_do = False
        bram_a_only = False
        bram = False
        if named_instance.cell_type.startswith("RAMB"):
            bram = True
            bram_do = named_instance.properties["DOA_REG"] == "0"
            if bram_do:
                assert named_instance.properties["DOB_REG"] == "0"

            bram_a_only = named_instance.properties["RAM_MODE"] == '"TDP"' and {
                None,
                GND_PIN.net,
            } >= {
                named_instance.get_pin("DOBDO", i).net
                for i in range(32)
                if named_instance.get_pin("DOBDO", i) is not None
            }

            if named_instance.cell_type.startswith("RAMB36E1"):
                # A15 is only connected to a non-const net when cascade is enabled
                # Right now, it seems vivado will connect to vcc, although unconnected is valid
                expected_properties = (
                    named_instance.properties["RAM_EXTENSION_A"] == '"NONE"'
                    and named_instance.properties["RAM_EXTENSION_B"] == '"NONE"'
                    and named_instance.get_pin("ADDRARDADDR", 15).net.is_vdd
                    and named_instance.get_pin("ADDRBWRADDR", 15).net.is_vdd
                )
                if not expected_properties:
                    raise CompareException("Unexpected BRAM CASCADE Configuration")

        for pin in named_instance.pins:
            # assert isinstance(pin, Pin)

            if bram:
                # For RAMB18E1, "REGCEAREGCE" and "REGCEB" only depend on DOA_REG and DOB_REG, respectively
                # Currently does not matter for our designs, but should be revisited if the assertion fails
                if bram_do and pin.name in {
                    "RSTREGARSTREG",
                    "RSTREGB",
                    "REGCEAREGCE",
                    "REGCEB",
                }:
                    pin.ignore_net_equivalency = True
                    continue  # These pins are ignored when DO_REG is 0
                if pin.name in {"RSTRAMARSTRAM", "RSTRAMB"}:
                    # FASM2BELS ties these to vcc which doesn't make sense. Should be gnd.
                    pin.ignore_net_equivalency = True
                    continue
                # These pins can be vdd or gnd when cascade is off
                if bram_a_only and pin.name in {
                    "CASCADEINB",
                    "CASCADEOUTB",
                    "CLKBWRCLK",
                    "ENBWREN",
                    "RSTRAMB",
                }:
                    pin.ignore_net_equivalency = True
                    continue

            # Skip pin that is not yet mapped
            if pin.net not in self.net_mapping:
                continue

            # Otherwise pin connected to a mapped net, and filter based on instances that are
            # connected to the corresponding mapped net.
            other_net = self.net_mapping[pin.net]

            self.log(f"  Filtering on pin {pin.name_with_index}, {other_net.name}")

            # for instance in instances_matching_connections:
            #     self.log(
            #         instance.get_pin(pin.name, pin.index).name_with_index,
            #         instance.get_pin(pin.name, pin.index).net.name,
            #     )

            # Extra step for LUTRAMS
            if named_instance.cell_type != "RAM32M" or not pin.name.startswith("D"):
                # for some reason RW sets DI* to the wrong bit, and SDN reads
                # DO* from the wrong bit for f2b netlist
                idx = pin.index
            else:
                idx = 0 if pin.index == 1 else 1

            tmp = [
                instance
                for instance in instances_matching_connections
                if instance.get_pin(pin.name, idx).net == other_net
            ]

            if not tmp and named_instance.cell_type == "BUFGCTRL" and pin.name[0] == "I":
                # sometimes f2b routes the clk net to both inputs
                other_pin = f"I{'1' if pin.name[1] == '0' else '0'}"
                tmp = [
                    inst
                    for inst in instances_matching_connections
                    if inst.get_pin(pin.name, idx).net == inst.get_pin(other_pin, idx).net
                ]
                pin.ignore_net_equivalency = True
            # if not tmp and pin.name == "CYINIT":
            #     tmp = [
            #         instance for instance in instances_matching_connections
            #         if instance.get_pin(pin.name, idx).net.
            #     ]
            if not tmp:
                if other_net.is_gnd:
                    tmp = [
                        instance
                        for instance in instances_matching_connections
                        if instance.get_pin(pin.name, idx).net is None
                        or instance.get_pin(pin.name, idx).net.is_gnd
                    ]
                elif other_net.is_vdd:
                    tmp = [
                        instance
                        for instance in instances_matching_connections
                        if instance.get_pin(pin.name, idx).net.is_vdd
                    ]
            instances_matching_connections = tmp

            num_instances = len(instances_matching_connections)
            info = (
                ": " + ",".join(i.name for i in instances_matching_connections)
                if num_instances <= 10
                else ""
            )
            self.log(f"    {num_instances} remaining{info}")

        self.log(
            f"  {len(instances_matching_connections)} instance(s) after filtering on connections"
        )
        self.possible_matches[named_instance] = instances_matching_connections
        return instances_matching_connections

    def get_properties_for_type(self, cell_type):
        """Return the list of properties that must match for a given cell type
        for the cell to be considered equivalent."""
        if cell_type in self._cell_props:
            return self._cell_props[cell_type]
        raise CompareException(f"Unhandled properties for type {cell_type}")

    def get_netlist(self, library):
        return Netlist(library, self)


class Netlist:
    """Wrapper class around spydernet top level library"""

    def __init__(self, library, tool) -> None:
        self.library = library
        self.tool = tool

        # Nets
        self.wire_to_net = {}

        t1 = time.time()
        self.build_nets()
        t2 = time.time()

        # Instances
        instances = [Instance(i, self) for i in library.get_instances()]
        # instances = [i for i in instances if i.cell_type not in ("VCC", "GND")]
        self.instances = instances

        self.instances_to_map = {i for i in self.instances if i.cell_type not in ("GND", "VCC")}

        global GND_NAMES
        GND_NAMES = {i.name for i in self.instances if i.cell_type == "GND"}
        global VCC_NAMES
        VCC_NAMES = {i.name for i in self.instances if i.cell_type == "VCC"}

        # This made it slower
        # sort instances to start with bigger primitives
        # self.buf = {
        #     i
        #     for i in self.instances_to_map
        #     if i.cell_type.startswith("OBUF") or i.cell_type.startswith("IBUF")
        # }
        # self.brams = {i for i in self.instances_to_map if i.cell_type.startswith("RAMB")}
        # self.carry = {i for i in self.instances_to_map if i.cell_type.startswith("CARRY")}
        # self.luts = {i for i in self.instances_to_map if i.cell_type.startswith("LUT")}
        # self.extras = {
        #     i
        #     for i in self.instances_to_map
        #     if i not in self.buf
        #     and i not in self.brams
        #     and i not in self.carry
        #     and i not in self.luts
        # }
        # assert len(self.instances_to_map) == (
        #     len(self.brams) + len(self.carry) + len(self.luts) + len(self.extras) + len(self.buf)
        # )

        # Top-level IO pins
        self.pins = [Pin(pin, None, self) for pin in library.get_pins()]

        self.pins_by_name_and_idx = {}
        for pin in self.pins:
            assert isinstance(pin, Pin)
            key = (pin.name, pin.index)
            assert key not in self.pins_by_name_and_idx
            self.pins_by_name_and_idx[key] = pin

    def get_pin(self, name, index):
        return self.pins_by_name_and_idx[(name, index)]

    def num_wires(self):
        return len(list(self.library.get_wires()))

    def build_nets(self):
        """Setup Net objects"""
        # First construct net objects for each wire, skipping alias wires
        non_alias_wires = [wire for wire in self.library.get_wires() if not Net.wire_is_alias(wire)]
        for wire in non_alias_wires:
            net = Net(wire, self.tool)
            # self.tool.log(f"New Net for wire {wire.cable.name}[{wire.index()}]")
            self.wire_to_net[wire] = net

        # Now add alias wires iteratively until they are all added
        alias_wires = [wire for wire in self.library.get_wires() if Net.wire_is_alias(wire)]

        self.tool.log("Processing alias wires (derived from assign statements)")

        progress = True
        while alias_wires and progress:
            progress = False
            processed_alias_wires = []
            for wire in alias_wires:
                driver_wire = Net.wire_derived_from(wire)
                if driver_wire not in self.wire_to_net:
                    continue

                net = self.wire_to_net[driver_wire]
                # self.tool.log(
                #     f"Adding alias wire {wire.cable.name}[{wire.index()}]",
                #     f"to net {net.name}[{net.wire.index()}]",
                # )
                net.add_alias_wire(wire)
                self.wire_to_net[wire] = net
                processed_alias_wires.append(wire)

            # Remove wires we processed
            old_len = len(alias_wires)
            alias_wires = [wire for wire in alias_wires if wire not in processed_alias_wires]
            if len(alias_wires) != old_len:
                progress = True

        if alias_wires and not progress:
            self.tool.log(
                "Failed to process all alias wires:",
                [w.cable.name for w in alias_wires],
            )
            raise RuntimeError("Failed to process all alias wires")

        # Now determine the driver for each net
        for net in self.nets:
            net.find_driver()

        # Now determine whether they are connected
        for net in self.nets:
            net.determine_is_connected()

    @property
    def nets(self):
        return set(self.wire_to_net.values())

    def get_connected_nets(self):
        """Return a list of nets that are connected to something"""
        return [net for net in self.nets if net.is_connected]


class Pin:
    """Wrapper class around spydernet InnerPin/OuterPin to add some helper properties"""

    def __init__(self, pin, instance, netlist):
        self.pin = pin
        self.instance = instance
        self.netlist = netlist
        if isinstance(pin, sdn.OuterPin):
            self.name = self.pin.inner_pin.port.name
            self.index = self.pin.inner_pin.port.pins.index(self.pin.inner_pin)
            self.ignore_net_equivalency = False
        else:
            self.name = self.pin.port.name
            self.index = self.pin.port.pins.index(self.pin)
            self.ignore_net_equivalency = False

    def _ignore_net_equivalency(self):
        """Determines whether the net equivalency should be ignored on this pin."""
        # Ignore net equivalency on constant LUT inputs
        # The logic function PROBABLY doesn't depend on this LUT input
        # TODO: Verify this by looking at the LUT INIT
        # if instance.cell_type == "LUT6_2" and self.net and (self.net.is_vdd or self.net.is_gnd):
        #     return True
        return False

        # This didn't work unfortunately
        # if instance.cell_type == "LUT6_2":
        #     eqn = LUTTools.getLUTEquation(instance.properties["INIT"])
        #     self.log(instance.properties["INIT"])
        #     # self.log(eqn)
        #     return self.name not in eqn
        # return False

    @property
    def net(self):
        # self.log(self.instance.name, self.name, self.pin.wire)'
        return self.netlist.wire_to_net.get(self.pin.wire)

    @property
    def name_with_index(self):
        return f"{self.name}[{self.index}]"


class Net:
    """Wrapper class around spydernet Wire to add some helper properties"""

    def __init__(self, wire, tool):
        self.wire = wire
        self.tool = tool
        self.alias_wires = []
        self.driver_pin = None
        self.is_vdd = None
        self.is_gnd = None
        self.is_connected = None

    def add_alias_wire(self, wire):
        assert wire not in self.alias_wires
        self.alias_wires.append(wire)

    def determine_is_connected(self):
        """Determine if this net drives anything"""

        # Net needs a driver pin (except VDD/GND have implicit drivers)
        if not self.driver_pin and not self.is_vdd and not self.is_gnd:
            return False

        pins_that_drive = [
            p
            for wire in ([self.wire] + self.alias_wires)
            for p in wire.pins
            if p != self.driver_pin
            and (
                isinstance(p, sdn.InnerPin)
                or not p.instance.reference.name.startswith("SDN_VERILOG_ASSIGNMENT_1")
            )
        ]
        self.is_connected = bool(pins_that_drive)

    def find_driver(self):
        """Determine the pin that drives this wire"""

        # If wire is not connected to any pins, just return
        if not self.wire.pins:
            return

        # Find the pin that drives this wire
        for pin in self.wire.pins:
            # If connected to top-level input
            if isinstance(pin, sdn.ir.InnerPin):
                if pin.port.direction == sdn.ir.Port.Direction.IN:
                    self.set_driver_pin(pin)
                    return
            else:
                pin_direction = self.get_direction_for_unisim(
                    pin.instance.reference.name, pin.inner_pin.port.name
                )
                if pin_direction == sdn.ir.Port.Direction.OUT:
                    self.set_driver_pin(pin)
                    return

        # Check for const0/const1 that may not have any driver
        if self.wire.cable.name == r"\<const0>" or self.wire.cable.name in GND_NAMES:
            self.is_gnd = True
        elif self.wire.cable.name == r"\<const1>" or self.wire.cable.name in VCC_NAMES:
            self.is_vdd = True

    def set_driver_pin(self, pin):
        """Set the driver pin"""
        assert self.driver_pin is None
        self.driver_pin = pin

        # Check for constant GND/VDD.  Top-level I/O will not be GND/VDD
        if isinstance(pin, sdn.OuterPin) and self.driver_pin.instance.reference.name == "GND":
            self.is_gnd = True
        else:
            self.is_gnd = False
        if isinstance(pin, sdn.OuterPin) and self.driver_pin.instance.reference.name in (
            "VDD",
            "VCC",
        ):
            self.is_vdd = True
        else:
            self.is_vdd = False

    @property
    def name(self):
        if len(self.wire.cable.wires) > 1:
            return f"{self.wire.cable.name}[{self.wire.index()}]"
        return self.wire.cable.name

    @staticmethod
    def get_direction_for_unisim(cell_type_name, port_name):
        """Get a pin direction for a UNISIM cell"""

        if cell_type_name.startswith("SDN_VERILOG_ASSIGNMENT"):
            if port_name == "i":
                return sdn.ir.Port.Direction.IN
            # Shouldn't be possible to get here.  The way the code is set up, this function
            # is never called on alias wires (wires driven by assign statement)
            assert False

        return rw.get_sdn_direction_for_unisim(cell_type_name, port_name)

    # @staticmethod
    # def get_assign_statement(wire):
    #     """Check if a wire is connected to an assign statement and return the pin"""

    #     return None

    @staticmethod
    def wire_is_alias(wire):
        """Return whether wire is an alias of another wire (ie derived from assign statement)"""
        for pin in wire.pins:
            # assign statements don't have InnerPins
            if isinstance(pin, sdn.InnerPin):
                continue

            if (
                pin.instance.reference.name.startswith("SDN_VERILOG_ASSIGNMENT")
                and pin.inner_pin.port.name == "o"
            ):
                return True
        return False

    @staticmethod
    def wire_derived_from(wire):
        """If a wire is derived from another wire via assign statement, return the driver wire"""
        for pin in wire.pins:
            # assign statements don't have InnerPins
            if isinstance(pin, sdn.InnerPin):
                continue

            if (
                pin.instance.reference.name.startswith("SDN_VERILOG_ASSIGNMENT")
                and pin.inner_pin.port.name == "o"
            ):
                # Get the wire driving the assign statement
                if pin.inner_pin.port.name == list(pin.instance.pins)[0].inner_pin.port.name:
                    return list(pin.instance.pins)[1].wire
                return list(pin.instance.pins)[0].wire

        return None


class Instance:
    """Wrapper class around spydernet Instance to add some helper properties"""

    def __init__(self, instance, netlist):
        self.instance = instance
        self.netlist = netlist

        self.net_set = set()

        self.pins = []
        self.pins_by_name_and_index = {}

        for pin_spydernet in self.instance.pins:
            pin = Pin(pin_spydernet, self, self.netlist)
            global GND_PIN
            if GND_PIN is None and pin.net is not None and pin.net.is_gnd:
                GND_PIN = pin
            self.pins.append(pin)
            self.pins_by_name_and_index[
                (
                    pin_spydernet.inner_pin.port.name,
                    pin_spydernet.inner_pin.port.pins.index(pin_spydernet.inner_pin),
                )
            ] = pin

    def init_connectivity(self):
        """Initialize connectivity for this instance"""
        for pin in self.pins:
            if pin.net is not None:
                self.net_set.add(pin.net.name)

    @property
    def name(self):
        return self.instance.name

    @property
    def cell_type(self):
        return self.instance.reference.name

    @property
    def properties(self):
        return self.instance.data.get("VERILOG.Parameters")

    def get_pin(self, name, index):
        try:
            return self.pins_by_name_and_index[(name, index)]
        except KeyError:
            return GND_PIN
