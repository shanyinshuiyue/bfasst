import enum
import abc
import os
import pathlib
import shutil

import bfasst
from bfasst import flows
from bfasst.utils import TermColor, error
from enum import Enum


class Args(Enum):
    SYNTH_STAGE = 0
    IMPL_STAGE = 1
    MAP_STAGE = 2
    EQUIV_STAGE = 3


class State(Enum):
    INIT = 0
    READING_STAGE = 1
    READING_TOOL = 2


@enum.unique
class Flows(enum.Enum):
    IC2_LSE_CONFORMAL = "IC2_lse_conformal"
    IC2_SYNPLIFY_CONFORMAL = "IC2_synplify_conformal"
    SYNPLIFY_IC2_ONESPIN = "synplify_IC2_icestorm_onespin"
    YOSYS_TECH_LSE_CONFORMAL = "yosys_tech_lse_conformal"
    YOSYS_TECH_SYNPLIFY_CONFORMAL = "yosys_tech_synplify_conformal"
    YOSYS_TECH_SYNPLIFY_ONESPIN = "yosys_tech_synplify_onespin"
    YOSYS_SYNPLIFY_ERROR_ONESPIN = "yosys_synplify_error_onespin"
    XILINX_CONFORMAL_RTL = "xilinx_conformal"
    XILINX_CONFORMAL_IMPL = "xilinx_conformal_impl"
    XILINX_YOSYS_IMPL = "xilinx_yosys_impl"
    XILINX_YOSYS_WAVEFORM = "xilinx_yosys_waveform"
    GATHER_IMPL_DATA = "gather_impl_data"
    CONFORMAL_ONLY = "conformal_only"
    XILINX = "xilinx"


# This uses a lambda so that I don't have to define all of the functions before this point
flow_fcn_map = {
    Flows.IC2_LSE_CONFORMAL: lambda: flow_ic2_lse_conformal,
    Flows.IC2_SYNPLIFY_CONFORMAL: lambda: flow_ic2_synplify_conformal,
    Flows.YOSYS_TECH_LSE_CONFORMAL: lambda: flow_yosys_tech_lse_conformal,
    Flows.YOSYS_TECH_SYNPLIFY_CONFORMAL: lambda: flow_yosys_tech_synplify_conformal,
    Flows.SYNPLIFY_IC2_ONESPIN: lambda: flow_synplify_ic2_icestorm_onespin,
    Flows.YOSYS_TECH_SYNPLIFY_ONESPIN: lambda: flow_yosys_tech_synplify_onespin,
    Flows.YOSYS_SYNPLIFY_ERROR_ONESPIN: lambda: flow_yosys_synplify_error_onespin,
    Flows.XILINX_CONFORMAL_RTL: lambda: flow_xilinx_conformal,
    Flows.XILINX_CONFORMAL_IMPL: lambda: flow_xilinx_conformal_impl,
    Flows.XILINX_YOSYS_IMPL: lambda: flow_xilinx_yosys_impl,
    Flows.XILINX_YOSYS_WAVEFORM: lambda: flow_xilinx_yosys_waveform,
    Flows.GATHER_IMPL_DATA: lambda: flow_gather_impl_data,
    Flows.CONFORMAL_ONLY: lambda: flow_conformal_only,
    Flows.XILINX: lambda: flow_xilinx,
}


class Vendor(enum.Enum):
    LATTICE = 1
    XILINX = 2


def get_flow_fcn_by_name(flow_name):
    try:
        flow_enum = Flows(flow_name)
    except ValueError:
        error(flow_name, "is not a valid flow name")

    fcn = flow_fcn_map[flow_enum]()
    return fcn


def run_flow(design, flow_type, build_dir, print_to_stdout=True):
    assert type(design) is bfasst.design.Design

    flow_fcn = flows.get_flow_fcn_by_name(flow_type)
    return flow_fcn(design, build_dir, print_to_stdout)


