"""Unit tests for the Vivado flow."""

# Disable this since we are testing a class
# pylint: disable=duplicate-code

import json
import unittest
from bfasst import config

from bfasst.flows.flow_utils import create_build_file
from bfasst.flows.vivado import Vivado
from bfasst.tools.synth.vivado_synth import VivadoSynth
from bfasst.tools.impl.vivado_impl import VivadoImpl
from bfasst.paths import (
    DESIGNS_PATH,
    NINJA_BUILD_PATH,
    FLOWS_PATH,
)
from bfasst.utils import compare_json


class TestVivadoFlow(unittest.TestCase):
    """Unit tests for the Vivado flow."""

    @classmethod
    def setUpClass(cls):
        # overwrite the build file so it is not appended to incorrectly
        create_build_file()

        cls.flow = Vivado(DESIGNS_PATH / "byu/alu")
        cls.flow.create_rule_snippets()
        cls.flow.create_build_snippets()

    def test_in_context_default(self):
        # test that the flow is in-context by default
        self.assertFalse(self.flow.ooc)

    def test_rule_snippets_exist(self):
        # test that there is a rule for vivado, template, and ioparse
        with open(NINJA_BUILD_PATH, "r") as f:
            ninja_rules = f.read()
        self.assertIn("rule vivado", ninja_rules)
        self.assertIn("rule vivado_ioparse", ninja_rules)

    def test_json_exist(self):
        # test that the json files for synth and impl templates exist
        self.assertTrue((self.flow.vivado_synth_tool.build_path / "synth.json").exists())
        self.assertTrue((self.flow.vivado_impl_tool.build_path / "impl.json").exists())

    def test_tcl_json_accurate(self):
        """Test that the json files for synth and impl templates are accurate."""
        synth_dict = {
            "part": config.PART,
            "verilog": self.flow.vivado_synth_tool.verilog,
            "system_verilog": self.flow.vivado_synth_tool.system_verilog,
            "vhdl": [],
            "vhdl_libs": [],
            "top": self.flow.vivado_synth_tool.design_props.top,
            "io": str(self.flow.vivado_synth_tool.build_path / "report_io.txt"),
            "synth_output": str(self.flow.vivado_synth_tool.build_path),
            "synth_args": "",
        }
        expected_synth_json = json.dumps(synth_dict, indent=4)
        self.assertTrue(
            compare_json(self.flow.vivado_synth_tool.build_path / "synth.json", expected_synth_json)
        )

        impl_dict = {
            "part": config.PART,
            "xdc": str(self.flow.vivado_synth_tool.build_path / ("design.xdc")),
            "bit": str(self.flow.vivado_impl_tool.build_path / ("design.bit")),
            "impl_output": str(self.flow.vivado_impl_tool.build_path),
            "synth_output": str(self.flow.vivado_synth_tool.build_path),
        }
        expected_impl_json = json.dumps(impl_dict, indent=4)
        self.assertTrue(
            compare_json(self.flow.vivado_impl_tool.build_path / "impl.json", expected_impl_json)
        )

    def test_build_snippets_exist(self):
        with open(NINJA_BUILD_PATH, "r") as f:
            build_statement_count = f.read().count("\nbuild ")

        # There should be 5 build statements for a single design in context
        self.assertEqual(build_statement_count, 5)

    def test_add_ninja_deps(self):
        """Test that the flow adds the correct dependencies for the build.ninja file."""
        observed = ["foo", "bar"]
        self.flow.add_ninja_deps(observed)
        expected = [
            "foo",
            "bar",
        ]
        design_path = DESIGNS_PATH / "byu/alu"
        VivadoSynth(None, design_path).add_ninja_deps(expected)
        VivadoImpl(None, design_path).add_ninja_deps(expected)
        expected.append(FLOWS_PATH / "vivado.py")

        self.assertEqual(observed, expected)

    def test_get_top_level_flow_path(self):
        self.assertEqual(self.flow.get_top_level_flow_path(), FLOWS_PATH / "vivado.py")


if __name__ == "__main__":
    unittest.main()
