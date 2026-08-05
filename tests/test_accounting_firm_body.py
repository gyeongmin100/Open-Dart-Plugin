import unittest

from opendartmcp.excel import dartdoc
from tests.fixtures import accounting_firm_body_xml, annual_body_xml


class AccountingFirmBodyTest(unittest.TestCase):
    """회계법인사업보고서 — 제표 제목이 SECTION 직속 TITLE인 양식.

    일반 정기보고서는 제표 제목을 "재무제표" 섹션 안에 중첩하지만
    회계법인사업보고서는 나란히 둔다. 중첩 여부만으로 섹션 경계를 정하면
    재무제표 섹션이 첫 제표 앞에서 잘려 빈 채로 남는다.
    """

    def test_statements_are_extracted(self):
        model = dartdoc.extract_model(accounting_firm_body_xml(), dartdoc.SEPARATE)
        self.assertEqual([s["sheet_name"] for s in model["statements"]],
                         ["재무상태표", "손익계산서", "현금흐름표", "자본변동표"])
        self.assertTrue(all(s["tables"] for s in model["statements"]))

    def test_notes_are_extracted(self):
        model = dartdoc.extract_model(accounting_firm_body_xml(), dartdoc.SEPARATE)
        self.assertEqual([note["number"] for note in model["notes"]], [1, 2, 3])

    def test_notes_stop_at_the_next_section(self):
        """주석 다음 섹션은 경계다 — 제표 제목만 경계에서 빼야 한다."""
        model = dartdoc.extract_model(accounting_firm_body_xml(), dartdoc.SEPARATE)
        self.assertNotIn("해당사항 없음",
                         "".join(str(note) for note in model["notes"]))

    def test_consolidated_is_reported_missing(self):
        """회계법인은 연결재무제표를 싣지 않는다 — '없음'으로 갈려야 한다."""
        with self.assertRaises(dartdoc.SectionNotFound) as ctx:
            dartdoc.extract_model(accounting_firm_body_xml(), dartdoc.CONSOLIDATED)
        self.assertEqual(ctx.exception.code, "scope_not_in_document")
        self.assertEqual(ctx.exception.available_scopes, ["separate"])

    def test_ordinary_annual_report_is_unchanged(self):
        """일반 정기보고서는 제표 제목이 경계가 아니어도 결과가 같아야 한다."""
        for scope in (dartdoc.CONSOLIDATED, dartdoc.SEPARATE):
            model = dartdoc.extract_model(annual_body_xml(scope), scope)
            prefix = "연결" if scope == dartdoc.CONSOLIDATED else ""
            self.assertEqual(
                [s["sheet_name"] for s in model["statements"]],
                [prefix + name for name in
                 ("재무상태표", "포괄손익계산서", "자본변동표", "현금흐름표")])


class StatementTitleNumberingTest(unittest.TestCase):
    def test_korean_ordinal_prefix_is_stripped(self):
        self.assertEqual(dartdoc._statement_title_in("가. 재무상태표"), "재무상태표")

    def test_arabic_prefix_still_stripped(self):
        self.assertEqual(dartdoc._statement_title_in("4-1. 재무상태표"), "재무상태표")

    def test_korean_ordinal_alone_does_not_promote_a_heading(self):
        """가나다 번호가 붙었다고 제표가 되는 것은 아니다 — 본문 명칭이 있어야 한다."""
        for heading in ("가. 요약재무정보", "나. 타법인 출자 현황", "마. 주석"):
            self.assertIsNone(dartdoc._statement_title_in(heading), heading)

    def test_long_note_numbering_is_not_a_statement_title(self):
        """세 자리 주석 번호는 제표 제목이 아니다."""
        self.assertIsNone(dartdoc._statement_title_in("134. 현금흐름표"))
