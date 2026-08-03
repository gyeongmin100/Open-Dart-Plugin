import tempfile
import unittest
from pathlib import Path

import httpx

from opendartmcp.excel import candidates, workflow
from tests.fixtures import (annual_report_zip, audit_report_xml, body_only_zip,
                            make_zip, viewer_fragment, viewer_page)
from tests.test_client_zip_helpers import make_client

RCEPT = "20250814003075"
ORIGIN = "20250320001635"
DCM = "10770117"

ATTACHMENTS = [(RCEPT, DCM, "2025.08.14 반기검토보고서")]


def _list_json(items: list[dict]) -> dict:
    return {"status": "000", "message": "정상", "page_no": 1, "page_count": 100,
            "total_count": len(items), "total_page": 1, "list": items}


def _filing(rcept_no: str, report_nm: str, corp_code: str = "00126380") -> dict:
    return {"corp_code": corp_code, "corp_name": "테스트 주식회사",
            "stock_code": "005930", "corp_cls": "Y", "report_nm": report_nm,
            "rcept_no": rcept_no, "flr_nm": "테스트 주식회사",
            "rcept_dt": rcept_no[:8], "rm": ""}


def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/api/list.json":
        return httpx.Response(200, json=_list_json(
            [_filing(RCEPT, "반기보고서 (2025.06)")]))
    if request.url.path == "/api/document.xml":
        return httpx.Response(200, content=body_only_zip(RCEPT, "separate"))
    if request.url.path == "/dsaf001/main.do":
        return httpx.Response(200, text=viewer_page(
            RCEPT, ATTACHMENTS, node_dcm=DCM))
    if request.url.path == "/report/viewer.do":
        return httpx.Response(200, text=viewer_fragment())
    return httpx.Response(404)


class CandidateListTest(unittest.IsolatedAsyncioTestCase):
    async def _list(self, rcept_no=RCEPT, request_handler=handler, calls=None,
                    corp_code=None, allow_body=False):
        client = make_client(request_handler, count=calls)
        try:
            return await candidates.list_candidates(
                client, rcept_no, corp_code, allow_body=allow_body)
        finally:
            await client.aclose()

    async def test_screen_fills_attachment_missing_from_zip(self):
        """반기 검토보고서는 ZIP에 없으므로 내부 문서 조회가 보완한다."""
        result = await self._list()
        self.assertTrue(result["ok"])
        self.assertEqual([item["title"] for item in result["candidates"]],
                         ["반기검토보고서"])
        self.assertEqual(result["candidates"][0]["source"], "dart_attachment")
        self.assertNotIn("content", str(result))

    async def test_screen_outage_is_not_mistaken_for_missing_attachment(self):
        """내부 조회 장애 때 본문 사용을 물으면 안 된다."""
        def no_screen(request):
            if request.url.path == "/dsaf001/main.do":
                raise httpx.ConnectError("blocked")
            return handler(request)

        result = await self._list(request_handler=no_screen)
        self.assertEqual(result["error"], "attachment_lookup_failed")
        self.assertTrue(result["body_available"])

    async def test_body_requires_confirmation_then_returns_one_candidate(self):
        def no_attachment(request):
            if request.url.path == "/dsaf001/main.do":
                return httpx.Response(200, text=viewer_page(RCEPT, []))
            return handler(request)

        blocked = await self._list(request_handler=no_attachment)
        self.assertEqual(blocked["error"], "confirmation_required")
        self.assertTrue(blocked["body_available"])

        approved = await self._list(
            request_handler=no_attachment, allow_body=True)
        self.assertTrue(approved["ok"])
        self.assertEqual(approved["candidates"][0]["candidate_id"],
                         f"body:{RCEPT}")
        self.assertTrue(approved["candidates"][0]["title"].endswith(" (본문)"))

    async def test_correction_series_exposes_the_original_attachment(self):
        """정정 공시는 본문만 재제출한다 — 첨부는 원본 제출본에 남는다."""
        corrected = "20250926000794"

        def correction_handler(request):
            if request.url.path == "/api/list.json":
                return httpx.Response(200, json=_list_json([
                    _filing(corrected, "[기재정정]사업보고서 (2024.12)"),
                    _filing(ORIGIN, "사업보고서 (2024.12)")]))
            if request.url.path == "/api/document.xml":
                if request.url.params.get("rcept_no") == ORIGIN:
                    return httpx.Response(200, content=annual_report_zip(ORIGIN))
                return httpx.Response(200, content=body_only_zip(corrected))
            if request.url.path == "/dsaf001/main.do":
                raise httpx.ConnectError("blocked")
            return httpx.Response(404)

        result = await self._list(corrected, correction_handler)
        attachment = [item for item in result["candidates"]
                      if item["title"] == "연결감사보고서"]
        self.assertEqual(len(attachment), 1)
        self.assertEqual(attachment[0]["rcept_no"], ORIGIN)
        self.assertEqual(attachment[0]["candidate_id"],
                         f"zip:{ORIGIN}:{ORIGIN}_00761.xml")
        self.assertEqual(attachment[0]["date"], "20250320")

    async def test_xml_attachment_skips_dart_screen(self):
        calls = []

        def xml_handler(request):
            if request.url.path == "/api/list.json":
                return httpx.Response(200, json=_list_json([
                    _filing(ORIGIN, "사업보고서 (2024.12)")]))
            if request.url.path == "/api/document.xml":
                return httpx.Response(200, content=annual_report_zip(ORIGIN))
            if request.url.path == "/dsaf001/main.do":
                raise AssertionError("XML 첨부가 있는데 화면을 조회함")
            return httpx.Response(404)

        result = await self._list(ORIGIN, xml_handler, calls=calls)
        self.assertTrue(result["ok"])
        self.assertNotIn("/dsaf001/main.do", calls)

    async def test_corp_code_avoids_scanning_the_whole_day(self):
        calls = []
        await self._list(calls=calls, corp_code="00126380")
        self.assertEqual(calls.count("/api/list.json"), 2)

    async def test_invalid_rcept_no_is_rejected(self):
        result = await self._list("123")
        self.assertEqual(result["error"], "invalid_rcept_no")


