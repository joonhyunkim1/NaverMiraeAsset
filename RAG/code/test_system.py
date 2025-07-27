#!/usr/bin/env python3
"""
LlamaIndex RAG 시스템 테스트 스크립트
"""

from llamaindex_rag_system import LlamaIndexRAGSystem

def test_system():
    """시스템 테스트"""
    print("=" * 50)
    print("LlamaIndex RAG 시스템 테스트")
    print("=" * 50)
    
    # RAG 시스템 초기화
    rag_system = LlamaIndexRAGSystem()
    
    # 시스템 정보 출력
    info = rag_system.get_system_info()
    print("\n시스템 정보:")
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 인덱스 구축 테스트
    print("\n인덱스 구축 테스트...")
    if rag_system.build_index(rebuild=True):
        print("✅ 인덱스 구축 성공!")
    else:
        print("❌ 인덱스 구축 실패!")
        return
    
    # 리트리버 설정 테스트
    print("\n리트리버 설정 테스트...")
    if rag_system.setup_retriever():
        print("✅ 리트리버 설정 성공!")
    else:
        print("❌ 리트리버 설정 실패!")
        return
    
    # 질문 테스트
    test_queries = [
        # "삼성전자 주식 정보"
        # "ETF 데이터",
        # "거래량이 많은 종목",
        # "종가 정보"
        "AP위성의 20250725 종가를 알려줘",
        "뉴스 중 집값에 관련된 뉴스의 내용을 요약해줘"
    ]
    
    print("\n질문 테스트:")
    for query in test_queries:
        print(f"\n질문: {query}")
        result = rag_system.ask(query)
        
        if result["success"]:
            print(f"답변: {result['answer'][:200]}...")
            if result.get("source_nodes"):
                print(f"참고 문서: {len(result['source_nodes'])}개")
        else:
            print(f"오류: {result['error']}")
    
    print("\n테스트 완료!")

if __name__ == "__main__":
    test_system() 