from __future__ import annotations

from typing import Literal

from mcp.server.fastmcp import FastMCP

from opendartmcp.client import DartClient
from opendartmcp.errors import DartApiError
from opendartmcp.excel import workflow


def register(mcp: FastMCP, client: DartClient) -> None:
    @mcp.tool()
    async def create_financial_workbook(
        rcept_no: str,
        scope: Literal["consolidated", "separate"],
        output_dir: str,
        output_name: str,
        use_body: bool = False,
    ) -> dict:
        """공시 1건에서 검증된 재무제표 Excel을 만들어 파일 경로만 반환합니다.

        서버가 공시 ZIP을 한 번 내려받아 감사·검토보고서 첨부를 고르고, 파싱과
        Excel 생성, 검증까지 수행합니다. 공시 원문은 반환하지 않습니다.

        Args:
            rcept_no: 접수번호 14자리. search_disclosures 결과 값을 그대로 전달.
            scope: consolidated(연결) 또는 separate(별도)
            output_dir: 최종 Excel을 저장할 기존 디렉터리 (쓰기 가능해야 함)
            output_name: 최종 파일명(.xlsx). 예: 회사명_2024_연결재무제표.xlsx
            use_body: 감사·검토보고서 첨부가 없을 때 정기보고서 본문을 쓸지 여부.
                기본 false. true일 때만 본문을 쓰며 주석 하이퍼링크가 없습니다.
        """
        try:
            return await workflow.create_workbook(
                client, rcept_no=rcept_no, scope=scope, output_dir=output_dir,
                output_name=output_name, use_body=use_body)
        except DartApiError as error:
            return {"ok": False, "error": "dart_api_error", "rcept_no": rcept_no,
                    "scope": scope, "status": error.status,
                    "message": error.message[:200]}
        except workflow.StageFailure as error:
            # plan.md §5.12/§12 — 예외 메시지에는 API 키(httpx의 URL)와 원문
            # (openpyxl의 셀 값)이 섞여 나온다. 단계와 예외 타입만 돌려준다.
            return {"ok": False, "error": "internal_error", "rcept_no": rcept_no,
                    "scope": scope, "stage": error.stage,
                    "message": error.error_type}
        except Exception as error:            # plan.md §5.12 traceback 반환 금지
            return {"ok": False, "error": "internal_error", "rcept_no": rcept_no,
                    "scope": scope, "stage": "workflow",
                    "message": type(error).__name__}
