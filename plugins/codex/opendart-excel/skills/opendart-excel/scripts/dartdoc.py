# -*- coding: utf-8 -*-
"""DART 공시 원문(XML/HTML) tolerant 파서 및 재무제표/주석 모델 추출.

입력: OpenDART MCP `get_disclosure_document` 결과의 content 문자열
      (사업보고서 본문 XML 또는 감사보고서 첨부 XML).
출력: JSON 직렬화 가능한 모델 dict.

모델 구조:
{
  "kind": "annual_report_body" | "audit_report",
  "scope": "consolidated" | "separate",
  "company_name": str,          # 문서 COMPANY-NAME
  "statements": [
    {
      "title": str,             # 예: "연 결 재 무 상 태 표" (원문 그대로)
      "sheet_name": str,        # 예: "연결재무상태표"
      "preamble": [ [ {"text","align","bold"} , ... ] ],   # 제목/기수/회사명/단위 행
      "postscript": [str],
      "tables": [ TABLE ],
    }
  ],
  "notes_preamble": [ [ {"text","align","bold"} ] ],
  "notes": [
    {"number": int, "title": str,
     "blocks": [ {"type":"paragraph","text":str} | {"type":"table","table":TABLE} ]}
  ],
}

TABLE = {
  "borderless": bool,
  "col_widths": [int],          # 원문 COL WIDTH(px)
  "note_col": int | None,       # "주석" 열 인덱스
  "rows": [ {"header": bool, "cells": [CELL|None]} ],   # None = 병합으로 덮인 자리
  "merges": [ [r1,c1,r2,c2] ],  # 0-based inclusive
}
CELL = {"text": str, "align": "left|center|right"|None, "bold": bool,
        "fill": str|None, "header": bool}
"""
from __future__ import annotations

import re
import warnings

from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from bs4.element import Tag, NavigableString

CONSOLIDATED = "consolidated"
SEPARATE = "separate"

_STATEMENT_BODIES = (
    "재무상태표",
    "대차대조표",
    "포괄손익계산서",
    "손익계산서",
    "자본변동표",
    "현금흐름표",
    "이익잉여금처분계산서(안)",
    "이익잉여금처분계산서",
    "결손금처리계산서(안)",
    "결손금처리계산서",
)
_STATEMENT_RE = re.compile(
    r"^(연결)?(" + "|".join(re.escape(b) for b in _STATEMENT_BODIES).replace(r"\(안\)", r"\(안\)") + r")$"
)
_NOTE_START_RE = re.compile(r"^(\d{1,3})\.(?!\d)\s*(.*)$", re.S)


def norm(text: str) -> str:
    """공백(전각 포함) 제거 정규화 — 제목 비교용."""
    return re.sub(r"\s+", "", text or "")


_XML_ENTITIES = ("amp", "lt", "gt", "quot", "apos")

# DART 원문에 등장하는 태그 목록 (dart3/dart4 스키마 + 일반 HTML 인라인).
# 이 목록에 없는 "<XXX"는 본문 텍스트로 간주해 이스케이프한다.
_KNOWN_TAGS = (
    "DOCUMENT-NAME", "DOCUMENT", "FORMULA-VERSION", "COMPANY-NAME",
    "SUMMARY", "BODY", "COVER-TITLE", "COVER", "TITLE",
    "SECTION-1", "SECTION-2", "SECTION-3", "LIBRARY", "PGBRK",
    "TABLE-GROUP", "TABLE", "COLGROUP", "COL", "CAPTION",
    "THEAD", "TBODY", "TFOOT", "TR", "TD", "TH", "TE", "TU",
    "P", "SPAN", "BR", "A", "B", "U", "I", "SUP", "SUB", "FONT",
    "IMAGE", "IMG-CAPTION", "IMG", "EXTRACTION", "ESG",
    "CORRECTION", "ANNOTATION", "REMARK", "INFORMATION", "PART",
)


