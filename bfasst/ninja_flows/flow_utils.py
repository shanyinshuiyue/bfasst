"""Utility methods for getting flows"""
from importlib import import_module
from pathlib import Path

from bfasst.paths import NINJA_BUILD_PATH


def get_flows():
    """Get all flows in the flows directory"""
    special_names = ["__init__", "flow_utils", "flow", "ninja_flow_manager", "vivado_phys_netlist"]
    flows = [
        flow.stem for flow in Path(__file__).parent.glob("*.py") if flow.stem not in special_names
    ]
    return flows


def get_flow(flow_name):
    """Get a flow by name"""
    flow_module = import_module(f"bfasst.ninja_flows.{flow_name}")
    flow_class = "".join(word.capitalize() for word in flow_name.split("_"))
    return getattr(flow_module, flow_class)


def create_build_file():
    """Overwrite the build.ninja file when running generation and build steps separately"""
    with open(NINJA_BUILD_PATH, "w") as f:
        f.write("# This file is autogenerated by bfasst\n\n")
