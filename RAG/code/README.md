# 주식 시장 분석 RAG 시스템

AI 기반 주식 시장 분석 및 보고서 생성 시스템입니다.

## 주요 기능

- **데이터 수집**: KRX 일일거래정보, 네이버 뉴스 수집
- **벡터 검색**: FAISS를 이용한 유사도 기반 검색
- **AI 분석**: CLOVA API를 이용한 주식 시장 분석
- **보고서 생성**: 일일 주식 시장 종합 분석 보고서
- **이메일 발송**: Naver Cloud Outbound Mailer를 이용한 자동 이메일 발송

## 환경 설정

### 1. 기본 환경 변수

`.env` 파일에 다음 변수들을 설정하세요:

```bash
# CLOVA API 설정
CLOVA_API_KEY=your_clova_api_key
CLOVA_REQUEST_ID=your_request_id
CLOVA_MODEL_ENDPOINT=/v3/chat-completions/HCX-005

# 새로운 CLOVA API 설정 (vector_db_1_analyzer용)
NEW_CLOVA_API_KEY=your_new_clova_api_key
NEW_CLOVA_REQUEST_ID=4997d0ab4e434139bd982084de885077
NEW_CLOVA_MODEL_ENDPOINT=/v3/tasks/yl1fvofj/chat-completions

# 네이버 API 설정
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret

# Naver Cloud Outbound Mailer API 설정
NAVER_CLOUD_ACCESS_KEY=your_access_key_here
NAVER_CLOUD_SECRET_KEY=your_secret_key_here
NAVER_CLOUD_MAIL_ENDPOINT=https://mail.apigw.ntruss.com/api/v1

# 이메일 발송 설정
EMAIL_SENDER_ADDRESS=your_sender_email@yourdomain.com
EMAIL_SENDER_NAME=주식시장분석봇
EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
```

### 2. Naver Cloud Platform 설정

1. [Naver Cloud Platform](https://www.ncloud.com/)에 가입
2. Cloud Outbound Mailer 서비스 신청
3. API 인증키 생성 (마이페이지 > 계정관리 > 인증키 관리)
4. 발송자 이메일 주소 등록 및 인증

## 사용법

### 1. 전체 시스템 실행

```bash
python test_main.py
```

이 명령어로 다음 작업들이 순차적으로 실행됩니다:
- 데이터 수집 (KRX, 네이버 뉴스)
- 벡터 데이터베이스 구축
- AI 분석 및 보고서 생성
- 이메일 발송

### 2. 이메일 발송만 테스트

```bash
python test_email_sender.py
```

### 3. 독립적인 이메일 발송

```bash
python email_sender.py
```

## 파일 구조

```
RAG/code/
├── test_main.py              # 메인 실행 스크립트
├── email_sender.py           # 이메일 발송 서비스
├── test_email_sender.py      # 이메일 발송 테스트
├── faiss_vector_api.py       # FAISS API 서버
├── faiss_vector_db1_api.py   # Vector DB1 API 서버
├── vector_db_1_analyzer.py   # Vector DB1 분석기
├── hybrid_vector_manager.py  # 벡터 관리자
├── clova_embedding.py        # CLOVA 임베딩 API
├── clova_segmentation.py     # CLOVA 세그멘테이션 API
├── news_content_extractor.py # 뉴스 본문 추출기
└── ...
```

## 이메일 발송 기능

### HTML 템플릿

보고서는 전문적인 HTML 이메일 템플릿으로 발송됩니다:

- 반응형 디자인
- 전문적인 스타일링
- 투자 유의사항 포함
- 자동 생성 표시

### 발송 설정

- **발송자**: 설정된 이메일 주소
- **수신자**: .env 파일에 설정된 이메일 목록
- **개별 발송**: 각 수신자에게 개별적으로 발송
- **광고성 메일 아님**: 일반 정보성 메일로 분류

### API 인증

Naver Cloud Outbound Mailer API는 HMAC-SHA256 서명을 사용합니다:

1. 타임스탬프 생성
2. 메시지 문자열 구성
3. Secret Key로 HMAC-SHA256 서명 생성
4. Base64 인코딩

## 주의사항

1. **API 키 보안**: .env 파일을 Git에 커밋하지 마세요
2. **이메일 발송 제한**: Naver Cloud Platform의 발송 제한을 확인하세요
3. **수신자 동의**: 수신자들의 이메일 수신 동의를 받으세요
4. **투자 유의사항**: 이메일에 투자 유의사항이 포함되어 있습니다

## 문제 해결

### 이메일 발송 실패 시

1. API 키 확인
2. 발송자 이메일 인증 확인
3. 수신자 이메일 형식 확인
4. 네트워크 연결 확인

### API 오류 코드

- `400`: 잘못된 요청
- `403`: 권한 없음
- `500`: 서버 오류

## 라이선스

이 프로젝트는 교육 및 연구 목적으로 제작되었습니다. 