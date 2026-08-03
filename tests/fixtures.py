# -*- coding: utf-8 -*-
"""테스트용 메모리 DART 원문/ZIP fixture. 실제 DART API를 호출하지 않는다."""
from __future__ import annotations

import io
import zipfile

_STATEMENTS = ("재무상태표", "포괄손익계산서", "자본변동표", "현금흐름표")


def _preamble(name: str, company: str) -> str:
    """실제 DART 원문처럼 제목/기수/회사명/단위를 borderless 표로 둔다."""
    return f"""
<TABLE BORDER="0">
<TR><TD>{name}</TD></TR>
<TR><TD>제 55 기 2024.12.31 현재</TD></TR>
<TR><TD>{company}</TD></TR>
<TR><TD>(단위: 원)</TD></TR>
</TABLE>
"""


def _statement_block(name: str, note_no: str, company: str) -> str:
    return _preamble(name, company) + f"""
<TABLE BORDER="1">
<TR><TH>과목</TH><TH>주석</TH><TH>당기</TH></TR>
<TR><TD>현금및현금성자산</TD><TD>{note_no}</TD><TD>1,000</TD></TR>
<TR><TD>매출채권</TD><TD>2</TD><TD>2,000</TD></TR>
</TABLE>
"""


def audit_report_xml(scope: str = "consolidated", *, with_notes: bool = True,
                     with_tables: bool = True, company: str = "테스트 주식회사",
                     title: str = "연결감사보고서") -> str:
    prefix = "연결" if scope == "consolidated" else ""
    fs_title = "(첨부)연결재무제표" if scope == "consolidated" else "(첨부)재무제표"
    body = "".join(_statement_block(prefix + s, "3", company) for s in _STATEMENTS) \
        if with_tables else "<P>재무제표를 첨부하지 않았습니다</P>"
    notes = """
<TITLE>주석</TITLE>
<P>1. 회사의 개요</P>
<P>당사는 테스트 목적으로 설립되었습니다.</P>
<P>2. 매출채권</P>
<P>매출채권의 내역은 다음과 같습니다.</P>
<P>3. 현금및현금성자산</P>
<P>현금및현금성자산의 내역은 다음과 같습니다.</P>
""" if with_notes else ""
    return f"""<?xml version="1.0" encoding="utf-8"?>
<DOCUMENT>
<DOCUMENT-NAME>{title}</DOCUMENT-NAME>
<COMPANY-NAME>{company}</COMPANY-NAME>
<BODY>
<SECTION-1>
<TITLE>{fs_title}</TITLE>
{body}
{notes}
</SECTION-1>
</BODY>
</DOCUMENT>
"""


def annual_body_xml(scope: str = "consolidated", company: str = "테스트 주식회사") -> str:
    """정기보고서 본문 — 주석 열이 없어 하이퍼링크 0개가 정상이다 (plan.md §5.7)."""
    prefix = "연결" if scope == "consolidated" else ""
    fs_title = prefix + "재무제표"
    blocks = "".join(_preamble(prefix + s, company) + """
<TABLE BORDER="1">
<TR><TH>과목</TH><TH>당기</TH></TR>
<TR><TD>현금및현금성자산</TD><TD>1,000</TD></TR>
</TABLE>
""" for s in _STATEMENTS)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<DOCUMENT>
<DOCUMENT-NAME>사업보고서</DOCUMENT-NAME>
<COMPANY-NAME>{company}</COMPANY-NAME>
<BODY>
<SECTION-1>
<TITLE>2. {fs_title}</TITLE>
{blocks}
<TITLE>3. {fs_title}주석</TITLE>
<P>1. 회사의 개요</P>
<P>당사는 테스트 목적으로 설립되었습니다.</P>
<P>2. 매출채권</P>
<P>매출채권의 내역은 다음과 같습니다.</P>
<P>3. 현금및현금성자산</P>
<P>현금및현금성자산의 내역은 다음과 같습니다.</P>
</SECTION-1>
</BODY>
</DOCUMENT>
"""


def titled_audit_report_xml(scope: str = "separate",
                            company: str = "테스트 주식회사",
                            title: str = "감사보고서") -> str:
    """비상장 외감법인 형식 — 재무제표 제목이 TABLE-GROUP 안 TITLE 태그다."""
    prefix = "연결" if scope == "consolidated" else ""
    fs_title = "(첨부)연결재무제표" if scope == "consolidated" else "(첨부)재무제표"
    blocks = "".join(f"""