def flow_ic2_lse_conformal(design, build_dir):
    # Run Icecube2 LSE synthesis
    synth_tool = bfasst.synth.ic2_lse.IC2_LSE_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design)
    

    # Run Icecube2 implementations
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design)
    

    # Run conformal
    design.compare_golden_files.append(design.top_file)
    design.compare_golden_files.extend(design.get_support_files())
    design.compare_golden_files_paths.append(design.full_path / design.top_file)
    design.compare_golden_files_paths.extend(
        [design.full_path / f for f in design.get_support_files()]
    )
    design.golden_is_verilog = design.top_is_verilog()
    compare_tool = bfasst.compare.conformal.Conformal_CompareTool(build_dir)
    status = None
    with bfasst.conformal_lock:
        status = compare_tool.compare_netlists(design)
    

    return status


def flow_conformal_only(design, flow_args, build_dir, print_to_stdout=True):
    assert(design.netlist_path is not None)
    assert(design.reversed_netlist_path is not None)

    design.golden_sources = [design.netlist_path,]
    compare_tool = bfasst.compare.conformal.Conformal_CompareTool(build_dir, Vendor.XILINX)
    with bfasst.conformal_lock:
        status = compare_tool.compare_netlists(design, print_to_stdout)
    

    return status

def flow_xilinx(design, flow_args, build_dir, print_to_stdout=True):
    # Run Xilinx synthesis and implementation
    synth_tool = bfasst.synth.vivado.Vivado_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design, print_to_stdout)
    

    impl_tool = bfasst.impl.vivado.Vivado_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design, print_to_stdout)
    

def flow_xilinx_conformal(design, flow_args, build_dir, print_to_stdout=True):
    # Run Xilinx synthesis and implementation
    synth_tool = bfasst.synth.vivado.Vivado_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design, print_to_stdout)
    

    impl_tool = bfasst.impl.vivado.Vivado_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design, print_to_stdout)
    

    reverse_bit_tool = bfasst.reverse_bit.xray.XRay_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design, print_to_stdout)
    

    compare_tool = bfasst.compare.conformal.Conformal_CompareTool(build_dir, Vendor.XILINX)
    with bfasst.conformal_lock:
        status = compare_tool.compare_netlists(design, print_to_stdout)
    

    return status

def flow_xilinx_conformal_impl(design, flow_args, build_dir, print_to_stdout=True):
    # Parse the arguments used for the different stages of the flow
    args = parse_flow_args(flow_args)

    # Run Xilinx synthesis and implementation
    synth_tool = bfasst.synth.vivado.Vivado_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design, print_to_stdout)
    
    impl_tool = bfasst.impl.vivado.Vivado_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design, print_to_stdout)
    

    # Run X-ray and fasm2bel
    reverse_bit_tool = bfasst.reverse_bit.xray.XRay_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design, print_to_stdout)
    

    # Use conformal to compare against IMPL netlist
    design.golden_sources = [design.impl_netlist_path,]
    compare_tool = bfasst.compare.conformal.Conformal_CompareTool(build_dir, Vendor.XILINX)
    with bfasst.conformal_lock:
        status = compare_tool.compare_netlists(design, args[Args.MAP_STAGE.value], print_to_stdout)
    if status.error:
        return status

    return status

def flow_xilinx_yosys_impl(design, flow_args, build_dir, print_to_stdout=True):
    # Run Xilinx synthesis and implementation
    synth_tool = bfasst.synth.vivado.Vivado_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design, print_to_stdout)
    
    impl_tool = bfasst.impl.vivado.Vivado_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design, print_to_stdout)
    

    # Run X-ray and fasm2bel
    reverse_bit_tool = bfasst.reverse_bit.xray.XRay_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design, print_to_stdout)
    

    compare_tool = bfasst.compare.yosys.Yosys_CompareTool(build_dir)
    status = compare_tool.compare_netlists(design, print_to_stdout)
    
    
    return status

def flow_xilinx_yosys_waveform(design, build_dir, print_to_stdout=True):
    # Run Xilinx synthesis and implementation
    synth_tool = bfasst.synth.vivado.Vivado_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design, print_to_stdout)
    
    impl_tool = bfasst.impl.vivado.Vivado_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design, print_to_stdout)
    

    # Run X-ray and fasm2bel
    reverse_bit_tool = bfasst.reverse_bit.xray.XRay_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design, print_to_stdout)
    

    compare_tool = bfasst.compare.waveform.Waveform_CompareTool(build_dir)
    status = compare_tool.compare_netlists(design, print_to_stdout)
    
    
    return status


