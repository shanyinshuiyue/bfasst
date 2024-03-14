"""Create the rule and build snippets for structural comparison."""

from bfasst.tools.tool import Tool
from bfasst.paths import BFASST_UTILS_PATH


class Structural(Tool):
    """Create the rule and build snippets for structural comparison."""

    def __init__(self, flow, design, log_name, golden_netlist, rev_netlist, expect_fail=False):
        super().__init__(flow, design)
        self.build_path = self.design_build_path / "struct_cmp"
        self.log_name = log_name
        self.golden_netlist = golden_netlist
        self.rev_netlist = rev_netlist
        self.expect_fail = expect_fail
        self._init_outputs()

    def create_rule_snippets(self):
        self._append_rule_snippets_default(__file__)

    def create_build_snippets(self):
        self._append_build_snippets_default(
            __file__,
            render_dict={
                "netlist_a": str(self.golden_netlist),
                "netlist_b": str(self.rev_netlist),
                "log_path": str(self.outputs["structural_log"]),
                "compare_script_path": str(BFASST_UTILS_PATH / "structural.py"),
                "expect_fail": "--expect_fail" if self.expect_fail else "",
            },
        )

    def _init_outputs(self):
        self.outputs["structural_log"] = self.build_path / self.log_name

    def add_ninja_deps(self, deps):
        self._add_ninja_deps_default(deps, __file__)
        deps.append(BFASST_UTILS_PATH / "structural.py")

    @staticmethod
    def get_build_path(design):
        return design.design_build_path / "struct_cmp"
