#!/usr/bin/env python3
"""
vector_db_1 벡터 기반 주식 분석 보고서 생성 시스템
- FAISS API를 통해 vector_db_1의 벡터 검색
- CLOVA 모델에게 4000자 보고서 요청
"""

import http.client
import json
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경변수 로드
env_path = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/code/.env")
load_dotenv(env_path)

class CompletionExecutor:
    def __init__(self, host, api_key, request_id, model_endpoint=None):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id
        self._model_endpoint = model_endpoint or "/v3/tasks/yl1fvofj/chat-completions"

    def _send_request(self, completion_request):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }

        print(f"🔍 CLOVA API 요청 정보:")
        print(f"   호스트: {self._host}")
        print(f"   엔드포인트: {self._model_endpoint}")
        print(f"   Request ID: {self._request_id}")
        print(f"   API 키: {self._api_key[:20]}...")
        print(f"   요청 데이터: {completion_request}")

        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', self._model_endpoint, json.dumps(completion_request), headers)
        response = conn.getresponse()
        
        print(f"📡 CLOVA API 응답:")
        print(f"   상태 코드: {response.status}")
        print(f"   응답 헤더: {response.getheaders()}")
        
        result = json.loads(response.read().decode(encoding='utf-8'))
        print(f"   응답 내용: {result}")
        
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            # 새로운 모델은 message.content 형식으로 응답
            if 'result' in res and 'message' in res['result'] and 'content' in res['result']['message']:
                return res['result']['message']['content']
            # 기존 text 형식도 지원
            elif 'result' in res and 'text' in res['result']:
                return res['result']['text']
            else:
                print(f"❌ 예상치 못한 응답 형식: {res}")
                return 'Error'
        else:
            return 'Error'

