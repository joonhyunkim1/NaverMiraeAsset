#!/usr/bin/env python3
"""
CSV 데이터 기반 RAG 시스템 메인 실행 파일 (LlamaIndex 기반)
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from llamaindex_rag_system import LlamaIndexRAGSystem

def load_environment():
    """환경 변수를 로드합니다."""
    # .env 파일 로드
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print("환경 변수 로드 완료")
    else:
        print("경고: .env 파일이 없습니다.")
        print("다음 내용으로 .env 파일을 생성하세요:")
        print("CLOVA_API_KEY=your_clova_api_key_here")
        print("CLOVA_EMBEDDING_REQUEST_ID=your_embedding_request_id_here")
        print("CLOVA_CHAT_REQUEST_ID=your_chat_request_id_here")

def print_system_info(rag_system: LlamaIndexRAGSystem):
    """시스템 정보를 출력합니다."""
    print("\n" + "=" * 50)
    print("LlamaIndex RAG 시스템 정보")
    print("=" * 50)
    
    info = rag_system.get_system_info()
    
    print(f"데이터 디렉토리: {info['data_directory']}")
    print(f"인덱스 구축: {'완료' if info['index_built'] else '미완료'}")
    print(f"리트리버 설정: {'완료' if info['retriever_setup'] else '미완료'}")
    
    print("\n--- 모델 정보 ---")
    print(f"LLM 모델: {info['llm_model']}")
    print(f"임베딩 모델: {info['embedding_model']}")
    print(f"세그멘테이션 모델: {info['segmentation_model']}")
    
    print("\n--- API 키 설정 ---")
    print(f"CLOVA API 키: {'설정됨' if info['clova_api_key_set'] else '미설정'}")
    # print(f"CLOVA Embedding Request ID: {'설정됨' if info['clova_embedding_request_id_set'] else '미설정'}")
    # print(f"CLOVA Chat Request ID: {'설정됨' if info['clova_chat_request_id_set'] else '미설정'}")
    # print(f"HuggingFace API 키: {'설정됨' if info['huggingface_api_key_set'] else '미설정'}")
    
    if info.get('index_info'):
        print("\n--- 인덱스 정보 ---")
        index_info = info['index_info']
        print(f"총 노드 수: {index_info['total_nodes']}")
        print(f"벡터 저장소 타입: {index_info['vector_store_type']}")

def main():
    """메인 함수"""
    print("=" * 50)
    print("LlamaIndex 기반 RAG 시스템")
    print("CLOVA X Embedding + HyperCLOVA X")
    print("=" * 50)
    
    # 환경 변수 로드
    load_environment()
    
    # RAG 시스템 초기화
    rag_system = LlamaIndexRAGSystem()
    
    # 시스템 초기화
    rebuild_index = "--rebuild" in sys.argv
    if not rag_system.build_index(rebuild=rebuild_index):
        print("인덱스 구축 실패!")
        return
    
    # 리트리버 설정
    if not rag_system.setup_retriever():
        print("리트리버 설정 실패!")
        return
    
    # 시스템 정보 출력
    print_system_info(rag_system)
    
    # 사용자 선택
    while True:
        print("\n" + "=" * 50)
        print("메뉴 선택:")
        print("1. 단일 질문하기")
        print("2. 대화형 채팅 모드")
        print("3. 시스템 정보 보기")
        print("4. 종료")
        print("=" * 50)
        
        choice = input("선택하세요 (1-4): ").strip()
        
        if choice == "1":
            # 단일 질문
            query = input("\n질문을 입력하세요: ").strip()
            if query:
                result = rag_system.ask(query)
                if result["success"]:
                    print(f"\n답변: {result['answer']}")
                    
                    # 소스 정보 출력
                    # if result.get("source_nodes"):
                    #     print(f"\n참고한 문서: {len(result['source_nodes'])}개")
                    #     for i, node in enumerate(result["source_nodes"][:3], 1):
                    #         print(f"  {i}. {node['metadata'].get('filename', 'Unknown')}")
                    #         print(f"     내용: {node['content'][:100]}...")
                else:
                    print(f"\n오류: {result['error']}")
        
        elif choice == "2":
            # 대화형 채팅
            rag_system.interactive_chat()
        
        elif choice == "3":
            # 시스템 정보
            print_system_info(rag_system)
        
        elif choice == "4":
            print("시스템을 종료합니다.")
            break
        
        else:
            print("잘못된 선택입니다. 다시 선택해주세요.")

if __name__ == "__main__":
    main() 