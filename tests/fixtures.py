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
