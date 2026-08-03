import tempfile
import unittest
from pathlib import Path

from opendartmcp.excel import dartdoc
from opendartmcp.excel.build_financial_excel import build_workbook
from opendartmcp.excel.verify_workbook import verify
from tests.fixtures import annual_body_xml, audit_report_xml


class VerifySourceContentTest(unittest.TestCase):
    def _build(self, content: str):
        model = dartdoc.extract_model(content, dartdoc.CONSOLIDATED)
        tmp = Path(tempfile.mkdtemp()) / "wb.xlsx"
        build_workbook(model, str(tmp))
        return model, str(tmp)

    def test_verify_takes_source_content_not_path(self):
        content = audit_report_xml("consolidated")
        model, path = self._build(content)
        report = verify(model, path, content)
        self.assertTrue(report["ok"], report["failures"])
        self.assertIn("hyperlinks", report["stats"])

    def test_verify_does_not_reparse_model(self):
        """plan.md §5.7: 검증 안에서 extract_model()을 다시 실행하지 않는다."""
        content = audit_report_xml("consolidated")
        model, path = self._build(content)
        calls = []
        original = dartdoc.extract_model
        dartdoc.extract_model = lambda *a, **k: (calls.append(a), original(*a, **k))[1]
        try:
            verify(model, path, content)
        finally:
            dartdoc.extract_model = original
        self.assertEqual(calls, [])

    def test_char_completeness_still_detects_missing_text(self):
        content = audit_report_xml("consolidated")
        model, path = self._build(content)
        model["notes"][1]["blocks"][1]["text"] = ""   # 결과물에서 한 문단 소실 흉내
        report = verify(model, path, content)
        self.assertFalse(report["ok"])
        self.assertTrue(any("원문 글자" in f for f in report["failures"]),
                        report["failures"])

    def test_body_workbook_passes_with_zero_hyperlinks(self):
        """plan.md §5.7: 본문 경로는 주석 열이 없어 링크 0개가 정상."""
        content = annual_body_xml("consolidated")
        model, path = self._build(content)
        self.assertEqual(model["kind"], "annual_report_body")
        report = verify(model, path, content)
        self.assertTrue(report["ok"], report["failures"])
        self.assertEqual(report["stats"]["hyperlinks"], 0)