def _sanitize(content: str) -> str:
    """XML 파서를 깨뜨리는 요소 제거: bare '&', 미정의 HTML 엔티티."""
    content = content.replace("&nbsp;", " ")
    content = re.sub(
        r"&(?!(?:" + "|".join(_XML_ENTITIES) + r"|#\d+|#x[0-9a-fA-F]+);)",
        "&amp;", content)
    # 태그가 아닌 bare '<' 이스케이프. 알려진 태그만 태그로 인정해
    # "<ABC" 같은 본문 텍스트가 마크업으로 오인돼 소실되지 않게 한다.
    content = re.sub(
        r"<(?!/?(?:" + "|".join(_KNOWN_TAGS) + r")[\s>/]|[!?])",
        "&lt;", content, flags=re.I)
    return content


def parse_document(content: str) -> BeautifulSoup:
    """DART 원문을 tolerant 파서로 파싱. 엄격 XML 실패에도 동작해야 한다.

    lxml recover 모드가 문서를 중간에서 잘라먹을 수 있으므로(깨진 구조),
    원문 대비 TABLE/TITLE 수가 부족하면 html.parser로 재시도한다.
    """
    sanitized = _sanitize(content)
    raw_tables = len(re.findall(r"<TABLE[\s>]", content, re.I))
    raw_titles = len(re.findall(r"<TITLE[\s>]", content, re.I))
    try:
        soup = BeautifulSoup(sanitized, "xml")  # lxml recover 모드
        n_tables = len(soup.find_all(lambda t: tag_is(t, "TABLE")))
        n_titles = len(soup.find_all(lambda t: tag_is(t, "TITLE")))
        if n_tables >= raw_tables * 0.99 and n_titles >= raw_titles * 0.99:
            return soup
    except Exception:
        pass
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", XMLParsedAsHTMLWarning)
        return BeautifulSoup(sanitized, "html.parser")


def tag_is(el, *names: str) -> bool:
    return isinstance(el, Tag) and el.name.upper() in names


def attr(el: Tag, name: str) -> str:
    for key, value in el.attrs.items():
        if key.upper() == name.upper():
            if isinstance(value, list):
                value = " ".join(value)
            return str(value)
    return ""


def text_of(el) -> str:
    """텍스트 추출. <BR>은 개행으로 보존, 블록 P 경계도 개행."""
    parts: list[str] = []

    def walk(node):
        for child in node.children:
            if isinstance(child, NavigableString):
                parts.append(str(child))
            elif isinstance(child, Tag):
                if child.name.upper() == "BR":
                    parts.append("\n")
                    continue
                if child.name.upper() == "P" and parts and not "".join(parts).endswith("\n"):
                    parts.append("\n")
                walk(child)

    if isinstance(el, NavigableString):
        return str(el)
    walk(el)
    text = "".join(parts)
    # NBSP 정규화. 행 앞머리 공백(전각 U+3000 포함)은 들여쓰기이므로 보존하고,
    # 단어 사이 연속 공백만 하나로 줄인다.
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"(?<=\S)[ \t]+", " ", ln).rstrip() for ln in text.split("\n")]
    return "\n".join(lines).strip("\n")


def _marks(el: Tag) -> str:
    """요소와 내부 P/SPAN의 USERMARK를 합침 (스타일이 안쪽에 붙는 경우)."""
    parts = [attr(el, "USERMARK")]
    for child in el.find_all(lambda t: tag_is(t, "P", "SPAN")):
        parts.append(attr(child, "USERMARK"))
    return " ".join(p for p in parts if p)


def _is_bold(el: Tag) -> bool:
    # USERMARK 토큰 "B"가 굵게. "BC0X..."(배경색)와 혼동하지 말 것.
    return "B" in _marks(el).split()


_FONT_NAME_MAP = {"GL": "굴림", "BT": "바탕", "DT": "돋움", "GG": "궁서"}


