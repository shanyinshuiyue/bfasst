"""Create the rule and build snippets for yosys comparison."""

import json
import chevron
from bfasst.ninja_tools.tool import Tool
from bfasst.paths import NINJA_BUILD_PATH, NINJA_UTILS_PATH, NINJA_YOSYS_TOOLS_PATH
from bfasst.utils.general import compare_json


class Yosys(Tool):
    """Create the rule and build snippets for yosys comparison."""

    def __init__(self, design):
        super().__init__(design)
        self.build_path = self.design_build_path / "yosys"
        self.log = self.build_path / "log.txt"
        self.json = self.build_path / "yosys.json"
        self.tcl = self.build_path / "compare.ys"
        self.tcl_template = NINJA_YOSYS_TOOLS_PATH / "yosys.tcl.mustache"
        self.rules_template = NINJA_YOSYS_TOOLS_PATH / "yosys_rules.ninja.mustache"
        self.build_template = NINJA_YOSYS_TOOLS_PATH / "yosys_build.ninja.mustache"
        self._create_build_dir()
        self._init_outputs()

    def create_rule_snippets(self):
        with open(self.rules_template, "r") as f:
            rules = chevron.render(f, {"utils": str(NINJA_UTILS_PATH)})

        with open(NINJA_BUILD_PATH, "a") as f:
            f.write(rules)

    def create_build_snippets(self, gold_netlist, rev_netlist):
        self.__write_json_file(gold_netlist, rev_netlist)
        self.__append_build_snippets(gold_netlist, rev_netlist)

    def __write_json_file(self, gold_netlist, rev_netlist):
        """Specify netlists for tcl template in json file.
        Chevron will use the file to create a yosys tcl script."""
        yosys_tcl_args = {
            "gold_netlist": str(gold_netlist),
            "rev_netlist": str(rev_netlist),
        }
        yosys_json = json.dumps(yosys_tcl_args, indent=4)

        # check if the json file already exists and compare it to what we're about to write
        json_equivalent = compare_json(self.json, yosys_json)

        if not json_equivalent:
            with open(self.json, "w") as f:
                f.write(yosys_json)

    def __append_build_snippets(self, gold_netlist, rev_netlist):
        """Create ninja snippets for yosys comparison."""
        with open(self.build_template, "r") as f:
            build = chevron.render(
                f,
                {
                    "tcl_script": str(self.tcl),
                    "json": str(self.json),
                    "tcl_template": str(self.tcl_template),
                    "log": str(self.log),
                    "gold_netlist": str(gold_netlist),
                    "rev_netlist": str(rev_netlist),
                },
            )

        with open(NINJA_BUILD_PATH, "a") as f:
            f.write(build)

    def _init_outputs(self):
        self.outputs["yosys_log"] = self.log
        self.outputs["yosys_json"] = self.json
        self.outputs["yosys_tcl"] = self.tcl

    def add_ninja_deps(self, deps):
        """Add the yosys ninja deps for the configure rule."""
        self._add_ninja_deps_default(deps, __file__)
        deps.append(self.tcl_template)
