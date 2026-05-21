# Open DART MCP

금융감독원 전자공시(DART) 데이터를 Claude에서 직접 조회할 수 있는 MCP(Model Context Protocol) 서버입니다.

## 프로젝트 소개

Open DART MCP 서버는 금융감독원의 [전자공시시스템(DART)](https://opendart.fss.or.kr) Open API를 MCP 프로토콜로 감싸, Claude Desktop 또는 MCP 호환 클라이언트에서 국내 상장기업의 공시정보, 재무제표, 지분현황 등을 자연어로 조회할 수 있게 합니다.

## 사전 요구사항

- Python 3.11 이상
- [uv](https://github.com/astral-sh/uv) (권장) 또는 pip
- Open DART API 키
  - [https://opendart.fss.or.kr](https://opendart.fss.or.kr) 에서 회원가입 후 API 키 발급
  - 마이페이지 > OpenAPI 이용현황 > 인증키 신청/관리

## 설치 방법

```bash
git clone https://github.com/your-username/opendartmcp.git
cd opendartmcp
pip install -e .
```

uv 사용 시:

```bash
git clone https://github.com/your-username/opendartmcp.git
cd opendartmcp
uv sync
```

## Claude Desktop 설정

### macOS

설정 파일 위치: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows

설정 파일 위치: `%APPDATA%\Claude\claude_desktop_config.json`

### python 사용 시

```json
{
  "mcpServers": {
    "open-dart": {
      "command": "python",
      "args": ["-m", "opendartmcp.server"],
      "env": {
        "DART_API_KEY": "여기에_API_키_입력"
      }
    }
  }
}
```

### uv 사용 시

```json
{
  "mcpServers": {
    "open-dart": {
      "command": "uv",
      "args": ["run", "--directory", "/절대경로/opendartmcp", "opendartmcp"],
      "env": {
        "DART_API_KEY": "여기에_API_키_입력"
      }
    }
  }
}
```

## 제공하는 툴 목록

총 **84개** 툴을 6개 그룹으로 제공합니다.

### DS001 공시정보 (4개)

| 툴 | 설명 |
|---|---|
| `search_disclosures` | 기업명 또는 법인코드로 공시 목록 검색 |
| `get_company_info` | 기업 기본정보 조회 |
| `get_disclosure_document` | 공시 원문 문서 조회 |
| `get_corp_codes` | 전체 법인코드 목록 다운로드 |

### DS002 정기보고서 주요정보 (29개)

배당, 임원, 직원, 보수, 감사, 최대주주, 자기주식, 배당, 회계감사 등 사업보고서 핵심 항목을 개별 툴로 제공합니다.

### DS003 재무정보 (7개)

| 툴 | 설명 |
|---|---|
| `get_financial_statements` | 단일 회사 재무제표 조회 |
| `get_multi_company_financials` | 다중 회사 재무제표 조회 |
| `get_xbrl_taxonomy` | XBRL 재무제표 양식 조회 |
| `get_xbrl_financial_statements` | XBRL 단일 회사 재무제표 |
| `get_financial_indicators` | 단일 회사 주요 재무지표 |
| `get_multi_company_indicators` | 다중 회사 주요 재무지표 |
| `get_full_xbrl` | 전체 XBRL 데이터 조회 |

### DS004 지분공시 (2개)

| 툴 | 설명 |
|---|---|
| `get_major_shareholders` | 5% 이상 대량보유 현황 |
| `get_executive_shareholders` | 임원 및 주요주주 소유보고 |

### DS005 주요사항보고서 (36개)

유상증자, 무상증자, 감자, 합병, 분할, 주식교환, 영업양수도, 자산양수도, 부도, 영업정지, 해산 등 주요 기업 이벤트 항목을 개별 툴로 제공합니다.

### DS006 증권신고서 (6개)

| 툴 | 설명 |
|---|---|
| `get_equity_securities` | 지분증권 신고서 |
| `get_debt_securities` | 채무증권 신고서 |
| `get_merger_securities` | 합병 관련 신고서 |
| `get_split_securities` | 분할 관련 신고서 |
| `get_equity_offer` | 지분증권 청약 현황 |
| `get_debt_offer` | 채무증권 청약 현황 |

## 사용 예시

Claude Desktop에서 다음과 같이 질문할 수 있습니다:

- "삼성전자 최근 공시 보여줘"
- "카카오 2023년 재무제표 알려줘"
- "현대자동차 최대주주 현황은?"
- "LG전자 임원 현황 조회해줘"
- "SK하이닉스 배당 이력 알려줘"
- "2024년 합병 공시 목록 검색해줘"

## 주의사항

- **API 일일 호출 한도**: 10,000건 (초과 시 오류 발생)
- **법인코드(`corp_code`)**: 기업명이 아닌 8자리 고유 코드. `get_corp_codes` 툴로 조회하거나 `search_disclosures`에서 반환된 값을 사용합니다.
- API 키는 환경변수 `DART_API_KEY`로 전달해야 하며, 코드에 직접 입력하지 마십시오.
