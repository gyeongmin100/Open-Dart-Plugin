from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from opendartmcp.client import DartClient


def register(mcp: FastMCP, client: DartClient) -> None:
    @mcp.tool()
    async def get_large_holding_report(corp_code: str) -> dict:
        """주식 대량보유 상황보고서를 조회합니다. 5% 이상 주식을 보유한 주요 주주의 보유 현황을 확인할 수 있습니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리, 필수)
        """
        return await client.get_json("/majorstock.json", {"corp_code": corp_code})

    @mcp.tool()
    async def get_executive_stock_report(corp_code: str) -> dict:
        """임원 및 주요주주 소유 보고서를 조회합니다. 내부자(임원, 주요주주)의 주식 소유 현황을 확인할 수 있습니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리, 필수)
        """
        return await client.get_json("/elestock.json", {"corp_code": corp_code})
