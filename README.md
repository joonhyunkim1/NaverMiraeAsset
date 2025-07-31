# 뉴스 및 주가 데이터에 기반한 일일 증시 보고서 작성 서비스

## 🚀 주요 기능

### 📊 데이터 수집 및 처리
- **KRX 일일거래정보 수집**: 국내 주식 시장의 일일 거래 데이터 자동 수집
- **네이버 뉴스 수집**: "국내 주식 주가" 키워드 기반 최신 뉴스 수집
- **주식 종목 추출**: CLOVA Function Calling을 통한 주목 종목 자동 추출
- **개별 종목 데이터 수집**: 추출된 종목들의 상세 주가 데이터 수집
- **개별 종목 뉴스 수집**: 추출된 종목들의 관련 뉴스 수집

### 🔍 벡터 데이터베이스 관리
- **Vector DB**: 전체 시장 데이터 기반 벡터 저장소
- **Vector DB1**: 개별 종목 상세 데이터 기반 벡터 저장소
- **CLOVA 임베딩**: 1024차원 벡터로 텍스트 임베딩
- **CLOVA 세그멘테이션**: 모델 최적화된 텍스트 청킹

### 📈 분석 및 보고서 생성
- **Vector DB 분석**: "어제 하루 뉴스 및 일일 거래데이터 이슈 요약"
- **Vector DB1 분석**: "오늘 이슈가 있을 것으로 예상되는 주목 종목 분석"
- **통합 보고서**: 두 분석 결과를 하나의 보고서로 결합
- **자동 폴더 생성**: 필요한 모든 폴더 자동 생성

### 🔧 API 서버
- **FAISS API 서버**: Vector DB 검색 API (포트 8000)
- **Vector DB1 API 서버**: Vector DB1 검색 API (포트 8001)

## 📁 프로젝트 구조

```
RAG/
├── code/
│   ├── main.py                    # 메인 실행 파일
│   ├── config.py                  # 설정 파일
│   ├── requirements.txt           # 의존성 패키지
│   ├── krx_api_client.py         # KRX API 클라이언트
│   ├── naver_news_client.py      # 네이버 뉴스 클라이언트
│   ├── stock_extractor.py        # 주식 종목 추출
│   ├── stock_data_collector.py   # 주식 데이터 수집
│   ├── stock_news_collector.py   # 주식 뉴스 수집
│   ├── hybrid_vector_manager.py  # 벡터 데이터 관리
│   ├── faiss_vector_api.py       # FAISS API 서버
│   ├── faiss_vector_db1_api.py   # Vector DB1 API 서버
│   ├── vector_db_1_analyzer.py   # Vector DB1 분석
│   └── rag_components.py         # RAG 컴포넌트
├── data/                         # 전체 시장 데이터
├── data_1/                       # 개별 종목 데이터
├── data_2/                       # 분석 결과 데이터
├── vector_db/                    # Vector DB 저장소
├── vector_db_1/                  # Vector DB1 저장소
└── daily_report/                 # 일일 보고서
```

## 🛠️ 설치 및 설정

### 1. 환경 설정

```bash
# 프로젝트 클론
git clone <repository-url>
cd MiraeassetNaver/RAG/code

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```env
# CLOVA API 설정
CLOVA_API_KEY=your_clova_api_key
CLOVA_REQUEST_ID=your_request_id
CLOVA_HOST=https://api.clovastudio.com

# Vector DB1 분석용 CLOVA 설정
VECTOR_DB1_CLOVA_API_KEY=your_vector_db1_api_key
VECTOR_DB1_CLOVA_REQUEST_ID=your_vector_db1_request_id
VECTOR_DB1_CLOVA_MODEL_ENDPOINT=/v3/tasks/yl1fvofj/chat-completions

