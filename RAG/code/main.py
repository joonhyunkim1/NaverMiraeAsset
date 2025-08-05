#!/usr/bin/env python3
"""
주식 시장 RAG 시스템 메인 실행 파일
- 데이터 수집, 임베딩, 분석, 보고서 생성의 전체 파이프라인 실행
"""

import os
import sys
import time
import subprocess
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

class StockMarketRAGSystem:
    """주식 시장 RAG 시스템 메인 클래스"""
    
    def __init__(self):
        """시스템 초기화"""
        # 현재 스크립트 위치를 기준으로 상대 경로 설정
        current_dir = Path(__file__).parent
        self.project_root = current_dir.parent  # RAG 폴더
        self.data_1_dir = self.project_root / "data_1"
        self.data_2_dir = self.project_root / "data_2"
        self.vector_db_dir = self.project_root / "vector_db"
        self.vector_db_1_dir = self.project_root / "vector_db_1"
        self.daily_report_dir = self.project_root / "daily_report"
        
        # 환경 변수 설정
        self.enable_data_collection = True
        
        # 필요한 폴더들 자동 생성
        self._create_required_directories()
        
        print("🚀 주식 시장 RAG 시스템 초기화 완료")
    
    def _create_required_directories(self):
        """필요한 폴더들 자동 생성"""
        try:
            print("\n📁 필요한 폴더들 확인 및 생성")
            print("=" * 40)
            
            directories = [
                self.project_root,
                self.data_1_dir,
                self.data_2_dir,
                self.vector_db_dir,
                self.vector_db_1_dir,
                self.daily_report_dir
            ]
            
            for directory in directories:
                if not directory.exists():
                    directory.mkdir(parents=True, exist_ok=True)
                    print(f"✅ 폴더 생성: {directory.name}")
                else:
                    print(f"✅ 폴더 존재: {directory.name}")
            
            print("✅ 모든 필요한 폴더 확인 완료")
            
        except Exception as e:
            print(f"❌ 폴더 생성 중 오류: {e}")
            raise
    
    def start_faiss_api_server(self) -> bool:
        """FAISS API 서버 시작"""
        try:
            print("\n" + "=" * 60)
            print("🔧 FAISS API 서버 시작")
            print("=" * 60)
            
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
                    print("✅ FAISS API 서버 시작 성공 (포트 8000)")
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
    
    def start_vector_db1_api_server(self) -> bool:
        """Vector DB1 API 서버 시작"""
        try:
            print("\n" + "=" * 60)
            print("🔧 Vector DB1 API 서버 시작")
            print("=" * 60)
            
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
                    print("✅ Vector DB1 API 서버 시작 성공 (포트 8001)")
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
    
    def collect_data(self):
        """데이터 수집"""
        if not self.enable_data_collection:
            print("⚠️ 데이터 수집이 비활성화되어 있습니다.")
            return True
        
        try:
            print("\n" + "=" * 60)
            print("📊 데이터 수집")
            print("=" * 60)
            
            # 뉴스 검색 파라미터 설정
            NEWS_CONFIG = {
                "query": "국내 주식 주가",  # 검색어
                "display": 100,           # 가져올 뉴스 개수 (최대 100)
                "start": 1,               # 검색 시작 위치
                "sort": "date",           # 정렬 방법 ("sim": 관련도순, "date": 날짜순)
                "filter_by_date": True,   # 날짜 필터링 사용 여부
                "days_back": 1,           # 지난 몇 일 뉴스를 가져올지 (1 = 지난 1일)
                "target_count": 30        # 필터링 후 목표 뉴스 개수 (최신순 30개)
            }
            
            print(f"📰 뉴스 검색 설정: {NEWS_CONFIG}")
            
            # 1. KRX 일일거래정보 수집
            print("\n" + "=" * 60)
            print("📈 KRX 일일거래정보 수집")
            print("=" * 60)
            
            from krx_api_client import KRXAPIClient
            krx_client = KRXAPIClient()
            krx_filename = krx_client.collect_and_save_daily_data()
            
            # 2. 네이버 뉴스 수집
            print("\n" + "=" * 60)
            print("📰 네이버 뉴스 수집")
            print("=" * 60)
            
            from naver_news_client import NaverNewsClient
            news_client = NaverNewsClient()
            
            # API 정보 확인
            api_info = news_client.get_api_info()
            if not api_info['client_id_set'] or not api_info['client_secret_set']:
                print("❌ 네이버 API 키가 설정되지 않았습니다!")
                print("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 .env 파일에 설정하세요.")
                news_filename = None
            else:
                print("✅ 네이버 API 키 설정 완료")
                print(f"🔍 '{NEWS_CONFIG['query']}' 키워드로 뉴스 검색 중...")
                
                # 사용자 정의 파라미터로 뉴스 수집
                success = news_client.get_custom_news(
                    query=NEWS_CONFIG["query"],
                    display=NEWS_CONFIG["display"],
                    start=NEWS_CONFIG["start"],
                    sort=NEWS_CONFIG["sort"],
                    filter_by_date=NEWS_CONFIG["filter_by_date"],
                    days_back=NEWS_CONFIG["days_back"],
                    target_count=NEWS_CONFIG["target_count"]
                )
                
                if success:
                    print("✅ 뉴스 수집 완료")
                    news_filename = "수집 완료"
                else:
                    print("❌ 뉴스 수집 실패")
                    news_filename = None
            
            # 3. 결과 요약
            print("\n" + "=" * 60)
            print("📋 수집 결과 요약")
            print("=" * 60)
            
            if krx_filename:
                print(f"✅ KRX 데이터: {krx_filename}")
            else:
                print("❌ KRX 데이터 수집 실패")
            
            if news_filename:
                print(f"✅ 네이버 뉴스: {news_filename}")
            else:
                print("❌ 네이버 뉴스 수집 실패")
            
            return True
                
        except Exception as e:
            print(f"❌ 데이터 수집 중 오류: {e}")
            return False
    
    def analyze_vector_db1(self, extracted_stocks=None):
        """Vector DB1 기반 분석"""
        try:
            print("\n" + "=" * 60)
            print("📊 Vector DB1 기반 주식 시장 분석")
            print("=" * 60)
            
            from vector_db_1_analyzer import VectorDB1Analyzer
            analyzer = VectorDB1Analyzer()
            
            # 추출된 종목명들을 전달
            if extracted_stocks:
                print(f"📋 추출된 종목명들을 Vector DB1 분석에 전달: {extracted_stocks}")
                success = analyzer.run_analysis(extracted_stocks=extracted_stocks)
            else:
                print("⚠️ 추출된 종목명이 없어 일반 분석을 수행합니다.")
                success = analyzer.run_analysis()
            
            if success:
                print("✅ Vector DB1 기반 분석 완료")
                return True
            else:
                print("❌ Vector DB1 기반 분석 실패")
                return False
                
        except Exception as e:
            print(f"❌ Vector DB1 분석 중 오류: {e}")
            return False
    
    def combine_reports(self):
        """보고서 합치기 및 저장"""
        try:
            print("\n" + "=" * 60)
            print("📋 보고서 합치기 및 저장")
            print("=" * 60)
            
            print(f"📁 daily_report 폴더 확인: {self.daily_report_dir}")
            
            # 최근 생성된 보고서 파일들 찾기
            vector_db_reports = list(self.data_2_dir.glob("vector_db_report_*.txt"))
            vector_db_report = None
            if vector_db_reports:
                vector_db_report = max(vector_db_reports, key=lambda x: x.stat().st_mtime)
                print(f"📄 Vector DB 보고서 발견: {vector_db_report.name}")
            
            vector_db1_reports = list(self.data_2_dir.glob("vector_db_1_report_*.txt"))
            vector_db1_report = None
            if vector_db1_reports:
                vector_db1_report = max(vector_db1_reports, key=lambda x: x.stat().st_mtime)
                print(f"📄 Vector DB1 보고서 발견: {vector_db1_report.name}")
            
            # 보고서 내용 읽기
            combined_content = []
            combined_content.append("# 일일 주식 시장 종합 분석 보고서")
            combined_content.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            combined_content.append("=" * 80)
            combined_content.append("")
            
            # Vector DB 보고서 추가
            if vector_db_report:
                try:
                    with open(vector_db_report, 'r', encoding='utf-8') as f:
                        content = f.read()
                        combined_content.append("## 📊 어제 하루 주식 시장 분석")
                        combined_content.append("")
                        combined_content.append(content)
                        combined_content.append("")
                        combined_content.append("=" * 80)
                        combined_content.append("")
                        print(f"✅ Vector DB 보고서 내용 추가: {len(content)}자")
                except Exception as e:
                    print(f"❌ Vector DB 보고서 읽기 실패: {e}")
            else:
                print("⚠️ Vector DB 보고서를 찾을 수 없습니다.")
            
            # Vector DB1 보고서 추가
            if vector_db1_report:
                try:
                    with open(vector_db1_report, 'r', encoding='utf-8') as f:
                        content = f.read()
                        combined_content.append("## 📈 오늘 이슈가 있을 것으로 예상되는 주목 종목 분석")
                        combined_content.append("")
                        combined_content.append(content)
                        print(f"✅ Vector DB1 보고서 내용 추가: {len(content)}자")
                except Exception as e:
                    print(f"❌ Vector DB1 보고서 읽기 실패: {e}")
            else:
                print("⚠️ Vector DB1 보고서를 찾을 수 없습니다.")
            
            # 합쳐진 보고서 저장
            if len(combined_content) > 4:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                combined_report_file = self.daily_report_dir / f"daily_combined_report_{timestamp}.txt"
                
                with open(combined_report_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(combined_content))
                
                combined_text = '\n'.join(combined_content)
                print(f"💾 합쳐진 보고서 저장 완료: {combined_report_file}")
                print(f"📊 총 길이: {len(combined_text)}자")
                
                # 요약 정보 출력
                print(f"\n📋 보고서 요약:")
                if vector_db_report:
                    print(f"  📊 Vector DB 보고서: {vector_db_report.name}")
                if vector_db1_report:
                    print(f"  📈 Vector DB1 보고서: {vector_db1_report.name}")
                print(f"  📄 합쳐진 보고서: {combined_report_file.name}")
                
                return True
            else:
                print("❌ 합칠 보고서가 없습니다.")
                return False
                
        except Exception as e:
            print(f"❌ 보고서 합치기 중 오류: {e}")
            return False
    
    def run(self):
        """전체 파이프라인 실행"""
        print("🚀 주식 시장 RAG 시스템 시작")
        print("=" * 60)
        
        try:
            # 1. 데이터 수집
            if not self.collect_data():
                print("❌ 데이터 수집 실패로 인해 프로세스를 중단합니다.")
                return False
            
            # 2. Vector DB 임베딩
            print("\n" + "=" * 60)
            print("🔍 Vector DB 임베딩")
            print("=" * 60)
            
            from hybrid_vector_manager import HybridVectorManager
            vector_manager = HybridVectorManager(str(self.project_root / "data"))
            success = vector_manager.process_documents()
            
            if success:
                print("✅ Vector DB 임베딩 완료")
            else:
                print("❌ Vector DB 임베딩 실패")
                return False
            
            # 3. FAISS API 서버 시작
            if not self.start_faiss_api_server():
                print("❌ FAISS API 서버 시작 실패로 인해 분석을 건너뜁니다.")
                return False
            
            # 4. Vector DB 기반 분석 (주식 종목 추출을 위해)
            print("\n" + "=" * 60)
            print("🤖 CLOVA 분석 및 주식 종목 추출")
            print("=" * 60)
            
            from faiss_data_analyzer import FAISSDataAnalyzer
            analyzer = FAISSDataAnalyzer()
            analysis_success = analyzer.run_analysis(rebuild_vectors=False)  # 이미 임베딩 완료
            
            if analysis_success:
                print("✅ FAISS 벡터 검색 기반 분석 완료")
                
                # 5. 주식 종목 추출 및 데이터 수집
                print("\n📊 주식 종목 추출 시작...")
                from stock_extractor import StockExtractor
                extractor = StockExtractor()
                extraction_success = extractor.run_extraction()
                
                if extraction_success:
                    print("✅ 주식 종목 추출 완료")
                    
                    # 5. 자동 주식 데이터 수집 (추출된 종목명 사용)
                    print("\n" + "=" * 60)
                    print("📈 자동 주식 데이터 수집")
                    print("=" * 60)
                    
                    extracted_stocks = extractor.get_extracted_stocks()
                    print(f"📋 추출된 종목 수: {len(extracted_stocks) if extracted_stocks else 0}")
                    
                    if extracted_stocks:
                        print(f"📋 추출된 종목들: {extracted_stocks}")
                        from stock_data_collector import StockDataCollector
                        stock_collector = StockDataCollector()
                        auto_collection_success = stock_collector.run_auto_collection(extracted_stocks)
                        
                        if auto_collection_success:
                            print("✅ 자동 주식 데이터 수집 완료")
                        else:
                            print("❌ 자동 주식 데이터 수집 실패")
                    else:
                        print("❌ 추출된 종목명이 없어 자동 수집을 건너뜁니다.")
                    
                    # 6. 개별 종목 뉴스 수집
                    print("\n" + "=" * 60)
                    print("📰 개별 종목 뉴스 수집")
                    print("=" * 60)
                    
                    news_stocks = extracted_stocks
                    from stock_news_collector import StockNewsCollector
                    news_collector = StockNewsCollector()
                    news_success = news_collector.run_collection(news_stocks)
                    
                    if news_success:
                        print("✅ 개별 종목 뉴스 수집 완료")
                    else:
                        print("❌ 개별 종목 뉴스 수집 실패")
                else:
                    print("❌ 주식 종목 추출 실패")
                    extracted_stocks = None
            else:
                print("❌ FAISS 벡터 검색 기반 분석 실패")
                extracted_stocks = None
            
            # 6. Vector DB1 임베딩
            print("\n" + "=" * 60)
            print("🔍 Vector DB1 임베딩 시작")
            print("=" * 60)
            
            # data_1 폴더 상태 확인
            data_1_files = list(self.data_1_dir.glob("*"))
            print(f"📁 data_1 폴더 파일 수: {len(data_1_files)}")
            if data_1_files:
                print(f"📁 data_1 폴더 파일들: {[f.name for f in data_1_files]}")
            else:
                print("⚠️ data_1 폴더가 비어있습니다. Vector DB1 임베딩을 건너뜁니다.")
                return True
            
            from hybrid_vector_manager import HybridVectorManager
            data1_manager = HybridVectorManager(str(self.data_1_dir))
            # vector_db_1에 저장하도록 수정
            data1_manager.vector_dir = self.vector_db_1_dir
            data1_manager.vectors_file = self.vector_db_1_dir / "vector_db_1_vectors.pkl"
            data1_manager.metadata_file = self.vector_db_1_dir / "vector_db_1_metadata.json"
            success = data1_manager.process_documents()
            
            if success:
                print("✅ Vector DB1 임베딩 완료")
            else:
                print("❌ Vector DB1 임베딩 실패")
                return False
            
            # 7. Vector DB1 API 서버 시작
            if not self.start_vector_db1_api_server():
                print("❌ Vector DB1 API 서버 시작 실패로 인해 분석을 건너뜁니다.")
            else:
                                        # Rate Limit 방지를 위한 지연
                        print("⏳ API Rate Limit 방지를 위한 90초 지연...")
                        time.sleep(90)
                        
                        # 8. Vector DB1 기반 분석
                        self.analyze_vector_db1(extracted_stocks)
            
            # 9. Vector DB 기반 주식 시장 분석 보고서 생성
            print("\n" + "=" * 60)
            print("📊 Vector DB 기반 주식 시장 분석 보고서")
            print("=" * 60)
            
            # Rate Limit 방지를 위한 지연
            print("⏳ API Rate Limit 방지를 위한 90초 지연...")
            time.sleep(90)
            
            try:
                # Vector DB 분석기 클래스 정의
                class VectorDBAnalyzer:
                    """vector_db 벡터 기반 분석기 (FAISS API 사용)"""
                    
                    def __init__(self):
                        self.api_base_url = "http://localhost:8000"  # 메인 FAISS API 서버
                        
                        # 새로운 CLOVA API 설정 (vector_db_1_analyzer와 동일)
                        self.api_key = os.getenv("NEW_CLOVA_API_KEY", "")
                        self.request_id = os.getenv("NEW_CLOVA_REQUEST_ID", "4997d0ab4e434139bd982084de885077")
                        self.model_endpoint = os.getenv("NEW_CLOVA_MODEL_ENDPOINT", "/v3/tasks/yl1fvofj/chat-completions")
                        
                        # data_2_dir 속성 추가 (절대 경로 사용)
                        self.data_2_dir = Path(__file__).parent.parent / "data_2"
                        
                        # CLOVA 클라이언트 초기화
                        self.clova_client = self._create_clova_client()
                        
                        print("🔧 VectorDBAnalyzer 초기화 완료")
                        print(f"📡 FAISS API 서버: {self.api_base_url}")
                    
                    def _create_clova_client(self):
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
                        print("🔍 vector_db 벡터 데이터 분석 중...")
                        
                        # 검색 쿼리 설정
                        search_query = "어제 하루 뉴스 및 일일 거래데이터 이슈 요약"
                        
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
                            "temperature": 0.7,
                            "topP": 0.8
                        }
                        
                        # CLOVA API 호출
                        response_text = self.clova_client.execute(request_data)
                        
                        if response_text and response_text != 'Error':
                            print(f"✅ 보고서 생성 완료: {len(response_text)}자")
                            return response_text
                        else:
                            print("❌ CLOVA API 호출 실패")
                            return ""
                        
                    def _create_analysis_prompt(self, text_contents: List[str]) -> str:
                        """분석용 프롬프트 생성"""
                        prompt = f"""
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
                        return prompt
                    
                    def save_report(self, report: str) -> str:
                        """보고서를 파일로 저장"""
                        try:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            report_file = self.data_2_dir / f"vector_db_report_{timestamp}.txt"
                            
                            with open(report_file, 'w', encoding='utf-8') as f:
                                f.write(f"# Vector DB 기반 어제 하루 주식 시장 분석 보고서\n")
                                f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                                f.write(f"분석 벡터 수: {len(report)}자\n")
                                f.write(f"=" * 60 + "\n\n")
                                f.write(report)
                            
                            print(f"💾 보고서 저장 완료: {report_file}")
                            return str(report_file)
                            
                        except Exception as e:
                            print(f"❌ 보고서 저장 실패: {e}")
                            return ""
                    
                    def run_analysis(self) -> bool:
                        """전체 분석 프로세스 실행"""
                        print("\n" + "=" * 60)
                        print("🔍 Vector DB 기반 어제 하루 주식 시장 분석")
                        print("=" * 60)
                        
                        # 1. FAISS API 서버 상태 확인
                        if not self.check_faiss_api_server():
                            return False
                        
                        # 2. 분석 실행
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
                
                # Vector DB 분석 실행
                analyzer = VectorDBAnalyzer()
                analysis_success = analyzer.run_analysis()
                
                if analysis_success:
                    print("✅ Vector DB 기반 분석 보고서 생성 완료")
                else:
                    print("❌ Vector DB 기반 분석 보고서 생성 실패")
                    
            except Exception as e:
                print(f"❌ Vector DB 분석 중 오류: {e}")
            
            # 11. 보고서 합치기 및 저장
            self.combine_reports()
            
            print("\n🎉 주식 시장 RAG 시스템 실행 완료!")
            return True
            
        except Exception as e:
            print(f"❌ 시스템 실행 중 오류: {e}")
            return False


def main():
    """메인 실행 함수"""
    system = StockMarketRAGSystem()
    success = system.run()
    
    if success:
        print("\n✅ 모든 작업이 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 일부 작업이 실패했습니다.")
        sys.exit(1)


if __name__ == "__main__":
    main() 