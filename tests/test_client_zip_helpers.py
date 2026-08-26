import time
import unittest

import httpx

from opendartmcp.client import CachingDartClient, DartClient
from opendartmcp.errors import DartApiError
from tests.fixtures import annual_report_zip


def make_client(handler, *, count=None, client_class=DartClient):
    """MockTransport로 DART HTTP 호출을 가로챈 DartClient."""
    client = client_class("test-key")

    async def wrapped(request):
        if count is not None:
            count.append(str(request.url.path))
        return handler(request)

    client._http = httpx.AsyncClient(
        base_url=DartClient.BASE_URL, transport=httpx.MockTransport(wrapped))
    return client


class ClientZipHelperTest(unittest.IsolatedAsyncioTestCase):
    async def test_download_zip_returns_bytes_once(self):
        calls = []
        client = make_client(
            lambda r: httpx.Response(200, content=annual_report_zip()), count=calls)
        try:
            content = await client.download_zip("/document.xml",
                                                {"rcept_no": "20250319000665"})
        finally:
            await client.aclose()
        self.assertEqual(content[:2], b"PK")
        self.assertEqual(calls, ["/api/document.xml"])

    async def test_same_filing_zip_is_reused(self):
        calls = []
        client = make_client(
            lambda r: httpx.Response(200, content=annual_report_zip()), count=calls,
            client_class=CachingDartClient)
        params = {"rcept_no": "20250319000665"}
        try:
            first = await client.download_zip("/document.xml", params)
            second = await client.download_zip("/document.xml", params)
        finally:
            await client.aclose()
        self.assertIs(first, second)
        self.assertEqual(calls, ["/api/document.xml"])

    async def test_expired_filing_zip_is_downloaded_again(self):
        calls = []
        client = make_client(
            lambda r: httpx.Response(200, content=annual_report_zip()), count=calls,
            client_class=CachingDartClient)
        params = {"rcept_no": "20250319000665"}
        key = "/document.xml:20250319000665"
        try:
            first = await client.download_zip("/document.xml", params)
            client._zips[key] = (time.monotonic() - 301, first)
            await client.download_zip("/document.xml", params)
        finally:
            await client.aclose()
        self.assertEqual(calls, ["/api/document.xml", "/api/document.xml"])

    async def test_cached_zip_can_seed_another_client(self):
        first = make_client(
            lambda r: httpx.Response(200, content=annual_report_zip()),
            client_class=CachingDartClient)
        params = {"rcept_no": "20250319000665"}
        try:
            expected = await first.download_zip("/document.xml", params)
            snapshot = first.snapshot_zips()
        finally:
            await first.aclose()

        calls = []
        second = CachingDartClient("test-key", snapshot)
        second._http = httpx.AsyncClient(
            base_url=DartClient.BASE_URL,
            transport=httpx.MockTransport(lambda r: calls.append(r)))
        try:
            actual = await second.download_zip("/document.xml", params)
        finally:
            await second.aclose()
        self.assertIs(actual, expected)
        self.assertEqual(calls, [])

    async def test_zip_documents_lists_titles(self):
        with DartClient.open_zip(annual_report_zip()) as zf:
            documents = DartClient.zip_documents(zf)
        self.assertEqual([d["title"] for d in documents],
                         ["사업보고서", "감사보고서", "연결감사보고서"])

    async def test_open_zip_maps_json_error_to_dart_api_error(self):
        with self.assertRaises(DartApiError):
            DartClient.open_zip(b'{"status":"013","message":"no data"}')

    async def test_get_zip_text_behaviour_unchanged(self):
        client = make_client(lambda r: httpx.Response(
            200, content=annual_report_zip()))
        try:
            result = await client.get_zip_text(
                "/document.xml", {"rcept_no": "20250319000665"},
                doc_name="20250319000665_00761.xml")
        finally:
            await client.aclose()
        self.assertEqual(set(result), {"filename", "content", "documents"})
        self.assertEqual(result["filename"], "20250319000665_00761.xml")
        self.assertIn("연결재무상태표", result["content"])
        self.assertEqual(len(result["documents"]), 3)

    async def test_get_zip_text_returns_body_without_doc_name(self):
        client = make_client(lambda r: httpx.Response(
            200, content=annual_report_zip()))
        try:
            result = await client.get_zip_text(
                "/document.xml", {"rcept_no": "20250319000665"})
        finally:
            await client.aclose()
        self.assertEqual(result["filename"], "20250319000665.xml")

    async def test_get_zip_text_rejects_unknown_doc_name(self):
        client = make_client(lambda r: httpx.Response(
            200, content=annual_report_zip()))
        try:
            with self.assertRaises(DartApiError):
                await client.get_zip_text(
                    "/document.xml", {"rcept_no": "20250319000665"},
                    doc_name="nope.xml")
        finally:
            await client.aclose()
