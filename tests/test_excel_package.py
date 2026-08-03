import unittest


class ExcelPackageImportTest(unittest.TestCase):
    def test_package_imports_with_relative_imports(self):
        from opendartmcp.excel import build_financial_excel, dartdoc, verify_workbook

        self.assertTrue(callable(build_financial_excel.build_workbook))
        self.assertTrue(callable(verify_workbook.verify))
        self.assertEqual(dartdoc.CONSOLIDATED, "consolidated")

    def test_no_sys_path_or_ensure_deps(self):
        from pathlib import Path

        import opendartmcp.excel as pkg

        for path in Path(pkg.__file__).parent.glob("*.py"):
            source = path.read_text(encoding="utf-8")
            self.assertNotIn("sys.path.insert", source, path.name)
            self.assertNotIn("_ensure_deps", source, path.name)
