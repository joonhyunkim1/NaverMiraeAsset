# 주식 시장 RAG 시스템

## 서비스 소개

이 프로젝트는 주식 시장 데이터와 뉴스를 수집하여 AI 기반 분석 보고서를 자동으로 생성하는 RAG(Retrieval-Augmented Generation) 시스템입니다.

### 주요 기능
- **데이터 수집**: KRX 일일거래정보 및 네이버 뉴스 자동 수집
- **AI 분석**: CLOVA AI를 활용한 주목 종목 추출 및 분석
- **벡터 검색**: FAISS를 이용한 고성능 벡터 데이터베이스
- **자동 보고서**: 일일 증시 분석 보고서 자동 생성

## 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd MiraeassetNaver/RAG/code
```

### 2. 가상환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
# env_template.txt를 참고하여 .env 파일 생성
cp env_template.txt .env

# .env 파일을 열어서 API 키들을 입력
# - CLOVA_API_KEY
# - CLOVA_EMBEDDING_REQUEST_ID
# - CLOVA_CHAT_REQUEST_ID
# - NAVER_CLIENT_ID
# - NAVER_CLIENT_SECRET
# - CLOVA_SEGMENTATION_REQUEST_ID
# - NEW_CLOVA_API_KEY
# - NEW_CLOVA_REQUEST_ID
# - NEW_CLOVA_MODEL_ENDPOINT
```

### 5. 시스템 실행
```bash
python main.py
```

## 프로젝트 구조

```text
RAG/
├── code/                    # 메인 코드
│   ├── main.py             # 시스템 실행 파일
│   ├── requirements.txt    # 의존성 패키지
│   ├── env_template.txt    # 환경변수 템플릿
│   └── ...                 # 기타 모듈들
├── data_1/                 # 수집된 데이터
├── vector_db_1/           # 벡터 데이터베이스
└── daily_report/          # 생성된 보고서
```

## 실행 과정

1. **데이터 수집**: KRX 거래정보 및 네이버 뉴스 수집
2. **AI 분석**: CLOVA AI를 통한 주목 종목 추출
3. **벡터 저장**: 수집된 데이터를 벡터로 변환하여 저장
4. **보고서 생성**: 일일 증시 분석 보고서 자동 생성

## ⚠️ 주의사항

- CLOVA API 키와 네이버 API 키가 필요합니다
- 안정적인 인터넷 연결이 필요합니다
- 첫 실행 시 데이터 수집에 시간이 걸릴 수 있습니다

## 문제 해결

- **API 키 오류**: `.env` 파일의 API 키가 올바른지 확인
- **포트 충돌**: 8000, 8001 포트가 사용 중인지 확인
- **메모리 부족**: 벡터 데이터베이스 용량을 확인
