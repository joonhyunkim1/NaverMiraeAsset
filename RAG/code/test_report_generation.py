#!/usr/bin/env python3
"""
보고서 생성 테스트 파일
- 기존 임베딩 벡터들을 사용하여 보고서 작성만 테스트
"""

import os
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class ReportGenerationTester:
    """보고서 생성 테스트 클래스"""
    
    def __init__(self):
        """초기화"""
        self.project_root = Path(__file__).parent.parent
        self.data_2_dir = self.project_root / "data_2"
        self.vector_db_dir = self.project_root / "vector_db"
        self.vector_db_1_dir = self.project_root / "vector_db_1"
        
        # CLOVA API 설정
        self.api_key = os.getenv("NEW_CLOVA_API_KEY", "")
        self.request_id = os.getenv("NEW_CLOVA_REQUEST_ID", "4997d0ab4e434139bd982084de885077")
        self.model_endpoint = os.getenv("NEW_CLOVA_MODEL_ENDPOINT", "/v3/tasks/yl1fvofj/chat-completions")
        
        print("🔧 보고서 생성 테스트 초기화 완료")
        print(f"📁 프로젝트 루트: {self.project_root}")
        print(f"📁 data_2 폴더: {self.data_2_dir}")
        print(f"📁 vector_db 폴더: {self.vector_db_dir}")
        print(f"📁 vector_db_1 폴더: {self.vector_db_1_dir}")
    
    def check_vector_files(self):
        """벡터 파일 존재 확인"""
        print("\n" + "=" * 60)
        print("📁 벡터 파일 확인")
        print("=" * 60)
        
        # Vector DB 파일 확인
        vector_db_files = {
            "vectors": self.vector_db_dir / "hybrid_vectors.pkl",
            "metadata": self.vector_db_dir / "hybrid_metadata.json"
        }
        
        print("🔍 Vector DB 파일 확인:")
        for name, file_path in vector_db_files.items():
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  ✅ {name}: {file_path.name} ({size:,} bytes)")
            else:
                print(f"  ❌ {name}: {file_path.name} (파일 없음)")
        
        # Vector DB1 파일 확인
        vector_db1_files = {
            "vectors": self.vector_db_1_dir / "vector_db_1_vectors.pkl",
            "metadata": self.vector_db_1_dir / "vector_db_1_metadata.json"
        }
        
        print("\n🔍 Vector DB1 파일 확인:")
        for name, file_path in vector_db1_files.items():
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"  ✅ {name}: {file_path.name} ({size:,} bytes)")
            else:
                print(f"  ❌ {name}: {file_path.name} (파일 없음)")
        
        return True
    
    def start_faiss_api_server(self):
        """FAISS API 서버 시작"""
        try:
            print("\n" + "=" * 60)
            print("🔧 FAISS API 서버 시작")
            print("=" * 60)
            
            import subprocess
            
            # 기존 서버 프로세스 종료
            try:
                subprocess.run(["pkill", "-f", "faiss_vector_api.py"], 
                             capture_output=True, timeout=5)
                time.sleep(2)
            except:
                pass
            
            # 새 서버 시작
            server_process = subprocess.Popen([
                sys.executable, "faiss_vector_api.py"
            ], cwd=str(Path(__file__).parent))
            
            # 서버 시작 대기
            time.sleep(5)
            
            # 서버 상태 확인
            try:
                response = requests.get("http://localhost:8000/health", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print("✅ FAISS API 서버 시작 성공 (포트 8000)")
                    print(f"   벡터 로드: {data.get('total_vectors', 0)}개")
                    print(f"   메타데이터: {data.get('total_metadata', 0)}개")
                    return True
                else:
                    print("❌ FAISS API 서버 응답 오류")
                    return False
            except Exception as e:
                print(f"❌ FAISS API 서버 연결 실패: {e}")
                return False
                
        except Exception as e:
            print(f"❌ FAISS API 서버 시작 실패: {e}")
            return False
    
    def start_vector_db1_api_server(self):
        """Vector DB1 API 서버 시작"""
        try:
            print("\n" + "=" * 60)
            print("🔧 Vector DB1 API 서버 시작")
            print("=" * 60)
            
            import subprocess
            
            # 기존 서버 프로세스 종료
            try:
                subprocess.run(["pkill", "-f", "faiss_vector_db1_api.py"], 
                             capture_output=True, timeout=5)
                time.sleep(2)
            except:
                pass
            
            # 새 서버 시작
            server_process = subprocess.Popen([
                sys.executable, "faiss_vector_db1_api.py"
            ], cwd=str(Path(__file__).parent))
            
            # 서버 시작 대기
            time.sleep(5)
            
            # 서버 상태 확인
            try:
                response = requests.get("http://localhost:8001/health", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    print("✅ Vector DB1 API 서버 시작 성공 (포트 8001)")
                    print(f"   벡터 로드: {data.get('total_vectors', 0)}개")
                    print(f"   메타데이터: {data.get('total_metadata', 0)}개")
                    return True
                else:
                    print("❌ Vector DB1 API 서버 응답 오류")
                    return False
            except Exception as e:
                print(f"❌ Vector DB1 API 서버 연결 실패: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Vector DB1 API 서버 시작 실패: {e}")
            return False
    
    def create_clova_client(self):
        """CLOVA 클라이언트 생성"""
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

                import http.client
                import json
                conn = http.client.HTTPSConnection(self._host)
                conn.request('POST', self._model_endpoint, json.dumps(completion_request), headers)
                response = conn.getresponse()
                
                print(f"📡 CLOVA API 응답:")
                print(f"   상태 코드: {response.status}")
                
                result = json.loads(response.read().decode(encoding='utf-8'))
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
        
        return CompletionExecutor(
            host='clovastudio.stream.ntruss.com',
            api_key=f'Bearer {self.api_key}',
            request_id=self.request_id,
            model_endpoint=self.model_endpoint
        )
    
    def test_vector_db_report(self):
        """Vector DB 기반 보고서 생성 테스트"""
        try:
            print("\n" + "=" * 60)
            print("📊 Vector DB 기반 보고서 생성 테스트")
            print("=" * 60)
            
            # CLOVA 클라이언트 생성
            clova_client = self.create_clova_client()
            
            # 검색 쿼리 설정
            search_query = "어제 하루 뉴스 및 일일 거래데이터 이슈 요약"
            
            # FAISS 벡터 검색 수행
            print(f"🔍 검색 쿼리: {search_query}")
            
            try:
                response = requests.post(
                    "http://localhost:8000/search",
                    json={"query": search_query, "top_k": 10},
                    timeout=60
                )
                
                if response.status_code == 200:
                    search_results = response.json().get('results', [])
                    print(f"✅ 검색 완료: {len(search_results)}개 결과")
                    
                    # 검색 결과에서 텍스트 내용 추출
                    text_contents = []
                    for result in search_results:
                        text_content = result.get('text_content', '')
                        if text_content:
                            text_contents.append(text_content)
                    
                    if text_contents:
                        # 분석용 프롬프트 구성
                        analysis_prompt = f"""
당신은 주식 시장 분석 전문가입니다. 제공된 데이터를 바탕으로 어제 하루의 뉴스 및 일일 거래데이터를 요약한 보고서를 최대한 자세히 작성해주세요.

다음은 분석할 데이터입니다:

{chr(15).join(text_contents[:15])}  # 처음 15개 텍스트만 사용

보고서 작성 요구사항:
1. 총 글자수: 3500자 정도
2. 구조:
   - 서론: 주요 증시 요약
   - 본론: 뉴스에 기반한 어제 하루의 주요 이슈 요약
   - 결론: 어제 하루의 종합적인 주식 시장 분석

3. 각 종목별 분석 내용:
   - 어제 거래 동향 (종목명, 시가, 고가, 저가, 종가, 거래량)
   - 관련 뉴스 및 이슈

4. 전문적이고 객관적인 톤으로 작성
5. 구체적인 데이터와 근거 제시
6. 어제 하루의 시장 전반적인 분위기 분석

위 데이터를 바탕으로 어제 하루의 종합적인 주식 시장 분석 보고서를 작성해주세요.
"""
                        
                        print("🤖 CLOVA 모델에게 보고서 요청 중...")
                        
                        # CLOVA API 호출
                        request_data = {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": analysis_prompt
                                }
                            ],
                            "maxTokens": 3500,
                            "temperature": 0.7,
                            "topP": 0.8
                        }
                        
                        response_text = clova_client.execute(request_data)
                        
                        if response_text and response_text != 'Error':
                            print(f"✅ Vector DB 보고서 생성 완료: {len(response_text)}자")
                            
                            # 보고서 저장
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            report_file = self.data_2_dir / f"test_vector_db_report_{timestamp}.txt"
                            
                            with open(report_file, 'w', encoding='utf-8') as f:
                                f.write(f"# Vector DB 기반 어제 하루 주식 시장 분석 보고서 (테스트)\n")
                                f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                f.write(f"분석 벡터 수: {len(response_text)}자\n")
                                f.write(f"=" * 60 + "\n\n")
                                f.write(response_text)
                            
                            print(f"💾 보고서 저장 완료: {report_file}")
                            return True
                        else:
                            print("❌ CLOVA API 호출 실패")
                            return False
                    else:
                        print("❌ 검색 결과에서 텍스트 내용을 찾을 수 없습니다.")
                        return False
                else:
                    print(f"❌ 검색 요청 실패: {response.status_code}")
                    return False
                    
            except requests.exceptions.Timeout:
                print(f"❌ 검색 타임아웃 (60초)")
                return False
            except Exception as e:
                print(f"❌ 검색 중 오류: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Vector DB 보고서 생성 테스트 실패: {e}")
            return False
    
    def test_vector_db1_report(self):
        """Vector DB1 기반 보고서 생성 테스트"""
        try:
            print("\n" + "=" * 60)
            print("📊 Vector DB1 기반 보고서 생성 테스트")
            print("=" * 60)
            
            # CLOVA 클라이언트 생성
            clova_client = self.create_clova_client()
            
            # 검색 쿼리 설정
            search_query = "주목해야 할 종목 주가 동향 뉴스 이슈"
            
            # FAISS 벡터 검색 수행
            print(f"🔍 검색 쿼리: {search_query}")
            
            try:
                response = requests.post(
                    "http://localhost:8001/search",
                    json={"query": search_query, "top_k": 15},
                    timeout=60
                )
                
                if response.status_code == 200:
                    search_results = response.json().get('results', [])
                    print(f"✅ 검색 완료: {len(search_results)}개 결과")
                    
                    # 검색 결과에서 텍스트 내용 추출
                    text_contents = []
                    for result in search_results:
                        text_content = result.get('text_content', '')
                        if text_content:
                            text_contents.append(text_content)
                    
                    if text_contents:
                        # 분석용 프롬프트 구성
                        analysis_prompt = f"""
당신은 주식 시장 분석 전문가입니다. 제공된 데이터를 바탕으로 요구사항에 따라 오늘 하루 주목해야 할 종목들을 정리한 보고서를 작성해주세요.

중요: 인사말이나 서론 없이 바로 분석 내용을 시작하세요.

다음은 분석할 데이터입니다:

{chr(20).join(text_contents[:20])}  # 처음 20개 텍스트만 사용

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
                        
                        print("🤖 CLOVA 모델에게 보고서 요청 중...")
                        
                        # CLOVA API 호출
                        request_data = {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": analysis_prompt
                                }
                            ],
                            "maxTokens": 3500,
                            "temperature": 0.5,
                            "topP": 0.8,
                            "topK": 0,
                            "repetitionPenalty": 1.1,
                            "stop": [],
                            "includeAiFilters": True,
                            "seed": 0
                        }
                        
                        response_text = clova_client.execute(request_data)
                        
                        if response_text and response_text != 'Error':
                            print(f"✅ Vector DB1 보고서 생성 완료: {len(response_text)}자")
                            
                            # 보고서 저장
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            report_file = self.data_2_dir / f"test_vector_db1_report_{timestamp}.txt"
                            
                            with open(report_file, 'w', encoding='utf-8') as f:
                                f.write(f"# Vector DB1 기반 오늘 이슈가 있을 것으로 예상되는 주목 종목 분석 (테스트)\n")
                                f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                f.write(f"분석 벡터 수: {len(response_text)}자\n")
                                f.write(f"=" * 60 + "\n\n")
                                f.write(response_text)
                            
                            print(f"💾 보고서 저장 완료: {report_file}")
                            return True
                        else:
                            print("❌ CLOVA API 호출 실패")
                            return False
                    else:
                        print("❌ 검색 결과에서 텍스트 내용을 찾을 수 없습니다.")
                        return False
                else:
                    print(f"❌ 검색 요청 실패: {response.status_code}")
                    return False
                    
            except requests.exceptions.Timeout:
                print(f"❌ 검색 타임아웃 (60초)")
                return False
            except Exception as e:
                print(f"❌ 검색 중 오류: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Vector DB1 보고서 생성 테스트 실패: {e}")
            return False
    
    def run_test(self):
        """전체 테스트 실행"""
        print("🚀 보고서 생성 테스트 시작")
        print("=" * 60)
        
        try:
            # 1. 벡터 파일 확인
            if not self.check_vector_files():
                print("❌ 벡터 파일 확인 실패")
                return False
            
            # 2. FAISS API 서버 시작
            if not self.start_faiss_api_server():
                print("❌ FAISS API 서버 시작 실패")
                return False
            
            # 3. Vector DB1 API 서버 시작
            if not self.start_vector_db1_api_server():
                print("❌ Vector DB1 API 서버 시작 실패")
                return False
            
            # 4. Vector DB 보고서 생성 테스트
            print("\n⏳ API Rate Limit 방지를 위한 90초 지연...")
            time.sleep(90)
            
            if not self.test_vector_db_report():
                print("❌ Vector DB 보고서 생성 테스트 실패")
                return False
            
            # 5. Vector DB1 보고서 생성 테스트
            print("\n⏳ API Rate Limit 방지를 위한 90초 지연...")
            time.sleep(90)
            
            if not self.test_vector_db1_report():
                print("❌ Vector DB1 보고서 생성 테스트 실패")
                return False
            
            print("\n🎉 모든 보고서 생성 테스트 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류: {e}")
            return False


def main():
    """메인 실행 함수"""
    tester = ReportGenerationTester()
    success = tester.run_test()
    
    if success:
        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 일부 테스트가 실패했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main() 