# -*- coding: utf-8 -*-
"""DART 원문(MCP 결과 JSON / XML / HTML / ZIP) -> 재무제표+주석 모델 JSON.

사용법:
    python prepare_notes_json.py --input doc.xml --scope consolidated --output model.json
    python prepare_notes_json.py --input mcp_result.json --scope separate --output model.json

--scope auto 인 경우 문서에 한 범위만 있으면 그것을 쓰고,
둘 다 있으면 종료코드 2로 사용 가능한 범위를 출력한다(사용자에게 물어볼 것).
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _ensure_deps import ensure_deps  # noqa: E402
ensure_deps()

import dartdoc  # noqa: E402


def load_content(path: str) -> str:
    """MCP 결과 JSON({filename, content}), 원문 XML/HTML, ZIP 모두 지원."""
    data = Path(path).read_bytes()
    if data[:2] == b"PK":  # ZIP
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            names = [n for n in zf.namelist()
                     if n.lower().endswith((".xml", ".html", ".htm"))]
            if not names:
                raise ValueError("ZIP 안에 문서 파일이 없습니다")
            names.sort(key=lambda n: (not n.lower().endswith(".xml"), n))
            data = zf.read(names[0])
    text = _decode(data)
    stripped = text.lstrip()
    if stripped.startswith("{"):
        obj = json.loads(stripped)
        if isinstance(obj, dict) and "content" in obj:
            return obj["content"]
        raise ValueError("JSON 입력에 'content' 키가 없습니다")
    return text


def _decode(data: bytes) -> str:
    for encoding in ("utf-8", "cp949", "euc-kr"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def resolve_scope(content: str, scope: str) -> str:
    if scope in (dartdoc.CONSOLIDATED, dartdoc.SEPARATE):
        return scope
    soup = dartdoc.parse_document(content)
    available = dartdoc.detect_scopes(soup)
    if len(available) == 1:
        return available[0]
    print(json.dumps({"error": "scope_ambiguous", "available": available},
                     ensure_ascii=False))
    sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--scope", default="auto",
                        choices=["auto", "consolidated", "separate"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    content = load_content(args.input)
    scope = resolve_scope(content, args.scope)
    model = dartdoc.extract_model(content, scope)
    Path(args.output).write_text(
        json.dumps(model, ensure_ascii=False), encoding="utf-8")

    summary = {
        "scope": scope,
        "kind": model["kind"],
        "statements": [s["sheet_name"] for s in model["statements"]],
        "notes": len(model["notes"]),
        "note_numbers": [n["number"] for n in model["notes"]],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
