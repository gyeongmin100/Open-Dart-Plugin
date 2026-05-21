import io
import zipfile

import httpx
import xmltodict

from opendartmcp.errors import DartApiError

BASE_URL = "https://opendart.fss.or.kr/api"


class DartClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_json(self, path: str, params: dict) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/{path}", params=params)
            response.raise_for_status()
            data = response.json()
        status = data.get("status", "000")
        if status != "000":
            message = data.get("message", "")
            raise DartApiError(status, message)
        return data

    async def get_xml_as_dict(self, path: str, params: dict) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/{path}", params=params)
            response.raise_for_status()
            data = xmltodict.parse(response.content)
        # XML 응답 중 status 필드가 있는 경우 오류 확인
        root = next(iter(data.values())) if data else {}
        if isinstance(root, dict):
            status = root.get("status")
            if status and status != "000":
                message = root.get("message", "")
                raise DartApiError(status, message)
        return data

    async def get_zip_xml(self, path: str, params: dict) -> dict:
        params = {**params, "crtfc_key": self.api_key}
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/{path}", params=params)
            response.raise_for_status()
            content = response.content
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            xml_names = [name for name in zf.namelist() if name.endswith(".xml")]
            if not xml_names:
                raise ValueError("ZIP 파일에 XML 파일이 없습니다")
            with zf.open(xml_names[0]) as xml_file:
                data = xmltodict.parse(xml_file.read())
        return data
