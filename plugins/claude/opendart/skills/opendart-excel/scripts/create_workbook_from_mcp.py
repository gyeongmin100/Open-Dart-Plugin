# -*- coding: utf-8 -*-
"""MCP 원문 -> 모델 -> Excel -> 검증까지 한 번에 수행.

사용법:
    python create_workbook_from_mcp.py --input mcp_result.json \
        --scope consolidated --output out.xlsx

--scope auto: 문서에 한 범위만 있으면 자동 선택, 둘 다 있으면
종료코드 2 + 사용 가능한 범위 출력(사용자에게 확인할 것).
검증 실패 시 종료코드 1, 재무제표 없음 시 종료코드 3.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ensure_deps import ensure_deps  # noqa: E402
ensure_deps()

import dartdoc  # noqa: E402
from build_financial_excel import build_workbook  # noqa: E402
from prepare_notes_json import (  # noqa: E402
    exit_no_statements, load_content, resolve_scope)
from verify_workbook import verify  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--scope", default="auto",
                        choices=["auto", "consolidated", "separate"])
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-output", help="중간 모델 JSON 저장 경로(선택)")
    args = parser.parse_args()

    content = load_content(args.input)
    scope = resolve_scope(content, args.scope)
    try:
        model = dartdoc.extract_model(content, scope)
    except LookupError as e:
        exit_no_statements(str(e))
    if args.model_output:
        Path(args.model_output).write_text(
            json.dumps(model, ensure_ascii=False), encoding="utf-8")

    build_result = build_workbook(model, args.output)
    report = verify(model, args.output, args.input)
    output = {
        "scope": scope,
        "workbook": args.output,
        "sheets": build_result["sheets"],
        "verification": report,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
