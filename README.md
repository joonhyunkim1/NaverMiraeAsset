# 🟠 코스피 7000간다 – 주식 시장 RAG 시스템

## 🧾 서비스 소개
- 전일 **KRX 일일 거래 데이터**와 **최근 24시간 뉴스**를 수집·정제하고, **LlamaIndex + CLOVA Segmentation/Embedding**으로 벡터 DB(`vector_db`, `vector_db_1`)를 구성한 뒤, **HCX-005**로 **전일 시장 요약** 및 **오늘 주목 종목 분석**을 생성하여 **일일 증시 보고서**로 저장하는 시스템입니다.
- 최종 결과물은 `daily_report/`에, 중간 산출물은 `data_2/`에 저장됩니다.
---

## 🗂️ 프로젝트 구조
    RAG/
    ├── code/                 #메인 코드
    │   └── main.py           #시스템 실행 파일
    │   └── requirements.txt  #의존성 패키지  
    │   └── env_template.txt  #환경변수 템플릿
    │   └──...                #기타 모듈들
    ├── data_1                #수집된 데이터   
    ├── vector_db_1           #벡터 데이터베이스
    ├── ...                   #기타 리소스
    └── daily_report          #생성된 보고서
    

---

## 🔄 실행 흐름

### 1. **데이터 수집 (개장 전)**
- **KRX 전 종목 일일 거래 데이터**를 수집해 **CSV**로 저장.
- **네이버 뉴스(최근 1일)**를 수집해 **JSON**으로 저장.
- 콘솔에 **수집 결과 요약** 형태로 KRX/뉴스 수집 성공 여부를 출력.
<br><br>
### 2. **전일 데이터 인덱싱 → `vector_db` 구축**
- 전일 KRX·뉴스 데이터(**CSV/JSON**)를 불러와 텍스트로 정규화.
- **Segmentation**으로 문단 분리 → **Embedding**으로 벡터화.
- 벡터 스토어에 저장하여 `vector_db` 생성.
<br><br>
### 3. **이슈 종목 후보 추출 (HCX-005)**
- `vector_db`에서 유사도 검색 결과를 바탕으로 **이슈 종목 3개** 후보를 도출(근거 포함).
<br><br>
### 4. **개별 종목 데이터 수집 → `data_1`**
- 후보 **종목별 거래 데이터**(시가/고가/저가/종가/거래량/등락률 등)를 수집해 **CSV**로 저장.
- 후보 **종목별 뉴스**를 각 종목명으로 재수집해 **JSON**으로 저장.
- 산출물은 `data_1`에 정리.
<br><br>
### 5. **개별 종목 인덱싱 → `vector_db_1` 구축**
- **`data_1/`**의 종목별 **CSV/JSON**을 통합하여 텍스트로 정규화.
- **Segmentation → Embedding**을 거쳐 벡터화하고 `vector_db_1`에 저장.
<br><br>
### 6. **분석/생성 – 두 갈래 보고서 만들기 → `data_2`**
- **전일 시장 요약(전체 시장)**: `vector_db`를 검색해 HCX-005로 리포트를 생성하고 `data_2/vector_db_report_YYYYMMDD_HHMMSS.txt`로 저장.
- **주목 종목 심화 분석(개별 종목)**: 후보 종목명을 `vector_db_1` 분석에 전달하여 리포트를 생성하고 `data_2/vector_db_1_report_YYYYMMDD_HHMMSS.txt`로 저장.
<br><br>
### 7. **최종 합치기 → `daily_report/`**
- `data_2`에서 최신 `vector_db_report_*.txt`와 `vector_db_1_report_*.txt`를 읽어 **최종 보고서**로 결합.
- 머리말(제목/생성일시) + 구획선과 함께 다음 두 섹션을 포함:
  - **📊 어제 하루 주식 시장 분석** (전일 시장 요약)
  - **📈 오늘 이슈가 있을 것으로 예상되는 주목 종목 분석** (종목 심화)
- 결과물을 `daily_report/daily_combined_report_YYYYMMDD_HHMMSS.txt`로 저장.
<br><br>
---


## 🧩 시스템 구조도 (FLOW)
<img width="400" height="600" alt="image" src="https://github.com/user-attachments/assets/6743f2b3-42d5-4fc7-8756-8cf2d673ac14" />

---

## ⚙️ 설치 및 실행

### 1. 프로젝트 클론
    git clone <repository-url>
    cd MiraeassetNaver/RAG/code

### 2. 가상환경 설정
    # 가상환경 생성
    python -m venv venv

    # 가상환경 활성화 (macOS/Linux)
    source venv/bin/activate

    # 가상환경 활성화 (Windows)
    venv\Scripts\activate

### 3. 의존성 설치
    pip install -r requirements.txt

### 4. 환경 변수 설정
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

### 5. 시스템 실행
    python main.py

---

## 📦 결과물 예시(형식)
        # 일일 주식 시장 종합 분석 보고서
        생성일시: YYYY-MM-DD HH:MM:SS
        ================================================================
        ## 📊 어제 하루 주식 시장 분석
        ... (vector_db 기반 요약)
        ================================================================
        ## 📈 오늘 이슈가 있을 것으로 예상되는 주목 종목 분석
        ... (vector_db_1 기반 분석)

---
## 📰 결과물 예시(보고서)
<img width="600" height="400" alt="image" src="https://github.com/user-attachments/assets/86cc0fa2-fabb-4393-bd17-c55002eddf79" />
<img width="600" height="400" alt="image" src="https://github.com/user-attachments/assets/5638f8ed-47a6-40d0-9137-ec8704ca42f3" />


        
