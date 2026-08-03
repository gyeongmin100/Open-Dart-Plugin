import json
import tempfile
import unittest
from pathlib import Path

import httpx

from opendartmcp.excel import workflow
from tests.fixtures import (annual_body_xml, annual_report_zip, audit_report_xml,
                            body_only_zip, make_zip, quarterly_report_zip)
from tests.test_client_zip_helpers import make_client

RCEPT = "20250319000665"


class WorkflowTestBase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.out = Path(tempfile.mkdtemp())
        self.calls = []

    async def run_workflow(self, zip_bytes, **kwargs):
        client = make_client(lambda r: httpx.Response(200, content=zip_bytes),
                             count=self.calls)
        params = {"rcept_no": RCEPT, "scope": "consolidated",
                  "output_dir": str(self.out), "output_name": "결과.xlsx"}
        params.update(kwargs)
        try:
            return await workflow.create_workbook(client, **params)
        finally:
            await client.aclose()


class DocumentSelectionTest(WorkflowTestBase):
    async def test_annual_zip_consolidated_picks_linked_audit_report(self):
        result = await self.run_workflow(annual_report_zip(RCEPT))
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["source_title"], "연결감사보고서")
        self.assertFalse(result["used_body"])

    async def test_annual_zip_separate_picks_audit_report(self):
        result = await self.run_workflow(annual_report_zip(RCEPT), scope="separate")
        self.assertEqual(result["source_title"], "감사보고서")

    async def test_quarterly_zip_picks_review_reports_without_period_input(self):
        zip_bytes = quarterly_report_zip(RCEPT)
        con = await self.run_workflow(zip_bytes)
        self.assertIn("검토보고서", con["source_title"].replace(" ", ""))
        self.assertIn("연결", con["source_title"])
        sep = await self.run_workflow(zip_bytes, scope="separate",
                                      output_name="별도.xlsx")
        self.assertNotIn("연결", sep["source_title"])
        self.assertIn("검토보고서", sep["source_title"].replace(" ", ""))

    async def test_downloads_document_xml_exactly_once(self):
        await self.run_workflow(annual_report_zip(RCEPT))
        self.assertEqual(self.calls, ["/api/document.xml"])

    async def test_server_does_not_look_up_other_rcept_no(self):
        await self.run_workflow(body_only_zip(RCEPT))
        self.assertEqual(len(self.calls), 1)


class BodyFallbackTest(WorkflowTestBase):
    async def test_missing_attachment_defaults_to_error(self):
        result = await self.run_workflow(body_only_zip(RCEPT))
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "audit_attachment_not_found")
        self.assertEqual([d["title"] for d in result["documents"]], ["사업보고서"])
        self.assertFalse(list(self.out.glob("*.xlsx")))

    async def test_use_body_true_uses_body_and_allows_zero_links(self):
        result = await self.run_workflow(body_only_zip(RCEPT), use_body=True)
        self.assertTrue(result["ok"], result)
        self.assertTrue(result["used_body"])
        self.assertEqual(result["verification"]["hyperlinks"], 0)

    async def test_use_body_selects_report_not_first_zip_entry(self):
        zip_bytes = make_zip({
            "000_attachment.xml": audit_report_xml(
                "separate", title="감사보고서"),
            "999_body.xml": annual_body_xml("consolidated"),
        })
        result = await self.run_workflow(zip_bytes, use_body=True)
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["source_title"], "사업보고서")
        self.assertTrue(result["used_body"])


class ErrorMappingTest(WorkflowTestBase):
    async def test_invalid_rcept_no_does_not_download(self):
        result = await self.run_workflow(annual_report_zip(RCEPT), rcept_no="123")
        self.assertEqual(result["error"], "invalid_rcept_no")
        self.assertEqual(self.calls, [])

    async def test_invalid_output_dir(self):
        result = await self.run_workflow(annual_report_zip(RCEPT),
                                         output_dir=str(self.out / "missing"))
        self.assertEqual(result["error"], "invalid_output_dir")
        self.assertEqual(self.calls, [])

    async def test_output_name_with_path_separator_is_rejected(self):
        result = await self.run_workflow(annual_report_zip(RCEPT),
                                         output_name="../escape.xlsx")
        self.assertEqual(result["error"], "invalid_output_dir")
        self.assertEqual(self.calls, [])

    async def test_scope_not_in_document_returns_available_scopes(self):
        """§5.6: DOCUMENT-NAME은 연결인데 내용에 연결 범위가 없는 경우."""
        zip_bytes = make_zip({f"{RCEPT}_1.xml": audit_report_xml(
            "separate", title="연결감사보고서")})
        result = await self.run_workflow(zip_bytes)
        self.assertEqual(result["error"], "scope_not_in_document")
        self.assertEqual(result["available_scopes"], ["separate"])

    async def test_missing_consolidated_attachment_is_attachment_error(self):
        """별도 첨부만 있는 공시에 연결을 요청하면 첨부 부재 오류다 (§5.5)."""
        zip_bytes = make_zip({f"{RCEPT}_1.xml": audit_report_xml(
            "separate", title="감사보고서")})
        result = await self.run_workflow(zip_bytes)
        self.assertEqual(result["error"], "audit_attachment_not_found")

    async def test_no_financial_statements_has_distinct_code(self):
        zip_bytes = make_zip({f"{RCEPT}_1.xml": audit_report_xml(
            "consolidated", with_tables=False, title="연결감사보고서")})
        result = await self.run_workflow(zip_bytes)
        self.assertEqual(result["error"], "no_financial_statements")

    async def test_library_errors_do_not_exit_or_print(self):
        import contextlib
        import io as _io

        buffer = _io.StringIO()
        with contextlib.redirect_stdout(buffer):
            result = await self.run_workflow(body_only_zip(RCEPT))
        self.assertFalse(result["ok"])
        self.assertEqual(buffer.getvalue(), "")