def _font_of(el: Tag) -> tuple[int | None, str | None]:
    """USERMARK의 F-GL11 / F-12 / F-BT14 → (크기, 서체명)."""
    m = re.search(r"F-([A-Z]{0,2})(\d{1,2})(?:\s|$)", _marks(el))
    if not m:
        return None, None
    return int(m.group(2)), _FONT_NAME_MAP.get(m.group(1))


def _fill_of(el: Tag) -> str | None:
    m = re.search(r"BC0X([0-9A-Fa-f]{6})", _marks(el))
    return m.group(1).upper() if m else None


def _align_of(el: Tag) -> str | None:
    a = attr(el, "ALIGN").upper()
    return {"LEFT": "left", "CENTER": "center", "RIGHT": "right"}.get(a)


def _valign_of(el: Tag) -> str | None:
    v = attr(el, "VALIGN").upper()
    return {"TOP": "top", "MIDDLE": "center", "BOTTOM": "bottom"}.get(v)


def _int_attr(el: Tag, name: str, default: int = 1) -> int:
    try:
        return max(1, int(attr(el, name)))
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------- 표 -> 그리드

_CELL_TAGS = ("TD", "TH", "TE", "TU")


def table_to_grid(table: Tag) -> dict:
    """TABLE 요소를 그리드/병합 정보로 변환 (rowspan/colspan 반영)."""
    trs = [tr for tr in table.find_all(lambda t: tag_is(t, "TR"))
           if tr.find_parent(lambda t: tag_is(t, "TABLE")) is table]
    grid: list[list[dict | None]] = []
    merges: list[list[int]] = []
    occupied: dict[tuple[int, int], bool] = {}
    header_flags: list[bool] = []

    for r, tr in enumerate(trs):
        in_thead = tr.find_parent(lambda t: tag_is(t, "THEAD")) is not None
        cells = [c for c in tr.find_all(lambda t: tag_is(t, *_CELL_TAGS))
                 if c.find_parent(lambda t: tag_is(t, "TR")) is tr]
        row: list[dict | None] = []
        col = 0

        def put(index, value):
            while len(row) <= index:
                row.append(None)
            row[index] = value

        for cell in cells:
            while occupied.get((r, col)):
                put(col, None)
                col += 1
            rowspan = _int_attr(cell, "ROWSPAN")
            colspan = _int_attr(cell, "COLSPAN")
            is_th = cell.name.upper() == "TH"
            size, font = _font_of(cell)
            put(col, {
                "text": text_of(cell),
                "align": _align_of(cell),
                "valign": _valign_of(cell),
                "bold": is_th or _is_bold(cell),
                "size": size,
                "font": font,
                "fill": _fill_of(cell),
                "header": is_th,
            })
            if rowspan > 1 or colspan > 1:
                merges.append([r, col, r + rowspan - 1, col + colspan - 1])
                for rr in range(r, r + rowspan):
                    for cc in range(col, col + colspan):
                        if (rr, cc) != (r, col):
                            occupied[(rr, cc)] = True
            col += colspan
        while occupied.get((r, col)):
            put(col, None)
            col += 1
        grid.append(row)
        header_flags.append(in_thead or (bool(cells) and all(c.name.upper() == "TH" for c in cells)))

    width = max((len(r) for r in grid), default=0)
    for row in grid:
        row.extend([None] * (width - len(row)))

    col_widths = [_int_attr(c, "WIDTH", 0)
                  for c in table.find_all(lambda t: tag_is(t, "COL"))
                  if c.find_parent(lambda t: tag_is(t, "TABLE")) is table]

    border = attr(table, "BORDER").strip()
    result = {
        "borderless": border == "0",
        "col_widths": col_widths,
        "note_col": None,
        "rows": [{"header": header_flags[i], "cells": grid[i]} for i in range(len(grid))],
        "merges": merges,
    }
    result["note_col"] = _detect_note_col(result)
    return result


