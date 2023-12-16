"""Tool for dumping the bels of a placed and routed design with Isoblaze"""
import chevron
from bfasst.tools.tool import ToolBase
from bfasst.paths import (
    BFASST_UTILS_PATH,
    DUMP_TOOL_BUILD_PATH,
    ISOBLAZE_DUMP_BUILD_PATH,
    NINJA_BUILD_PATH,
    RAND_SOC_BUILD_PATH,
)


class IsoblazeDump(ToolBase):
    """Tool for dumping the bels of a placed and routed design with Isoblaze"""

    def __init__(self, flow, num_designs):
        super().__init__(flow)

        self.build_path = DUMP_TOOL_BUILD_PATH
        self.num_designs = num_designs
        self._init_outputs()

    def _init_outputs(self):
        self.outputs["isoblaze_dump_output"] = [
            f"{self.build_path}/design_{i}.dump" for i in range(self.num_designs)
        ]
        self.outputs["labelfile_output"] = [
            f"{self.build_path}/design_{i}_golden.dump" for i in range(self.num_designs)
        ]

    def add_ninja_deps(self, deps):
        self._add_ninja_deps_default(deps, __file__)
        deps.append(BFASST_UTILS_PATH / "isoblaze_dump.py")
        deps.append(BFASST_UTILS_PATH / "collect_ip.tcl")

    def create_rule_snippets(self):
        self._append_rule_snippets_default(__file__)

    def create_build_snippets(self):
        impl_checkpoint_base_path = RAND_SOC_BUILD_PATH
        for i in range(self.num_designs):
            impl_checkpoint_path = impl_checkpoint_base_path / f"design_{i}" / "impl" / "impl.dcp"
            with open(ISOBLAZE_DUMP_BUILD_PATH, "r") as f:
                build = chevron.render(
                    f,
                    {
                        "dumpfile": self.outputs["isoblaze_dump_output"][i],
                        "labelfile": self.outputs["labelfile_output"][i],
                        "design_checkpoint": impl_checkpoint_path,
                        "isoblaze_dump_util": BFASST_UTILS_PATH / "isoblaze_dump.py",
                        "collect_ip_util": BFASST_UTILS_PATH / "collect_ip.tcl",
                    },
                )

            with open(NINJA_BUILD_PATH, "a") as f:
                f.write(build)