class CandidateIdTest(unittest.TestCase):
    def test_round_trip(self):
        self.assertEqual(candidates.parse_candidate_id(f"viewer:{RCEPT}:{DCM}"),
                         ("viewer", RCEPT, DCM))
        self.assertEqual(candidates.parse_candidate_id(f"body:{RCEPT}"),
                         ("body", RCEPT, ""))

    def test_rejects_malformed(self):
        for bad in ("", "zip:1:2", f"viewer:{RCEPT}", f"viewer:{RCEPT}:x",
                    "body:123", f"body:{RCEPT}:{DCM}"):
            with self.assertRaises(candidates.CandidateError, msg=bad):
                candidates.parse_candidate_id(bad)


class BodyApprovalTest(unittest.IsolatedAsyncioTestCase):
    async def test_workflow_rejects_body_before_download_without_approval(self):
        calls = []
        client = make_client(handler, count=calls)
        try:
            result = await workflow.create_workbook(
                client, candidate_id=f"body:{RCEPT}", scope="separate",
                output_dir=tempfile.mkdtemp(), output_name="result.xlsx")
        finally:
            await client.aclose()
        self.assertEqual(result["error"], "confirmation_required")
        self.assertEqual(calls, [])


class NotesTitleMarkerTest(unittest.TestCase):
    """주석 제목은 문서마다 문단이거나 표 셀이다. 수치 표와 혼동하면 안 된다."""

    def _mark(self, html):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        candidates._mark_notes_title(soup)
        return str(soup)

    def test_paragraph_and_borderless_table_titles_are_marked(self):
        for html in ("<body><p>주 석</p></body>",
                     '<body><table border="0"><tr><td>주석</td></tr></table></body>',
                     '<body><table class="nb"><tr><td>주석</td></tr></table></body>'):
            with self.subTest(html=html):
                self.assertIn("<TITLE>주석</TITLE>", self._mark(html))

    def test_note_column_header_is_not_a_title(self):
        html = ('<body><table border="1">'
                "<tr><th><p>과목</p></th><th><p>주석</p></th></tr>"
                "<tr><td>현금</td><td>3</td></tr></table></body>")
        with self.assertRaises(candidates.CandidateError):
            self._mark(html)

    def test_numeric_table_cell_is_not_a_title(self):
        html = '<body><table border="1"><tr><td>주석</td></tr></table></body>'
        with self.assertRaises(candidates.CandidateError):
            self._mark(html)