def _detect_note_col(table: dict) -> int | None:
    for row in table["rows"]:
        if not row["header"]:
            continue
        for idx, cell in enumerate(row["cells"]):
            if cell and norm(cell["text"]) in ("주석", "주석번호"):
                return idx
    return None


def split_note_refs(text: str) -> list[str]:
    """주석 셀 값 "4,5,7,8" -> ["4","5","7","8"]. 숫자 아닌 토큰도 보존."""
    tokens = [t.strip() for t in re.split(r"[,，、;]", text or "") if t.strip()]
    return tokens


# 은행/보험 재무제표는 별도 주석 열 없이 계정명 안에 번호를 박아 넣는다.
# 표기가 "(주석4,6,7)"뿐 아니라 "(주석 15 참조)", "(주석 18 및 29 참조)"처럼
# 숫자 사이에 조사/단어가 낄 수 있어, 괄호 안 전체를 잡고 숫자만 뽑아낸다.
# DART 원문에는 이를 구분하는 태그/속성이 없어(평범한 TD 텍스트) 이 방식이
# 유일한 신호원이다 — "주석" 표제어 자체가 문서가 제공하는 유일한 근거.
_INLINE_NOTE_RE = re.compile(r"\(\s*주석\s*([^)]{1,60})\)")


def inline_note_refs(text: str) -> list[str]:
    """셀 텍스트에 박힌 "(주석 ...)" 괄호 안의 모든 번호를 추출."""
    tokens: list[str] = []
    for m in _INLINE_NOTE_RE.finditer(text or ""):
        tokens.extend(re.findall(r"\d+", m.group(1)))
    return tokens


# ------------------------------------------------------------ 섹션 찾기

def _titles(soup: BeautifulSoup) -> list[Tag]:
    return list(soup.find_all(lambda t: tag_is(t, "TITLE")))


def detect_kind(soup: BeautifulSoup) -> str:
    for title in _titles(soup):
        if re.match(r"^\(첨부\)(연결)?재무제표$", norm(text_of(title))):
            return "audit_report"
    return "annual_report_body"


def detect_scopes(soup: BeautifulSoup) -> list[str]:
    """문서에 존재하는 재무제표 범위 목록."""
    kind = detect_kind(soup)
    scopes = []
    if kind == "audit_report":
        for title in _titles(soup):
            t = norm(text_of(title))
            if t == "(첨부)연결재무제표":
                scopes.append(CONSOLIDATED)
            elif t == "(첨부)재무제표":
                scopes.append(SEPARATE)
    else:
        for title in _titles(soup):
            t = re.sub(r"^\d+\.", "", norm(text_of(title)))
            if t == "연결재무제표":
                scopes.append(CONSOLIDATED)
            elif t == "재무제표":
                scopes.append(SEPARATE)
    return scopes


# ------------------------------------------------------ 문서 flow 순회

_CONTAINER_TAGS = ("DOCUMENT", "BODY", "LIBRARY", "EXTRACTION", "SUMMARY",
                   "SECTION-1", "SECTION-2", "SECTION-3", "TABLE-GROUP", "COVER")


def _document_flow(soup: BeautifulSoup) -> list[Tag]:
    """문서 전체의 최상위 TITLE/P/TABLE을 문서 순서대로 나열."""
    items: list[Tag] = []

    def walk(node):
        for child in node.children:
            if not isinstance(child, Tag):
                continue
            name = child.name.upper()
            if name in ("TITLE", "P", "TABLE"):
                items.append(child)
            elif name in _CONTAINER_TAGS:
                walk(child)

    walk(soup)
    return items


