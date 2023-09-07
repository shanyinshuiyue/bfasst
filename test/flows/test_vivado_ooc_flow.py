"""Unit tests for the Vivado ooc flow."""
import json
import unittest
from bfasst.ninja_flows.vivado_ooc import VivadoOoc
from bfasst.ninja_tools.vivado.vivado import Vivado
from bfasst.paths import (
    NINJA_BUILD_PATH,
    NINJA_FLOWS_PATH,
)
from bfasst.utils import compare_json


class TestVivadoOocFlow(unittest.TestCase):
    """Unit tests for the Vivado ooc flow."""

    @classmethod
    def setUpClass(cls):
        # overwrite the build file so it is not appended to incorrectly
        with open(NINJA_BUILD_PATH, "w") as f:
            f.write("")

        cls.flow = VivadoOoc("byu/alu")
        cls.flow.create_rule_snippets()
        cls.flow.create_build_snippets()

    def test_ooc_default(self):
        # test that the flow is ooc by default
        self.assertTrue(self.flow.ooc)

    def test_rule_snippets_exist(self):
        # test that there is a rule for vivado, template, but not ioparse
        with open(NINJA_BUILD_PATH, "r") as f:
            ninja_rules = f.read()
        self.assertIn("rule vivado", ninja_rules)
        self.assertNotIn("rule vivado_ioparse", ninja_rules)

    def test_tcl_json_accurate(self):
        """Test that the json file used to template the tcl file is accurate"""
        synth_dict = {
            "part": self.flow.vivado_tool.part,
            "verilog": self.flow.vivado_tool.verilog,
            "system_verilog": self.flow.vivado_tool.system_verilog,
            "vhdl": [],
            "top": self.flow.vivado_tool.top,
            "io": False,
            "synth_output": str(self.flow.vivado_tool.synth_output),
            "flow_args": "",
        }
        expected_synth_json = json.dumps(synth_dict, indent=4)
        self.assertTrue(
            compare_json(self.flow.vivado_tool.synth_output / "synth.json", expected_synth_json)
        )

        impl_dict = {
            "part": self.flow.vivado_tool.part,
            "xdc": False,
            "bit": False,
            "impl_output": str(self.flow.vivado_tool.impl_output),
            "synth_output": str(self.flow.vivado_tool.synth_output),
        }
        expected_impl_json = json.dumps(impl_dict, indent=4)
        self.assertTrue(
            compare_json(self.flow.vivado_tool.impl_output / "impl.json", expected_impl_json)
        )

    def test_build_snippets_exist(self):
        with open(NINJA_BUILD_PATH, "r") as f:
            build_statement_count = f.read().count("\nbuild ")

        # There should be 4 build statements for a single design ooc
        self.assertEqual(build_statement_count, 4)

    def test_add_ninja_deps(self):
        """Test that the flow adds the correct dependencies for the build.ninja file."""
        observed = self.flow.add_ninja_deps(["foo", "bar"])
        expected = [
            "foo",
            "bar",
        ]
        expected.extend(Vivado("byu/alu").add_ninja_deps())
        expected.append(f"{NINJA_FLOWS_PATH}/vivado_ooc.py ")
        expected.append(f"{NINJA_FLOWS_PATH}/vivado.py ")

        expected.sort()
        observed.sort()

        self.assertEqual(observed, expected)

    def test_get_top_level_flow_path(self):
        self.assertEqual(self.flow.get_top_level_flow_path(), f"{NINJA_FLOWS_PATH}/vivado_ooc.py")


if __name__ == "__main__":
    unittest.main()
