import unittest
from pathlib import Path

SKILLS = [Path("plugins/claude/opendart/skills/opendart-excel/SKILL.md"),
          Path("plugins/codex/opendart/skills/opendart-excel/SKILL.md")]
REMOVED = ["create_workbook_from_mcp.py", "prepare_notes_json.py",
           "build_financial_excel.py", "verify_workbook.py", "_ensure_deps.py",
           "requirements.txt", "doc.json", "model.json",
           "get_disclosure_document", "use_body", "rcept_nos",
           "audit_attachment_not_found"]
KEPT_USER_LINES = [
    "회사명이나 사업연도가 없거나 모호하면 사용자에게 확인한다.",
    "회사 별칭을 정식 회사명으로 확정할 수 없으면 사용자에게 확인한다.",
    "Excel 요청인지 불명확하면 출력 형식을 확인한다.",
    "여러 항목이 모호하면 한 번에 질문하고, 명확한 항목은 다시 묻지 않는다.",
]


class SkillDocTest(unittest.TestCase):
    def test_skills_describe_new_flow(self):
        for path in SKILLS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(path)):
                self.assertIn("create_financial_workbook", text)
                for token in ("list_financial_document_candidates",
                              "candidate_id", "candidate_unavailable",
                              "scope_not_in_document",
                              "no_financial_statements",
                              "output_dir", "output_name", "get_corp_codes",
                              "search_disclosures"):
                    self.assertIn(token, text)
                for token in REMOVED:
                    self.assertNotIn(token, text)

    def test_user_added_lines_are_preserved(self):
        for path in SKILLS:
            text = path.read_text(encoding="utf-8")
            for line in KEPT_USER_LINES:
                with self.subTest(path=str(path), line=line):
                    self.assertIn(line, text)

    def test_both_skills_share_the_same_body(self):
        bodies = [p.read_text(encoding="utf-8") for p in SKILLS]
        self.assertEqual(bodies[0], bodies[1])

    def test_skills_forbid_handling_raw_content(self):
        for path in SKILLS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(path)):
                self.assertIn("원문 content를 요청하거나 대화에 출력하지 않는다", text)
                self.assertIn("중간 XML", text)
                self.assertIn("검증에 실패한 파일", text)

    def test_skills_document_file_naming_rule(self):
        for path in SKILLS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=str(path)):
                self.assertIn("_2024_연결재무제표.xlsx", text)

    def test_readme_reflects_new_structure(self):
        text = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("create_financial_workbook", text)
        self.assertIn("src/opendartmcp/excel/", text)
        for token in ("_ensure_deps.py", "create_workbook_from_mcp.py",
                      "prepare_notes_json.py"):
            self.assertNotIn(token, text)