def flow_ic2_synplify_conformal(design, flow_args, build_dir):
    # Run Icecube2 Synplify synthesis
    synth_tool = bfasst.synth.ic2_synplify.IC2_Synplify_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design)
    

    # Run Icecube2 implementations
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design)
    

    # Run conformal
    design.compare_golden_files.append(design.top_file)
    design.compare_golden_files.extend(design.get_support_files())
    design.compare_golden_files_paths.append(design.full_path / design.top_file)
    design.compare_golden_files_paths.extend(
        [design.full_path / f for f in design.get_support_files()]
    )
    design.golden_is_verilog = design.top_is_verilog()
    compare_tool = bfasst.compare.conformal.Conformal_CompareTool(build_dir)
    with bfasst.conformal_lock:
        status = compare_tool.compare_netlists(design)
    

    return status


def flow_synplify_ic2_icestorm_onespin(design, flow_args, build_dir):
    # Run Icecube2 Synplify synthesis
    synth_tool = bfasst.synth.ic2_synplify.IC2_Synplify_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design)
    

    # Run Icecube2 implementations
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design)
    

    # Run conformal
    design.compare_golden_files.append(design.top_file)
    design.compare_golden_files.extend(design.get_support_files())
    design.compare_golden_files_paths.append(design.full_path / design.top_file)
    design.compare_golden_files_paths.extend(
        [design.full_path / f for f in design.get_support_files()]
    )
    design.golden_is_verilog = design.top_is_verilog()

    compare_tool = bfasst.compare.onespin.OneSpin_CompareTool(build_dir)
    with bfasst.onespin_lock:
        status = compare_tool.compare_netlists(design)
    

    return status


def flow_yosys_tech_lse_conformal(design, flow_args, build_dir):
    # Run the Yosys synthesizer
    yosys_synth_tool = bfasst.synth.yosys.Yosys_Tech_SynthTool(build_dir)
    status = yosys_synth_tool.create_netlist(design)
    

    # Now run the LSE synthesizer on the Yosys output
    yosys_netlist_path = design.netlist_path
    design.compare_golden_files.append(yosys_netlist_path.name)
    design.compare_golden_files_paths.append(yosys_netlist_path)
    design.golden_is_verilog = True
    lse_opt_tool = bfasst.opt.ic2_lse.IC2_LSE_OptTool(build_dir)
    status = lse_opt_tool.create_netlist(design, [str(yosys_netlist_path)], [])
    

    # Try fixing the netlist LUT inits (there's some issue with how LSE
    #   generates them)
    lse_opt_tool.fix_lut_inits(design)

    # Run IC2 Implementation
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design)
    

    # Run conformal
    compare_tool = bfasst.compare.conformal.Conformal_CompareTool(build_dir)
    with bfasst.conformal_lock:
        status = compare_tool.compare_netlists(design)
    

    return status


def flow_yosys_tech_synplify_conformal(design, flow_args, build_dir):
    # Run the Yosys synthesizer
    yosys_synth_tool = bfasst.synth.yosys.Yosys_Tech_SynthTool(build_dir)
    status = yosys_synth_tool.create_netlist(design)
    

    # Now run the Synplify synthesizer on the Yosys output
    yosys_netlist_path = design.netlist_path
    design.compare_golden_files.append(yosys_netlist_path.name)
    design.compare_golden_files_paths.append(yosys_netlist_path)
    design.golden_is_verilog = True
    synp_opt_tool = bfasst.opt.ic2_synplify.IC2_Synplify_OptTool(build_dir)
    status = synp_opt_tool.create_netlist(design, [str(yosys_netlist_path)], [])
    

    # Run IC2 Implementation
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    # Now actually reverse the bitstream
    status = reverse_bit_tool.reverse_bitstream(design)
    

    # Run conformal
    compare_tool = bfasst.compare.conformal.Conformal_CompareTool(build_dir)
    with bfasst.conformal_lock:
        status = compare_tool.compare_netlists(design)
    

    return status


