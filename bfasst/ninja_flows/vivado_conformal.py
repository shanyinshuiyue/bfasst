"""Run vivado, phys_netlist, reverse with xray, then compare with conformal."""

from bfasst.ninja_flows.flow import Flow
from bfasst.ninja_tools.impl.vivado_impl import VivadoImpl
from bfasst.ninja_tools.compare.conformal.conformal import Conformal
from bfasst.ninja_tools.rev_bit.xray import Xray
from bfasst.paths import NINJA_FLOWS_PATH
from bfasst.types import Vendor
from bfasst.ninja_tools.synth.vivado_synth import VivadoSynth
from bfasst.utils.general import ensure


class VivadoConformal(Flow):
    """Run vivado, phys_netlist, reverse with xray, then compare with conformal."""

    def __init__(self, design, flow_args=None):
        super().__init__(design)
        self.vivado_synth_tool = VivadoSynth(self, design, ensure(flow_args, {}).get("synth"))
        self.vivado_impl_tool = VivadoImpl(self, design)
        self.xrev_tool = Xray(self, design)
        self.conformal_tool = Conformal(self, design)

    def create_rule_snippets(self):
        self.vivado_synth_tool.create_rule_snippets()
        self.vivado_impl_tool.create_rule_snippets()
        self.xrev_tool.create_rule_snippets()
        self.conformal_tool.create_rule_snippets()

    def create_build_snippets(self):
        self.vivado_synth_tool.create_build_snippets()
        self.vivado_impl_tool.create_build_snippets()
        self.xrev_tool.create_build_snippets(str(self.vivado_impl_tool.outputs["bitstream"]))
        self.conformal_tool.create_build_snippets(
            impl_netlist=str(self.vivado_impl_tool.outputs["impl_verilog"]),
            rev_netlist=str(self.xrev_tool.outputs["xray_netlist"]),
            vendor=Vendor.XILINX,
        )

    def add_ninja_deps(self, deps):
        self.vivado_synth_tool.add_ninja_deps(deps)
        self.vivado_impl_tool.add_ninja_deps(deps)
        self.xrev_tool.add_ninja_deps(deps)
        self.conformal_tool.add_ninja_deps(deps)
        deps.append(NINJA_FLOWS_PATH / "vivado_conformal.py")

    def get_top_level_flow_path(self) -> str:
        return NINJA_FLOWS_PATH / "vivado_conformal.py"
