# KRX API 설정 파일
# 이 파일에 API 키와 기타 설정을 입력하세요

# KRX API 키 (필요한 경우)
KRX_API_KEY = "030F222D0C2848DAB90417BA8B3CFB5FEFB5BD4E"

# API 기본 설정
API_BASE_URL = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"

# 요청 헤더 설정
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'http://data.krx.co.kr',
    'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101'
}

# 환경 변수에서 API 키를 가져오는 함수
def get_api_key():
    """환경 변수에서 API 키를 가져옵니다."""
    import os
    return os.getenv('KRX_API_KEY', KRX_API_KEY) 