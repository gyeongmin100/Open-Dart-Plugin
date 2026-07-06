---
name: opendart-excel
description: 사용자가 특정 기업/사업연도의 연결·별도 재무제표를 엑셀로 요청하면, OpenDART MCP로 공시 원문을 받아 DART 원문 양식(재무제표 시트 + 클릭 가능한 주석 링크)의 검증된 Excel 파일을 생성한다.
---

# OpenDART 재무제표 Excel 생성 스킬

사용자 요청 예: "삼성전자 2022년 연결재무제표 엑셀로 만들어줘"

## 사용 흐름

### 1. 요청 파싱
- 추출: **회사명**, **사업연도**, **범위**(연결 `consolidated` / 별도 `separate`).
- 범위가 명시되지 않았고 문서에 연결·별도가 **둘 다** 있으면 반드시 사용자에게 물어본다. 임의로 기본값을 선택하지 말 것. 스크립트가 이를 지원한다: `--scope auto`는 문서에 한 범위만 있으면 자동 선택하고, 둘 다 있으면 **종료코드 2** + `{"error":"scope_ambiguous","available":[...]}` 출력 후 종료한다.

### 2. MCP 호출 순서
a. `get_corp_codes` 또는 `search_disclosures`(`mcp__open-dart__search_disclosures`)로 corp_code 확인.
   - `search_disclosures` 파라미터: `corp_code`, `bgn_de`/`end_de`(사업연도+1년 범위, 예: 2022년 → `20230101`~`20231231`), `pblntf_detail_ty="A001"`(사업보고서).
   - `report_nm`에 `"사업보고서 (YYYY.12)"`가 포함된 공시를 선택하고 `rcept_no`를 얻는다.
b. `get_disclosure_document(rcept_no)` 호출 → `{filename, content, documents}` 반환.
   - `documents`는 공시에 포함된 문서 목록 `[{filename, title}]` (예: 사업보고서, 감사보고서, 연결감사보고서).
   - **감사보고서 우선 규칙**: 원문 양식 충실도가 높고 주석번호 열(→하이퍼링크)이 있는 감사보고서 첨부를 우선 사용한다.
     - 연결 요청 → `title == "연결감사보고서"` 인 문서를 `doc_name`으로 재요청
     - 별도 요청 → `title == "감사보고서"` 인 문서를 `doc_name`으로 재요청
     - 해당 첨부가 없으면(분기보고서 등) 사업보고서 본문(첫 응답의 content)으로 진행 — 본문에는 주석 열이 없어 링크 0개가 정상이다.
   - **툴 결과 전체를 JSON 파일로 저장**한다(예: 임시 폴더의 `doc.json`). content를 대화에 인라인으로 붙여넣지 말 것(대용량). 이 입력 JSON은 중간 파일이므로 작업 후 정리한다.

### 3. 워크북 생성 (원스텝, 권장)
```
python scripts/create_workbook_from_mcp.py --input doc.json --scope consolidated|separate|auto \
    --output 회사명_연도_연결재무제표.xlsx
```
- **최종 산출물은 엑셀 파일 하나뿐이다.** 사용자에겐 `.xlsx`만 필요하다.
- `--model-output`(중간 모델 JSON 저장)은 **디버깅 시에만** 쓴다. 평상시엔 생략 — 붙이면 부가 JSON 파일이 남는다.
- 검증 리포트는 stdout(JSON)으로만 출력되며 파일을 만들지 않는다. 셸 리다이렉트(`> x.log`)로 로그 파일을 만들지 말 것.
- 입력용 `doc.json`은 임시 폴더에 두고 작업 완료 후 지운다. 결과 폴더엔 `.xlsx`만 남긴다.

종료코드 처리:
- **0**: 생성 + 검증 완료. 파일을 사용자에게 전달.
- **2**: 범위 모호(`scope_ambiguous`). 사용자에게 연결/별도를 물어본 뒤 `--scope`를 지정해 재실행.
- **1**: 검증 실패. 출력 JSON의 `verification.failures`를 확인하고 원인을 고친 뒤 재시도. **검증에 실패한 파일을 절대 전달하지 말 것.**

