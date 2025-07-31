#!/usr/bin/env python3
"""
RAG 시스템 컴포넌트들
- test_main.py에서 사용되는 클래스들을 별도 모듈로 분리
"""

import os
import json
import time
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from hybrid_vector_manager import HybridVectorManager
from clova_embedding import ClovaEmbeddingAPI
from clova_segmentation import ClovaSegmentationClient
from news_content_extractor import NewsContentExtractor


class Data1VectorManager(HybridVectorManager):
    """data_1 디렉토리용 벡터 매니저"""
    
    def __init__(self, data_dir: str):
        """초기화"""
        super().__init__(data_dir)
        self.clova_embedding = ClovaEmbeddingAPI()
        self.clova_segmentation = ClovaSegmentationClient()
        self.news_extractor = NewsContentExtractor()
    
    def _csv_to_summary_text(self, csv_file: Path) -> str:
        """CSV 파일을 LlamaIndex 방식으로 텍스트 변환"""
        try:
            df = pd.read_csv(csv_file)
            
            if df.empty:
                return f"파일명: {csv_file.name}\n데이터 없음"
            
            # LlamaIndex 방식으로 DataFrame을 텍스트로 변환
            text_parts = []
            
            # 파일명 정보
            text_parts.append(f"파일명: {csv_file.name}")
            text_parts.append(f"총 {len(df)}행, {len(df.columns)}컬럼")
            text_parts.append("")
            
            # KRX 데이터인 경우 특별 처리
            if 'ISU_ABBRV' in df.columns and 'TDD_CLSPRC' in df.columns:
                text_parts.append("=== KRX 일일거래정보 (70% 기준 필터링) ===")
                text_parts.append("")
                
                # 전체 데이터에서 거래대금 하위 70%와 등락률 하위 70%에서 겹치는 주식 제외
                df_processed = df.copy()
                
                # FLUC_RT 컬럼을 등락률로 사용
                df_processed['등락률'] = df_processed['FLUC_RT']
                df_processed['등락률_절대값'] = df_processed['등락률'].abs()
                
                # 거래대금 기준 하위 70% 찾기
                df_trading_value_sorted = df_processed.sort_values('ACC_TRDVAL', ascending=True)
                bottom_70_percent_trading = int(len(df_trading_value_sorted) * 0.7)
                low_trading_stocks = set(df_trading_value_sorted.head(bottom_70_percent_trading)['ISU_ABBRV'].tolist())
                
                # 등락률 기준 하위 70% 찾기 (절대값 기준)
                df_change_rate_sorted = df_processed.sort_values('등락률_절대값', ascending=True)
                bottom_70_percent_change = int(len(df_change_rate_sorted) * 0.7)
                low_change_stocks = set(df_change_rate_sorted.head(bottom_70_percent_change)['ISU_ABBRV'].tolist())
                
                # 겹치는 주식들 찾기
                overlapping_stocks = low_trading_stocks.intersection(low_change_stocks)
                
                # 겹치는 주식들을 제외한 최종 필터링
                df_final_filtered = df_processed[~df_processed['ISU_ABBRV'].isin(overlapping_stocks)]
                
                # 각 종목별로 읽기 쉬운 형태로 변환
                for idx, row in df_final_filtered.iterrows():
                    stock_name = row.get('ISU_ABBRV', '')
                    stock_code = row.get('ISU_CD', '')
                    
                    if stock_name and stock_code:
                        # 가격 정보
                        open_price = row.get('TDD_OPNPRC', 0)
                        high_price = row.get('TDD_HGPRC', 0)
                        low_price = row.get('TDD_LWPRC', 0)
                        close_price = row.get('TDD_CLSPRC', 0)
                        trading_value = row.get('ACC_TRDVAL', 0)
                        change_rate = row.get('FLUC_RT', 0.0)
                        
                        # 종목 정보를 읽기 쉬운 형태로 구성
                        stock_info = f"종목명: {stock_name}, 시가: {open_price}, 고가: {high_price}, 저가: {low_price}, 종가: {close_price}, 거래대금: {trading_value}, 등락률: {change_rate:.2f}"
                        text_parts.append(stock_info)
                
                text_parts.append("")
                text_parts.append(f"총 {len(df_final_filtered)}개 종목의 거래 정보 (70% 기준 필터링)")
            else:
                # 일반 CSV 파일 처리 (LlamaIndex 방식)
                text_parts.append("컬럼명:")
                for col in df.columns:
                    text_parts.append(f"  - {col}")
                text_parts.append("")
                
                # 데이터 샘플 (처음 10행)
                text_parts.append("데이터 샘플 (처음 10행):")
                sample_df = df.head(10)
                text_parts.append(sample_df.to_string(index=False))
            
            return "\n".join(text_parts)
            
        except Exception as e:
            print(f"❌ CSV 텍스트 변환 실패 ({csv_file.name}): {e}")
            return f"파일명: {csv_file.name} (변환 실패)"
    
    def _single_article_to_text(self, article: dict, article_index: int) -> str:
        """뉴스 기사를 LlamaIndex 방식으로 텍스트 변환"""
        try:
            text_parts = []
            
            # 기사 제목
            title = article.get('title', '')
            if title:
                text_parts.append(f"제목: {title}")
            
            # 기사 내용 (설명)
            description = article.get('description', '')
            if description:
                # HTML 태그 제거
                import re
                clean_description = re.sub(r'<[^>]+>', '', description)
                text_parts.append(f"내용: {clean_description}")
            
            # 발행일
            pub_date = article.get('pubDate', '')
            if pub_date:
                text_parts.append(f"발행일: {pub_date}")
            
            # 링크
            link = article.get('link', '')
            if link:
                text_parts.append(f"링크: {link}")
                
                # URL에서 전체 내용 추출 시도
                try:
                    full_content = self.news_extractor.extract_article_content(link)
                    if full_content and len(full_content) > 50:
                        text_parts.append(f"전체 내용: {full_content}")
                        print(f"✅ URL에서 전체 내용 추출 성공: {len(full_content)}자")
                    else:
                        print(f"⚠️ URL에서 내용 추출 실패")
                except Exception as e:
                    print(f"⚠️ URL 처리 실패: {e}")
            
            # 기사 번호
            text_parts.append(f"기사 번호: {article_index + 1}")
            
            return "\n".join(text_parts)
            
        except Exception as e:
            print(f"❌ 뉴스 기사 변환 실패: {e}")
            return f"뉴스 기사 {article_index + 1}: 처리 오류"
    
    def process_documents(self) -> bool:
        """문서 처리 및 벡터 생성"""
        try:
            print(f"📁 데이터 디렉토리: {self.data_dir}")
            
            # 디렉토리 확인
            data_path = Path(self.data_dir)
            if not data_path.exists():
                print(f"❌ 데이터 디렉토리가 존재하지 않습니다: {self.data_dir}")
                return False
            
            # 파일 목록 수집
            csv_files = list(data_path.glob("*.csv"))
            json_files = list(data_path.glob("*.json"))
            
            print(f"📊 발견된 파일:")
            print(f"  CSV 파일: {len(csv_files)}개")
            print(f"  JSON 파일: {len(json_files)}개")
            
            # 메타데이터 초기화
            metadata = []
            vectors = []
            
            # CSV 파일 처리
            for csv_file in csv_files:
                try:
                    print(f"\n📈 CSV 파일 처리: {csv_file.name}")
                    
                    # CSV를 요약 텍스트로 변환
                    summary_text = self._csv_to_summary_text(csv_file)
                    print(f"   요약 텍스트 길이: {len(summary_text)}자")
                    
                    # 텍스트를 청크로 분할
                    chunks = self._split_text(summary_text)
                    print(f"   생성된 청크: {len(chunks)}개")
                    
                    # 각 청크를 벡터로 변환
                    for i, chunk in enumerate(chunks):
                        try:
                            vector = self.clova_embedding.get_embedding(chunk)
                            if vector is not None:
                                vectors.append(vector)
                                metadata.append({
                                    'filename': csv_file.name,
                                    'chunk_index': i,
                                    'text_content': chunk,
                                    'file_type': 'csv',
                                    'stock_name': csv_file.stem
                                })
                                print(f"   ✅ 청크 {i+1} 벡터 생성 완료")
                            else:
                                print(f"   ❌ 청크 {i+1} 벡터 생성 실패")
                        except Exception as e:
                            print(f"   ❌ 청크 {i+1} 처리 오류: {e}")
                    
                except Exception as e:
                    print(f"❌ CSV 파일 처리 실패 ({csv_file.name}): {e}")
            
            # JSON 파일 처리 (뉴스 데이터)
            for json_file in json_files:
                try:
                    print(f"\n📰 JSON 파일 처리: {json_file.name}")
                    
                    with open(json_file, 'r', encoding='utf-8') as f:
                        news_data = json.load(f)
                    
                    # 뉴스 데이터에서 개별 기사 추출
                    all_articles = []
                    for stock_name, stock_data in news_data.get('stocks', {}).items():
                        for item in stock_data.get('items', []):
                            item['stock_name'] = stock_name
                            all_articles.append(item)
                    
                    print(f"   총 뉴스 기사: {len(all_articles)}개")
                    
                    # 각 기사를 개별적으로 처리
                    for article_index, article in enumerate(all_articles):
                        try:
                            # 기사를 텍스트로 변환
                            article_text = self._single_article_to_text(article, article_index)
                            print(f"   기사 {article_index + 1} 텍스트 길이: {len(article_text)}자")
                            
                            # 텍스트를 청크로 분할
                            chunks = self._split_text(article_text)
                            print(f"   기사 {article_index + 1} 청크: {len(chunks)}개")
                            
                            # 각 청크를 벡터로 변환
                            for chunk_index, chunk in enumerate(chunks):
                                try:
                                    vector = self.clova_embedding.get_embedding(chunk)
                                    if vector is not None:
                                        vectors.append(vector)
                                        metadata.append({
                                            'filename': json_file.name,
                                            'chunk_index': chunk_index,
                                            'text_content': chunk,
                                            'file_type': 'json',
                                            'article_index': article_index,
                                            'stock_name': article.get('stock_name', 'Unknown')
                                        })
                                        print(f"   ✅ 기사 {article_index + 1} 청크 {chunk_index + 1} 벡터 생성 완료")
                                    else:
                                        print(f"   ❌ 기사 {article_index + 1} 청크 {chunk_index + 1} 벡터 생성 실패")
                                except Exception as e:
                                    print(f"   ❌ 기사 {article_index + 1} 청크 {chunk_index + 1} 처리 오류: {e}")
                            
                        except Exception as e:
                            print(f"   ❌ 기사 {article_index + 1} 처리 오류: {e}")
                    
                except Exception as e:
                    print(f"❌ JSON 파일 처리 실패 ({json_file.name}): {e}")
            
            # 벡터와 메타데이터 저장
            if vectors and metadata:
                print(f"\n💾 벡터 및 메타데이터 저장")
                print(f"   총 벡터: {len(vectors)}개")
                print(f"   총 메타데이터: {len(metadata)}개")
                
                # 벡터 저장
                import numpy as np
                vectors_array = np.array(vectors)
                
                # 현재 스크립트 위치를 기준으로 상대 경로 설정
                current_dir = Path(__file__).parent
                vector_db_1_dir = current_dir.parent / "vector_db_1"
                vector_db_1_dir.mkdir(exist_ok=True)
                
                # FAISS 인덱스 저장
                import faiss
                dimension = vectors_array.shape[1]
                index = faiss.IndexFlatIP(dimension)
                index.add(vectors_array.astype('float32'))
                
                faiss.write_index(index, str(vector_db_1_dir / "hybrid_vectors.faiss"))
                
                # 메타데이터 저장
                with open(vector_db_1_dir / "hybrid_metadata.json", 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                print("✅ 벡터 및 메타데이터 저장 완료")
                return True
            else:
                print("❌ 저장할 벡터가 없습니다.")
                return False
                
        except Exception as e:
            print(f"❌ 문서 처리 중 오류: {e}")
            return False


class VectorDBAnalyzer:
    """Vector DB 기반 분석기"""
    
    def __init__(self):
        """초기화"""
        self.api_base_url = "http://localhost:8000"
        self.clova_client = self._create_clova_client()
    
    def _create_clova_client(self):
        """CLOVA 클라이언트 생성"""
        class CompletionExecutor:
            def __init__(self, host, api_key, request_id, model_endpoint=None):
                self.host = host
                self.api_key = api_key
                self.request_id = request_id
                self.model_endpoint = model_endpoint or "/v3/tasks/yl1fvofj/chat-completions"
            
            def _send_request(self, completion_request):
                """API 요청 전송"""
                import http.client
                import json
                
                request_message = json.dumps(completion_request)
                
                conn = http.client.HTTPSConnection(self.host)
                headers = {
                    'Content-Type': 'application/json',
                    'X-NCP-CLOVASTUDIO-API-KEY': self.api_key,
                    'X-NCP-APIGW-API-KEY': self.api_key
                }
                
                conn.request('POST', self.model_endpoint, request_message, headers)
                response = conn.getresponse()
                result = json.loads(response.read().decode(encoding='utf-8'))
                conn.close()
                return result
            
            def execute(self, completion_request):
                """실행"""
                try:
                    res = self._send_request(completion_request)
                    return res
                except Exception as e:
                    print(f'Exception: {e}')
                    return None
        
        # 환경 변수에서 설정 가져오기
        host = "clovastudio.apigw.ntruss.com"
        api_key = os.getenv("CLOVA_API_KEY")
        request_id = os.getenv("CLOVA_REQUEST_ID")
        
        return CompletionExecutor(host, api_key, request_id)
    
    def check_faiss_api_server(self) -> bool:
        """FAISS API 서버 상태 확인"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ FAISS API 서버 연결 실패: {e}")
            return False
    
    def search_vectors(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """벡터 검색"""
        try:
            response = requests.post(
                f"{self.api_base_url}/search",
                json={"query": query, "top_k": top_k},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()["results"]
            else:
                print(f"❌ 벡터 검색 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 벡터 검색 중 오류: {e}")
            return []
    
    def analyze_vectors(self) -> str:
        """벡터 분석"""
        try:
            # 관련 문서 검색
            query = "지난 24시간의 국내 주식 시장에서 가장 이슈가 된 주식 종목 3개를 알려주세요"
            results = self.search_vectors(query, top_k=15)
            
            if not results:
                return "관련 문서를 찾을 수 없습니다."
            
            # 텍스트 내용 추출
            text_contents = [result["text_content"] for result in results]
            
            # 분석 프롬프트 생성
            prompt = self._create_analysis_prompt(text_contents)
            
            # CLOVA API 호출
            completion_request = {
                'messages': [{'role': 'user', 'content': prompt}],
                'topP': 0.8,
                'temperature': 0.3,
                'maxTokens': 4000
            }
            
            response = self.clova_client.execute(completion_request)
            
            if response and 'choices' in response:
                return response['choices'][0]['message']['content']
            else:
                return "분석 결과를 생성할 수 없습니다."
                
        except Exception as e:
            print(f"❌ 벡터 분석 중 오류: {e}")
            return f"분석 중 오류가 발생했습니다: {e}"
    
    def _create_analysis_prompt(self, text_contents: List[str]) -> str:
        """분석 프롬프트 생성"""
        combined_text = "\n\n".join(text_contents)
        
        prompt = f"""
다음은 국내 주식 시장 관련 뉴스와 데이터입니다. 이를 바탕으로 지난 24시간의 국내 주식 시장에서 가장 이슈가 된 주식 종목 3개를 분석해주세요.

중요: 인사말이나 서론 없이 바로 분석 내용을 시작하세요.

분석 요구사항:
1. 가장 이슈가 된 주식 종목 3개를 선정
2. 각 종목별로 다음 정보 포함:
   - 종목명과 종목코드
   - 주가 변동 추이
   - 주요 뉴스 및 이슈
   - 투자 포인트
   - 주의사항

분석 형식:
## 📊 지난 24시간 국내 주식 시장 이슈 종목 분석

### 1. [종목명] (종목코드)
- **주가 변동**: [변동 내용]
- **주요 뉴스**: [뉴스 요약]
- **투자 포인트**: [투자 관점]
- **주의사항**: [리스크 요소]

### 2. [종목명] (종목코드)
[동일한 형식]

### 3. [종목명] (종목코드)
[동일한 형식]

## 📈 종합 분석
[전체적인 시장 동향 및 투자자 관점에서의 분석]

---

참고 데이터:
{combined_text}
"""
        
        return prompt
    
    def save_report(self, report: str) -> str:
        """보고서 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 현재 스크립트 위치를 기준으로 상대 경로 설정
            current_dir = Path(__file__).parent
            report_file = current_dir.parent / "data_2" / f"vector_db_report_{timestamp}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"💾 Vector DB 분석 보고서 저장: {report_file}")
            return report_file
            
        except Exception as e:
            print(f"❌ 보고서 저장 실패: {e}")
            return ""
    
    def run_analysis(self) -> bool:
        """분석 실행"""
        try:
            # FAISS API 서버 확인
            if not self.check_faiss_api_server():
                print("❌ FAISS API 서버가 실행되지 않았습니다.")
                return False
            
            # 벡터 분석
            analysis_result = self.analyze_vectors()
            
            if analysis_result:
                # 보고서 저장
                report_file = self.save_report(analysis_result)
                if report_file:
                    print("✅ Vector DB 기반 분석 완료")
                    return True
                else:
                    print("❌ 보고서 저장 실패")
                    return False
            else:
                print("❌ 분석 결과가 없습니다.")
                return False
                
        except Exception as e:
            print(f"❌ Vector DB 분석 중 오류: {e}")
            return False 