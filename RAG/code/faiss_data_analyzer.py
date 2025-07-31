#!/usr/bin/env python3
"""
FAISS 벡터 검색 기반 데이터 분석기
- FAISS API 서버에서 벡터 검색 수행
- 검색된 관련 텍스트를 CLOVA에게 전달
- 실제 벡터 검색을 활용한 RAG 시스템
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from clova_chat_client import ClovaChatClient
from hybrid_vector_manager import HybridVectorManager

class FAISSDataAnalyzer:
    def __init__(self):
        self.chat_client = ClovaChatClient()
        self.vector_manager = HybridVectorManager()
        self.api_base_url = "http://localhost:8000"
        self.data_1_path = current_dir.parent / "data_1"
        self.data_1_path.mkdir(exist_ok=True)
    
    def check_api_server(self):
        """API 서버 연결 확인"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FAISS API 서버 연결 성공")
                print(f"   벡터 로드: {data.get('vectors_loaded', 0)}개")
                print(f"   FAISS 인덱스: {'구축됨' if data.get('faiss_index_built') else '미구축'}")
                return True
            else:
                print(f"❌ API 서버 응답 오류: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API 서버 연결 실패: {e}")
            print("💡 FAISS API 서버를 먼저 실행해주세요: python faiss_vector_api.py")
            return False
    
    def search_vectors(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """FAISS API 서버에서 벡터 검색"""
        try:
            response = requests.post(
                f"{self.api_base_url}/search",
                json={"query": query, "top_k": top_k},
                timeout=120
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                print(f"❌ 검색 요청 실패: {response.status_code}")
                return []
        except requests.exceptions.Timeout:
            print(f"❌ 검색 타임아웃 (120초)")
            return []
        except Exception as e:
            print(f"❌ 검색 중 오류: {e}")
            return []
    
    def create_context_from_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """검색 결과를 컨텍스트로 변환"""
        if not results:
            return f"질문: {query}\n\n관련된 데이터를 찾을 수 없습니다."
        
        context = f"질문: {query}\n\n관련 데이터:\n"
        
        for i, result in enumerate(results, 1):
            context += f"\n=== 관련 데이터 {i} ===\n"
            context += f"유사도: {result['similarity']:.4f}\n"
            context += f"타입: {result['type']}\n"
            context += f"파일: {result['filename']}\n"
            
            if result.get('title'):
                context += f"제목: {result['title']}\n"
            
            context += f"내용:\n{result['text_content']}\n"
        
        return context
    
    def run_analysis(self, rebuild_vectors: bool = False):
        """FAISS 벡터 검색 기반 분석 실행"""
        print("\n" + "=" * 60)
        print("🔍 FAISS 벡터 검색 기반 분석")
        print("=" * 60)
        
        # 1. API 서버 연결 확인
        if not self.check_api_server():
            return False
        
        # 2. 벡터 재구축 (필요한 경우)
        if rebuild_vectors:
            print("\n📊 벡터 재구축 중...")
            if not self.vector_manager.process_documents():
                print("❌ 벡터 재구축 실패!")
                return False
            print("✅ 벡터 재구축 완료")
        else:
            print("\n📊 기존 벡터 사용 중...")
            # 기존 벡터 파일이 있는지 확인
            vector_file = self.vector_manager.vector_dir / "hybrid_vectors.pkl"
            metadata_file = self.vector_manager.vector_dir / "hybrid_metadata.json"
            
            if not vector_file.exists() or not metadata_file.exists():
                print("❌ 기존 벡터 파일이 없습니다!")
                print("벡터 재구축을 시도합니다...")
                if not self.vector_manager.process_documents():
                    print("❌ 벡터 재구축 실패!")
                    return False
                print("✅ 벡터 재구축 완료")
            else:
                print("✅ 기존 벡터 파일 확인됨")
        
        # 3. 분석 질문 정의
        analysis_query = "지난 24시간의 국내 주식 시장에서 가장 이슈가 된 주식 종목 3개를 알려주세요"
        
        # 4. FAISS 벡터 검색 수행
        print("\n🔍 FAISS 벡터 검색 중...")
        search_results = self.search_vectors(analysis_query, top_k=10)
        
        if not search_results:
            print("❌ 벡터 검색 결과가 없습니다!")
            return False
        
        print(f"✅ 검색 완료: {len(search_results)}개 결과")
        
        # 5. 컨텍스트 생성
        context = self.create_context_from_results(analysis_query, search_results)
        
        # 6. CLOVA 분석
        print("\n🤖 CLOVA 분석 중...")
        
        messages = [
            {
                "role": "system", 
                "content": "당신은 주식 시장 데이터 분석 전문가입니다. 제공된 데이터를 바탕으로 이슈가 되는 종목에 대한 데이터를 수집하기 위한 종목명이 필요합니다. 이슈가 되는 종목명 3개를 알려주세요."
            },
            {
                "role": "user", 
                "content": context
            }
        ]
        
        try:
            response = self.chat_client.create_chat_completion(messages)
            
            # 7. 결과 저장 (data_2 폴더에 저장)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_2") / f"faiss_analysis_{timestamp}.json"
            
            result_data = {
                "timestamp": datetime.now().isoformat(),
                "query": analysis_query,
                "search_results_count": len(search_results),
                "result": response,  # stock_extractor.py와 호환되도록 변경
                "clova_response": response,
                "search_results": search_results
            }
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ 분석 결과 저장 완료: {result_file}")
            print(f"📝 응답 길이: {len(response)} 문자")
            
            return True
            
        except Exception as e:
            print(f"❌ CLOVA 분석 중 오류: {e}")
            return False

def main():
    """테스트 함수"""
    analyzer = FAISSDataAnalyzer()
    success = analyzer.run_analysis(rebuild_vectors=True)
    
    if success:
        print("\n🎉 FAISS 벡터 검색 기반 분석 완료!")
    else:
        print("\n❌ FAISS 벡터 검색 기반 분석 실패!")

if __name__ == "__main__":
    main() 