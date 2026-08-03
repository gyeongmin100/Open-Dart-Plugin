import unittest

from opendartmcp.excel import dartdoc
from tests.fixtures import audit_report_xml


class DartdocErrorCodeTest(unittest.TestCase):
    def test_scope_missing_raises_code_and_available_scopes(self):
        content = audit_report_xml(scope="separate")
        with self.assertRaises(dartdoc.SectionNotFound) as ctx:
            dartdoc.extract_model(content, dartdoc.CONSOLIDATED)
        self.assertEqual(ctx.exception.code, "scope_not_in_document")
        self.assertEqual(ctx.exception.available_scopes, ["separate"])

    def test_section_not_found_is_lookup_error_subclass(self):
        self.assertTrue(issubclass(dartdoc.SectionNotFound, LookupError))

    def test_missing_notes_section_has_its_own_code(self):
        content = audit_report_xml(scope="consolidated", with_notes=False)
        with self.assertRaises(dartdoc.SectionNotFound) as ctx:
            dartdoc.extract_model(content, dartdoc.CONSOLIDATED)
        self.assertEqual(ctx.exception.code, "notes_section_not_found")

    def test_no_statement_tables_has_its_own_code(self):
        content = audit_report_xml(scope="consolidated", with_tables=False)
        with self.assertRaises(dartdoc.SectionNotFound) as ctx:
            dartdoc.extract_model(content, dartdoc.CONSOLIDATED)
        self.assertEqual(ctx.exception.code, "no_statement_tables")
