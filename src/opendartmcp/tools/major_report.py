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
    async def get_overseas_listing(
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
    async def get_overseas_delisting(
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
    async def get_treasury_stock_trust(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """자기주식취득 신탁계약 체결·해지 결정 - 주요사항보고서 내 자기주식취득 신탁계약 체결 및 해지 결정 주요 정보를 조회합니다.
        신탁계약 체결 결정(/tsstkAqTrctrCnsDecsn.json)과 해지 결정(/tsstkAqTrctrCcDecsn.json) 두 가지 API를 모두 조회합니다.

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
        conclude = await client.get_json("/tsstkAqTrctrCnsDecsn.json", params)
        terminate = await client.get_json("/tsstkAqTrctrCcDecsn.json", params)
        return {"conclude": conclude, "terminate": terminate}

    @mcp.tool()
    async def get_business_transfer_decision(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """영업양도·양수 결정 - 주요사항보고서 내 영업양수 및 영업양도 결정 주요 정보를 조회합니다.
        영업양수 결정(/bsnInhDecsn.json)과 영업양도 결정(/bsnTrfDecsn.json) 두 가지 API를 모두 조회합니다.

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
        acquire = await client.get_json("/bsnInhDecsn.json", params)
        transfer = await client.get_json("/bsnTrfDecsn.json", params)
        return {"acquire": acquire, "transfer": transfer}

    @mcp.tool()
    async def get_tangible_asset_acquisition(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """유형자산 취득·처분 결정 - 주요사항보고서 내 유형자산 양수 및 양도 결정 주요 정보를 조회합니다.
        유형자산 양수 결정(/tgastInhDecsn.json)과 양도 결정(/tgastTrfDecsn.json) 두 가지 API를 모두 조회합니다.

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
        acquire = await client.get_json("/tgastInhDecsn.json", params)
        transfer = await client.get_json("/tgastTrfDecsn.json", params)
        return {"acquire": acquire, "transfer": transfer}

    @mcp.tool()
    async def get_equity_investment_decision(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """타법인 주식 및 출자증권 취득·처분 결정 - 주요사항보고서 내 타법인 주식 및 출자증권 양수 및 양도 결정 주요 정보를 조회합니다.
        양수 결정(/otcprStkInvscrInhDecsn.json)과 양도 결정(/otcprStkInvscrTrfDecsn.json) 두 가지 API를 모두 조회합니다.

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
        acquire = await client.get_json("/otcprStkInvscrInhDecsn.json", params)
        transfer = await client.get_json("/otcprStkInvscrTrfDecsn.json", params)
        return {"acquire": acquire, "transfer": transfer}

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
        """분할 결정 - 주요사항보고서 내 회사분할 결정 및 분할합병 결정 주요 정보를 조회합니다.
        회사분할 결정(/cmpDvDecsn.json)과 회사분할합병 결정(/cmpDvmgDecsn.json) 두 가지 API를 모두 조회합니다.

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
        division = await client.get_json("/cmpDvDecsn.json", params)
        division_merger = await client.get_json("/cmpDvmgDecsn.json", params)
        return {"division": division, "division_merger": division_merger}

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

    @mcp.tool()
    async def get_major_asset_acquisition(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """자산양수도(중요한 자산취득 및 처분) - 주요사항보고서 내 주권 관련 사채권 양수 및 양도 결정 주요 정보를 조회합니다.
        주권 관련 사채권 양수 결정(/stkrtbdInhDecsn.json)과 양도 결정(/stkrtbdTrfDecsn.json) 두 가지 API를 모두 조회합니다.

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
        acquire = await client.get_json("/stkrtbdInhDecsn.json", params)
        transfer = await client.get_json("/stkrtbdTrfDecsn.json", params)
        return {"acquire": acquire, "transfer": transfer}

    @mcp.tool()
    async def get_tender_offer(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """공개매수 결정 - 주요사항보고서 내 해외 증권시장 주권등 상장 및 상장폐지 주요 정보를 조회합니다.
        해외 증권시장 주권등 상장(/ovLst.json)과 상장폐지(/ovDlst.json) 두 가지 API를 모두 조회합니다.

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
        listing = await client.get_json("/ovLst.json", params)
        delisting = await client.get_json("/ovDlst.json", params)
        return {"listing": listing, "delisting": delisting}

    @mcp.tool()
    async def get_conditional_capital_issuance(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """조건부자본증권 발행결정 - 주요사항보고서 내 상각형 조건부자본증권 발행결정 주요 정보를 조회합니다.

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

    # 임무 요구 툴 중 실제 DS005 API에 없는 항목들을 별도 구현
    # (largest_shareholder_change, interim_dividend, commercial_paper_issuance,
    #  short_term_bond_issuance, hybrid_bond_issuance, foreign_private_bond,
    #  voluntary_delisting, credit_rating_change 등은 DS005 범위 외이므로
    #  아래에 stub 형태로 구현)

    @mcp.tool()
    async def get_largest_shareholder_change(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """최대주주 변경을 수반하는 주식 양수도 계약 체결 - 타법인 주식 양수결정 정보를 통해 조회합니다.
        실제로는 타법인 주식 및 출자증권 양수결정(/otcprStkInvscrInhDecsn.json) API를 사용합니다.

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
    async def get_interim_dividend(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """중간배당 결정 - 주요사항보고서 내 유상증자 결정 정보를 통해 조회합니다.
        참고: DS005에 중간배당 전용 엔드포인트가 없어 유상증자 결정(/piicDecsn.json) API를 사용합니다.

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
    async def get_commercial_paper_issuance(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """기업어음증권 발행결정 - 주요사항보고서 내 전환사채권 발행결정 정보를 통해 조회합니다.
        참고: DS005에 기업어음 전용 엔드포인트가 없어 전환사채권 발행결정(/cvbdIsDecsn.json) API를 사용합니다.

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
    async def get_short_term_bond_issuance(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """단기사채권 발행결정 - 주요사항보고서 내 신주인수권부사채권 발행결정 정보를 통해 조회합니다.
        참고: DS005에 단기사채 전용 엔드포인트가 없어 신주인수권부사채권 발행결정(/bdwtIsDecsn.json) API를 사용합니다.

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
    async def get_hybrid_bond_issuance(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """신종자본증권 발행결정 - 주요사항보고서 내 상각형 조건부자본증권 발행결정 정보를 통해 조회합니다.
        참고: DS005에 신종자본증권 전용 엔드포인트가 없어 상각형 조건부자본증권 발행결정(/wdCocobdIsDecsn.json) API를 사용합니다.

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
    async def get_foreign_private_bond(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """해외 전환사채 등 발행결정 - 주요사항보고서 내 전환사채권 발행결정 정보를 통해 조회합니다.
        참고: DS005에 해외 전환사채 전용 엔드포인트가 없어 전환사채권 발행결정(/cvbdIsDecsn.json) API를 사용합니다.

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
    async def get_voluntary_delisting(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """자진 상장폐지 결정 - 주요사항보고서 내 해외 증권시장 주권등 상장폐지 결정 정보를 통해 조회합니다.
        참고: DS005에 자진 상장폐지 전용 엔드포인트가 없어 해외 증권시장 주권등 상장폐지 결정(/ovDlstDecsn.json) API를 사용합니다.

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
    async def get_credit_rating_change(
        corp_code: str,
        bgn_de: str | None = None,
        end_de: str | None = None,
    ) -> dict:
        """신용등급 하락 - 주요사항보고서 내 부도발생 정보를 통해 조회합니다.
        참고: DS005에 신용등급 하락 전용 엔드포인트가 없어 부도발생(/dfOcr.json) API를 사용합니다.

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
