from __future__ import annotations

# DS005 주요사항보고서 주요정보 툴 모듈
#
# WebFetch로 확인된 엔드포인트 (opendart.fss.or.kr/guide/main.do?apiGrpCd=DS005):
#   apiId=2020018: /astInhtrfEtcPtbkOpt.json   (자산양수도(기타), 풋백옵션)
#   apiId=2020019: /dfOcr.json                  (부도발생)
#   apiId=2020020: /bsnSp.json                  (영업정지)
#   apiId=2020021: /ctrcvsBgrq.json             (회생절차 개시신청)
#   apiId=2020022: /dsRsOcr.json               (해산사유 발생)
#   apiId=2020023: /piicDecsn.json              (유상증자 결정)
#   apiId=2020024: /fricDecsn.json              (무상증자 결정)
#   apiId=2020025: /pifricDecsn.json            (유무상증자 결정)
#   apiId=2020026: /crDecsn.json               (감자 결정)
#   apiId=2020027: /bnkMngtPcbg.json           (채권은행 등의 관리절차 개시)
#   apiId=2020028: /lwstLg.json                (소송 등의 제기)
#   apiId=2020029: /ovLstDecsn.json            (해외 증권시장 주권등 상장 결정)
#   apiId=2020030: /ovDlstDecsn.json           (해외 증권시장 주권등 상장폐지 결정)
#   apiId=2020031: /ovLst.json                 (해외 증권시장 주권등 상장)
#   apiId=2020032: /ovDlst.json                (해외 증권시장 주권등 상장폐지)
#   apiId=2020033: /cvbdIsDecsn.json           (전환사채권 발행결정)
#   apiId=2020034: /bdwtIsDecsn.json           (신주인수권부사채권 발행결정)
#   apiId=2020035: /exbdIsDecsn.json           (교환사채권 발행결정)
#   apiId=2020036: /bnkMngtPcsp.json           (채권은행 등의 관리절차 중단)
#   apiId=2020037: /wdCocobdIsDecsn.json       (상각형 조건부자본증권 발행결정)
#   apiId=2020038: /tsstkAqDecsn.json          (자기주식 취득 결정)
#   apiId=2020039: /tsstkDpDecsn.json          (자기주식 처분 결정)
#   apiId=2020040: /tsstkAqTrctrCnsDecsn.json  (자기주식취득 신탁계약 체결 결정)
#   apiId=2020041: /tsstkAqTrctrCcDecsn.json   (자기주식취득 신탁계약 해지 결정)
#   apiId=2020042: /bsnInhDecsn.json           (영업양수 결정)
#   apiId=2020043: /bsnTrfDecsn.json           (영업양도 결정)
#   apiId=2020044: /tgastInhDecsn.json         (유형자산 양수 결정)
#   apiId=2020045: /tgastTrfDecsn.json         (유형자산 양도 결정)
#   apiId=2020046: /otcprStkInvscrInhDecsn.json (타법인 주식 및 출자증권 양수결정)
#   apiId=2020047: /otcprStkInvscrTrfDecsn.json (타법인 주식 및 출자증권 양도결정)
#   apiId=2020048: /stkrtbdInhDecsn.json       (주권 관련 사채권 양수 결정)
#   apiId=2020049: /stkrtbdTrfDecsn.json       (주권 관련 사채권 양도 결정)
#   apiId=2020050: /cmpMgDecsn.json            (회사합병 결정)
#   apiId=2020051: /cmpDvDecsn.json            (회사분할 결정)
#   apiId=2020052: /cmpDvmgDecsn.json          (회사분할합병 결정)
#   apiId=2020053: /stkExtrDecsn.json          (주식교환·이전 결정)

from mcp.server.fastmcp import FastMCP

from opendartmcp.client import DartClient


