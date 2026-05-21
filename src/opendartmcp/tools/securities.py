from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from opendartmcp.client import DartClient


def register(mcp: FastMCP, client: DartClient) -> None:
    @mcp.tool()
    async def get_equity_securities(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """지분증권 증권신고서 주요 정보를 조회합니다. 주식 발행 및 공모 관련 정보를 포함합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리, 필수)
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)
        """
        params: dict = {"corp_code": corp_code}
        if bgn_de is not None:
            params["bgn_de"] = bgn_de
        if end_de is not None:
            params["end_de"] = end_de
        return await client.get_json("/estkRs.json", params)

    @mcp.tool()
    async def get_debt_securities(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """채무증권(회사채 등) 증권신고서 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리, 필수)
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)
        """
        params: dict = {"corp_code": corp_code}
        if bgn_de is not None:
            params["bgn_de"] = bgn_de
        if end_de is not None:
            params["end_de"] = end_de
        return await client.get_json("/bdRs.json", params)

    @mcp.tool()
    async def get_depositary_receipts(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """증권예탁증권(DR) 증권신고서 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리, 필수)
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)
        """
        params: dict = {"corp_code": corp_code}
        if bgn_de is not None:
            params["bgn_de"] = bgn_de
        if end_de is not None:
            params["end_de"] = end_de
        return await client.get_json("/stkdpRs.json", params)

    @mcp.tool()
    async def get_merger_securities(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """합병 관련 증권신고서 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리, 필수)
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)
        """
        params: dict = {"corp_code": corp_code}
        if bgn_de is not None:
            params["bgn_de"] = bgn_de
        if end_de is not None:
            params["end_de"] = end_de
        return await client.get_json("/mgRs.json", params)

    @mcp.tool()
    async def get_stock_exchange_securities(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """주식의 포괄적 교환·이전 증권신고서 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리, 필수)
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)
        """
        params: dict = {"corp_code": corp_code}
        if bgn_de is not None:
            params["bgn_de"] = bgn_de
        if end_de is not None:
            params["end_de"] = end_de
        return await client.get_json("/extrRs.json", params)

    @mcp.tool()
    async def get_division_securities(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """분할 관련 증권신고서 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리, 필수)
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)
        """
        params: dict = {"corp_code": corp_code}
        if bgn_de is not None:
            params["bgn_de"] = bgn_de
        if end_de is not None:
            params["end_de"] = end_de
        return await client.get_json("/dvRs.json", params)
