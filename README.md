# OpenDART MCP Server

[![PyPI version](https://img.shields.io/pypi/v/opendart-mcp-server)](https://pypi.org/project/opendart-mcp-server/)
[![Python](https://img.shields.io/pypi/pyversions/opendart-mcp-server)](https://pypi.org/project/opendart-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[OpenDART API](https://opendart.fss.or.kr)를 MCP 클라이언트에서 사용할 수 있게 해주는 서버입니다.
기업 공시, 재무제표, 주주 현황 등 금융감독원 전자공시 데이터를 자연어로 조회할 수 있습니다.

DS001부터 DS006까지 6개 API 그룹의 **85개 도구**를 제공합니다.

---

## 요구 사항

- Python 3.11+
- OpenDART API 키: [OpenDART](https://opendart.fss.or.kr)에서 발급

---

## 설치

패키지를 설치하거나 `uvx`로 바로 실행할 수 있습니다.

### 방법 1. 패키지 설치

```bash
pip install opendart-mcp-server
# 또는
uv tool install opendart-mcp-server
```

설치 후에는 `opendartmcp` 명령을 사용합니다.

### 방법 2. uvx로 바로 실행

```bash
uvx --from opendart-mcp-server opendartmcp
```

설치하지 않고 CLI 하위 명령을 실행할 때도 같은 접두사를 사용합니다.

```bash
uvx --from opendart-mcp-server opendartmcp <command>
```

---

## API 키 설정

아래 방법 중 하나를 선택하세요. 일반적인 로컬 환경에서는 CLI 등록 방식을 권장합니다.

### 방법 1. CLI로 등록

```bash
opendartmcp config set-api-key
```

입력한 API 키는 화면에 표시되지 않습니다. 등록 상태 확인, 인증 테스트, 삭제도 CLI에서 처리할 수 있습니다.

```bash
opendartmcp config show
opendartmcp config test
opendartmcp config clear-api-key
```

패키지를 설치하지 않았다면 각 명령 앞에 `uvx --from opendart-mcp-server`를 붙이세요.

### 방법 2. 환경 변수로 설정

MCP 클라이언트 설정, Docker, CI 환경에서는 `DART_API_KEY` 환경 변수를 사용할 수 있습니다.

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

> CLI로 등록한 키와 `DART_API_KEY`가 모두 있으면 환경 변수 값이 우선 적용됩니다.

---

## MCP 설정

사용 중인 MCP 클라이언트의 설정 파일에 아래 내용을 추가하세요.

### 패키지를 설치한 경우

```json
{
  "mcpServers": {
    "open-dart": {
      "command": "opendartmcp"
    }
  }
}
```

### uvx로 바로 실행하는 경우

```json
{
  "mcpServers": {
    "open-dart": {
      "command": "uvx",
      "args": ["--from", "opendart-mcp-server", "opendartmcp"]
    }
  }
}
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
```

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

---

## 라이선스

MIT