def _find_slices(flow: list[Tag], kind: str, scope: str) -> tuple[list[Tag], list[Tag]]:
    """flow에서 (재무제표 항목들, 주석 항목들)을 TITLE 경계로 잘라 반환."""
    def title_norm(el: Tag) -> str | None:
        if not tag_is(el, "TITLE"):
            return None
        return re.sub(r"^\d+\.", "", norm(text_of(el)))

    if kind == "audit_report":
        want_fs = "(첨부)연결재무제표" if scope == CONSOLIDATED else "(첨부)재무제표"
        want_notes = "주석"
    else:
        want_fs = "연결재무제표" if scope == CONSOLIDATED else "재무제표"
        want_notes = want_fs + "주석"

    fs_idx = notes_idx = None
    for i, el in enumerate(flow):
        t = title_norm(el)
        if t is None:
            continue
        if fs_idx is None and t == want_fs:
            fs_idx = i
        elif fs_idx is not None and notes_idx is None and t == want_notes:
            notes_idx = i
    if fs_idx is None:
        raise LookupError(f"섹션을 찾을 수 없습니다: {want_fs}")
    if notes_idx is None:
        raise LookupError(f"주석 섹션을 찾을 수 없습니다: {want_notes}")

    def is_boundary(el: Tag) -> bool:
        # 섹션 경계 = SECTION 직속 TITLE.
        # dart4가 TABLE-GROUP 안에 넣는 중첩 TITLE(재무제표 제목,
        # 주석 제목)은 경계가 아니다.
        if not tag_is(el, "TITLE"):
            return False
        return el.find_parent(lambda t: tag_is(t, "TABLE-GROUP")) is None

    def slice_after(idx: int) -> list[Tag]:
        # 비경계 TITLE(dart4 중첩 제목)은 유지 — 주석 제목일 수 있다
        out = []
        for el in flow[idx + 1:]:
            if is_boundary(el):
                break
            out.append(el)
        return out

    return slice_after(fs_idx), slice_after(notes_idx)


def _statement_title_in(text: str) -> str | None:
    t = norm(text)
    m = _STATEMENT_RE.match(t)
    return t if m else None


# ------------------------------------------- 완전성 검증용 원문 글자 집계

def _raw_chars(el: Tag) -> "Counter[str]":
    """요소의 모든 텍스트를 파서 로직과 독립적으로 집계 (공백류 제외).

    엑셀로 옮기지 않는 요소(이미지 파일명/캡션)는 제외한다.
    """
    from collections import Counter

    counter: Counter[str] = Counter()
    skip = {"IMG", "IMG-CAPTION", "IMAGE"}
    for node in el.descendants:
        if isinstance(node, NavigableString):
            parent = node.parent
            if parent is not None and any(
                    tag_is(a, *skip) for a in [parent, *parent.parents]
                    if isinstance(a, Tag)):
                continue
            for ch in str(node):
                if not ch.isspace():
                    counter[ch] += 1
    return counter


def section_raw_char_counts(content: str, scope: str) -> dict:
    """섹션별 원문 글자 출현 횟수 — 파싱 결과의 완전성 검증 기준.

    반환: {"statements": Counter, "notes": Counter,
           "statement_snippets": [...], "note_snippets": [...]}
    snippets는 누락 위치 진단용 (항목별 원문 텍스트 앞부분).
    """
    from collections import Counter

    soup = parse_document(content)
    kind = detect_kind(soup)
    flow = _document_flow(soup)
    fs_items, notes_items = _find_slices(flow, kind, scope)

    # 재무제표: 첫 재무제표 제목 이후부터 집계
    # (그 앞의 표지/목차성 내용은 의도적으로 옮기지 않는다)
    fs_counter: Counter[str] = Counter()
    fs_snippets: list[str] = []
    started = False
    for item in fs_items:
        if not started:
            if tag_is(item, "TITLE"):
                continue
            text = text_of(item)
            if any(_statement_title_in(ln) for ln in text.split("\n") if ln):
                started = True
            elif tag_is(item, "TABLE") and any(
                    _statement_title_in(text_of(tr) or "")
                    for tr in item.find_all(lambda t: tag_is(t, "TR"))):
                started = True
        if not started:
            continue
        if tag_is(item, "TITLE"):
            continue  # dart4 중첩 제목은 엑셀로 옮기지 않는다
        fs_counter += _raw_chars(item)
        fs_snippets.append(re.sub(r"\s+", " ", text_of(item))[:60])

    notes_counter: Counter[str] = Counter()
    note_snippets: list[str] = []
    for item in notes_items:
        notes_counter += _raw_chars(item)
        note_snippets.append(re.sub(r"\s+", " ", text_of(item))[:60])

    return {"statements": fs_counter, "notes": notes_counter,
            "statement_snippets": fs_snippets, "note_snippets": note_snippets}


