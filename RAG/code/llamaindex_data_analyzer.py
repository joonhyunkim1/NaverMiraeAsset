#!/usr/bin/env python3
"""
LlamaIndex RAG 기반 데이터 분석 시스템
- KRX 일일 주가 데이터 및 뉴스 데이터를 Vector DB에 저장
- CLOVA 모델에게 Vector DB에서 검색된 관련 문서를 전달하여 이슈 종목 추출
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# LlamaIndex RAG 시스템
from llamaindex_rag_system import LlamaIndexRAGSystem

# 환경변수 로드
env_path = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/code/.env")
load_dotenv(env_path)

class LlamaIndexDataAnalyzer:
    """LlamaIndex RAG 기반 데이터 분석 클래스"""
    
    def __init__(self):
        self.data_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data")
        self.output_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1")
        self.output_dir.mkdir(exist_ok=True)
        
        # LlamaIndex RAG 시스템 초기화
        self.rag_system = LlamaIndexRAGSystem(str(self.data_dir))
        
        print("🔧 LlamaIndexDataAnalyzer 초기화 완료")
        print(f"📁 데이터 디렉토리: {self.data_dir}")
        print(f"📁 출력 디렉토리: {self.output_dir}")
    
    def build_vector_index(self, rebuild: bool = False) -> bool:
        """Vector DB 인덱스 구축"""
        try:
            print("=" * 60)
            print("🏗️ Vector DB 인덱스 구축")
            print("=" * 60)
            
            # LlamaIndex RAG 시스템으로 인덱스 구축
            success = self.rag_system.build_index(rebuild=rebuild)
            
            if success:
                print("✅ Vector DB 인덱스 구축 완료")
                
                # 시스템 정보 출력
                system_info = self.rag_system.get_system_info()
                print(f"📊 인덱스 정보:")
                print(f"  - 총 노드 수: {system_info.get('index_info', {}).get('total_nodes', 'N/A')}")
                print(f"  - 벡터 스토어 타입: {system_info.get('index_info', {}).get('vector_store_type', 'N/A')}")
                
                return True
            else:
                print("❌ Vector DB 인덱스 구축 실패")
                return False
                
        except Exception as e:
            print(f"❌ Vector DB 인덱스 구축 오류: {e}")
            return False
    
    def setup_retriever(self) -> bool:
        """리트리버 설정"""
        try:
            print("\n🔍 리트리버 설정 중...")
            
            success = self.rag_system.setup_retriever()
            
            if success:
                print("✅ 리트리버 설정 완료")
                return True
            else:
                print("❌ 리트리버 설정 실패")
                return False
                
        except Exception as e:
            print(f"❌ 리트리버 설정 오류: {e}")
            return False
    
    def analyze_with_rag(self) -> Optional[str]:
        """RAG 시스템을 사용하여 이슈 종목 분석"""
        try:
            print("\n🤖 RAG 시스템으로 이슈 종목 분석 중...")
            
            # 이슈 종목 추출을 위한 질문
            analysis_query = """
지난 24시간의 국내 주식 시장 데이터를 분석하여 이슈가 되었던 주식 종목들을 추출해주세요.

다음 정보를 포함해서 JSON 형태로 답변해주세요:
1. 종목명
2. 이슈가 된 이유 (뉴스 내용 기반)
3. 주가 변동 상황
4. 향후 전망

예시 형식:
```json
[
    {
        "종목명": "종목명",
        "이슈가 된 이유": "이슈 이유",
        "주가 변동 상황": "주가 변동 상황",
        "향후 전망": "향후 전망"
    }
]
```
"""
            
            # RAG 시스템으로 질문
            result = self.rag_system.ask(analysis_query)
            
            if result["success"]:
                print("✅ RAG 분석 완료")
                print(f"📝 응답 길이: {len(result['answer'])} 문자")
                
                # 소스 정보 출력
                if result.get("source_nodes"):
                    print(f"📚 참고한 문서: {len(result['source_nodes'])}개")
                    for i, node in enumerate(result["source_nodes"][:3], 1):
                        filename = node['metadata'].get('filename', 'Unknown')
                        print(f"  {i}. {filename}")
                
                return result["answer"]
            else:
                print(f"❌ RAG 분석 실패: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ RAG 분석 오류: {e}")
            return None
    
    def save_analysis_result(self, result: str, filename: str = None) -> str:
        """분석 결과 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"llamaindex_analysis_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        try:
            # JSON 형태로 저장
            analysis_data = {
                "analysis_time": datetime.now().isoformat(),
                "analysis_method": "LlamaIndex RAG",
                "result": result
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 분석 결과 저장 완료: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ 분석 결과 저장 실패: {e}")
            return ""
    
    def run_analysis(self) -> bool:
        """전체 분석 프로세스 실행"""
        print("=" * 60)
        print("🚀 LlamaIndex RAG 기반 데이터 분석 시스템")
        print("=" * 60)
        
        # 1. Vector DB 인덱스 구축
        print("\n1️⃣ Vector DB 인덱스 구축 중...")
        index_success = self.build_vector_index(rebuild=True)  # 새로운 인덱스 구축
        
        if not index_success:
            print("❌ Vector DB 인덱스 구축 실패")
            return False
        
        # 2. 리트리버 설정
        print("\n2️⃣ 리트리버 설정 중...")
        retriever_success = self.setup_retriever()
        
        if not retriever_success:
            print("❌ 리트리버 설정 실패")
            return False
        
        # 3. RAG 분석 실행
        print("\n3️⃣ RAG 분석 실행 중...")
        analysis_result = self.analyze_with_rag()
        
        if analysis_result is None:
            print("❌ RAG 분석 실패")
            return False
        
        # 4. 분석 결과 저장
        print("\n4️⃣ 분석 결과 저장 중...")
        saved_path = self.save_analysis_result(analysis_result)
        
        if saved_path:
            print(f"\n🎉 LlamaIndex RAG 분석 완료!")
            print(f"📁 결과 파일: {saved_path}")
            return True
        
        print("\n❌ 분석 결과 저장 실패")
        return False

def main():
    """메인 실행 함수"""
    analyzer = LlamaIndexDataAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("\n✅ 전체 LlamaIndex RAG 분석 프로세스 완료!")
    else:
        print("\n❌ LlamaIndex RAG 분석 프로세스 실패!")

if __name__ == "__main__":
    main() 