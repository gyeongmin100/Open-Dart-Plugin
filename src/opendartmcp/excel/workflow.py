# -*- coding: utf-8 -*-
"""공시 ZIP → 감사·검토보고서 선택 → 파싱 → Excel → 검증 (plan.md §5).

AI에게 원문을 전달하지 않기 위해, 선택한 XML은 이 모듈의 메모리에만 존재한다.
"""
from __future__ import annotations

import os
import re
import tempfile
from pathlib import Path

from ..errors import DartApiError
from . import dartdoc
from .build_financial_excel import build_workbook
from .verify_workbook import verify

SCOPES = (dartdoc.CONSOLIDATED, dartdoc.SEPARATE)
_RCEPT_RE = re.compile(r"^\d{14}$")
_AUDIT_KEYWORDS = ("감사보고서", "검토보고서")
_BODY_KEYWORDS = ("사업보고서", "반기보고서", "분기보고서")
_INVALID_NAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
# DOCUMENT-NAME은 원문 머리 4096바이트에서 뽑으므로 비정상적으로 길 수 있다.
# 결과 크기를 수 KB 이하로 유지하기 위해 자른다 (§5.12).
_TITLE_MAX = 200


def is_audit_title(title: str) -> bool:
    normalized = dartdoc.norm(title)
    return any(keyword in normalized for keyword in _AUDIT_KEYWORDS)


def select_document(documents: list[dict], scope: str,
                    use_body: bool) -> tuple[dict | None, bool]:
    """§5.5 — 감사·검토보고서 첨부 우선. 없으면 use_body일 때만 본문(첫 문서).

    반환: (선택 문서, 본문 폴백 여부). 폴백 여부는 제목이 아니라 어느 분기로
    선택했는지를 그대로 알려준다 — 검증 기준(§5.7)이 여기에 달려 있다.
    """
    for document in documents:
        if not is_audit_title(document["title"]):
            continue
        has_consolidated = "연결" in dartdoc.norm(document["title"])
        if has_consolidated == (scope == dartdoc.CONSOLIDATED):
            return document, False
    if use_body:
        for document in documents:
            title = dartdoc.norm(document["title"])
            if any(keyword in title for keyword in _BODY_KEYWORDS):
                return document, True
    return None, False


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


async def create_workbook(client, rcept_no: str, scope: str, output_dir: str,
                          output_name: str, use_body: bool = False) -> dict:
    """공시 1건에서 검증된 재무제표 Excel을 만들고 파일 참조만 반환한다."""
    stage = "download"

    def _set(name: str) -> None:
        nonlocal stage
        stage = name

    try:
        return await _pipeline(client, rcept_no, scope, output_dir,
                               output_name, use_body, _set)
    except DartApiError:
        raise
    except Exception as error:
        raise StageFailure(stage, error) from None


async def _pipeline(client, rcept_no: str, scope: str, output_dir: str,
                    output_name: str, use_body: bool, set_stage) -> dict:
    # --- §5.2 입력 검증 (다운로드 전에 수행한다) ---
    if not _RCEPT_RE.match(rcept_no or ""):
        return _error("invalid_rcept_no", rcept_no, scope,
                      detail="rcept_no는 14자리 숫자여야 합니다.")
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

    # --- §5.3 공시 ZIP 1회 다운로드, 이후 같은 bytes만 재사용 ---
    set_stage("download")
    zip_bytes = await client.download_zip("/document.xml", {"rcept_no": rcept_no})
    with client.open_zip(zip_bytes) as zf:
        documents = client.zip_documents(zf)
        selected, used_body = select_document(documents, scope, use_body)
        # ZIP 엔트리 경로를 파일 경로로 쓰지 않는다 — 진단용 이름은 basename만.
        summary = [{"filename": os.path.basename(d["filename"]),
                    "title": d["title"][:_TITLE_MAX]} for d in documents]
        if selected is None:
            return _error("audit_attachment_not_found", rcept_no, scope,
                          documents=summary)
        source_content = client._decode_document(zf.read(selected["filename"]))

    source_title = selected["title"][:_TITLE_MAX]

    # --- §5.8 파싱 → 생성 → 검증 ---
    set_stage("parse")
    try:
        model = dartdoc.extract_model(source_content, scope)
    except dartdoc.SectionNotFound as error:
        if error.code == "scope_not_in_document":
            return _error("scope_not_in_document", rcept_no, scope,
                          available_scopes=error.available_scopes,
                          source_title=source_title)
        return _error("no_financial_statements", rcept_no, scope,
                      source_title=source_title, documents=summary)

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