# ------------------------------------------------------ 재무제표 추출

def extract_statements(items: list[Tag]) -> list[dict]:
    statements: list[dict] = []
    current: dict | None = None

    def preamble_cell(cell_el: Tag) -> dict:
        size, font = _font_of(cell_el)
        return {"text": text_of(cell_el), "align": _align_of(cell_el),
                "bold": _is_bold(cell_el), "size": size, "font": font}

    for item in items:
        if tag_is(item, "P"):
            text = text_of(item)
            if not text:
                continue
            title = _statement_title_in(text)
            if title:
                current = {"title": text.strip(), "sheet_name": title,
                           "preamble": [], "postscript": [], "tables": []}
                statements.append(current)
            elif current is not None:
                if current["tables"]:
                    current["postscript"].append(text)
                else:
                    current["preamble"].append([{"text": text, "align": None, "bold": False}])
            continue

        # TABLE
        border = attr(item, "BORDER").strip()
        if border == "0":
            # 제목/기수/회사명/단위 등 서식 표 — 행 단위로 스캔
            rows_buffer: list[list[dict]] = []
            found_title: str | None = None
            title_text = ""
            for tr in item.find_all(lambda t: tag_is(t, "TR")):
                cells = [c for c in tr.find_all(lambda t: tag_is(t, *_CELL_TAGS))]
                row = [preamble_cell(c) for c in cells]
                joined = norm("".join(c["text"] for c in row))
                st = _STATEMENT_RE.match(joined)
                if st and found_title is None:
                    found_title = joined
                    title_text = " ".join(c["text"] for c in row if c["text"]).strip()
                    if current is None or current["tables"]:
                        current = {"title": title_text, "sheet_name": found_title,
                                   "preamble": [], "postscript": [], "tables": []}
                        statements.append(current)
                    else:
                        current["title"] = title_text
                        current["sheet_name"] = found_title
                    current["preamble"].extend(rows_buffer)
                    current["preamble"].append(row)
                    rows_buffer = []
                    continue
                rows_buffer.append(row)
            if rows_buffer:
                if current is not None and not current["tables"]:
                    current["preamble"].extend(rows_buffer)
                # 데이터 표 이후의 borderless 표는 버리지 않고 postscript로
                elif current is not None and current["tables"]:
                    for row in rows_buffer:
                        text = " ".join(c["text"] for c in row if c["text"]).strip()
                        if text:
                            current["postscript"].append(text)
        else:
            if current is not None:
                current["tables"].append(table_to_grid(item))

    return [s for s in statements if s["tables"]]


# ------------------------------------------------------ 주석 추출

# 숫자. 형태의 주석 번호. 날짜/소수("2022.12.")는 제외하되
# 문장 끝 마침표 뒤("...습니다.4. 제목")는 허용해야 한다.
# 하이픈 하위주석("4-5. 운영위험")은 앞 번호(4)의 하위이므로 새 주석으로
# 잡지 않는다 — 숫자 앞에 '-'가 오면 제외한다.
_NOTE_HEAD_RE = re.compile(r"(?<!-)(?<!\d)(?<!\d\.)(\d{1,3})\.(?!\d)\s*")