class VectorDB1Analyzer:
    """vector_db_1 벡터 기반 분석기 (FAISS API 사용)"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:8001"  # Vector DB1 FAISS API 서버
        
        # 새로운 CLOVA API 설정
        self.api_key = os.getenv("NEW_CLOVA_API_KEY", "")
        self.request_id = os.getenv("NEW_CLOVA_REQUEST_ID", "4997d0ab4e434139bd982084de885077")
        self.model_endpoint = os.getenv("NEW_CLOVA_MODEL_ENDPOINT", "/v3/tasks/yl1fvofj/chat-completions")
        
        # CLOVA 클라이언트 초기화
        self.clova_client = CompletionExecutor(
            host='clovastudio.stream.ntruss.com',
            api_key=f'Bearer {self.api_key}',
            request_id=self.request_id,
            model_endpoint=self.model_endpoint
        )
        
        print("🔧 VectorDB1Analyzer 초기화 완료")
        print(f"📡 FAISS API 서버: {self.api_base_url}")
    
    def check_faiss_api_server(self) -> bool:
        """FAISS API 서버 상태 확인"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FAISS API 서버 연결 성공")
                print(f"   벡터 로드: {data.get('total_vectors', 0)}개")
                print(f"   메타데이터: {data.get('total_metadata', 0)}개")
                return True
            else:
                print(f"❌ FAISS API 서버 응답 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ FAISS API 서버 연결 실패: {e}")
            return False
    
    def search_vectors(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """FAISS API를 통한 벡터 검색"""
        try:
            response = requests.post(
                f"{self.api_base_url}/search",
                json={"query": query, "top_k": top_k},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            else:
                print(f"❌ 검색 요청 실패: {response.status_code}")
                return []
                
        except requests.exceptions.Timeout:
            print(f"❌ 검색 타임아웃 (60초)")
            return []
        except Exception as e:
            print(f"❌ 검색 중 오류: {e}")
            return []
    
    def analyze_vectors(self) -> str:
        """벡터 데이터를 분석하여 보고서 생성"""
        print("🔍 vector_db_1 벡터 데이터 분석 중...")
        
        # 검색 쿼리 설정
        search_query = "주목해야 할 종목 주가 동향 뉴스 이슈"
        
        # FAISS 벡터 검색 수행
        print(f"🔍 검색 쿼리: {search_query}")
        search_results = self.search_vectors(search_query, top_k=10)
        
        if not search_results:
            print("❌ 검색 결과가 없습니다.")
            return ""
        
        print(f"✅ 검색 완료: {len(search_results)}개 결과")
        
        # 검색 결과에서 텍스트 내용 추출
        text_contents = []
        for result in search_results:
            text_content = result.get('text_content', '')
            if text_content:
                text_contents.append(text_content)
        
        # 분석용 프롬프트 구성
        analysis_prompt = self._create_analysis_prompt(text_contents)
        
        print("🤖 CLOVA 모델에게 보고서 요청 중...")
        
        # 새로운 CLOVA 모델 형식 사용 (messages 형식)
        request_data = {
            "messages": [
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            "maxTokens": 3500,  # 3500자 보고서
            "temperature": 0.5,
            "topP": 0.8,
            "topK": 0,
            "repetitionPenalty": 1.1,
            "stop": [],
            "includeAiFilters": True,
            "seed": 0
        }
        
        try:
            response_text = self.clova_client.execute(request_data)
            
            if response_text == 'Error':
                print("❌ CLOVA API 호출 실패")
                return ""
            
            print(f"✅ 보고서 생성 완료: {len(response_text)}자")
            return response_text
            
        except Exception as e:
            print(f"❌ CLOVA 분석 실패: {e}")
            return ""
    
    def _create_analysis_prompt(self, text_contents: List[str]) -> str:
        """분석용 프롬프트 생성"""
        prompt = f"""
당신은 주식 시장 분석 전문가입니다. 제공된 데이터를 바탕으로 요구사항에 따라 오늘 하루 주목해야 할 종목들을 정리한 보고서를 작성해주세요.

중요: 인사말이나 서론 없이 바로 분석 내용을 시작하세요.

다음은 분석할 데이터입니다:

{chr(20).join(text_contents[:20])}  # 처음 10개 텍스트만 사용

보고서 작성 요구사항:
1. 총 글자수: 3500자 정도
2. 구조:
   - 오늘 주목해야할 종목명 3가지
   - 주목해야 할 종목별 상세 분석 (3개 종목)
   - 투자 전략 및 주의사항

3. 각 종목별 분석 내용:
   - 종목명 및 종목코드
   - 최근 주가 동향
   - 관련 뉴스 및 이슈
   - 투자 포인트
   - 위험 요소

4. 전문적이고 객관적인 톤으로 작성
5. 구체적인 데이터와 근거 제시
6. '서론', '본론', '결론' 등의 단어를 사용하지 말고 자연스럽게 연결

위 데이터를 바탕으로 종합적인 주식 시장 분석 보고서를 작성해주세요.
"""
        return prompt
    
    def analyze_vectors_with_extracted_stocks(self, extracted_stocks: List[str]) -> str:
        """추출된 종목명을 사용하여 벡터 데이터 분석"""
        print("🔍 추출된 종목명을 사용한 vector_db_1 벡터 데이터 분석 중...")
        
        # 검색 쿼리 설정 (추출된 종목명 포함)
        search_query = f"주목해야 할 종목 주가 동향 뉴스 이슈 {', '.join(extracted_stocks)}"
        
        # FAISS 벡터 검색 수행
        print(f"🔍 검색 쿼리: {search_query}")
        search_results = self.search_vectors(search_query, top_k=15)  # 더 많은 결과 검색
        
        if not search_results:
            print("❌ 검색 결과가 없습니다.")
            return ""
        
        print(f"✅ 검색 완료: {len(search_results)}개 결과")
        
        # 검색 결과에서 텍스트 내용 추출
        text_contents = []
        for result in search_results:
            text_content = result.get('text_content', '')
            if text_content:
                text_contents.append(text_content)
        
        # 분석용 프롬프트 구성 (추출된 종목명 포함)
        analysis_prompt = self._create_analysis_prompt_with_extracted_stocks(text_contents, extracted_stocks)
        
        print("🤖 CLOVA 모델에게 보고서 요청 중...")
        
        # 새로운 CLOVA 모델 형식 사용 (messages 형식)
        request_data = {
            "messages": [
                {
                    "role": "user",
                    "content": analysis_prompt
                }
            ],
            "maxTokens": 3500,  # 3500자 보고서
            "temperature": 0.5,
            "topP": 0.8,
            "topK": 0,
            "repetitionPenalty": 1.1,
            "stop": [],
            "includeAiFilters": True,
            "seed": 0
        }
        
        try:
            response_text = self.clova_client.execute(request_data)
            
            if response_text == 'Error':
                print("❌ CLOVA API 호출 실패")
                return ""
            
            print(f"✅ 보고서 생성 완료: {len(response_text)}자")
            return response_text
            
        except Exception as e:
            print(f"❌ CLOVA 분석 실패: {e}")
            return ""
    
    def _create_analysis_prompt_with_extracted_stocks(self, text_contents: List[str], extracted_stocks: List[str]) -> str:
        """추출된 종목명을 포함한 분석용 프롬프트 생성"""
        prompt = f"""
당신은 주식 시장 분석 전문가입니다. 제공된 데이터를 바탕으로 요구사항에 따라 오늘 하루 주목해야 할 종목들을 정리한 보고서를 작성해주세요.

중요: 인사말이나 서론 없이 바로 분석 내용을 시작하세요.

다음은 분석할 데이터입니다:

{chr(20).join(text_contents[:20])}  # 처음 20개 텍스트만 사용

추출된 주목 종목명: {', '.join(extracted_stocks)}

보고서 작성 요구사항:
1. 총 글자수: 3500자 정도
2. 구조:
   - 오늘 주목해야할 종목명 3가지 (반드시 추출된 종목명 중에서 선택)
   - 주목해야 할 종목별 상세 분석 (3개 종목)
   - 투자 전략 및 주의사항

3. 각 종목별 분석 내용:
   - 종목명 및 종목코드
   - 최근 주가 동향
   - 관련 뉴스 및 이슈
   - 투자 포인트
   - 위험 요소

4. 전문적이고 객관적인 톤으로 작성
5. 구체적인 데이터와 근거 제시
6. '서론', '본론', '결론' 등의 단어를 사용하지 말고 자연스럽게 연결
7. 반드시 추출된 종목명 중에서 3개를 선택하여 분석

위 데이터를 바탕으로 종합적인 주식 시장 분석 보고서를 작성해주세요.
"""
        return prompt
    
    def save_report(self, report: str) -> str:
        """보고서를 파일로 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 현재 스크립트 위치를 기준으로 상대 경로 설정
            current_dir = Path(__file__).parent
            report_file = current_dir.parent / "data_2" / f"vector_db_1_report_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"💾 보고서 저장 완료: {report_file}")
            return str(report_file)
            
        except Exception as e:
            print(f"❌ 보고서 저장 실패: {e}")
            return ""
    
    def run_analysis(self, extracted_stocks=None) -> bool:
        """전체 분석 프로세스 실행"""
        print("\n" + "=" * 60)
        print("🔍 Vector DB1 기반 오늘 이슈가 있을 것으로 예상되는 주목 종목 분석")
        print("=" * 60)
        
        # 1. FAISS API 서버 상태 확인
        if not self.check_faiss_api_server():
            return False
        
        # 2. 분석 실행 (추출된 종목명 전달)
        if extracted_stocks:
            print(f"📋 추출된 종목명을 사용한 분석: {extracted_stocks}")
            report = self.analyze_vectors_with_extracted_stocks(extracted_stocks)
        else:
            print("⚠️ 추출된 종목명이 없어 일반 분석을 수행합니다.")
            report = self.analyze_vectors()
        
        if not report:
            return False
        
        # 3. 보고서 저장
        report_file = self.save_report(report)
        if not report_file:
            return False
        
        # 4. 결과 출력
        print("\n" + "=" * 60)
        print("📊 분석 결과 전체 보고서")
        print("=" * 60)
        print(report)
        
        return True

def main():
    """메인 실행 함수"""
    analyzer = VectorDB1Analyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("\n🎉 Vector DB1 기반 분석 완료!")
    else:
        print("\n❌ Vector DB1 기반 분석 실패!")

if __name__ == "__main__":
    main() 