# OpenDART Plugin

[![PyPI version](https://img.shields.io/pypi/v/opendart-mcp-server)](https://pypi.org/project/opendart-mcp-server/)
[![Python](https://img.shields.io/pypi/pyversions/opendart-mcp-server)](https://pypi.org/project/opendart-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[OpenDART API](https://opendart.fss.or.kr)(금융감독원 전자공시시스템 오픈API)를 이용해 **MCP 서버**를 만들고, 특정 기업의 재무제표를  **Excel 파일**로 만들어주는 SKILL을 포함한 **Claude Code / Codex 플러그인**입니다.

- "삼성전자 2023년 연결재무제표 엑셀로 만들어줘" 한마디로 **재무제표 원문(감사보고서)을 가져와 시트별로 정리하고, 각 주석번호에 하이퍼링크**까지 걸린 `.xlsx` 파일을 생성합니다.
- 공시 검색, 재무제표, 임원/주주 현황, 주요사항보고서 등 DS001~DS006 전 영역 **85개 도구**도 자연어 질의로 바로 사용할 수 있습니다.

---

## 준비물

- Claude Code 또는 Codex CLI
- Python 3.11+
- `uv` / `uvx` ([설치](https://docs.astral.sh/uv/getting-started/installation/)) — 없다면 `pip install uv`
- OpenDART API KEY: [OpenDART](https://opendart.fss.or.kr)에서 KEY 발급

---

## 설치

플러그인을 설치하면 `open-dart` MCP 서버 설정과 `opendart-excel` 스킬이 함께 설치됩니다.

**Claude Code**

```text
/plugin marketplace add gyeongmin100/Open-Dart-Plugin
/plugin install opendart-excel@open-dart-mcp
```

설치 중 `DART_API_KEY`를 입력하라는 프롬프트가 뜹니다.

사용 예:

```text
/opendart-excel:opendart-excel 삼성전자 2023년 연결 재무제표를 엑셀로 만들어줘
```

**Codex**

```bash
codex plugin marketplace add gyeongmin100/Open-Dart-Plugin
```

Codex에서 `/plugins`를 열고 `OpenDART MCP` marketplace의 `opendart-excel` 플러그인을 설치합니다. Codex 실행 환경에는 `DART_API_KEY`가 미리 설정되어 있어야 합니다.

```bash
export DART_API_KEY="your-api-key"      # bash/zsh
$env:DART_API_KEY="your-api-key"        # PowerShell
```

사용 예:

```text
$opendart-excel 삼성전자 2023년 연결 재무제표를 엑셀로 만들어줘
```

---

### AI 에이전트용 설치 프롬프트

아래 블록을 그대로 복사해서 Claude Code나 Codex 채팅창에 붙여넣으면, 에이전트가 알아서 marketplace 등록 → 플러그인 설치 → API 키 설정까지 진행합니다.

```text
OpenDART Excel 플러그인을 설치해줘.

1. 저장소: https://github.com/gyeongmin100/Open-Dart-Plugin
2. Claude Code라면:
   - /plugin marketplace add gyeongmin100/Open-Dart-Plugin 실행
   - /plugin install opendart-excel@open-dart-mcp 실행
   - 설치 중 DART_API_KEY를 물어보면, 아직 없다고 하면 https://opendart.fss.or.kr 에서
     API 키를 발급받는 방법을 안내해줘.
   Codex라면:
   - codex plugin marketplace add gyeongmin100/Open-Dart-Plugin 실행
   - /plugins 메뉴에서 "OpenDART MCP" marketplace의 opendart-excel 플러그인 설치 안내
   - 실행 환경에 DART_API_KEY 환경변수가 필요하다는 것도 안내해줘.
3. 설치가 끝나면 opendart-excel 스킬로 "삼성전자 2023년 연결재무제표 엑셀로 만들어줘" 같은
   요청을 처리할 수 있다는 것을 확인해줘.
4. Python 3.11+ 와 uv/uvx가 없으면 먼저 설치 방법을 안내해줘 (pip install uv).
```

---

## 사용 예시

```
삼성전자 최근 공시 보여줘
카카오 2023년 재무제표 알려줘
현대자동차 최대주주 현황은?
LG전자 임원 현황 조회해줘
SK하이닉스 배당 이력 알려줘
2024년 합병 공시 목록 검색해줘
삼성전자 2023년 연결 재무제표를 엑셀로 만들어줘   ← opendart-excel 플러그인
```

---

## opendart-excel 스킬 동작 방식

1. 회사명·사업연도·범위(연결/별도)를 파악하고, 범위가 모호하면 반드시 사용자에게 확인합니다.
2. MCP로 공시 검색 → 사업보고서(가능하면 감사보고서 첨부)의 원문을 가져옵니다.
3. 원문을 파싱해 재무제표별 시트 + `주석` 시트로 구성된 Excel을 생성합니다. 주석번호는 표 우측 열에 개별 셀로 분리되고, 파란색 하이퍼링크로 `주석` 시트의 해당 항목으로 연결됩니다.
4. 시트 구성·프리앰블·주석 연속성·하이퍼링크·글자 단위 완전성까지 자동 검증한 뒤, 검증을 통과한 `.xlsx` 파일만 전달합니다.

---

## 제공 도구 (85개)

### DS001 · 공시정보 (4)

<details>
<summary>목록 펼치기</summary>

| Tool | Description |
|------|-------------|
| `search_disclosures` | 공시 목록 검색 |
| `get_company_info` | 기업 기본정보 조회 |
| `get_disclosure_document` | 공시 원문 문서 조회 |
| `get_corp_codes` | 전체 법인코드 목록 다운로드 |

</details>

### DS002 · 정기보고서 주요정보 (30)

<details>
<summary>목록 펼치기</summary>

| Tool | Description |
|------|-------------|
| `get_capital_change_status` | 증자(감자) 현황 |
| `get_dividend_info` | 배당에 관한 사항 |
| `get_treasury_stock` | 자기주식 취득 및 처분 현황 |
| `get_largest_shareholder` | 최대주주 현황 |
| `get_largest_shareholder_changes` | 최대주주 변동현황 |
| `get_minority_shareholders` | 소액주주 현황 |
| `get_executives` | 임원 현황 |
| `get_employees` | 직원 현황 |
| `get_executive_compensation_total` | 이사·감사 전체의 보수현황 |
| `get_executive_compensation_gmtsck` | 이사·감사 전체 보수현황 (주총승인금액) |
| `get_executive_compensation_type` | 이사·감사 전체 보수현황 (유형별) |
| `get_executive_compensation_individual` | 이사·감사 개인별 보수현황 5억원 이상 |
| `get_individual_pay_over5` | 개인별 보수지급 금액 5억 이상 상위 5인 |
| `get_executive_compensation_individual_v2` | 이사·감사 개인별 보수현황 5억원 이상 (V2) |
| `get_individual_pay_over5_v2` | 개인별 보수지급 금액 상위 5인 (V2) |
| `get_unregistered_executives` | 미등기임원 보수현황 |
| `get_investment_in_other_corps` | 타법인 출자현황 |
| `get_audit_opinion` | 회계감사인 명칭 및 감사의견 |
| `get_audit_fee` | 감사용역체결현황 |
| `get_non_audit_service` | 비감사용역 계약체결 현황 |
| `get_outside_director_changes` | 사외이사 및 변동현황 |
| `get_stock_total_qty` | 주식의 총수 현황 |
| `get_bond_issuance` | 채무증권 발행실적 |
| `get_commercial_paper` | 기업어음증권 미상환 잔액 |
| `get_short_term_bond` | 단기사채 미상환 잔액 |
| `get_corp_bond_outstanding` | 회사채 미상환 잔액 |
| `get_hybrid_bond` | 신종자본증권 미상환 잔액 |
| `get_debt_securities_outstanding` | 조건부자본증권 미상환 잔액 |
| `get_public_offering_fund_usage` | 공모자금 사용내역 |
| `get_private_placement_fund_usage` | 사모자금 사용내역 |

</details>

### DS003 · 재무정보 (7)

<details>
<summary>목록 펼치기</summary>

| Tool | Description |
|------|-------------|
| `get_single_company_account` | 단일 회사 주요 재무제표 계정 조회 |
| `get_multi_company_account` | 다중 회사 주요 재무제표 계정 조회 |
| `get_xbrl_financial` | XBRL 재무제표 원본 조회 |
| `get_single_full_financial` | 단일 회사 전체 재무제표 조회 |
| `get_xbrl_taxonomy` | XBRL 표준 재무제표 양식 조회 |
| `get_single_financial_index` | 단일 회사 주요 재무지표 조회 |
| `get_multi_financial_index` | 다중 회사 주요 재무지표 조회 |

</details>

### DS004 · 지분공시 (2)

<details>
<summary>목록 펼치기</summary>

| Tool | Description |
|------|-------------|
| `get_large_holding_report` | 5% 이상 대량보유 현황 |
| `get_executive_stock_report` | 임원 및 주요주주 소유보고 |

</details>

### DS005 · 주요사항보고서 (36)

<details>
<summary>목록 펼치기</summary>

| Tool | Description |
|------|-------------|
| `get_paid_capital_increase` | 유상증자 결정 |
| `get_free_capital_increase` | 무상증자 결정 |
| `get_paid_free_capital_increase` | 유무상증자 결정 |
| `get_capital_reduction` | 감자 결정 |
| `get_convertible_bond` | 전환사채권 발행결정 |
| `get_bond_with_warrants` | 신주인수권부사채권 발행결정 |
| `get_exchangeable_bond` | 교환사채권 발행결정 |
| `get_conditional_capital_issuance` | 상각형 조건부자본증권 발행결정 |
| `get_stock_acquisition` | 자기주식 취득 결정 |
| `get_stock_disposal` | 자기주식 처분 결정 |
| `get_treasury_stock_trust_conclude` | 자기주식취득 신탁계약 체결 결정 |
| `get_treasury_stock_trust_terminate` | 자기주식취득 신탁계약 해지 결정 |
| `get_merger_decision` | 회사합병 결정 |
| `get_division_decision` | 회사분할 결정 |
| `get_division_merger_decision` | 회사분할합병 결정 |
| `get_stock_exchange_decision` | 주식교환·이전 결정 |
| `get_business_acquisition` | 영업양수 결정 |
| `get_business_transfer` | 영업양도 결정 |
| `get_tangible_asset_acquisition` | 유형자산 양수 결정 |
| `get_tangible_asset_transfer` | 유형자산 양도 결정 |
| `get_equity_investment_acquisition` | 타법인 주식 및 출자증권 양수결정 |
| `get_equity_investment_transfer` | 타법인 주식 및 출자증권 양도결정 |
| `get_equity_securities_acquisition` | 주권 관련 사채권 양수 결정 |
| `get_equity_securities_transfer` | 주권 관련 사채권 양도 결정 |
| `get_other_asset_acquisition` | 자산양수도(기타), 풋백옵션 |
| `get_overseas_listing_decision` | 해외 증권시장 상장 결정 |
| `get_overseas_delisting_decision` | 해외 증권시장 상장폐지 결정 |
| `get_overseas_listing` | 해외 증권시장 상장 |
| `get_overseas_delisting` | 해외 증권시장 상장폐지 |
| `get_bankruptcy_report` | 부도발생 |
| `get_business_suspension_report` | 영업정지 |
| `get_rehabilitation_report` | 회생절차 개시신청 |
| `get_dissolution_report` | 해산사유 발생 |
| `get_creditor_management` | 채권은행 등의 관리절차 개시 |
| `get_creditor_management_suspension` | 채권은행 등의 관리절차 중단 |
| `get_lawsuit_report` | 소송 등의 제기 |

</details>

### DS006 · 증권신고서 (6)

<details>
<summary>목록 펼치기</summary>

| Tool | Description |
|------|-------------|
| `get_equity_securities` | 지분증권 증권신고서 |
| `get_debt_securities` | 채무증권(회사채) 증권신고서 |
| `get_depositary_receipts` | 증권예탁증권(DR) 증권신고서 |
| `get_merger_securities` | 합병 관련 증권신고서 |
| `get_stock_exchange_securities` | 주식 포괄적 교환·이전 증권신고서 |
| `get_division_securities` | 분할 관련 증권신고서 |

</details>

---

## 주의사항

- **API 일일 호출 한도**: 10,000건 (초과 시 오류 발생)
- `opendart-excel` 스킬은 검증에 실패한 Excel 파일은 전달하지 않습니다.

---

<details>
<summary><b>부록: MCP 서버만 단독 설치</b> (Claude Code/Codex 플러그인 없이, 스킬 없이 도구만 필요한 경우)</summary>

플러그인 내부에서 쓰이는 MCP 서버 본체는 PyPI 패키지 `opendart-mcp-server`로 별도 배포됩니다. Claude Code/Codex가 아닌 다른 MCP 클라이언트(Claude Desktop 등)에서 85개 도구만 쓰고 싶다면 아래처럼 단독 설치할 수 있습니다.

**패키지 설치**

```bash
pip install opendart-mcp-server
# 또는
uv tool install opendart-mcp-server
```

설치 후 `opendartmcp` 명령을 사용합니다.

**uvx로 바로 실행 (설치 없이)**

```bash
uvx --from opendart-mcp-server opendartmcp
```

**API 키 설정**

```bash
# 1) CLI로 등록 (로컬 환경 권장)
opendartmcp config set-api-key
opendartmcp config show
opendartmcp config test
opendartmcp config clear-api-key
```

패키지를 설치하지 않았다면 각 명령 앞에 `uvx --from opendart-mcp-server`를 붙이세요.

```bash
# 2) 환경 변수로 설정 (MCP 클라이언트 설정, Docker, CI 환경)
DART_API_KEY=your-api-key-here
```

> CLI로 등록한 키와 `DART_API_KEY`가 모두 있으면 환경 변수 값이 우선 적용됩니다.

**MCP 클라이언트 설정**

```json
{
  "mcpServers": {
    "open-dart": {
      "command": "uvx",
      "args": ["--from", "opendart-mcp-server", "opendartmcp"],
      "env": {
        "DART_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

패키지를 설치했다면 `command`를 `opendartmcp` 하나로 바꿔도 됩니다.

</details>


