import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 현재 스크립트 위치를 기준으로 상대 경로 설정
current_dir = Path(__file__).parent
PROJECT_ROOT = current_dir.parent

# 데이터 디렉토리
DATA_DIR = PROJECT_ROOT / "data"

# 모델 설정
MODEL_NAME = "MLP-KTLim/llama-3-Korean-Bllossom-8B"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# 벡터 데이터베이스 설정
VECTOR_DB_PATH = PROJECT_ROOT / "vector_db"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# RAG 설정
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.7

# API 키 설정 (환경변수에서 로드)
# TODO: .env 파일에 다음 키들을 추가하세요:
# CLOVA_API_KEY=your_clova_api_key_here
# CLOVA_REQUEST_ID=your_request_id_here

def get_clova_api_key():
    """CLOVA API 키를 반환합니다."""
    return os.getenv("CLOVA_API_KEY", "")

def get_clova_embedding_request_id():
    """CLOVA Embedding Request ID를 반환합니다."""
    return os.getenv("CLOVA_EMBEDDING_REQUEST_ID", "")

def get_clova_chat_request_id():
    """CLOVA Chat Request ID를 반환합니다."""
    return os.getenv("CLOVA_CHAT_REQUEST_ID", "")

def get_clova_segmentation_request_id():
    """CLOVA Segmentation Request ID를 반환합니다."""
    return os.getenv("CLOVA_SEGMENTATION_REQUEST_ID", "")

def get_clova_segmentation_app_id():
    """CLOVA Segmentation App ID를 반환합니다."""
    return os.getenv("CLOVA_SEGMENTATION_APP_ID", "")

# Hugging Face API 키 (임베딩 모델용)
def get_huggingface_api_key():
    """Hugging Face API 키를 반환합니다."""
    return os.getenv("HUGGINGFACE_API_KEY", "")

# 네이버 뉴스 검색 API 키
def get_naver_client_id():
    """네이버 클라이언트 ID를 반환합니다."""
    return os.getenv("NAVER_CLIENT_ID", "")

def get_naver_client_secret():
    """네이버 클라이언트 시크릿을 반환합니다."""
    return os.getenv("NAVER_CLIENT_SECRET", "")

# KRX API 설정
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

def get_api_key():
    """환경 변수에서 API 키를 가져옵니다."""
    return os.getenv('KRX_API_KEY', KRX_API_KEY)
