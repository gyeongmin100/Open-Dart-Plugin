import io
import zipfile
import unittest

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from opendartmcp.client import DartClient


class FakeResponse:
    def __init__(self, content: bytes):
        self.content = content

    def raise_for_status(self) -> None:
        return None


class FakeHttp:
    def __init__(self, content: bytes):
        self.content = content
        self.request_params = None

    async def get(self, path: str, params: dict):
        self.request_params = (path, params)
        return FakeResponse(self.content)


def zip_bytes(filename: str, content: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(filename, content)
    return buffer.getvalue()


def multi_zip_bytes(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for filename, content in entries.items():
            archive.writestr(filename, content)
    return buffer.getvalue()


class DocumentDownloadTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_zip_text_returns_malformed_document_without_xml_parsing(self) -> None:
        document = "<DOCUMENT><P>삼양식품 & 원문</P></DOCUMENT>".encode("utf-8")
        client = DartClient("test-key")
        client._http = FakeHttp(zip_bytes("document.xml", document))

        result = await client.get_zip_text("/document.xml", {"rcept_no": "20230321001381"})

        self.assertEqual(result["filename"], "document.xml")
        self.assertEqual(result["content"], "<DOCUMENT><P>삼양식품 & 원문</P></DOCUMENT>")
        self.assertEqual(client._http.request_params[1]["crtfc_key"], "test-key")

    def _multi_doc_zip(self) -> bytes:
        body = "<DOCUMENT><DOCUMENT-NAME ACODE=\"11011\">사업보고서</DOCUMENT-NAME><P>본문</P></DOCUMENT>"
        audit = "<DOCUMENT><DOCUMENT-NAME>감사보고서</DOCUMENT-NAME><P>별도</P></DOCUMENT>"
        consolidated = "<DOCUMENT><DOCUMENT-NAME>연결감사보고서</DOCUMENT-NAME><P>연결</P></DOCUMENT>"
        return multi_zip_bytes({
            "20230321001381.xml": body.encode("utf-8"),
            "20230321001381_00760.xml": audit.encode("utf-8"),
            "20230321001381_00761.xml": consolidated.encode("utf-8"),
        })

    async def test_get_zip_text_lists_all_documents_with_titles(self) -> None:
        client = DartClient("test-key")
        client._http = FakeHttp(self._multi_doc_zip())

        result = await client.get_zip_text("/document.xml", {"rcept_no": "20230321001381"})

        self.assertEqual(result["filename"], "20230321001381.xml")
        self.assertIn("본문", result["content"])
        self.assertEqual(result["documents"], [
            {"filename": "20230321001381.xml", "title": "사업보고서"},
            {"filename": "20230321001381_00760.xml", "title": "감사보고서"},
            {"filename": "20230321001381_00761.xml", "title": "연결감사보고서"},
        ])

    async def test_get_zip_text_selects_attachment_by_doc_name(self) -> None:
        client = DartClient("test-key")
        client._http = FakeHttp(self._multi_doc_zip())

        result = await client.get_zip_text(
            "/document.xml", {"rcept_no": "20230321001381"},
            doc_name="20230321001381_00761.xml")

        self.assertEqual(result["filename"], "20230321001381_00761.xml")
        self.assertIn("연결", result["content"])

    async def test_get_zip_text_unknown_doc_name_raises(self) -> None:
        from opendartmcp.errors import DartApiError

        client = DartClient("test-key")
        client._http = FakeHttp(self._multi_doc_zip())

        with self.assertRaises(DartApiError):
            await client.get_zip_text(
                "/document.xml", {"rcept_no": "20230321001381"},
                doc_name="nope.xml")


if __name__ == "__main__":
    unittest.main()
