import io
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
