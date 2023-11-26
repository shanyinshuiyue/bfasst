"""Flow to compare reversed netlist to original using yosys."""
import pathlib

from bfasst.ninja_flows.flow import Flow
from bfasst.ninja_tools.impl.vivado_impl import VivadoImpl
from bfasst.ninja_tools.compare.yosys.yosys import Yosys
from bfasst.ninja_tools.rev_bit.xray import Xray
from bfasst.ninja_tools.synth.vivado_synth import VivadoSynth
from bfasst.utils.general import ensure


class VivadoYosysImpl(Flow):
    """Flow to compare reversed netlist to original using yosys."""

    def __init__(self, design, flow_args=None):
        super().__init__(design)
        self.vivado_synth_tool = VivadoSynth(self, design, ensure(flow_args, {}).get("synth"))
        self.vivado_impl_tool = VivadoImpl(self, design)
        self.xrev_tool = Xray(self, design)
        self.yosys_tool = Yosys(self, design)

    def create_build_snippets(self):
        self.vivado_synth_tool.create_build_snippets()
        self.vivado_impl_tool.create_build_snippets()
        self.xrev_tool.create_build_snippets(str(self.vivado_impl_tool.outputs["bitstream"]))
        self.yosys_tool.create_build_snippets(
            gold_netlist=self.vivado_impl_tool.outputs["impl_verilog"],
            rev_netlist=self.xrev_tool.outputs["xray_netlist"],
        )

    def get_top_level_flow_path(self):
        return pathlib.Path(__file__).parent / "vivado_yosys_impl.py"
