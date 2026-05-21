from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from opendartmcp.client import DartClient


def register(mcp: FastMCP, client: DartClient) -> None:
    @mcp.tool()
    async def get_single_company_account(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """단일 회사의 주요 재무제표 계정을 조회합니다 (자산총계, 부채총계, 자본총계, 매출액, 영업이익, 당기순이익 등).

        Args:
            corp_code: DART 기업 고유번호 8자리 (get_corp_codes 툴로 조회)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11013"=1분기, "11012"=반기, "11014"=3분기, "11011"=사업보고서)
        """
        params = {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        }
        return await client.get_json("/fnlttSinglAcnt.json", params)

    @mcp.tool()
    async def get_multi_company_account(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """여러 회사의 주요 재무 계정을 한 번에 조회합니다.

        Args:
            corp_code: 쉼표로 구분한 복수 기업 고유번호 (최대 100개, 예: "00126380,00164742")
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11013"=1분기, "11012"=반기, "11014"=3분기, "11011"=사업보고서)
        """
        params = {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        }
        return await client.get_json("/fnlttMultiAcnt.json", params)

    @mcp.tool()
    async def get_xbrl_financial(rcept_no: str, reprt_code: str) -> dict:
        """XBRL 형식의 재무제표 원본을 조회합니다 (ZIP → XML → dict 변환).

        Args:
            rcept_no: 접수번호 14자리 (필수)
            reprt_code: 보고서 코드 ("11013"=1분기, "11012"=반기, "11014"=3분기, "11011"=사업보고서)
        """
        return await client.get_zip_xml("/fnlttXbrl.xml", {"rcept_no": rcept_no, "reprt_code": reprt_code})

    @mcp.tool()
    async def get_single_full_financial(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
        fs_div: str,
    ) -> dict:
        """단일 회사의 전체 재무제표를 조회합니다 (모든 계정 포함).

        Args:
            corp_code: DART 기업 고유번호 8자리 (get_corp_codes 툴로 조회)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11013"=1분기, "11012"=반기, "11014"=3분기, "11011"=사업보고서)
            fs_div: 재무제표 구분 ("OFS"=별도, "CFS"=연결)
        """
        params = {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
            "fs_div": fs_div,
        }
        return await client.get_json("/fnlttSinglAcntAll.json", params)

    @mcp.tool()
    async def get_xbrl_taxonomy(sj_div: str) -> dict:
        """XBRL 표준 재무제표 양식(택사노미)을 조회합니다.

        Args:
            sj_div: 재무제표 구분 코드. 재무상태표="BS1"~"BS4", 손익계산서="IS1"~"IS4", 포괄손익계산서="CIS1"~"CIS4", 단일포괄손익계산서="DCIS1"~"DCIS8", 현금흐름표="CF1"~"CF4", 자본변동표="SCE1"~"SCE2" (숫자 접미사는 연결/개별 및 분류방식 조합)
        """
        return await client.get_json("/xbrlTaxonomy.json", {"sj_div": sj_div})

    @mcp.tool()
    async def get_single_financial_index(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
        idx_cl_code: str,
    ) -> dict:
        """단일 회사의 주요 재무 지표를 조회합니다 (수익성, 안정성, 성장성, 활동성 지표).

        Args:
            corp_code: DART 기업 고유번호 8자리 (get_corp_codes 툴로 조회)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11013"=1분기, "11012"=반기, "11014"=3분기, "11011"=사업보고서)
            idx_cl_code: 지표 분류 코드 ("M210000"=수익성지표, "M220000"=안정성지표, "M230000"=성장성지표, "M240000"=활동성지표)
        """
        params = {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
            "idx_cl_code": idx_cl_code,
        }
        return await client.get_json("/fnlttSinglIndx.json", params)

    @mcp.tool()
    async def get_multi_financial_index(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
        idx_cl_code: str,
    ) -> dict:
        """여러 회사의 주요 재무 지표를 한 번에 조회합니다.

        Args:
            corp_code: 쉼표로 구분한 복수 기업 고유번호 (최대 100개, 예: "00126380,00164742")
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11013"=1분기, "11012"=반기, "11014"=3분기, "11011"=사업보고서)
            idx_cl_code: 지표 분류 코드 ("M210000"=수익성지표, "M220000"=안정성지표, "M230000"=성장성지표, "M240000"=활동성지표)
        """
        params = {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
            "idx_cl_code": idx_cl_code,
        }
        return await client.get_json("/fnlttCmpnyIndx.json", params)
