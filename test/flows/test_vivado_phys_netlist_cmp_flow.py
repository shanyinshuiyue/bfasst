"""Unit tests for VivadoPhysNetlistCmp class."""
import unittest

from bfasst.ninja_flows.flow_utils import create_build_file
from bfasst.ninja_flows.vivado_phys_netlist_cmp import VivadoPhysNetlistCmp
from bfasst.paths import (
    NINJA_BUILD_PATH,
    NINJA_COMPARE_TOOLS_PATH,
    NINJA_FLOWS_PATH,
    NINJA_UTILS_PATH,
)


class TestVivadoPhysNetlistCmp(unittest.TestCase):
    """Unit tests for VivadoPhysNetlistCmp class."""

    @classmethod
    def setUpClass(cls):
        # overwrite the build file so it is not appended to incorrectly
        create_build_file()

        cls.flow = VivadoPhysNetlistCmp("byu/alu")
        cls.flow.create_rule_snippets()
        cls.flow.create_build_snippets()

    def test_rule_snippets_exist(self):
        """Test that there is a rule for vivado, ioparse, phys_netlist
        bit_to_fasm, fasm_to_netlist, and compare"""
        with open(NINJA_BUILD_PATH, "r") as f:
            ninja_rules = f.read()

        self.assertIn("rule vivado", ninja_rules)
        self.assertIn("rule vivado_ioparse", ninja_rules)
        self.assertIn("rule phys_netlist", ninja_rules)
        self.assertIn("rule bit_to_fasm", ninja_rules)
        self.assertIn("rule fasm_to_netlist", ninja_rules)
        self.assertIn("rule compare", ninja_rules)

    def test_build_snippets_exist(self):
        with open(NINJA_BUILD_PATH, "r") as f:
            build_statement_count = f.read().count("\nbuild ")

        # There should be 11 build statements for a single design using this flow
        self.assertEqual(build_statement_count, 10)

    def test_add_ninja_deps(self):
        """Test that the flow adds the correct dependencies to the ninja file"""
        observed = self.flow.add_ninja_deps(["foo", "bar"])
        expected = [
            "foo",
            "bar",
            f"{NINJA_FLOWS_PATH}/vivado_phys_netlist_cmp.py ",
            f"{NINJA_UTILS_PATH}/structural.py ",
            f"{NINJA_COMPARE_TOOLS_PATH}/structural.ninja_rules.mustache ",
            f"{NINJA_COMPARE_TOOLS_PATH}/structural.ninja_build.mustache ",
        ]
        expected.extend(self.flow.phys_and_xrev_flow.add_ninja_deps())

        observed.sort()
        expected.sort()
        self.assertEqual(observed, expected)

    def test_get_top_level_flow_path(self):
        self.assertEqual(
            self.flow.get_top_level_flow_path(), f"{NINJA_FLOWS_PATH}/vivado_phys_netlist_cmp.py"
        )


if __name__ == "__main__":
    unittest.main()
