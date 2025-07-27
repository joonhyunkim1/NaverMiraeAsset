# 📈 FinanceDataReader 기반 주식 데이터 수집 시스템

CLOVA Function Calling을 통한 지능형 주식 데이터 수집 및 분석 시스템입니다.

## 🚀 주요 기능

- **지능형 종목 검색**: 종목명 또는 종목코드로 자동 검색
- **CLOVA Function Calling**: 자연어로 주식 데이터 요청
- **자동 CSV 저장**: 수집된 데이터를 자동으로 CSV 파일로 저장
- **데이터 수집**: Open, High, Low, Close, Volume 데이터 자동 수집
- **기본값 설정**: 기간 미지정 시 최근 2년간 데이터 자동 수집

## 📋 요구사항

### Python 패키지
```bash
pip install finance-datareader pandas requests python-dateutil
```

### CLOVA API 설정
- CLOVA API 키 필요
- Function Calling 지원 모델 사용

## 🛠️ 설치 및 설정

1. **저장소 클론**
```bash
git clone <repository-url>
cd stock-data-collector
```

2. **가상환경 생성 및 활성화**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **CLOVA API 키 설정**
```python
# stock_data_collector.py 파일에서 API_KEY 수정
API_KEY = "your_clova_api_key_here"
```

## 📖 사용법

### 1. 기본 실행
```bash
python stock_data_collector.py
```

### 2. 대화형 모드
```
📥 종목명 또는 종목코드를 입력하세요: 삼성전자
```

### 3. 다양한 요청 예시
```
사용자: "삼성전자 주가 데이터를 가져와줘"
사용자: "005930 2024년 데이터"
사용자: "SK하이닉스 최근 1년간 주가"
사용자: "삼성전자 2023년 1월부터 12월까지"
```

## 📊 데이터 형식

### 수집되는 데이터
- **Date**: 거래일
- **Open**: 시가
- **High**: 고가
- **Low**: 저가
- **Close**: 종가
- **Volume**: 거래량

### CSV 파일명 형식
```
{종목명}_{종목코드}_{시작일}_{종료일}_{타임스탬프}.csv
예: 삼성전자_005930_2024-01-01_2024-12-31_20250127_143022.csv
```

## 🗂️ 파일 구조

```
stock-data-collector/
├── stock_data_collector.py    # 메인 시스템
├── test_stock_collector.py    # 테스트 스크립트
├── README.md                  # 이 파일
├── requirements.txt           # 의존성 목록
└── data/                     # 수집된 데이터 저장소
    └── *.csv                 # CSV 파일들
```

## 🧪 테스트

### 테스트 실행
```bash
python test_stock_collector.py
```

### 테스트 항목
- 종목코드 변환 테스트
- 데이터 수집 테스트
- CSV 파일 저장 테스트
- 결과 포맷팅 테스트

## 🔧 Function Calling 정의

```json
{
  "name": "get_stock_data",
  "description": "특정 종목의 주가 데이터를 조회하여 CSV 파일로 저장합니다.",
  "parameters": {
    "ticker": "종목코드 또는 종목명 (필수)",
    "start_date": "조회 시작 날짜 (YYYY-MM-DD, 선택)",
    "end_date": "조회 종료 날짜 (YYYY-MM-DD, 선택)",

  }
}
```

## 📈 데이터 수집 기능

### 수집되는 데이터
- **Date**: 거래일
- **Open**: 시가
- **High**: 고가
- **Low**: 저가
- **Close**: 종가
- **Volume**: 거래량

### 데이터 요약 정보
- **가격 변동**: 기간 내 가격 변화율
- **거래량 분석**: 평균 거래량, 총 거래량
- **가격 범위**: 최고가, 최저가

## 🎯 사용 예시

### 1. 기본 사용 (2년간 데이터)
```
사용자: "삼성전자"
→ 자동으로 최근 2년간 데이터 수집
```

### 2. 특정 기간 지정
```
사용자: "삼성전자 2024년 데이터"
→ 2024-01-01 ~ 2024-12-31 데이터 수집
```

### 3. 종목코드 사용
```
사용자: "005930"
→ 삼성전자 종목코드로 데이터 수집
```

## 🔍 FinanceDataReader 정보

- **GitHub**: https://github.com/financedata-org/FinanceDataReader
- **문서**: https://financedata.github.io/posts/FinanceDataReader.html
- **지원 시장**: 한국(KRX), 미국, 일본, 중국 등

## ⚠️ 주의사항

1. **API 제한**: CLOVA API 호출 제한이 있을 수 있습니다
2. **데이터 지연**: 실시간 데이터가 아닌 종가 기준 데이터입니다
3. **휴장일**: 주말 및 공휴일에는 거래 데이터가 없습니다
4. **파일 저장**: 데이터는 지정된 경로에 자동 저장됩니다

## 🐛 문제 해결

### 일반적인 오류

1. **종목코드 찾을 수 없음**
   - 종목명 철자 확인
   - 정확한 종목코드 사용

2. **API 오류**
   - CLOVA API 키 확인
   - 네트워크 연결 상태 확인

3. **데이터 없음**
   - 조회 기간 확인
   - 휴장일 여부 확인

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. Python 버전 (3.7 이상 권장)
2. 필요한 패키지 설치 여부
3. CLOVA API 키 설정
4. 네트워크 연결 상태

## 📄 라이선스

MIT License

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요. 