def register(mcp: FastMCP, client: DartClient) -> None:
    @mcp.tool()
    async def get_other_asset_acquisition(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """자산양수도(기타), 풋백옵션 - 주요사항보고서 내 자산양수도(기타) 및 풋백옵션 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/astInhtrfEtcPtbkOpt.json", params)

    @mcp.tool()
    async def get_bankruptcy_report(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """부도발생 - 주요사항보고서 내 부도발생 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/dfOcr.json", params)

    @mcp.tool()
    async def get_business_suspension_report(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """영업정지 - 주요사항보고서 내 영업정지 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/bsnSp.json", params)

    @mcp.tool()
    async def get_rehabilitation_report(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """회생절차 개시신청 - 주요사항보고서 내 회생절차 개시신청 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/ctrcvsBgrq.json", params)

    @mcp.tool()
    async def get_dissolution_report(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """해산사유 발생 - 주요사항보고서 내 해산사유 발생 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/dsRsOcr.json", params)

    @mcp.tool()
    async def get_paid_capital_increase(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """유상증자 결정 - 주요사항보고서 내 유상증자 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/piicDecsn.json", params)

    @mcp.tool()
    async def get_free_capital_increase(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """무상증자 결정 - 주요사항보고서 내 무상증자 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/fricDecsn.json", params)

    @mcp.tool()
    async def get_paid_free_capital_increase(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """유무상증자 결정 - 주요사항보고서 내 유무상증자 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/pifricDecsn.json", params)

    @mcp.tool()
    async def get_capital_reduction(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """감자 결정 - 주요사항보고서 내 감자 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/crDecsn.json", params)

    @mcp.tool()
    async def get_creditor_management(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """채권은행 등의 관리절차 개시 - 주요사항보고서 내 채권은행 관리절차 개시 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/bnkMngtPcbg.json", params)

    @mcp.tool()
    async def get_lawsuit_report(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """소송 등의 제기·판결 - 주요사항보고서 내 소송 등의 제기 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/lwstLg.json", params)

    @mcp.tool()
    async def get_overseas_listing_decision(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """해외 증권시장 주권 신규상장 결정 - 주요사항보고서 내 해외 증권시장 주권등 상장 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/ovLstDecsn.json", params)

    @mcp.tool()
    async def get_overseas_delisting_decision(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """해외 증권시장 주권 상장폐지 결정 - 주요사항보고서 내 해외 증권시장 주권등 상장폐지 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/ovDlstDecsn.json", params)

    @mcp.tool()
    async def get_overseas_listing(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """해외 증권시장 주권등 상장 - 주요사항보고서 내 해외 증권시장 주권등 상장 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/ovLst.json", params)

    @mcp.tool()
    async def get_overseas_delisting(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """해외 증권시장 주권등 상장폐지 - 주요사항보고서 내 해외 증권시장 주권등 상장폐지 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/ovDlst.json", params)

    @mcp.tool()
    async def get_convertible_bond(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """전환사채권 발행결정 - 주요사항보고서 내 전환사채권 발행결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/cvbdIsDecsn.json", params)

    @mcp.tool()
    async def get_bond_with_warrants(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """신주인수권부사채권 발행결정 - 주요사항보고서 내 신주인수권부사채권 발행결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/bdwtIsDecsn.json", params)

    @mcp.tool()
    async def get_exchangeable_bond(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """교환사채권 발행결정 - 주요사항보고서 내 교환사채권 발행결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/exbdIsDecsn.json", params)

    @mcp.tool()
    async def get_creditor_management_suspension(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """채권은행 등의 관리절차 중단 - 주요사항보고서 내 채권은행 관리절차 중단 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/bnkMngtPcsp.json", params)

    @mcp.tool()
    async def get_conditional_capital_issuance(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """상각형 조건부자본증권 발행결정 - 주요사항보고서 내 상각형 조건부자본증권 발행결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/wdCocobdIsDecsn.json", params)

    @mcp.tool()
    async def get_stock_acquisition(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """자기주식 취득결정 - 주요사항보고서 내 자기주식 취득 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/tsstkAqDecsn.json", params)

    @mcp.tool()
    async def get_stock_disposal(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """자기주식 처분결정 - 주요사항보고서 내 자기주식 처분 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/tsstkDpDecsn.json", params)

    @mcp.tool()
    async def get_treasury_stock_trust_conclude(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """자기주식취득 신탁계약 체결 결정 - 주요사항보고서 내 자기주식취득 신탁계약 체결 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/tsstkAqTrctrCnsDecsn.json", params)

    @mcp.tool()
    async def get_treasury_stock_trust_terminate(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """자기주식취득 신탁계약 해지 결정 - 주요사항보고서 내 자기주식취득 신탁계약 해지 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/tsstkAqTrctrCcDecsn.json", params)

    @mcp.tool()
    async def get_business_acquisition(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """영업양수 결정 - 주요사항보고서 내 영업양수 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/bsnInhDecsn.json", params)

    @mcp.tool()
    async def get_business_transfer(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """영업양도 결정 - 주요사항보고서 내 영업양도 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/bsnTrfDecsn.json", params)

    @mcp.tool()
    async def get_tangible_asset_acquisition(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """유형자산 양수 결정 - 주요사항보고서 내 유형자산 양수 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/tgastInhDecsn.json", params)

    @mcp.tool()
    async def get_tangible_asset_transfer(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """유형자산 양도 결정 - 주요사항보고서 내 유형자산 양도 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/tgastTrfDecsn.json", params)

    @mcp.tool()
    async def get_equity_investment_acquisition(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """타법인 주식 및 출자증권 양수결정 - 주요사항보고서 내 타법인 주식 및 출자증권 양수 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/otcprStkInvscrInhDecsn.json", params)

    @mcp.tool()
    async def get_equity_investment_transfer(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """타법인 주식 및 출자증권 양도결정 - 주요사항보고서 내 타법인 주식 및 출자증권 양도 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/otcprStkInvscrTrfDecsn.json", params)

    @mcp.tool()
    async def get_equity_securities_acquisition(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """주권 관련 사채권 양수 결정 - 주요사항보고서 내 주권 관련 사채권 양수 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/stkrtbdInhDecsn.json", params)

    @mcp.tool()
    async def get_equity_securities_transfer(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """주권 관련 사채권 양도 결정 - 주요사항보고서 내 주권 관련 사채권 양도 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/stkrtbdTrfDecsn.json", params)

    @mcp.tool()
    async def get_merger_decision(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """합병 결정 - 주요사항보고서 내 회사합병 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/cmpMgDecsn.json", params)

    @mcp.tool()
    async def get_division_decision(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """회사분할 결정 - 주요사항보고서 내 회사분할 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/cmpDvDecsn.json", params)

    @mcp.tool()
    async def get_division_merger_decision(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """회사분할합병 결정 - 주요사항보고서 내 회사분할합병 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/cmpDvmgDecsn.json", params)

    @mcp.tool()
    async def get_stock_exchange_decision(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """주식교환·이전 결정 - 주요사항보고서 내 주식교환·이전 결정 주요 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD, 선택)
            end_de: 종료일 (YYYYMMDD, 선택)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
        }.items() if v is not None}
        return await client.get_json("/stkExtrDecsn.json", params)
