import logging
import unittest

import httpx

from opendartmcp.client import DartClient
from opendartmcp.errors import DartHttpError
from tests.test_client_zip_helpers import make_client


API_KEY = "secret-api-key-value"


class SecretRedactionTest(unittest.IsolatedAsyncioTestCase):
    def _client(self):
        client = make_client(lambda request: httpx.Response(500))
        client.api_key = API_KEY
        return client

    async def _assert_safe_error(self, call):
        client = self._client()
        try:
            with self.assertRaises(DartHttpError) as caught:
                await call(client)
        finally:
            await client.aclose()
        message = str(caught.exception)
        self.assertNotIn(API_KEY, message)
        self.assertNotIn("crtfc_key", message)
        self.assertEqual(caught.exception.status_code, 500)

    async def test_get_json_http_error_is_safe(self):
        await self._assert_safe_error(
            lambda client: client.get_json("/company.json", {}))

    async def test_download_zip_http_error_is_safe(self):
        await self._assert_safe_error(
            lambda client: client.download_zip("/document.xml", {}))

    async def test_get_zip_xml_http_error_is_safe(self):
        await self._assert_safe_error(
            lambda client: client.get_zip_xml("/corpCode.xml", {}))

    async def test_httpx_log_redacts_api_key(self):
        records = []

        class Capture(logging.Handler):
            def emit(self, record):
                records.append(record.getMessage())

        logger = logging.getLogger("httpx")
        handler = Capture()
        old_level = logger.level
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        client = self._client()
        try:
            with self.assertRaises(DartHttpError):
                await client.get_json("/company.json", {})
        finally:
            await client.aclose()
            logger.removeHandler(handler)
            logger.setLevel(old_level)

        blob = "\n".join(records)
        self.assertTrue(records)
        self.assertNotIn(API_KEY, blob)
        self.assertIn("crtfc_key=***", blob)
