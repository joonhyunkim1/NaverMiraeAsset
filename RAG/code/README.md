# LlamaIndex 기반 RAG 시스템

이 프로젝트는 LlamaIndex를 사용하여 구현된 RAG(Retrieval Augmented Generation) 시스템입니다. CLOVA X API를 사용하여 임베딩을 생성하고, HyperCLOVA X를 사용하여 답변을 생성합니다.

## 🚀 주요 특징

- **LlamaIndex 프레임워크**: LangChain 대신 LlamaIndex를 사용하여 RAG 구현
- **CLOVA X Embedding API**: NAVER Cloud Platform의 CLOVA X API를 사용한 임베딩 생성
- **HyperCLOVA X**: NAVER의 최신 LLM을 사용한 답변 생성
- **CSV 데이터 지원**: 로컬 CSV 파일을 지식 베이스로 활용
- **대화형 인터페이스**: 대화형 채팅 모드 지원

## 📋 요구사항

### API 키
1. **CLOVA X API 키**: 공통 API 키
2. **CLOVA X Embedding Request ID**: 임베딩 API 전용 Request ID
3. **CLOVA X Chat Request ID**: Chat Completion API 전용 Request ID

### 데이터
- `/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data` 디렉토리에 CSV 파일들

## 🛠️ 설치 및 설정

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
```bash
# env_template.txt를 .env로 복사
cp env_template.txt .env

# .env 파일에 실제 API 키 입력
CLOVA_API_KEY=your_actual_clova_api_key
CLOVA_EMBEDDING_REQUEST_ID=your_actual_embedding_request_id
CLOVA_CHAT_REQUEST_ID=your_actual_chat_request_id
```

## 🎯 사용법

### 메인 실행
```bash
python main.py
```

### 테스트 실행
```bash
python test_clova_api.py
```

### 인덱스 재구축
```bash
python main.py --rebuild
```

## 📁 파일 구조

```
RAG/code/
├── llamaindex_rag_system.py    # 메인 RAG 시스템 클래스
├── main.py                     # 메인 실행 파일
├── test_clova_api.py           # CLOVA API 테스트
├── clova_api_client.py         # CLOVA API 클라이언트 (레거시)
├── config.py                   # 설정 파일
├── requirements.txt            # 필요한 패키지 목록
├── env_template.txt            # 환경 변수 템플릿
└── README.md                   # 이 파일
```

## 🔧 시스템 아키텍처

1. **데이터 로딩**: CSV 파일을 LlamaIndex Document로 변환
2. **텍스트 청킹**: SentenceSplitter를 사용한 텍스트 분할
3. **임베딩 생성**: CLOVA X API를 사용한 벡터 임베딩
4. **벡터 검색**: FAISS 기반 유사도 검색
5. **답변 생성**: HyperCLOVA X를 사용한 응답 생성

## 🎮 메뉴 옵션

1. **단일 질문하기**: 한 번의 질문에 답변
2. **대화형 채팅 모드**: 연속적인 대화 가능
3. **시스템 정보 보기**: 현재 시스템 상태 확인
4. **종료**: 시스템 종료

## 📊 성능 최적화

- CSV 파일당 최대 1000행만 처리하여 메모리 사용량 제한
- 벡터 인덱스 자동 저장/로드
- 대화 내용 JSON 형태로 저장

## 🔍 문제 해결

### 일반적인 오류
1. **API 키 오류**: .env 파일의 API 키 확인
2. **임베딩 실패**: CLOVA API 키 및 Request ID 확인
3. **답변 생성 실패**: HyperCLOVA X API 연결 확인

### 로그 확인
시스템 실행 시 상세한 로그가 출력되므로 오류 발생 시 로그를 확인하세요.

## 📚 참고 자료

- [LlamaIndex 공식 문서](https://docs.llamaindex.ai/)
- [CLOVA X API 문서](https://www.ncloud.com/product/aiService/clovaStudio)
- [NAVER Cloud Platform Forum - CLOVA Studio RAG 구현](https://www.ncloud-forums.com/topic/307/#comment-1219) 