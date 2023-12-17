""" Repository paths using pathlib """

import pathlib
import os

ROOT_PATH = pathlib.Path(__file__).resolve().parent.parent

BUILD_PATH = pathlib.Path().cwd() / "build"

DESIGNS_PATH = ROOT_PATH / "designs"
BFASST_PATH = ROOT_PATH / "bfasst"
TESTS_PATH = ROOT_PATH / "tests"
RESOURCES_PATH = ROOT_PATH / "resources"
SCRIPTS_PATH = ROOT_PATH / "scripts"
ERROR_FLOW_PATH = ROOT_PATH / "error_flows"
THIRD_PARTY_PATH = ROOT_PATH / "third_party"

TOOLS_PATH = BFASST_PATH / "tools"
FLOWS_PATH = BFASST_PATH / "flows"

COMMON_TOOLS_PATH = TOOLS_PATH / "common"

REV_BIT_TOOLS_PATH = TOOLS_PATH / "rev_bit"
NINJA_TRANSFORM_TOOLS_PATH = TOOLS_PATH / "transform"
PHYS_NETLIST_RULES_PATH = NINJA_TRANSFORM_TOOLS_PATH / "phys_netlist_rules.ninja"

COMPARE_TOOLS_PATH = TOOLS_PATH / "compare"
CONFORMAL_TOOLS_PATH = COMPARE_TOOLS_PATH / "conformal"
STRUCTURAL_TOOLS_PATH = COMPARE_TOOLS_PATH / "structural"
YOSYS_TOOLS_PATH = COMPARE_TOOLS_PATH / "yosys"

NINJA_BUILD_PATH = ROOT_PATH / "build.ninja"

I2C_RESOURCES = RESOURCES_PATH / "iCEcube2"
YOSYS_RESOURCES = RESOURCES_PATH / "yosys"
ONESPIN_RESOURCES = RESOURCES_PATH / "onespin"
YOSYS_INSTALL_DIR = THIRD_PARTY_PATH / "yosys"
GMT_TOOLS_PATH = THIRD_PARTY_PATH / "gmt_tools"
RAPIDWRIGHT_PATH = THIRD_PARTY_PATH / "RapidWright"
YOSYS_PATH = THIRD_PARTY_PATH / "yosys"

ISOBLAZE_PATH = THIRD_PARTY_PATH / "isoblaze"
ISOBLAZE_SRC_PATH = ISOBLAZE_PATH / "src"
ISOBLAZE_DUMP_PATH = ISOBLAZE_SRC_PATH / "dump.tcl"
ISOBLAZE_DUMP_DCP_PATH = ISOBLAZE_SRC_PATH / "dump-dcp.tcl"
ISOBLAZE_GOLDEN_PATH = ISOBLAZE_SRC_PATH / "golden.tcl"

BFASST_UTILS_PATH = BFASST_PATH / "utils"

RAND_SOC_BUILD_PATH = BUILD_PATH / "rand_soc"
DUMP_TOOL_BUILD_PATH = RAND_SOC_BUILD_PATH / "isoblaze_dump"

FLOW_DESCRIPTIONS_PATH = FLOWS_PATH / "flow_descriptions.yaml"


def get_fasm2bels_path():
    if "BFASST_PATH_FASM2BELS" in os.environ:
        return pathlib.Path(os.environ["BFASST_PATH_FASM2BELS"])
    return THIRD_PARTY_PATH / "fasm2bels"


XRAY_PATH = get_fasm2bels_path() / "third_party" / "prjxray"
