import json
import tempfile
import unittest
from pathlib import Path

import httpx
from mcp.server.fastmcp import FastMCP

from opendartmcp.tools import workbook
from tests.fixtures import annual_report_zip
from tests.test_client_zip_helpers import make_client

RCEPT = "20250319000665"


def _payload(result):
    """FastMCP call_tool 결과에서 도구 반환 dict를 꺼낸다."""
    if isinstance(result, tuple):
        content, structured = result
        if isinstance(structured, dict):
            return structured.get("result", structured)
        return json.loads(content[0].text)
    return json.loads(result[0].text)


class WorkbookToolTest(unittest.IsolatedAsyncioTestCase):
    async def test_tool_is_registered_with_scope_enum(self):
        mcp = FastMCP("test")
        client = make_client(lambda r: httpx.Response(200, content=annual_report_zip()))
        try:
            workbook.register(mcp, client)
            tools = {t.name: t for t in await mcp.list_tools()}
            self.assertIn("create_financial_workbook", tools)
            self.assertIn("list_financial_document_candidates", tools)
            schema = tools["create_financial_workbook"].inputSchema
            self.assertEqual(schema["properties"]["scope"]["enum"],
                             ["consolidated", "separate"])
            self.assertEqual(sorted(schema["required"]),
                             ["candidate_id", "output_dir", "output_name", "scope"])
            listing = tools["list_financial_document_candidates"].inputSchema
            self.assertEqual(sorted(listing["required"]), ["rcept_no"])
        finally:
            await client.aclose()

    async def test_successful_call_returns_workbook_path_only(self):
        out = Path(tempfile.mkdtemp())
        mcp = FastMCP("test")
        client = make_client(lambda r: httpx.Response(200, content=annual_report_zip()))
        try:
            workbook.register(mcp, client)
            result = await mcp.call_tool("create_financial_workbook", {
                "candidate_id": f"body:{RCEPT}", "scope": "consolidated",
                "output_dir": str(out), "output_name": "결과.xlsx",
                "allow_body": True})
        finally:
            await client.aclose()
        payload = _payload(result)
        self.assertTrue(payload["ok"], payload)
        self.assertEqual(Path(payload["workbook"]).name, "결과.xlsx")
        self.assertNotIn("content", payload)

    async def test_dart_api_error_becomes_structured_error(self):
        mcp = FastMCP("test")
        client = make_client(lambda r: httpx.Response(
            200, content=b'{"status":"013","message":"no data"}'))
        try:
            workbook.register(mcp, client)
            result = await mcp.call_tool("create_financial_workbook", {
                "candidate_id": f"body:{RCEPT}", "scope": "consolidated",
                "output_dir": ".", "output_name": "x.xlsx",
                "allow_body": True})
        finally:
            await client.aclose()
        payload = _payload(result)
        self.assertEqual(payload["error"], "dart_api_error")
        self.assertEqual(payload["status"], "013")

    async def test_unexpected_error_has_no_traceback(self):
        mcp = FastMCP("test")
        client = make_client(lambda r: httpx.Response(500))
        try:
            workbook.register(mcp, client)
            result = await mcp.call_tool("create_financial_workbook", {
                "candidate_id": f"body:{RCEPT}", "scope": "consolidated",
                "output_dir": ".", "output_name": "x.xlsx",
                "allow_body": True})
        finally:
            await client.aclose()
        payload = _payload(result)
        self.assertEqual(payload["error"], "internal_error")
        self.assertNotIn("Traceback", json.dumps(payload))
        self.assertLess(len(json.dumps(payload, ensure_ascii=False)), 1024)