<TABLE-GROUP>
<TITLE>{prefix}{name}</TITLE>
<TABLE BORDER="0"><TR><TD>제 26 기 2024.12.31 현재</TD></TR></TABLE>
</TABLE-GROUP>
<TABLE BORDER="1">
<TR><TH>과목</TH><TH>주석</TH><TH>당기</TH></TR>
<TR><TD>현금및현금성자산</TD><TD>3</TD><TD>1,000</TD></TR>
</TABLE>
""" for name in _STATEMENTS)
    return f"""<?xml version="1.0" encoding="utf-8"?>
<DOCUMENT>
<DOCUMENT-NAME>{title}</DOCUMENT-NAME>
<COMPANY-NAME>{company}</COMPANY-NAME>
<BODY>
<SECTION-1>
<TITLE>{fs_title}</TITLE>
{blocks}
<TITLE>주석</TITLE>
<P>1. 회사의 개요</P>
<P>당사는 테스트 목적으로 설립되었습니다.</P>
<P>2. 매출채권</P>
<P>매출채권의 내역은 다음과 같습니다.</P>
<P>3. 현금및현금성자산</P>
<P>현금및현금성자산의 내역은 다음과 같습니다.</P>
</SECTION-1>
</BODY>
</DOCUMENT>
"""


def viewer_page(rcept_no: str, attachments: list[tuple[str, str, str]],
                *, company: str = "테스트", report: str = "반기보고서",
                node_dcm: str = "", node_text: str = "(첨부)반 기 재 무 제 표") -> str:
    """DART 화면 HTML — 첨부 선택 상자와 문서 목차 노드.

    attachments: [(rcpNo, dcmNo, 표시제목)] — rcpNo가 조회 접수번호와
    달라도 된다(정정 공시에서 첨부가 원본에 남아 있는 경우).
    """
    options = "\n".join(
        f'<option value="rcpNo={rcpt}&amp;dcmNo={dcm}">{label}</option>'
        for rcpt, dcm, label in attachments)
    nodes = ""
    if node_dcm:
        nodes = f"""<script>
var node1 = {{}};
node1['text'] = "{node_text}";
node1['rcpNo'] = "{rcept_no}"; node1['dcmNo'] = "{node_dcm}";
node1['eleId'] = "3"; node1['offset'] = "100";
node1['length'] = "999"; node1['dtd'] = "dart4.xsd";
//js tree
</script>"""
    return (f"<html><head><title>{company}/{report}/2025.08.14</title></head>"
            f'<body><select id="att">{options}</select>{nodes}</body></html>')


def viewer_fragment(prefix: str = "요약 반 기 ") -> str:
    """화면이 돌려주는 재무제표 조각 — 제목에 수식어가 붙는다."""
    statements = "".join(f"""
<table class="nb"><tr><td>{prefix}{name}</td></tr>
<tr><td>테스트 주식회사</td></tr><tr><td>(단위: 원)</td></tr></table>
<table border="1"><tr><th>과목</th><th>주석</th><th>당기</th></tr>
<tr><td>현금</td><td>1</td><td>1,000</td></tr></table>""" for name in _STATEMENTS)
    return ("<html><body><p>(첨부)반 기 재 무 제 표</p>" + statements +
            '<p class="section-2">주 석</p><p>1. 현금</p>'
            "<p>현금의 내역입니다.</p></body></html>")


def make_zip(entries: dict[str, str]) -> bytes:
    """{엔트리명: 원문} → ZIP bytes (메모리)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, text in entries.items():
            zf.writestr(name, text.encode("utf-8"))
    return buffer.getvalue()


def annual_report_zip(rcept_no: str = "20250319000665") -> bytes:
    """사업보고서 ZIP: 본문 + 감사보고서 + 연결감사보고서 (plan.md §9 구조)."""
    return make_zip({
        f"{rcept_no}.xml": annual_body_xml("consolidated"),
        f"{rcept_no}_00760.xml": audit_report_xml("separate", title="감사보고서"),
        f"{rcept_no}_00761.xml": audit_report_xml("consolidated", title="연결감사보고서"),
    })


def quarterly_report_zip(rcept_no: str = "20250515000001") -> bytes:
    """분기보고서 ZIP: 본문 + 검토보고서 + 연결검토보고서."""
    return make_zip({
        f"{rcept_no}.xml": annual_body_xml("consolidated"),
        f"{rcept_no}_00010.xml": audit_report_xml("separate", title=" 검토 보고서 "),
        f"{rcept_no}_00011.xml": audit_report_xml("consolidated", title="연결 검토보고서"),
    })


def body_only_zip(rcept_no: str = "20250515000002",
                  scope: str = "consolidated") -> bytes:
    """감사·검토보고서 첨부가 없는 ZIP."""
    return make_zip({f"{rcept_no}.xml": annual_body_xml(scope)})