def flow_yosys_tech_synplify_onespin(design, flow_args, build_dir):
    # Run the Yosys synthesizer
    yosys_synth_tool = bfasst.synth.yosys.Yosys_Tech_SynthTool(build_dir)
    status = yosys_synth_tool.create_netlist(design)
    

    # Now run the Synplify synthesizer on the Yosys output
    yosys_netlist_path = design.netlist_path
    design.compare_golden_files.append(yosys_netlist_path.name)
    design.compare_golden_files_paths.append(yosys_netlist_path)
    design.golden_is_verilog = True
    synp_opt_tool = bfasst.opt.ic2_synplify.IC2_Synplify_OptTool(build_dir)
    status = synp_opt_tool.create_netlist(design, [str(yosys_netlist_path)], [])
    

    # Run IC2 Implementation
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    # Now actually reverse the bitstream
    status = reverse_bit_tool.reverse_bitstream(design)
    

    design.compare_revised_file = design.reversed_netlist_filename()
    compare_tool = bfasst.compare.onespin.OneSpin_CompareTool(build_dir)
    with bfasst.onespin_lock:
        status = compare_tool.compare_netlists(design)
    

    return status


def flow_yosys_synplify_error_onespin(design, flow_args, build_dir):
    # Set the results file path so it can be used in the different tools
    design.results_summary_path = build_dir / "results_summary.txt"

    # Run the Yosys synthesizer
    yosys_synth_tool = bfasst.synth.yosys.Yosys_Tech_SynthTool(build_dir)
    status = yosys_synth_tool.create_netlist(design)
    

    # Run error injection
    error_inj_tool = bfasst.error_injection.error_injector.ErrorInjector_ErrorInjectionTool(
        build_dir
    )
    ret = error_inj_tool.run_error_flows(design)
    status = ret[0]
    

    # Run Synth, impl, and icestorm on the original netlist
    # Now run the Synplify synthesizer on the Yosys output
    yosys_netlist_path = design.netlist_path
    design.compare_golden_files.append(yosys_netlist_path.name)
    design.compare_golden_files_paths.append(yosys_netlist_path)
    design.golden_is_verilog = True
    synp_opt_tool = bfasst.opt.ic2_synplify.IC2_Synplify_OptTool(build_dir)
    status = synp_opt_tool.create_netlist(design, [str(yosys_netlist_path)], [])
    

    # Run IC2 Implementation
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    print(status)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    # Now actually reverse the bitstream
    status = reverse_bit_tool.reverse_bitstream(design)
    

    compare_tool = bfasst.compare.onespin.OneSpin_CompareTool(build_dir)
    design.compare_revised_file = design.reversed_netlist_filename()
    with bfasst.onespin_lock:
        status = compare_tool.compare_netlists(design)

    # Also use the compare tool to make a compare script for rtl to yosys
    design.compare_revised_file = yosys_netlist_path.name
    design.compare_golden_files = design.get_support_files()
    design.compare_golden_files.append(pathlib.Path(design.top_path()).name)
    compare_tool = bfasst.compare.onespin.OneSpin_CompareTool(build_dir)
    with bfasst.onespin_lock:
        status = compare_tool.compare_netlists(design)

    # Run synth, impl, icestorm, and onespin on each corrupted netlist
    design.compare_golden_files = [yosys_netlist_path.name]
    design.compare_golden_files_paths = [yosys_netlist_path]
    for netlist_name_tuple in ret[1]:
        netlist = netlist_name_tuple[0]
        error_flow_name = netlist_name_tuple[1]
        design.cur_error_flow_name = error_flow_name

        # Now run the Synplify synthesizer on the Yosys output
        design.golden_is_verilog = True
        # Blow away the opt dir so we know we're getting a fresh build
        shutil.rmtree(synp_opt_tool.work_dir)
        synp_opt_tool = bfasst.opt.ic2_synplify.IC2_Synplify_OptTool(build_dir)
        status = synp_opt_tool.create_netlist(design, [str(netlist)], [])

        # Run IC2 Implementation
        shutil.rmtree(impl_tool.work_dir)
        impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
        status = impl_tool.implement_bitstream(design)

        # Run icestorm bitstream reversal
        shutil.rmtree(reverse_bit_tool.work_dir)
        reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
        # Now actually reverse the bitstream
        status = reverse_bit_tool.reverse_bitstream(design)

        # Run compare to create a onespin tcl for yosys->corrupt reversed netlist
        compare_tool = bfasst.compare.onespin.OneSpin_CompareTool(build_dir)
        design.compare_revised_file = design.reversed_netlist_filename()
        with bfasst.onespin_lock:
            status = compare_tool.compare_netlists(design)

        # Run compare again so we can check yosys netlist -> corrupt yosys
        #   netlist
        # This lets us make sure that any compare errors are because of the
        #   netlist corruption, and not some other issue
        design.compare_revised_file = netlist.name
        with bfasst.onespin_lock:
            status = compare_tool.compare_netlists(design)

    # Write the python script to run all of the compare tcl scripts
    compare_tool.write_compare_script(design)

    return status


