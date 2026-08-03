import io
import json
import logging
import re
import zipfile

import httpx
import xmltodict

from opendartmcp.errors import DartApiError, DartHttpError


_API_KEY_QUERY = re.compile(r"(?i)(crtfc_key=)[^&\s\"]+")


class _RedactApiKeyFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self._redact(record.msg)
        if isinstance(record.args, dict):
            record.args = {key: self._redact(value)
                           for key, value in record.args.items()}
        elif record.args:
            record.args = tuple(self._redact(value) for value in record.args)
        return True

    @staticmethod
    def _redact(value):
        if isinstance(value, str) or "crtfc_key=" in str(value).lower():
            return _API_KEY_QUERY.sub(r"\1***", str(value))
        return value


logging.getLogger("httpx").addFilter(_RedactApiKeyFilter())


class DartClient:
    BASE_URL = "https://opendart.fss.or.kr/api"
    DART_URL = "https://dart.fss.or.kr"
    # 공시 ZIP은 수 MB라 기본 타임아웃과 분리한다 (plan.md §5.13).
    DOWNLOAD_TIMEOUT = 120.0

    def __init__(self, api_key: str):
        self.api_key = api_key
        # DART는 연결을 간헐적으로 끊는다. 연결 단계 실패만 두 번 더 시도한다
        # (요청이 서버에 닿기 전이라 재시도가 안전하다).
        self._http = httpx.AsyncClient(
            base_url=self.BASE_URL, timeout=30.0,
            transport=httpx.AsyncHTTPTransport(retries=2))

    async def aclose(self):
        await self._http.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()

    async def get_json(self, path: str, params: dict) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        response = await self._http.get(path, params=params)
        self._raise_for_status(response)
        data = response.json()
        status = data.get("status", "000")
        if status != "000":
            message = data.get("message", "")
            raise DartApiError(status, message)
        return data

    async def download_zip(self, path: str, params: dict) -> bytes:
        """공시 ZIP 원본 bytes. 호출자가 같은 bytes를 재사용한다 (plan.md §5.3)."""
        params = {**params, "crtfc_key": self.api_key}
        response = await self._http.get(path, params=params,
                                        timeout=self.DOWNLOAD_TIMEOUT)
        self._raise_for_status(response)
        return response.content

    async def get_dart_html(self, path: str, params: dict) -> str:
        """DART 공개 문서뷰어 HTML. OpenDART ZIP에 빠진 첨부 조회용."""
        response = await self._http.get(f"{self.DART_URL}{path}", params=params,
                                        timeout=self.DOWNLOAD_TIMEOUT)
        self._raise_for_status(response)
        return response.text

    @staticmethod
    def open_zip(content: bytes) -> "zipfile.ZipFile":
        """ZIP bytes를 연다. ZIP이 아니면 DART 오류 JSON으로 간주한다."""
        try:
            return zipfile.ZipFile(io.BytesIO(content))
        except zipfile.BadZipFile:
            try:
                error_data = json.loads(content)
                status = error_data.get("status", "999")
                message = error_data.get("message", "")
            except (ValueError, AttributeError):
                raise DartApiError("999", "ZIP response could not be parsed.")
            raise DartApiError(status, message)

    @staticmethod
    def zip_documents(zf: "zipfile.ZipFile") -> list[dict]:
        """ZIP 안의 문서 목록 [{filename, title}] (xml 우선 정렬)."""
        names = [
            name for name in zf.namelist()
            if name.lower().endswith((".xml", ".html", ".htm"))
        ]
        names.sort(key=lambda name: (not name.lower().endswith(".xml"), name))
        return [{"filename": name, "title": DartClient._document_title(zf, name)}
                for name in names]

    async def get_zip_text(self, path: str, params: dict,
                           doc_name: str | None = None) -> dict:
        content = await self.download_zip(path, params)
        try:
            with self.open_zip(content) as zf:
                documents = self.zip_documents(zf)
                if not documents:
                    raise ValueError(
                        "ZIP response does not contain a document file.")
                document_names = [d["filename"] for d in documents]
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
        except zipfile.BadZipFile:
            # 엔트리가 손상된 경우도 기존처럼 DART 오류로 전달한다.
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

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            raise DartHttpError(response.status_code,
                                response.request.url.path) from None

    async def get_zip_xml(self, path: str, params: dict) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        response = await self._http.get(path, params=params)
        self._raise_for_status(response)
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
