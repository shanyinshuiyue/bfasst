"""Tool to inject errors into a netlist"""
from enum import Enum
from random import randrange, sample
import spydrnet as sdn
from bfasst.transform.base import TransformTool
from bfasst.status import Status, TransformStatus
from bfasst.utils import convert_verilog_literal_to_int


class ErrorType(Enum):
    """Types of errors that can be injected"""

    BIT_FLIP = "BIT_FLIP"
    WIRE_SWAP = "WIRE_SWAP"


class ErrorInjector(TransformTool):
    """Tool to inject errors into a netlist"""

    success_status = Status(TransformStatus.SUCCESS)
    TOOL_WORK_DIR = "error_injection"

    def __init__(self, cwd, design) -> None:
        super().__init__(cwd, design)
        self.clean_netlist = sdn.parse(self.design.reversed_netlist_path)
        self.hierarchical_luts = []
        self.all_luts = None

    def inject(self, error_type):
        """Injects an error into the netlist of the given type"""
        if error_type == ErrorType.BIT_FLIP:
            self.inject_bit_flip()
        elif error_type == ErrorType.WIRE_SWAP:
            self.inject_wire_swap()
        else:
            return Status(TransformStatus.ERROR, "Invalid error type")
        return Status(TransformStatus.SUCCESS)

    def inject_bit_flip(self):
        """Injects a bit flip error into the netlist"""
        num_luts = self.pick_luts_from_netlist()
        self.get_all_luts()
        lut_number = randrange(num_luts)
        lut_size = self.get_lut_init_size(lut_number)
        bit_number = randrange(lut_size)
        self.flip_bit(lut_number, bit_number)
        self.compose_corrupt_netlist()

    def pick_luts_from_netlist(self):
        """Calculates the number of LUTs in the netlist"""
        num_luts = 0
        for library in self.clean_netlist.libraries:
            for definition in library.definitions:
                if "LUT" in definition.name.upper():
                    num_luts += len(definition.references)
                    self.hierarchical_luts.append(definition.references)
        return num_luts

    def get_all_luts(self):
        """Flattens the LUTs into a single list"""
        self.all_luts = [lut for sublist in self.hierarchical_luts for lut in sublist]

    def get_lut_init_size(self, lut_number):
        """
        Gets the size of the LUT init string for the given LUT by reading the init string.
        The init string is "X'h####" where X is the size of the LUT init string in bits.
        X is always 2^n where n is the number of inputs to the LUT.
        For example, a LUT5 would have an init string of "32'h####"
        and this function would return 32 as the size.
        """
        lut = self.all_luts[lut_number]
        init_string = lut.data["VERILOG.Parameters"]["INIT"].upper()
        return int(init_string.split("'")[0])

    def flip_bit(self, lut_number, bit_number):
        """Flips the bit at the given index"""
        lut = self.all_luts[lut_number]
        lut_properties = lut.data["VERILOG.Parameters"]

        config_string_prefixed = lut_properties["INIT"].lower() # must be lower for int conversion
        config_string_int = convert_verilog_literal_to_int(config_string_prefixed)

        new_config = hex(config_string_int ^ (1 << bit_number))
        lut_properties["INIT"] = (
            config_string_prefixed.split("H")[0] + "h" + str(new_config).upper()[2:]
        )

    def compose_corrupt_netlist(self):
        """Writes the netlist to the corrupted netlist path in the design"""
        sdn.compose(self.clean_netlist, self.design.corrupted_netlist_path)

    def inject_wire_swap(self):
        """Injects a wire swap error into the netlist"""

        # Pick three random instances
        three_instances = self.get_random_instances(3)
        # Get the outer pins of the first instance that are inputs
        first_instance_pins = self.get_outer_pin_inputs(three_instances[0])

        # Pick a random input from the first instance
        selected_input = first_instance_pins[randrange(len(first_instance_pins))]
        # Get the source of the input
        driving_pin = self.get_source(selected_input)
        # Get a new driver for the input. It will be an output pin of one of the other two instances
        # that is not already driving the input.
        new_driver = self.get_new_driver(driving_pin, three_instances[1], three_instances[2])

        self.detach_wire(selected_input)
        self.attach_wire(selected_input, new_driver)

        self.compose_corrupt_netlist()

    def get_random_instances(self, num_instances):
        """Gets a list of random instances from the netlist"""
        instances = [
            instance
            for instance in self.clean_netlist.get_instances()
            if "GND" not in instance.reference.name.upper()
            and "VCC" not in instance.reference.name.upper()
            and "VDD" not in instance.reference.name.upper()
        ]
        return sample(instances, num_instances)

    def get_outer_pin_inputs(self, instance):
        """Gets all the outer pins of the given instance that are inputs"""
        outer_pin_inputs = [pin for pin in instance.pins if pin.inner_pin.port.direction is sdn.IN]
        if not outer_pin_inputs:
            outer_pin_inputs = self.get_unisim_outer_pin_inputs(instance)

        return outer_pin_inputs

    def get_unisim_outer_pin_inputs(self, instance):
        """Collect all the pins for a UNISIM cell that are inputs"""

        cell_inputs = (
            (("LUT6_2",), ("I0", "I1", "I2", "I3", "I4", "I5")),
            (("IBUF", "OBUF", "OBUFT"), ("I", "T")),
            (("GND",), ()),
            (("VCC",), ()),
            (("FDSE", "FDRE"), ("D", "CE", "R", "C", "S")),
            (("CARRY4",), ("CI", "CYINIT", "DI", "S")),
            (("BUFGCTRL",), ("CE0", "CE1", "I0", "I1", "IGNORE0", "IGNORE1", "S0", "S1")),
            (("MUXF7", "MUXF8"), ("I0", "I1", "S")),
        )

        outer_pin_inputs = []
        for name, inputs in cell_inputs:
            if instance.reference.name in name:
                pins = list(instance.pins)
                for pin in pins:
                    if pin.inner_pin.port.name in inputs:
                        outer_pin_inputs.append(pin)

        return outer_pin_inputs

    def get_outer_pin_outputs(self, instance):
        """Gets all the outer pins of the given instance that are outputs"""
        outer_pin_outputs = [
            pin for pin in instance.pins if pin.inner_pin.port.direction is sdn.OUT
        ]
        if not outer_pin_outputs:
            outer_pin_outputs = self.get_unisim_outer_pin_outputs(instance)

        return outer_pin_outputs

    def get_unisim_outer_pin_outputs(self, instance):
        """Collect all the pins for a UNISIM cell that are outputs"""

        cell_outputs = (
            (("LUT6_2",), ("O5", "O6")),
            (("IBUF", "OBUF", "OBUFT"), ("O",)),
            (("GND",), ("G",)),
            (("VCC",), ("P",)),
            (("FDSE", "FDRE"), ("Q",)),
            (("CARRY4",), ("O", "CO")),
            (("BUFGCTRL",), ("O",)),
            (("MUXF7", "MUXF8"), ("O",)),
        )

        outer_pin_outputs = []
        for name, outputs in cell_outputs:
            if instance.reference.name in name:
                pins = list(instance.pins)
                for pin in pins:
                    if pin.inner_pin.port.name in outputs:
                        outer_pin_outputs.append(pin)

        return outer_pin_outputs

    def get_source(self, pin):
        """Gets the source pin of the given pin. The pin must be a sink pin."""
        sources = [pin for pin in pin.wire.pins if pin.inner_pin.port.direction is sdn.OUT]
        if sources:
            return sources[0]
        return None

    def get_new_driver(self, driving_pin, instance_2, instance_3):
        """Gets the new driver for the given driving pin"""
        if driving_pin in instance_2.pins:
            return self.get_outer_pin_outputs(instance_3)[0]

        return self.get_outer_pin_outputs(instance_2)[0]

    def detach_wire(self, pin):
        """Detaches the wire from the given pin"""
        pin.wire.disconnect_pin(pin)

    def attach_wire(self, sink_pin, new_driver):
        """Attaches the given sink to the new_driver"""
        new_driver.wire.connect_pin(sink_pin)
