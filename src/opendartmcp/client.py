import io
import re
import zipfile

import httpx
import xmltodict

from opendartmcp.errors import DartApiError


class DartClient:
    BASE_URL = "https://opendart.fss.or.kr/api"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._http = httpx.AsyncClient(base_url=self.BASE_URL, timeout=30.0)

    async def aclose(self):
        await self._http.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()

    async def get_json(self, path: str, params: dict) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        response = await self._http.get(path, params=params)
        response.raise_for_status()
        data = response.json()
        status = data.get("status", "000")
        if status != "000":
            message = data.get("message", "")
            raise DartApiError(status, message)
        return data

    async def get_zip_text(self, path: str, params: dict,
                           doc_name: str | None = None) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        response = await self._http.get(path, params=params)
        response.raise_for_status()
        content = response.content
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                document_names = [
                    name for name in zf.namelist()
                    if name.lower().endswith((".xml", ".html", ".htm"))
                ]
                if not document_names:
                    raise ValueError("ZIP response does not contain a document file.")
                document_names.sort(key=lambda name: (not name.lower().endswith(".xml"), name))
                if doc_name:
                    if doc_name not in document_names:
                        raise DartApiError(
                            "999",
                            f"'{doc_name}' is not in this disclosure. "
                            f"Available: {document_names}",
                        )
                    filename = doc_name
                else:
                    filename = document_names[0]
                with zf.open(filename) as document_file:
                    raw_content = document_file.read()
                documents = [
                    {"filename": name, "title": self._document_title(zf, name)}
                    for name in document_names
                ]
        except zipfile.BadZipFile:
            try:
                error_data = response.json()
                status = error_data.get("status", "999")
                message = error_data.get("message", "")
                raise DartApiError(status, message)
            except (ValueError, KeyError):
                raise DartApiError("999", "ZIP response could not be parsed.")

        return {
            "filename": filename,
            "content": self._decode_document(raw_content),
            "documents": documents,
        }

    @staticmethod
    def _document_title(zf: "zipfile.ZipFile", name: str) -> str:
        """문서 머리의 <DOCUMENT-NAME>에서 제목 추출 (예: 감사보고서)."""
        with zf.open(name) as document_file:
            head = document_file.read(4096)
        text = DartClient._decode_document(head)
        match = re.search(r"<DOCUMENT-NAME[^>]*>([^<]*)", text)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _decode_document(content: bytes) -> str:
        for encoding in ("utf-8", "cp949", "euc-kr"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace")

    async def get_zip_xml(self, path: str, params: dict) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        response = await self._http.get(path, params=params)
        response.raise_for_status()
        content = response.content
        # ZIP이 아닌 경우 JSON 에러 응답일 수 있음
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                xml_names = [name for name in zf.namelist() if name.endswith(".xml")]
                if not xml_names:
                    raise ValueError("ZIP 파일에 XML 파일이 없습니다")
                with zf.open(xml_names[0]) as xml_file:
                    data = xmltodict.parse(xml_file.read())
        except zipfile.BadZipFile:
            # API 인증 오류 등의 경우 JSON 에러 응답이 반환될 수 있음
            try:
                error_data = response.json()
                status = error_data.get("status", "999")
                message = error_data.get("message", "")
                raise DartApiError(status, message)
            except (ValueError, KeyError):
                raise DartApiError("999", "ZIP 파일 응답을 파싱할 수 없습니다. API 인증 오류이거나 잘못된 요청일 수 있습니다.")
        return data