### 3'. 단계별 실행 (대안)
```
# 1) 원문 -> 모델 JSON (범위 모호 시 종료코드 2)
python scripts/prepare_notes_json.py --input doc.json --scope consolidated --output model.json

# 2) 모델 -> Excel
python scripts/build_financial_excel.py --model model.json --output out.xlsx

# 3) 검증 (--source 로 원문 재파싱 대조 권장; 실패 시 종료코드 1)
python scripts/verify_workbook.py --model model.json --workbook out.xlsx --source doc.json
```

## 연결/별도 처리 규칙
- **사업보고서 본문**: TITLE 섹션으로 필터링한다 — 연결은 "2. 연결재무제표" + "3. 연결재무제표 주석", 별도는 "4. 재무제표" + "5. 재무제표 주석" (번호 접두는 무시하고 제목으로 매칭).
- **감사보고서 첨부 XML**도 입력 가능: "(첨부)연결재무제표"(연결감사보고서) 또는 "(첨부)재무제표"(감사보고서). 첨부 파일은 각각 **단일 범위만** 포함하므로 `--scope auto`로 자동 선택된다.

## 입력 형식 유연성 (`load_content`)
다음 세 가지를 모두 지원하며 자동 감지한다:
- MCP 결과 JSON: `{filename, content}` (content 키 필수)
- 원문 XML/HTML 파일 (utf-8 / cp949 / euc-kr 자동 감지)
- ZIP 파일 (내부의 .xml/.html 중 첫 문서 사용)

## 출력 명세
- 재무제표별 시트(예: 연결재무상태표, 연결포괄손익계산서, 연결자본변동표, 연결현금흐름표) + 마지막에 `주석` 시트.
- 주석번호는 표의 **우측 끝 열**로 이동, "4,21" 같은 복수 참조는 **번호마다 개별 셀**로 분리.
- 각 숫자 주석번호는 파란색(0000FF)/밑줄 하이퍼링크로 `주석` 시트의 해당 주석 **제목 행**(`N.` 으로 시작)으로 이동.
- 테두리는 **실제 표 범위에만** 적용. 제목/회사명/기간/단위(프리앰블)와 문단에는 테두리 없음.
- freeze panes, auto filter **사용 안 함**.
- 정수 금액은 숫자 셀(`#,##0;(#,##0)` 서식), 괄호 숫자는 음수로 변환.

## 검증 (verify_workbook.py 체크리스트)
1. 시트 구성: 재무제표 시트들 + `주석`이 원문과 일치.
2. 재무제표 수: 원문과 동일, 4종 미만이면 실패(4종이면 손익/포괄손익 통합 형식 경고).
3. 프리앰블(제목/기수/회사명/단위)이 원문과 일치.
4. 주석 번호 연속성: 중복/역순/번호 누락(병합 의심) 탐지, 참조된 주석이 모두 존재.
5. 주석 링크: 모든 숫자 주석번호가 개별 셀 + 하이퍼링크, 링크가 `주석` 시트의 정확한 제목 행을 가리키는지, 파랑/밑줄 서식, 링크 수가 원문 기대값 이상인지.
6. freeze panes / auto filter 부재.
7. `--source` 지정 시: 원문을 재파싱해 주석 번호 목록·재무제표 목록을 모델과 대조.
8. `--source` 지정 시 **글자 단위 완전성**: 원문 섹션의 모든 글자(공백 제외) 출현 횟수와 결과물의 글자 출현 횟수를 전수 대조 — 번호 체계가 안 바뀌는 내부 문단/셀 누락까지 검출. 이미지 파일명·캡션 등 엑셀로 옮기지 않는 요소만 집계에서 제외.

**주의**: 원문 재무제표에 주석 열 자체가 없으면 "링크 0개"는 정상이다(warnings에 표시됨) — 실패로 취급하지 말 것.

## 주의사항
- DART 원문은 깨진 XML일 수 있다(bare `&`, 미정의 엔티티, bare `<`). 파서(`dartdoc.parse_document`)가 자동으로 정제·복구하므로 별도 전처리 불필요.
- 대용량 문서(수 MB)는 파싱에 ~10초 걸릴 수 있다.
- Windows 콘솔에서 한글이 깨지면 `PYTHONIOENCODING=utf-8` 환경변수를 설정하고 실행.
- **특정 기업 하드코딩 금지**: 모든 파싱/생성 로직은 범용이어야 하며, 특정 회사 이름·계정과목을 조건으로 넣지 말 것.

## 의존성
Python 3.11+ / `pip install -r requirements.txt`
- beautifulsoup4
- lxml
- openpyxl
