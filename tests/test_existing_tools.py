import unittest

import httpx
from mcp.server.fastmcp import FastMCP

from opendartmcp.tools import disclosure
from tests.fixtures import annual_report_zip
from tests.test_client_zip_helpers import make_client


class ExistingToolsTest(unittest.IsolatedAsyncioTestCase):
    async def test_disclosure_tools_still_registered(self):
        mcp = FastMCP("test")
        client = make_client(lambda r: httpx.Response(200, content=annual_report_zip()))
        try:
            disclosure.register(mcp, client)
            names = {t.name for t in await mcp.list_tools()}
        finally:
            await client.aclose()
        self.assertLessEqual(
            {"search_disclosures", "get_company_info",
             "get_disclosure_document", "get_corp_codes"}, names)

    async def test_search_disclosures_still_calls_list_json(self):
        calls = []
        mcp = FastMCP("test")
        client = make_client(
            lambda r: httpx.Response(200, json={"status": "000", "list": []}),
            count=calls)
        try:
            disclosure.register(mcp, client)
            await mcp.call_tool("search_disclosures", {"corp_code": "00164779"})
        finally:
            await client.aclose()
        self.assertEqual(calls, ["/api/list.json"])

    async def test_server_registers_all_tool_groups(self):
        """create_financial_workbook 추가 후에도 기존 도구 수가 유지된다."""
        from opendartmcp.client import DartClient
        from opendartmcp.tools import (business_report, disclosure as ds,
                                       financial, major_report, securities,
                                       stock_holdings, workbook)

        mcp = FastMCP("test")
        client = DartClient("test-key")
        try:
            for module in (ds, business_report, financial, stock_holdings,
                           major_report, securities, workbook):
                module.register(mcp, client)
            names = {t.name for t in await mcp.list_tools()}
        finally:
            await client.aclose()
        self.assertEqual(len(names), 86)
        self.assertIn("create_financial_workbook", names)
