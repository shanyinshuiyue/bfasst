"""Ic2 LSE Synthesis Tool (ninja snippet generation for ic2 lse synthesis)"""

import json
import pathlib
from bfasst.config import (
    IC2_SYNPLIFY_LD_LIBRARY_PATH,
    IC2_SYNPLIFY_PATH,
    IC2_SBT_DIR,
    IC2_SYNPLIFY_BIN,
)
from bfasst.paths import SYNPLIFY_PRJ_TEMPLATE, TOOLS_PATH
from bfasst.tools.synth.synth_tool import SynthTool
from bfasst.utils.general import json_write_if_changed


class Ic2SynplifySynth(SynthTool):
    """Ic2 Synplify Synthesis Tool (ninja snippet generation for ic2 synplify synthesis)"""

    def __init__(self, flow, design_path):
        super().__init__(flow, design_path)
        self._my_dir_path = pathlib.Path(__file__).parent
        self.build_path = self.build_path.with_name("ic2_synplify_synth")

        # outputs must be initialized AFTER output paths are set
        self._init_outputs()
        self.rule_snippet_path = TOOLS_PATH / "synth" / "ic2_synplify_synth.ninja"

    def create_build_snippets(self):
        # first, the project file must be created with ninja and chevron.
        # Arguments are passed to the template in a json file
        synth = {
            "verilog": self.verilog,
            "vhdl": self.vhdl,
            "top": self.design_props.top,
            "edf_output": str(self.outputs["edf_output"]),
        }
        synth_json = json.dumps(synth, indent=4)
        json_write_if_changed(self.outputs["synth_json"], synth_json)

        # then the build snippet can be created as normal
        self._append_build_snippets_default(
            __file__,
            {
                "ld_library_path": IC2_SYNPLIFY_LD_LIBRARY_PATH,
                "sbt_dir": IC2_SBT_DIR,
                "synth_bin_path": IC2_SYNPLIFY_BIN,
                "synplify_path": IC2_SYNPLIFY_PATH,
                "prj_path": self.outputs["prj_file"],
                "json_render_dict": self.outputs["synth_json"],
                "prj_template": SYNPLIFY_PRJ_TEMPLATE,
                "design": self.design_path,
                "build_path": self.build_path,
                "outputs": [
                    v
                    for _, v in self.outputs.items()
                    if (v not in [self.outputs["prj_file"], self.outputs["synth_json"]])
                ],  # all outputs not related to prj file are built by synp synth tool with ninja
            },
        )

    def _init_outputs(self):
        impl_path = self.build_path / "rev_1"
        self.outputs["prj_file"] = self.build_path / "synplify_project.prj"
        self.outputs["golden_netlist"] = impl_path / "synth.vm"
        self.outputs["edf_output"] = impl_path / "synth.edf"
        self.outputs["synth_json"] = self.build_path / "synth.json"

        # files generated by synp tool
        self.outputs["auto_constraints_sdc"] = (
            impl_path / f"AutoConstraints_{self.design_props.top}.sdc"
        )
        self.outputs["areassr"] = impl_path / f"rpt_{self.design_props.top}.areassr"
        self.outputs["areassr_htm"] = impl_path / f"rpt_{self.design_props.top}_areassr.htm"
        self.outputs["run_options"] = impl_path / "run_options.txt"
        self.outputs["scratch_project"] = impl_path / "scratch_project.prs"
        self.outputs["cck_rpt"] = impl_path / "synth_cck.rpt"
        self.outputs["synth_fse"] = impl_path / "synth.fse"
        self.outputs["synth_htm"] = impl_path / "synth.htm"
        self.outputs["synth_map"] = impl_path / "synth.map"
        self.outputs["synth_sap"] = impl_path / "synth.sap"
        self.outputs["scck_rpt"] = impl_path / "synth_scck.rpt"
        self.outputs["synth_scf"] = impl_path / "synth.scf"
        self.outputs["synth_srd"] = impl_path / "synth.srd"
        self.outputs["synth_srm"] = impl_path / "synth.srm"
        self.outputs["synth_srr"] = impl_path / "synth.srr"
        self.outputs["synth_srs"] = impl_path / "synth.srs"
        self.outputs["synth_synp_fdc"] = impl_path / "synth_synp.fdc"

        self.outputs["stdout_log"] = self.build_path / "stdout.log"
        self.outputs["synlog_tcl"] = self.build_path / "synlog.tcl"

        # dirs generated by synp tool
        # (may be empty or not, but they are always created by synp tool)
        self.outputs["backup_dir"] = impl_path / "backup"
        self.outputs["coreip_dir"] = impl_path / "coreip"
        self.outputs["dm_dir"] = impl_path / "dm"
        self.outputs["synlog_dir"] = impl_path / "synlog"
        self.outputs["syntmp_dir"] = impl_path / "syntmp"
        self.outputs["synwork_dir"] = impl_path / "synwork"

    def add_ninja_deps(self, deps):
        self._add_ninja_deps_default(deps, __file__)
        deps.append(SYNPLIFY_PRJ_TEMPLATE)
