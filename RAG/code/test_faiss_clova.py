#!/usr/bin/env python3
"""
FAISS 벡터 검색 API + CLOVA 연동 테스트
- API 서버에서 벡터 검색 결과 받아오기
- 검색된 텍스트를 CLOVA에게 전달
- CLOVA가 실제 관련 데이터를 바탕으로 분석하는지 확인
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import List, Dict, Any

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from clova_chat_client import ClovaChatClient

class FAISSClovaTester:
    def __init__(self):
        self.chat_client = ClovaChatClient()
        self.api_base_url = "http://localhost:8000"
    
    def test_api_connection(self):
        """API 서버 연결 테스트"""
        print("🔍 API 서버 연결 테스트 중...")
        
        try:
            # 헬스 체크
            response = requests.get(f"{self.api_base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API 서버 연결 성공")
                print(f"   벡터 로드: {data.get('vectors_loaded', 0)}개")
                print(f"   FAISS 인덱스: {'구축됨' if data.get('faiss_index_built') else '미구축'}")
                return True
            else:
                print(f"❌ API 서버 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API 서버 연결 오류: {e}")
            return False
    
    def search_vectors(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """API 서버에서 벡터 검색"""
        try:
            response = requests.post(
                f"{self.api_base_url}/search",
                json={"query": query, "top_k": top_k}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("results", [])
            else:
                print(f"❌ 검색 요청 실패: {response.status_code}")
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
    
    def test_clova_with_vector_search(self, query: str):
        """벡터 검색 결과를 CLOVA에게 전달하여 테스트"""
        print(f"\n🔍 검색어: {query}")
        
        # 1. 벡터 검색
        print("📊 FAISS 벡터 검색 중...")
        results = self.search_vectors(query, top_k=3)
        
        if not results:
            print("❌ 검색 결과가 없습니다.")
            return
        
        print(f"✅ 검색 완료: {len(results)}개 결과")
        
        # 2. 컨텍스트 생성
        context = self.create_context_from_results(query, results)
        
        # 3. CLOVA에게 전달
        print("🤖 CLOVA 분석 중...")
        
        messages = [
            {
                "role": "system", 
                "content": "당신은 주식 시장 데이터 분석 전문가입니다. 제공된 데이터를 바탕으로 구체적이고 정확한 분석을 제공해주세요."
            },
            {
                "role": "user", 
                "content": f"{context}\n\n위 데이터를 바탕으로 다음을 분석해주세요:\n1. 주요 이슈나 종목\n2. 구체적인 수치나 정보\n3. 투자자들이 주목할 포인트"
            }
        ]
        
        try:
            response = self.chat_client.create_chat_completion(messages)
            
            print("\n" + "=" * 60)
            print("✅ CLOVA 분석 결과")
            print("=" * 60)
            print(response)
            
        except Exception as e:
            print(f"❌ CLOVA 분석 중 오류: {e}")
    
    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("=" * 60)
        print("🧪 FAISS + CLOVA 종합 테스트")
        print("=" * 60)
        
        # 1. API 서버 연결 테스트
        if not self.test_api_connection():
            print("❌ API 서버 연결 실패!")
            return
        
        # 2. 다양한 질문으로 테스트
        test_queries = [
            "삼성전자 주가 상황",
            "하이브 세무조사 관련 뉴스",
            "거래대금이 많은 종목들",
            "주식 시장 주요 이슈",
            "ETF 관련 뉴스"
        ]
        
        for query in test_queries:
            self.test_clova_with_vector_search(query)
            print("\n" + "-" * 40)
        
        print("\n🎉 종합 테스트 완료!")

def main():
    """메인 함수"""
    tester = FAISSClovaTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main() 