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

    async def get_xml_as_dict(self, path: str, params: dict) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        response = await self._http.get(path, params=params)
        response.raise_for_status()
        data = xmltodict.parse(response.text)
        root = next(iter(data.values()), {}) if data else {}
        if isinstance(root, dict):
            status = root.get("status", "000")
            if status != "000":
                message = root.get("message", "")
                raise DartApiError(status, message)
        return data

    async def get_zip_xml(self, path: str, params: dict) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        response = await self._http.get(path, params=params)
        response.raise_for_status()
        content = response.content
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as zf:
                xml_names = [name for name in zf.namelist() if name.endswith(".xml")]
                if not xml_names:
                    raise ValueError("ZIP 파일에 XML 파일이 없습니다")
                with zf.open(xml_names[0]) as xml_file:
                    data = xmltodict.parse(xml_file.read())
        except zipfile.BadZipFile:
            raise DartApiError("000", "ZIP 파일 응답을 파싱할 수 없습니다. API 인증 오류이거나 잘못된 요청일 수 있습니다.")
        return data