# 데이터 수집 설정
ENABLE_DATA_COLLECTION=true
```

## 🚀 사용법

### 기본 실행

```bash
python main.py
```

### 실행 과정

1. **데이터 수집** (KRX + 네이버 뉴스)
2. **Vector DB 임베딩** (전체 시장 데이터)
3. **주식 종목 추출** (CLOVA Function Calling)
4. **개별 종목 데이터 수집** (추출된 종목들)
5. **Vector DB1 임베딩** (개별 종목 데이터)
6. **FAISS API 서버 시작** (포트 8000, 8001)
7. **Vector DB 분석** (어제 하루 이슈 요약)
8. **Vector DB1 분석** (오늘 주목 종목 분석)
9. **보고서 합치기** (통합 일일 보고서)

### 출력 파일

- `data/`: KRX 일일거래정보, 네이버 뉴스 데이터
- `data_1/`: 개별 종목 주가 데이터, 종목별 뉴스
- `vector_db/`: 전체 시장 벡터 데이터
- `vector_db_1/`: 개별 종목 벡터 데이터
- `daily_report/`: 통합 일일 보고서

## 📋 주요 클래스

### StockMarketRAGSystem
메인 시스템 클래스로 전체 파이프라인을 관리합니다.

#### 주요 메서드:
- `collect_data()`: KRX 및 네이버 뉴스 데이터 수집
- `embed_data()`: Vector DB 및 Vector DB1 임베딩
- `start_faiss_api_server()`: FAISS API 서버 시작
- `start_vector_db1_api_server()`: Vector DB1 API 서버 시작
- `analyze_vector_db()`: Vector DB 기반 분석
- `analyze_vector_db1()`: Vector DB1 기반 분석
- `combine_reports()`: 보고서 합치기

## 🔧 API 서버

### FAISS API 서버 (포트 8000)
```bash
# 서버 시작
python faiss_vector_api.py

# API 엔드포인트
GET  /health                    # 서버 상태 확인
POST /search                    # 벡터 검색
```

### Vector DB1 API 서버 (포트 8001)
```bash
# 서버 시작
python faiss_vector_db1_api.py

# API 엔드포인트
GET  /health                    # 서버 상태 확인
POST /search                    # 벡터 검색
```

## 📊 데이터 흐름

```
1. 데이터 수집
   ├── KRX 일일거래정보 → data/
   └── 네이버 뉴스 → data/

2. Vector DB 임베딩
   └── data/ → vector_db/

3. 주식 종목 추출
   └── Vector DB 분석 → 종목명 리스트

4. 개별 종목 데이터 수집
   ├── 주가 데이터 → data_1/
   └── 종목별 뉴스 → data_1/

5. Vector DB1 임베딩
   └── data_1/ → vector_db_1/

6. 분석 및 보고서 생성
   ├── Vector DB 분석 → 일일 이슈 요약
   ├── Vector DB1 분석 → 주목 종목 분석
   └── 보고서 합치기 → daily_report/
```

## ⚠️ 주의사항

1. **API 키 관리**: CLOVA API 키는 안전하게 관리하세요
2. **네트워크 연결**: 데이터 수집 시 안정적인 인터넷 연결이 필요합니다
3. **디스크 공간**: 벡터 데이터베이스는 상당한 용량을 사용할 수 있습니다
4. **API 제한**: CLOVA API 호출 제한을 고려하여 사용하세요

## 🐛 문제 해결

### 일반적인 오류

1. **"CSV 파일을 찾을 수 없습니다"**
   - `data/` 또는 `data_1/` 폴더에 데이터가 있는지 확인
   - 데이터 수집이 성공했는지 확인

2. **"FAISS API 서버 시작 실패"**
   - 포트 8000, 8001이 사용 중인지 확인
   - 기존 서버 프로세스를 종료 후 재시작

3. **"주식 종목 추출 실패"**
   - CLOVA API 키와 요청 ID가 올바른지 확인
   - 네트워크 연결 상태 확인

### 로그 확인

실행 중 상세한 로그가 출력되므로 각 단계별 진행 상황을 확인할 수 있습니다.
