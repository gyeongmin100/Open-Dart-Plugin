from __future__ import annotations

# DS002 정기보고서 주요정보 툴 모듈
#
# WebFetch로 확인된 엔드포인트 (opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS002):
#   apiId=2019004: /irdsSttus.json              (증자(감자) 현황)
#   apiId=2019005: /alotMatter.json             (배당에 관한 사항)
#   apiId=2019006: /tesstkAcqsDspsSttus.json    (자기주식 취득 및 처분 현황)
#   apiId=2019007: /hyslrSttus.json             (최대주주 현황)
#   apiId=2019008: /hyslrChgSttus.json          (최대주주 변동현황)
#   apiId=2019009: /mrhlSttus.json              (소액주주 현황)
#   apiId=2019010: /exctvSttus.json             (임원 현황)
#   apiId=2019011: /empSttus.json               (직원 현황)
#   apiId=2019012: /hmvAuditIndvdlBySttus.json  (이사·감사 개인별 보수현황 5억원 이상)
#   apiId=2019013: /hmvAuditAllSttus.json       (이사·감사 전체의 보수현황)
#   apiId=2019014: /indvdlByPay.json            (개인별 보수지급 금액 5억 이상 상위5인)
#   apiId=2019015: /otrCprInvstmntSttus.json    (타법인 출자현황)
#   apiId=2020002: /stockTotqySttus.json        (주식의 총수 현황)
#   apiId=2020003: /detScritsIsuAcmslt.json     (채무증권 발행실적)
#   apiId=2020004: /entrprsBilScritsNrdmpBlce.json (기업어음증권 미상환 잔액)
#   apiId=2020005: /srtpdPsndbtNrdmpBlce.json   (단기사채 미상환 잔액)
#   apiId=2020006: /cprndNrdmpBlce.json         (회사채 미상환 잔액)
#   apiId=2020007: /newCaplScritsNrdmpBlce.json (신종자본증권 미상환 잔액)
#   apiId=2020008: /cndlCaplScritsNrdmpBlce.json (조건부 자본증권 미상환 잔액)
#   apiId=2020009: /accnutAdtorNmNdAdtOpinion.json (회계감사인 명칭 및 감사의견)
#   apiId=2020010: /adtServcCnclsSttus.json     (감사용역체결현황)
#   apiId=2020011: /accnutAdtorNonAdtServcCnclsSttus.json (비감사용역 계약체결 현황)
#   apiId=2020012: /outcmpnyDrctrNdChangeSttus.json (사외이사 및 변동현황)
#   apiId=2020013: /unrstExctvMendngSttus.json  (미등기임원 보수현황)
#   apiId=2020014: /drctrAdtAllMendngSttusGmtsckConfmAmount.json (이사·감사 전체 보수현황 주총승인)
#   apiId=2020015: /drctrAdtAllMendngSttusMendngPymntamtTyCl.json (이사·감사 전체 보수현황 유형별)
#   apiId=2020016: /pssrpCptalUseDtls.json      (공모자금 사용내역)
#   apiId=2020017: /prvsrpCptalUseDtls.json     (사모자금 사용내역)
#   apiId=2026001: /hmvAuditIndvdlBySttusV2.json (이사·감사 개인별 보수현황 Ver 2.0)
#   apiId=2026002: /indvdlByPayV2.json          (개인별 보수지급 금액 Ver 2.0)
#
# 확인 필요 (DS002 공식 목록에 없어 추정된 엔드포인트):
#   get_audit_hours           → /adtAdtorHrsSttus.json
#   get_related_party_transactions → /spclReltrTrnsctn.json
#   get_private_equity_fund   → /priFinVhclSttus.json
#   get_customer_deposits     → /custDpstSttus.json
#   get_credit_extension      → /crdtGrnItmSttus.json
#   get_stockholder_meeting   → /vtrRghtSttus.json
#   get_insider_trading       → /exctvMjrStkholdrSpclStckPssrpSttus.json
#   get_foreign_investment    → /frgnInvstSttus.json

from mcp.server.fastmcp import FastMCP

from opendartmcp.client import DartClient