def flow_gather_impl_data(design, flow_args, build_dir):
    # This flow is mainly to try running the tools with different synthesis/
    #   implementation (e.g. synplify vs yosys, etc.) options to compare their
    #   physical results (e.g. LUT counts, FF counts, etc)

    # Set the results file path so it can be used in the different tools
    design.results_summary_path = build_dir / "results_summary.txt"

    # Start with an RTL->Synplify->IC2->Icestorm flow
    # Run Icecube2 Synplify synthesis
    synth_tool = bfasst.synth.ic2_synplify.IC2_Synplify_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design)
    

    # Run Icecube2 implementations
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design)
    

    # Clean up project directories so we get fresh results later
    if synth_tool.opt_tool is not None:
        shutil.rmtree(synth_tool.opt_tool.work_dir)
    shutil.rmtree(synth_tool.work_dir)
    shutil.rmtree(impl_tool.work_dir)
    shutil.rmtree(reverse_bit_tool.work_dir)

    # Now do RTL->LSE->IC2->Icestorm
    # Run Icecube2 LSE synthesis
    synth_tool = bfasst.synth.ic2_lse.IC2_LSE_SynthesisTool(build_dir)
    status = synth_tool.create_netlist(design)
    

    # Run Icecube2 implementations
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design)
    

    # Clean up project directories so we get fresh results later
    if synth_tool.opt_tool is not None:
        shutil.rmtree(synth_tool.opt_tool.work_dir)
    shutil.rmtree(synth_tool.work_dir)
    shutil.rmtree(impl_tool.work_dir)
    shutil.rmtree(reverse_bit_tool.work_dir)

    # Now do Yosys->Synplify->IC2->Icestorm
    # Run the Yosys synthesizer
    yosys_synth_tool = bfasst.synth.yosys.Yosys_Tech_SynthTool(build_dir)
    status = yosys_synth_tool.create_netlist(design)
    

    # Now run the Synplify synthesizer on the Yosys output
    yosys_netlist_path = design.netlist_path
    synp_opt_tool = bfasst.opt.ic2_synplify.IC2_Synplify_OptTool(build_dir)
    status = synp_opt_tool.create_netlist(design, [str(yosys_netlist_path)], [])
    

    # Run IC2 Implementation
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    # Now actually reverse the bitstream
    status = reverse_bit_tool.reverse_bitstream(design)
    

    # Clean up project directories so we get fresh results later
    shutil.rmtree(synp_opt_tool.work_dir)
    shutil.rmtree(impl_tool.work_dir)
    shutil.rmtree(reverse_bit_tool.work_dir)

    # Now do Yosys->LSE->IC2->Icestorm
    # Run the Yosys synthesizer
    yosys_synth_tool = bfasst.synth.yosys.Yosys_Tech_SynthTool(build_dir)
    status = yosys_synth_tool.create_netlist(design)
    

    # Now run the LSE synthesizer on the Yosys output
    yosys_netlist_path = design.netlist_path
    lse_opt_tool = bfasst.opt.ic2_lse.IC2_LSE_OptTool(build_dir)
    status = lse_opt_tool.create_netlist(design, [str(yosys_netlist_path)], [])
    

    # Try fixing the netlist LUT inits (there's some issue with how LSE
    #   generates them)
    lse_opt_tool.fix_lut_inits(design)

    # Run IC2 Implementation
    impl_tool = bfasst.impl.ic2.IC2_ImplementationTool(build_dir)
    status = impl_tool.implement_bitstream(design)
    

    # Run icestorm bitstream reversal
    reverse_bit_tool = bfasst.reverse_bit.icestorm.Icestorm_ReverseBitTool(build_dir)
    status = reverse_bit_tool.reverse_bitstream(design)
    

    return status
