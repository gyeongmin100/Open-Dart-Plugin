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


class DocumentDownloadTests(unittest.IsolatedAsyncioTestCase):
    async def test_get_zip_text_returns_malformed_document_without_xml_parsing(self) -> None:
        document = "<DOCUMENT><P>삼양식품 & 원문</P></DOCUMENT>".encode("utf-8")
        client = DartClient("test-key")
        client._http = FakeHttp(zip_bytes("document.xml", document))

        result = await client.get_zip_text("/document.xml", {"rcept_no": "20230321001381"})

        self.assertEqual(result["filename"], "document.xml")
        self.assertEqual(result["content"], "<DOCUMENT><P>삼양식품 & 원문</P></DOCUMENT>")
        self.assertEqual(client._http.request_params[1]["crtfc_key"], "test-key")


if __name__ == "__main__":
    unittest.main()
