#!/usr/bin/env python3
"""
뉴스 RAG 시스템 통합 테스트 스크립트
"""

from naver_news_client import NaverNewsClient
from news_content_extractor import NewsContentExtractor
from llamaindex_rag_system import LlamaIndexRAGSystem
import os
from pathlib import Path

def test_news_rag_system():
    """뉴스 RAG 시스템 통합 테스트"""
    print("=" * 60)
    print("뉴스 RAG 시스템 통합 테스트")
    print("=" * 60)
    
    # 1. 네이버 뉴스 API로 최신 뉴스 3개 가져오기
    print("\n1️⃣ 네이버 뉴스 API로 최신 뉴스 가져오기...")
    news_client = NaverNewsClient()
    
    # API 키 확인
    api_info = news_client.get_api_info()
    if not api_info['client_id_set'] or not api_info['client_secret_set']:
        print("❌ 네이버 API 키가 설정되지 않았습니다!")
        return
    
    # '금융' 관련 최신 뉴스 10개 가져오기
    success = news_client.get_latest_finance_news(count=10)
    if not success:
        print("❌ 뉴스 가져오기 실패!")
        return
    
    print("✅ 뉴스 가져오기 완료!")
    
    # 2. 뉴스 본문 추출
    print("\n2️⃣ 뉴스 본문 추출...")
    extractor = NewsContentExtractor()
    
    # 가장 최근 뉴스 JSON 파일 찾기
    data_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data")
    news_files = list(data_dir.glob("naver_news_*.json"))
    
    if not news_files:
        print("❌ 뉴스 JSON 파일을 찾을 수 없습니다!")
        return
    
    # 가장 최근 파일 선택
    latest_news_file = max(news_files, key=lambda x: x.stat().st_mtime)
    print(f"처리할 뉴스 파일: {latest_news_file.name}")
    
    # 본문 추출
    success = extractor.extract_and_save_articles(latest_news_file.name)
    if not success:
        print("❌ 본문 추출 실패!")
        return
    
    print("✅ 뉴스 본문 추출 완료!")
    
    # 3. LlamaIndex RAG 시스템 테스트
    print("\n3️⃣ LlamaIndex RAG 시스템 테스트...")
    rag_system = LlamaIndexRAGSystem()
    
    # 인덱스 구축 (뉴스 본문 포함)
    print("인덱스 구축 중...")
    if not rag_system.build_index(rebuild=True):
        print("❌ 인덱스 구축 실패!")
        return
    
    # 리트리버 설정
    if not rag_system.setup_retriever():
        print("❌ 리트리버 설정 실패!")
        return
    
    print("✅ RAG 시스템 설정 완료!")
    
    # 4. 뉴스 요약 테스트
    print("\n4️⃣ 뉴스 요약 테스트...")
    test_query = "가장 최근 '금융' 관련 뉴스를 1개 요약해줘"
    
    print(f"질문: {test_query}")
    result = rag_system.ask(test_query)
    
    if result["success"]:
        print(f"\n답변: {result['answer']}")
        
        # 소스 정보 출력
        if result.get("source_nodes"):
            print(f"\n참고한 문서: {len(result['source_nodes'])}개")
            for i, node in enumerate(result["source_nodes"][:3], 1):
                doc_type = node['metadata'].get('type', 'Unknown')
                filename = node['metadata'].get('filename', 'Unknown')
                print(f"  {i}. [{doc_type}] {filename}")
                if doc_type == 'news_article':
                    url = node['metadata'].get('url', 'N/A')
                    print(f"     URL: {url}")
    else:
        print(f"❌ 오류: {result['error']}")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_news_rag_system() 