class OutputFileTest(WorkflowTestBase):
    async def test_existing_file_is_preserved_and_suffixed(self):
        (self.out / "결과.xlsx").write_bytes(b"old")
        result = await self.run_workflow(annual_report_zip(RCEPT))
        self.assertEqual((self.out / "결과.xlsx").read_bytes(), b"old")
        self.assertEqual(Path(result["workbook"]).name, "결과 (1).xlsx")

    async def test_no_temp_files_left_on_success(self):
        result = await self.run_workflow(annual_report_zip(RCEPT))
        self.assertEqual([p.name for p in self.out.iterdir()],
                         [Path(result["workbook"]).name])

    async def test_failed_verification_leaves_no_workbook(self):
        original = workflow.verify
        workflow.verify = lambda *a, **k: {
            "ok": False, "failures": ["강제 실패"], "warnings": [], "stats": {}}
        try:
            result = await self.run_workflow(annual_report_zip(RCEPT))
        finally:
            workflow.verify = original
        self.assertEqual(result["error"], "verification_failed")
        self.assertEqual(result["failures"], ["강제 실패"])
        self.assertEqual(list(self.out.iterdir()), [])

    async def test_cancellation_cleans_up_temp_file(self):
        original = workflow.build_workbook

        def boom(model, path):
            Path(path).write_bytes(b"partial")
            raise KeyboardInterrupt()

        workflow.build_workbook = boom
        try:
            with self.assertRaises(KeyboardInterrupt):
                await self.run_workflow(annual_report_zip(RCEPT))
        finally:
            workflow.build_workbook = original
        self.assertEqual(list(self.out.iterdir()), [])

    async def test_final_move_failure_cleans_reserved_file(self):
        original = workflow.os.replace

        def boom(source, destination):
            raise OSError("move failed")

        workflow.os.replace = boom
        try:
            with self.assertRaises(workflow.StageFailure):
                await self.run_workflow(annual_report_zip(RCEPT))
        finally:
            workflow.os.replace = original
        self.assertEqual(list(self.out.iterdir()), [])

    async def test_zip_entry_path_is_not_used_as_file_path(self):
        """Zip Slip 방지: 엔트리 경로로 파일을 쓰지 않는다 (plan.md §8)."""
        zip_bytes = make_zip({
            "../../evil_00761.xml": audit_report_xml("consolidated",
                                                     title="연결감사보고서")})
        result = await self.run_workflow(zip_bytes)
        self.assertTrue(result["ok"], result)
        self.assertEqual(Path(result["workbook"]).parent, self.out)
        self.assertFalse((self.out.parent.parent / "evil_00761.xml").exists())


class ResultSizeTest(WorkflowTestBase):
    async def test_result_has_no_raw_content(self):
        result = await self.run_workflow(annual_report_zip(RCEPT))
        blob = json.dumps(result, ensure_ascii=False)
        for forbidden in ("<DOCUMENT", "<TABLE", "현금및현금성자산", "PK\x03\x04"):
            self.assertNotIn(forbidden, blob)
        self.assertNotIn("content", result)
        self.assertLess(len(blob.encode("utf-8")), 4096)

    async def test_error_result_has_no_raw_content(self):
        result = await self.run_workflow(body_only_zip(RCEPT))
        blob = json.dumps(result, ensure_ascii=False)
        self.assertNotIn("<DOCUMENT", blob)
        self.assertLess(len(blob.encode("utf-8")), 4096)

    async def test_success_reports_company_and_verification_stats(self):
        result = await self.run_workflow(annual_report_zip(RCEPT))
        self.assertEqual(result["company"], "테스트 주식회사")
        self.assertEqual(result["rcept_no"], RCEPT)
        self.assertEqual(result["scope"], "consolidated")
        self.assertEqual(result["verification"]["statements"], 4)
        self.assertEqual(result["verification"]["notes"], 3)
        self.assertGreater(result["verification"]["hyperlinks"], 0)
