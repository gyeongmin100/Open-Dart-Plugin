class DartApiError(Exception):
    ERROR_CODES = {
        "010": "미등록 인증키",
        "011": "사용할 수 없는 인증키",
        "012": "접근할 수 없는 IP",
        "013": "조회된 데이터가 없습니다",
        "014": "파일이 존재하지 않습니다",
        "020": "요청 제한을 초과하였습니다",
        "021": "조회 가능한 회사 개수가 초과하였습니다(최대 100건)",
        "100": "필드 오류",
        "101": "부적절한 접근",
        "800": "시스템 점검으로 인한 서비스가 중지 중",
        "900": "정의되지 않은 오류",
        "901": "사용자 계정의 개인정보 보유기간 만료",
    }

    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message
        desc = self.ERROR_CODES.get(status, "알 수 없는 오류")
        super().__init__(f"[{status}] {desc}: {message}")