class AttachmentFromZipTest(unittest.IsolatedAsyncioTestCase):
    """첨부는 공시 ZIP의 정식 XML을 먼저 쓴다 — 화면 목차가 없어도 열린다."""

    ZIP_RCEPT = "20110331002189"
    ZIP_DCM = "10440952"

    def _handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/document.xml":
            return httpx.Response(200, content=annual_report_zip(self.ZIP_RCEPT))
        if request.url.path == "/dsaf001/main.do":
            # 2014년 이전 화면처럼 목차 노드가 없다.
            return httpx.Response(200, text=viewer_page(
                self.ZIP_RCEPT,
                [(self.ZIP_RCEPT, self.ZIP_DCM, "2011.03.31 [정정] 연결감사보고서")]))
        return httpx.Response(404)

    async def test_zip_attachment_is_used_and_viewer_is_not_fetched(self):
        calls = []
        client = make_client(self._handler, count=calls)
        try:
            result = await workflow.create_workbook(
                client, candidate_id=f"viewer:{self.ZIP_RCEPT}:{self.ZIP_DCM}",
                scope="consolidated", output_dir=tempfile.mkdtemp(),
                output_name="result.xlsx")
        finally:
            await client.aclose()
        self.assertTrue(result["ok"], result)
        self.assertNotIn("/report/viewer.do", calls)
        self.assertFalse(result["used_body"])

    async def test_bracket_marks_do_not_block_the_title_match(self):
        """화면 제목의 '[정정]' 표식은 ZIP 제목에 없다."""
        client = make_client(self._handler)
        try:
            content, title = await candidates.load_attachment(
                client, self.ZIP_RCEPT, self.ZIP_DCM, "consolidated")
        finally:
            await client.aclose()
        self.assertEqual(title, "[정정] 연결감사보고서")
        self.assertIn("<DOCUMENT-NAME>연결감사보고서</DOCUMENT-NAME>", content)


class ViewerDocumentTest(unittest.IsolatedAsyncioTestCase):
    async def test_selected_viewer_candidate_builds_verified_workbook(self):
        """ZIP에 없는 첨부는 화면 조각으로 넘어간다."""
        calls = []
        client = make_client(handler, count=calls)
        try:
            result = await workflow.create_workbook(
                client, candidate_id=f"viewer:{RCEPT}:{DCM}", scope="separate",
                output_dir=tempfile.mkdtemp(), output_name="result.xlsx")
        finally:
            await client.aclose()
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["source_title"], "반기검토보고서")
        self.assertEqual(result["verification"]["statements"], 4)
        self.assertFalse(result["used_body"])
        self.assertIn("/report/viewer.do", calls)

    async def test_qualified_statement_titles_keep_their_names(self):
        """'요약 반기 재무상태표'도 인식하고 시트명에 기간이 남아야 한다."""
        client = make_client(handler)
        try:
            content, _ = await candidates.load_attachment(
                client, RCEPT, DCM, "separate")
        finally:
            await client.aclose()
        from opendartmcp.excel import dartdoc
        model = dartdoc.extract_model(content, "separate")
        self.assertEqual([s["sheet_name"] for s in model["statements"]],
                         ["요약반기재무상태표", "요약반기포괄손익계산서",
                          "요약반기자본변동표", "요약반기현금흐름표"])

    async def test_missing_financial_node_is_candidate_unavailable(self):
        def no_node(request):
            if request.url.path == "/api/document.xml":
                return httpx.Response(200, content=body_only_zip(RCEPT))
            if request.url.path == "/dsaf001/main.do":
                return httpx.Response(200, text=viewer_page(RCEPT, ATTACHMENTS))
            return httpx.Response(404)

        client = make_client(no_node)
        try:
            result = await workflow.create_workbook(
                client, candidate_id=f"viewer:{RCEPT}:{DCM}", scope="separate",
                output_dir=tempfile.mkdtemp(), output_name="result.xlsx")
        finally:
            await client.aclose()
        self.assertEqual(result["error"], "candidate_unavailable")

    async def test_invalid_candidate_is_rejected_before_any_request(self):
        calls = []
        client = make_client(handler, count=calls)
        try:
            result = await workflow.create_workbook(
                client, candidate_id="viewer:not-a-receipt:bad",
                scope="separate", output_dir=tempfile.mkdtemp(),
                output_name="result.xlsx")
        finally:
            await client.aclose()
        self.assertEqual(result["error"], "invalid_candidate_id")
        self.assertEqual(calls, [])