def register(mcp: FastMCP, client: DartClient) -> None:
    @mcp.tool()
    async def get_capital_change_status(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """증자(감자) 현황 - 주식 증자 및 감자 이력을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/irdsSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_dividend_info(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """배당에 관한 사항 - 현금배당 및 주식배당 정보를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/alotMatter.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_treasury_stock(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """자기주식 취득 및 처분 현황을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/tesstkAcqsDspsSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_largest_shareholder(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """최대주주 현황 - 최대주주 지분율 및 변동을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/hyslrSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_largest_shareholder_changes(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """최대주주 변동현황을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/hyslrChgSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_minority_shareholders(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """소액주주 현황을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/mrhlSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_executives(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """임원 현황 - 등기임원 명단 및 보수를 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/exctvSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_employees(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """직원 현황 - 직원 수, 평균 연봉 등을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/empSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_executive_compensation_individual(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """이사·감사의 개인별 보수현황 (5억원 이상)을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/hmvAuditIndvdlBySttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_executive_compensation_total(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """이사·감사 전체의 보수현황을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/hmvAuditAllSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_individual_pay_over5(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """개인별 보수지급 금액 (5억 이상 상위 5인)을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/indvdlByPay.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_investment_in_other_corps(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """타법인 출자 현황을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/otrCprInvstmntSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_audit_opinion(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """회계감사인의 명칭 및 감사의견을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/accnutAdtorNmNdAdtOpinion.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_audit_fee(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """감사보수 현황 (감사용역 체결현황)을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/adtServcCnclsSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_non_audit_service(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """비감사용역 현황 (회계감사인과의 비감사용역 계약체결 현황)을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/accnutAdtorNonAdtServcCnclsSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_audit_hours(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """감사인의 감사시간 현황을 조회합니다.
        (확인 필요: DS002 공식 목록 외 추정 엔드포인트 사용)

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/adtAdtorHrsSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_related_party_transactions(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """특수관계인과의 거래내용을 조회합니다.
        (확인 필요: DS002 공식 목록 외 추정 엔드포인트 사용)

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/spclReltrTrnsctn.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_bond_issuance(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """회사채 발행 및 상환 실적 (채무증권 발행실적)을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/detScritsIsuAcmslt.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_commercial_paper(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """기업어음증권 미상환 잔액을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/entrprsBilScritsNrdmpBlce.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_short_term_bond(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """단기사채 미상환 잔액을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/srtpdPsndbtNrdmpBlce.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_hybrid_bond(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """신종자본증권 미상환 잔액을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/newCaplScritsNrdmpBlce.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_debt_securities_outstanding(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """조건부 자본증권 미상환 잔액을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/cndlCaplScritsNrdmpBlce.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_private_equity_fund(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """사모펀드 현황을 조회합니다.
        (확인 필요: DS002 공식 목록 외 추정 엔드포인트 사용)

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/priFinVhclSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_customer_deposits(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """고객예탁금 등 현황을 조회합니다 (금융회사).
        (확인 필요: DS002 공식 목록 외 추정 엔드포인트 사용)

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/custDpstSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_credit_extension(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """신용공여 현황을 조회합니다 (금융회사).
        (확인 필요: DS002 공식 목록 외 추정 엔드포인트 사용)

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/crdtGrnItmSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_stockholder_meeting(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """의결권 현황을 조회합니다.
        (확인 필요: DS002 공식 목록 외 추정 엔드포인트 사용)

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/vtrRghtSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_insider_trading(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """임원·주요주주 특정증권 소유 현황을 조회합니다.
        (확인 필요: DS002 공식 목록 외 추정 엔드포인트 사용)

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/exctvMjrStkholdrSpclStckPssrpSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_foreign_investment(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """외국인 지분율 현황을 조회합니다.
        (확인 필요: DS002 공식 목록 외 추정 엔드포인트 사용)

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/frgnInvstSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_unregistered_executives(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """미등기임원 보수 현황을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/unrstExctvMendngSttus.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })

    @mcp.tool()
    async def get_executive_compensation_v2(
        corp_code: str,
        bsns_year: str,
        reprt_code: str,
    ) -> dict:
        """개인별 보수지급 금액 V2 (최신 버전) - 5억 이상 상위 5인 보수지급 금액을 조회합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bsns_year: 사업연도 (YYYY, 예: "2023")
            reprt_code: 보고서 코드 ("11011"=사업보고서, "11012"=반기, "11013"=1분기, "11014"=3분기)
        """
        return await client.get_json("/indvdlByPayV2.json", {
            "corp_code": corp_code,
            "bsns_year": bsns_year,
            "reprt_code": reprt_code,
        })
