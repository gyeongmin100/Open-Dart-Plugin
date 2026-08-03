from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP

from opendartmcp.client import DartClient
from opendartmcp.errors import DartApiError
from opendartmcp.excel import candidates, workflow


def register(mcp: FastMCP, client: DartClient) -> None:
    @mcp.tool()
    async def list_financial_document_candidates(
        rcept_no: str,
        corp_code: str | None = None,
        allow_body: bool = False,
    ) -> dict:
        """공시 계열(원본·정정·추가) 전체의 문서를 후보로 반환합니다.

        정정 공시는 본문만 재제출하고 첨부는 원본 제출본에 남으므로, 같은
        보고서의 제출본을 모두 훑습니다. 정정 번호 하나만 넘겨도 원본에 붙은
        감사·검토보고서가 나옵니다. 후보의 rcept_no는 넘긴 값과 다를 수
        있으며 그것이 정상입니다.

        AI는 반환된 날짜·제목만 보고 candidate_id 하나를 골라
        create_financial_workbook에 그대로 전달합니다. 원문은 반환하지 않습니다.

        Args:
            rcept_no: 접수번호 14자리. search_disclosures 결과 값을 그대로 전달.
            corp_code: 고유번호 8자리. search_disclosures가 함께 주므로 있으면
                반드시 전달하세요 — 없으면 접수일자 전체를 훑어 느립니다.
            allow_body: confirmation_required를 사용자에게 보여주고 본문 사용
                승인을 받은 뒤에만 true. 기본 false에서는 본문을 숨깁니다.
        """
        try:
            return await candidates.list_candidates(
                client, rcept_no, corp_code, allow_body=allow_body)
        except DartApiError as error:
            return {"ok": False, "error": "dart_api_error",
                    "status": error.status, "message": error.message[:200]}
        except Exception as error:
            return {"ok": False, "error": "internal_error",
                    "stage": "candidate_list",
                    "message": type(error).__name__}

    @mcp.tool()
    async def create_financial_workbook(
        candidate_id: str,
        scope: Literal["consolidated", "separate"],
        output_dir: str,
        output_name: str,
        allow_body: bool = False,
    ) -> dict:
        """선택한 문서에서 검증된 재무제표 Excel을 만들어 경로만 반환합니다.

        서버가 그 문서만 내려받아 파싱·Excel 생성·검증까지 수행합니다.
        공시 원문은 반환하지 않습니다.

        Args:
            candidate_id: list_financial_document_candidates가 준 값 그대로.
                직접 만들지 마세요.
            scope: consolidated(연결) 또는 separate(별도)
            output_dir: 최종 Excel을 저장할 기존 디렉터리 (쓰기 가능해야 함)
            output_name: 최종 파일명(.xlsx). 예: 회사명_2024_연결재무제표.xlsx
            allow_body: 감사·검토보고서가 없음을 사용자에게 알리고 승인을 받은
                경우에만 true. 기본 false에서는 본문 생성을 거부합니다.
        """
        try:
            return await workflow.create_workbook(
                client, candidate_id=candidate_id, scope=scope,
                output_dir=output_dir, output_name=output_name,
                allow_body=allow_body)
        except DartApiError as error:
            return {"ok": False, "error": "dart_api_error",
                    "candidate_id": candidate_id,
                    "scope": scope, "status": error.status,
                    "message": error.message[:200]}
        except workflow.StageFailure as error:
            # plan.md §5.12/§12 — 예외 메시지에는 API 키(httpx의 URL)와 원문
            # (openpyxl의 셀 값)이 섞여 나온다. 단계와 예외 타입만 돌려준다.
            return {"ok": False, "error": "internal_error",
                    "candidate_id": candidate_id,
                    "scope": scope, "stage": error.stage,
                    "message": error.error_type}
        except Exception as error:            # plan.md §5.12 traceback 반환 금지
            return {"ok": False, "error": "internal_error",
                    "candidate_id": candidate_id,
                    "scope": scope, "stage": "workflow",
                    "message": type(error).__name__}
