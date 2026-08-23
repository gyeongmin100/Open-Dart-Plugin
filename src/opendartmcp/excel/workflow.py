# -*- coding: utf-8 -*-
"""선택된 문서 1건 → 파싱 → Excel → 검증 (plan.md §5).

어느 문서를 쓸지는 AI가 candidate_id로 지정한다. 이 모듈은 그 문서만
받아온다. AI에게 원문을 전달하지 않기 위해, 받은 원문은 이 모듈의
메모리에만 존재한다.
"""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

import httpx

from ..errors import DartApiError, DartHttpError
from . import candidates, dartdoc
from .build_financial_excel import build_workbook
from .verify_workbook import verify

SCOPES = (dartdoc.CONSOLIDATED, dartdoc.SEPARATE)
_BODY_KEYWORDS = ("사업보고서", "반기보고서", "분기보고서")
_INVALID_NAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
# DOCUMENT-NAME은 원문 머리 4096바이트에서 뽑으므로 비정상적으로 길 수 있다.
# 결과 크기를 수 KB 이하로 유지하기 위해 자른다 (§5.12).
_TITLE_MAX = 200


def select_body_document(documents: list[dict]) -> dict | None:
    """ZIP의 본문. 정기보고서가 있으면 그것, 없으면(외부감사 단독 공시) 첫 문서."""
    for document in documents:
        title = dartdoc.norm(document["title"])
        if any(keyword in title for keyword in _BODY_KEYWORDS):
            return document
    return documents[0] if documents else None


def sanitize_output_name(name: str) -> str:
    """§5.11 — Windows에서 못 쓰는 문자만 제거한다. 이름을 새로 만들지 않는다."""
    return _INVALID_NAME_CHARS.sub("", name).strip() or "workbook.xlsx"


def reserve_output_path(directory: Path, name: str) -> Path:
    """§5.11 — 비어 있는 첫 이름을 배타적으로 선점한다.

    존재 여부만 확인하고 나중에 rename하면, 같은 워크스페이스를 쓰는 다른
    프로세스가 그 사이에 같은 이름을 만들 수 있고 rename이 그것을 덮어쓴다.
    O_EXCL로 자리를 먼저 잡아 그 창을 없앤다.
    """
    candidate = directory / name
    stem, suffix = candidate.stem, candidate.suffix
    index = 0
    while True:
        try:
            handle = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            index += 1
            candidate = directory / f"{stem} ({index}){suffix}"
            continue
        os.close(handle)
        return candidate


def _error(code: str, rcept_no: str, scope: str, **extra) -> dict:
    return {"ok": False, "error": code, "rcept_no": rcept_no,
            "scope": scope, **extra}


class StageFailure(Exception):
    """예기치 못한 실패가 난 단계를 알린다 (§5.13).

    원래 예외 메시지는 담지 않는다. httpx는 URL(=API 키)을, openpyxl은 셀
    내용(=원문)을 메시지에 넣기 때문이다 (§5.12, §12).
    """

    def __init__(self, stage: str, error: BaseException):
        self.stage = stage
        self.error_type = type(error).__name__
        super().__init__(f"{stage}: {self.error_type}")


async def create_workbook(client, candidate_id: str, scope: str,
                          output_dir: str, output_name: str,
                          allow_body: bool = False) -> dict:
    """선택된 문서 1건에서 검증된 Excel을 만들고 파일 참조만 반환한다."""
    stage = "download"

    def _set(name: str) -> None:
        nonlocal stage
        stage = name

    try:
        return await _pipeline(client, candidate_id, scope, output_dir,
                               output_name, allow_body, _set)
    except DartApiError:
        raise
    except Exception as error:
        raise StageFailure(stage, error) from None