def split_note_segments(line: str, last_number: int, has_current: bool):
    """한 문단 안에 이어 붙은 주석 제목들을 분리.

    반환: [(번호|None, 텍스트)] — 번호 None은 직전 문맥에 속하는 텍스트.
    라인 시작 매치는 번호 건너뜀(≤10)을 허용하고, 문단 중간 매치는
    엄격히 last+1만 허용해 본문 속 숫자 오인식을 막는다.
    """
    matches: list[tuple[int, int]] = []  # (라인 내 위치, 주석 번호)
    last = last_number
    exists = has_current
    for m in _NOTE_HEAD_RE.finditer(line):
        n = int(m.group(1))
        at_start = m.start() == 0
        if not exists:
            ok = at_start and n <= 2
        elif at_start:
            ok = last < n <= last + 10
        else:
            ok = n == last + 1
        if ok:
            matches.append((m.start(), n))
            last = n
            exists = True
    if not matches:
        return [(None, line)] if line.strip() else []
    result: list[tuple[int | None, str]] = []
    if matches[0][0] > 0:
        pre = line[:matches[0][0]].strip()
        if pre:
            result.append((None, pre))
    for i, (start, n) in enumerate(matches):
        end = matches[i + 1][0] if i + 1 < len(matches) else len(line)
        result.append((n, line[start:end].strip()))
    return result


def extract_notes(items: list[Tag]) -> tuple[list[list[dict]], list[dict]]:
    """(notes_preamble, notes) 반환."""
    preamble: list[list[dict]] = []
    notes: list[dict] = []
    current: dict | None = None
    last_number = 0

    def start_note(number: int, text: str):
        nonlocal current, last_number
        current = {"number": number, "title": text.split("\n")[0].strip(),
                   "blocks": [{"type": "paragraph", "text": text}]}
        notes.append(current)
        last_number = number

    for item in items:
        if tag_is(item, "P", "TITLE"):
            # dart4 본문 주석은 TABLE-GROUP 내 중첩 TITLE이 주석 제목이다
            text = text_of(item)
            if not text:
                continue
            for line in text.split("\n"):
                if not line.strip():
                    continue
                for number, seg in split_note_segments(
                        line.strip(), last_number, current is not None):
                    if number is not None and (
                            current is None or number > last_number):
                        start_note(number, seg)
                    elif current is not None:
                        current["blocks"].append({"type": "paragraph", "text": seg})
                    else:
                        preamble.append([{"text": seg, "align": None, "bold": False}])
            continue

        # TABLE
        table = table_to_grid(item)
        if current is None:
            for row in table["rows"]:
                preamble.append([
                    {"text": c["text"], "align": c["align"], "bold": c["bold"]}
                    for c in row["cells"] if c is not None
                ])
        else:
            current["blocks"].append({"type": "table", "table": table})

    return preamble, notes


# ------------------------------------------------------ 모델 조립

def extract_model(content: str, scope: str) -> dict:
    if scope not in (CONSOLIDATED, SEPARATE):
        raise ValueError(f"scope must be consolidated|separate: {scope}")
    soup = parse_document(content)
    kind = detect_kind(soup)
    available = detect_scopes(soup)
    if scope not in available:
        raise LookupError(
            f"요청한 범위({scope})가 문서에 없습니다. 문서 내 범위: {available}")

    flow = _document_flow(soup)
    fs_items, notes_items = _find_slices(flow, kind, scope)
    statements = extract_statements(fs_items)
    notes_preamble, notes = extract_notes(notes_items)

    company = ""
    company_el = soup.find(lambda t: tag_is(t, "COMPANY-NAME"))
    if company_el is not None:
        company = text_of(company_el)

    return {
        "kind": kind,
        "scope": scope,
        "company_name": company,
        "statements": statements,
        "notes_preamble": notes_preamble,
        "notes": notes,
    }
