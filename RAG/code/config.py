import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG")

# 데이터 디렉토리
DATA_DIR = PROJECT_ROOT / "/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data"

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
