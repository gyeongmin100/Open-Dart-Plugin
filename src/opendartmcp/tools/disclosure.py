from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from opendartmcp.client import DartClient


def _filter_corps(
    corps: list[dict], corp_name: str, stock_code: str, limit: int = 50
) -> dict:
    name_q = corp_name.strip().lower()
    code_q = stock_code.strip()
    matches = []
    for c in corps:
        if code_q:
            sc = (c.get("stock_code") or "").strip()
            if sc != code_q:
                continue
        if name_q:
            cn = (c.get("corp_name") or "").lower()
            en = (c.get("corp_eng_name") or "").lower()
            if name_q not in cn and name_q not in en:
                continue
        matches.append(c)
    total = len(matches)
    return {
        "count": total,
        "returned": min(total, limit),
        "list": matches[:limit],
        "truncated": total > limit,
    }


def register(mcp: FastMCP, client: DartClient) -> None:
    @mcp.tool()
    async def search_disclosures(
        corp_code: str | None = None,
        bgn_de: str | None = None,
        end_de: str | None = None,
        last_reprt_at: str | None = None,
        pblntf_ty: str | None = None,
        pblntf_detail_ty: str | None = None,
        corp_cls: str | None = None,
        sort: str | None = None,
        sort_mth: str | None = None,
        page_no: int | None = None,
        page_count: int | None = None,
    ) -> dict:
        """공시 목록을 검색합니다. 기업, 날짜, 공시 유형 등으로 필터링 가능합니다.

        Args:
            corp_code: DART 기업 고유번호 (8자리)
            bgn_de: 시작일 (YYYYMMDD)
            end_de: 종료일 (YYYYMMDD)
            last_reprt_at: 최종보고서 여부 (Y/N)
            pblntf_ty: 공시 유형 코드 (A:정기, B:주요, C:발행, D:지분, E:기타)
            pblntf_detail_ty: 공시 상세 유형
            corp_cls: 법인 구분 (Y:유가, K:코스닥, N:코넥스, E:기타)
            sort: 정렬 기준 (date/crp/rpt)
            sort_mth: 정렬 방법 (asc/desc)
            page_no: 페이지 번호
            page_count: 페이지당 건수 (최대 100)
        """
        params = {k: v for k, v in {
            "corp_code": corp_code,
            "bgn_de": bgn_de,
            "end_de": end_de,
            "last_reprt_at": last_reprt_at,
            "pblntf_ty": pblntf_ty,
            "pblntf_detail_ty": pblntf_detail_ty,
            "corp_cls": corp_cls,
            "sort": sort,
            "sort_mth": sort_mth,
            "page_no": page_no,
            "page_count": page_count,
        }.items() if v is not None}
        return await client.get_json("/list.json", params)

    @mcp.tool()
    async def get_company_info(corp_code: str) -> dict:
        """기업의 기본 정보를 조회합니다 (회사명, 대표자, 사업자번호, 주소 등).

        Args:
            corp_code: DART 기업 고유번호 (8자리, 필수)
        """
        return await client.get_json("/company.json", {"corp_code": corp_code})

    @mcp.tool()
    async def get_disclosure_document(rcept_no: str, doc_name: str = "") -> dict:
        """공시서류의 원문을 조회합니다. 접수번호로 특정 공시 문서를 가져옵니다.

        하나의 공시에는 본문 외에 첨부 문서(감사보고서, 연결감사보고서 등)가
        포함될 수 있습니다. doc_name 없이 호출하면 본문을 반환하며, 결과의
        `documents` 목록에서 첨부 파일명과 제목을 확인한 뒤 doc_name으로
        특정 첨부를 다시 요청할 수 있습니다.

        Args:
            rcept_no: 접수번호 (14자리, 필수)
            doc_name: 가져올 문서 파일명 (선택, `documents`의 filename 값.
                생략 시 본문)
        """
        return await client.get_zip_text(
            "/document.xml", {"rcept_no": rcept_no}, doc_name=doc_name or None)

    @mcp.tool()
    async def get_corp_codes(corp_name: str = "", stock_code: str = "") -> dict:
        """기업명 또는 종목코드로 DART 고유번호(corp_code)를 검색합니다.

        DART 오픈API는 회사명 검색을 지원하지 않으므로, 전체 고유번호 목록을
        내려받아 서버에서 필터링합니다. corp_name 또는 stock_code 중 최소
        하나를 지정해야 합니다 — 둘 다 생략하면 검색하지 않습니다(전체 목록은
        11만 건 이상이라 반환하지 않습니다).

        Args:
            corp_name: 회사명 부분일치 (한글 또는 영문, 대소문자 무시)
            stock_code: 상장사 종목코드 6자리 (예: "000660") 정확히 일치
        """
        if not corp_name.strip() and not stock_code.strip():
            return {
                "error": "corp_name 또는 stock_code 중 하나 이상을 지정하세요.",
                "hint": "회사명(부분일치) 또는 종목코드(6자리)로 검색합니다.",
            }
        data = await client.get_zip_xml("/corpCode.xml", {})
        corps = data.get("result", {}).get("list", [])
        if isinstance(corps, dict):
            corps = [corps]
        return _filter_corps(corps, corp_name, stock_code)
