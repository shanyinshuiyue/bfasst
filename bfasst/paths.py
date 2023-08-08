""" Repository paths using pathlib """

import pathlib
import os

ROOT_PATH = pathlib.Path(__file__).resolve().parent.parent

DESIGNS_PATH = ROOT_PATH / "designs"
BFASST_PATH = ROOT_PATH / "bfasst"
EXPERIMENTS_PATH = ROOT_PATH / "experiments"
RESOURCES_PATH = ROOT_PATH / "resources"
SCRIPTS_PATH = ROOT_PATH / "scripts"
ERROR_FLOW_PATH = ROOT_PATH / "error_flows"
THIRD_PARTY_PATH = ROOT_PATH / "third_party"

NINJA_TOOLS_PATH = BFASST_PATH / "ninja_tools"
NINJA_UTILS_PATH = BFASST_PATH / "ninja_utils"
NINJA_FLOWS_PATH = BFASST_PATH / "ninja_flows"

NINJA_SYNTH_TOOLS_PATH = NINJA_TOOLS_PATH / "synth"
NINJA_IMPL_TOOLS_PATH = NINJA_TOOLS_PATH / "impl"
VIVADO_RULES_PATH = NINJA_TOOLS_PATH / "vivado" / "vivado.ninja.mustache"
REV_BIT_TOOLS_PATH = NINJA_TOOLS_PATH / "rev_bit"

NINJA_BUILD_PATH = ROOT_PATH / "build.ninja"

I2C_RESOURCES = RESOURCES_PATH / "iCEcube2"
YOSYS_RESOURCES = RESOURCES_PATH / "yosys"
ONESPIN_RESOURCES = RESOURCES_PATH / "onespin"
YOSYS_INSTALL_DIR = THIRD_PARTY_PATH / "yosys"


def get_fasm2bels_path():
    if "BFASST_PATH_FASM2BELS" in os.environ:
        return pathlib.Path(os.environ["BFASST_PATH_FASM2BELS"])
    return THIRD_PARTY_PATH / "fasm2bels"


XRAY_PATH = get_fasm2bels_path() / "third_party" / "prjxray"