async def _pipeline(client, candidate_id: str, scope: str, output_dir: str,
                    output_name: str, allow_body: bool, set_stage) -> dict:
    # --- §5.2 입력 검증 (다운로드 전에 수행한다) ---
    try:
        kind, rcept_no, dcm_no = candidates.parse_candidate_id(candidate_id)
    except candidates.CandidateError:
        return _error("invalid_candidate_id", "", scope,
                      detail="candidate_id는 후보 목록의 값을 그대로 써야 합니다.")
    if kind == "body" and not allow_body:
        return _error(
            "confirmation_required", rcept_no, scope,
            detail="감사·검토보고서가 없습니다. 사용자 승인 후 allow_body=true로 재호출하세요.")
    if scope not in SCOPES:
        return _error("invalid_scope", rcept_no, scope,
                      detail="scope는 consolidated 또는 separate여야 합니다.")
    directory = Path(output_dir)
    if not directory.is_dir() or not os.access(directory, os.W_OK):
        return _error("invalid_output_dir", rcept_no, scope,
                      detail="output_dir이 존재하지 않거나 쓸 수 없습니다.")
    if ("/" in output_name or "\\" in output_name or ".." in output_name
            or not output_name.lower().endswith(".xlsx")):
        return _error("invalid_output_dir", rcept_no, scope,
                      detail="output_name은 경로 없이 .xlsx로 끝나야 합니다.")

    # --- §5.3 선택된 문서 1건만 받는다 ---
    set_stage("download")
    if kind in ("zip", "viewer"):
        try:
            if kind == "zip":
                source_content, source_title = await candidates.load_zip_document(
                    client, rcept_no, dcm_no)
            else:
                source_content, source_title = await candidates.load_attachment(
                    client, rcept_no, dcm_no, scope)
        except candidates.CandidateError:
            return _error("candidate_unavailable", rcept_no, scope,
                          detail="후보 목록의 다른 문서를 선택하세요.")
        source_title = source_title[:_TITLE_MAX]
    else:
        zip_bytes = await client.download_zip(
            "/document.xml", {"rcept_no": rcept_no})
        with client.open_zip(zip_bytes) as zf:
            selected = select_body_document(client.zip_documents(zf))
            if selected is None:
                return _error("candidate_unavailable", rcept_no, scope,
                              detail="공시 ZIP에 문서가 없습니다.")
            source_content = client._decode_document(zf.read(selected["filename"]))
        source_title = selected["title"][:_TITLE_MAX]

    # --- §5.8 파싱 → 생성 → 검증 ---
    set_stage("parse")
    try:
        model = dartdoc.extract_model(source_content, scope)
    except dartdoc.SectionNotFound as error:
        if error.code in ("scope_not_in_document", "scope_not_applicable"):
            return _error(error.code, rcept_no, scope,
                          available_scopes=error.available_scopes,
                          source_title=source_title)
        # 어느 단계에서 끊겼는지는 재시도 가치 판단에 필요하다 (§7).
        return _error("no_financial_statements", rcept_no, scope,
                      source_title=source_title, reason=error.code)

    # ZIP XML은 일부 문서에서 화면의 BR을 잃는다. 표/금액은 XML 모델을
    # 유지하고, 글자가 모두 일치할 때만 주석 블록을 화면 HTML 것으로 바꾼다.
    if kind in ("zip", "viewer"):
        try:
            viewer_content = await candidates.load_viewer_document(
                client, rcept_no, scope,
                dcm_no=dcm_no if kind == "viewer" else "",
                title=source_title if kind == "zip" else "")
            viewer_model = dartdoc.extract_model(viewer_content, scope)
            source_chars = dartdoc.section_raw_char_counts(
                source_content, scope)["notes"]
            viewer_chars = dartdoc.section_raw_char_counts(
                viewer_content, scope)["notes"]
            source_by_number = {n["number"]: n for n in model["notes"]}
            same_numbers = (list(source_by_number)
                            == [n["number"] for n in viewer_model["notes"]])
            same_tables = same_numbers and all(
                sum(b["type"] == "table" for b in
                    source_by_number[n["number"]]["blocks"])
                == sum(b["type"] == "table" for b in n["blocks"])
                for n in viewer_model["notes"])
            if source_chars == viewer_chars and same_tables:
                # 문단 위치는 HTML, 표 데이터/병합은 XML 것을 쓴다.
                for viewer_note in viewer_model["notes"]:
                    source_note = source_by_number[viewer_note["number"]]
                    source_tables = iter(
                        b["table"] for b in source_note["blocks"]
                        if b["type"] == "table")
                    for block in viewer_note["blocks"]:
                        if block["type"] == "table":
                            block["table"] = next(source_tables)
                model["notes_preamble"] = viewer_model["notes_preamble"]
                model["notes"] = viewer_model["notes"]
        except (candidates.CandidateError, dartdoc.SectionNotFound,
                DartApiError, DartHttpError, httpx.HTTPError):
            pass

    # 본문 여부는 제목이 아니라 문서 구조로 판단한다 — 정기보고서 본문에는
    # 주석번호 열이 없어 링크 0개가 정상이고, 검증 기준(§5.7)이 여기 달려 있다.
    # 두 조건을 함께 본다. 외부감사 단독 공시의 본문은 감사보고서 자체라
    # 주석번호 열이 있고(구조), 2014년 이전 첨부는 "(첨부)재무제표" 표기가
    # 없어 구조만 보면 본문으로 오인된다(후보 종류).
    # 공시 ZIP의 본문은 접미사 없는 엔트리(<접수번호>.xml)다.
    is_body_doc = kind == "body" or dcm_no == f"{rcept_no}.xml"
    used_body = is_body_doc and model["kind"] == "annual_report_body"
    if used_body and not allow_body:
        return _error(
            "confirmation_required", rcept_no, scope,
            detail="본문 후보입니다. 사용자 승인 후 allow_body=true로 재호출하세요.")

    try:
        handle, temp_path = tempfile.mkstemp(dir=str(directory), suffix=".xlsx")
    except OSError:
        # Windows의 os.access(W_OK)는 디렉터리에 대해 사실상 항상 참이라,
        # 쓰기 불가는 여기서만 드러난다 (§5.2).
        return _error("invalid_output_dir", rcept_no, scope,
                      detail="output_dir에 파일을 만들 수 없습니다.")
    os.close(handle)
    try:
        set_stage("build")
        build_workbook(model, temp_path)
        set_stage("verify")
        report = verify(model, temp_path, source_content, used_body=used_body)
        if not report["ok"]:
            return _error("verification_failed", rcept_no, scope,
                          source_title=source_title,
                          failures=[f[:200] for f in report["failures"][:10]])
        final_path = reserve_output_path(
            directory, sanitize_output_name(output_name))
        try:
            os.replace(temp_path, final_path)
        except BaseException:
            final_path.unlink(missing_ok=True)
            raise
    finally:
        # §5.13 실패·취소·타임아웃에서도 정확히 이 임시 파일만 지운다.
        if os.path.exists(temp_path):
            os.remove(temp_path)

    stats = report["stats"]
    return {
        "ok": True,
        "rcept_no": rcept_no,
        "candidate_id": candidate_id,
        "scope": scope,
        "source_title": source_title,
        "used_body": used_body,
        "company": model["company_name"],
        "workbook": str(final_path),
        "verification": {
            "ok": True,
            "statements": stats["statements"],
            "notes": stats["notes"],
            "hyperlinks": stats["hyperlinks"],
            "warnings": report["warnings"][:5],
        },
    }
