import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "src" / "opendartmcp" / "tools"


def tool_names(module_name: str | None = None) -> set[str]:
    names: set[str] = set()
    paths = [TOOLS_DIR / f"{module_name}.py"] if module_name else TOOLS_DIR.glob("*.py")
    for path in paths:
        if path.name == "__init__.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        names.update(
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.AsyncFunctionDef)
        )
    return names


class ToolRegistryTests(unittest.TestCase):
    def test_official_opendart_tool_count_is_85(self) -> None:
        self.assertEqual(len(tool_names()), 85)

    def test_ds002_exposes_v1_and_v2_compensation_tools(self) -> None:
        business_report_tools = tool_names("business_report")

        self.assertIn("get_executive_compensation_individual", business_report_tools)
        self.assertIn("get_individual_pay_over5", business_report_tools)
        self.assertIn("get_executive_compensation_individual_v2", business_report_tools)
        self.assertIn("get_individual_pay_over5_v2", business_report_tools)
        self.assertEqual(len(business_report_tools), 30)


if __name__ == "__main__":
    unittest.main()
