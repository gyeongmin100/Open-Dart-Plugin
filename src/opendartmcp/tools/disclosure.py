from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from opendartmcp.client import DartClient


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
    async def get_corp_codes() -> dict:
        """DART에 등록된 모든 기업의 고유번호 목록을 조회합니다.

        ZIP 압축 XML 파일로 반환됩니다. 기업명으로 corp_code를 찾을 때 사용하세요.
        """
        return await client.get_zip_xml("/corpCode.xml", {})
