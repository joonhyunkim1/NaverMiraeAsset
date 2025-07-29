#!/usr/bin/env python3
"""
CLOVA 벡터 관리 시스템을 사용하는 데이터 분석기
- CLOVA와 호환되는 벡터를 직접 사용
- CLOVA Chat API로 벡터 기반 분석
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from clova_vector_manager import ClovaVectorManager
from clova_chat_client import ClovaChatClient


class ClovaDataAnalyzer:
    """CLOVA 벡터 기반 데이터 분석기"""
    
    def __init__(self):
        self.data_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data")
        self.output_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1")
        self.output_dir.mkdir(exist_ok=True)
        
        # CLOVA 벡터 관리자 초기화
        self.vector_manager = ClovaVectorManager()
        
        # CLOVA Chat 클라이언트 초기화
        self.chat_client = ClovaChatClient()
        
        print("🔧 ClovaDataAnalyzer 초기화 완료")
        print(f"📁 데이터 디렉토리: {self.data_dir}")
        print(f"📁 출력 디렉토리: {self.output_dir}")
    
    def analyze_with_vectors(self, query: str) -> Optional[str]:
        """벡터 기반 분석 수행"""
        try:
            print(f"질문: {query}")
            print("CLOVA 벡터 기반 분석 시작...")
            
            # 벡터와 메타데이터 가져오기
            vectors, metadata = self.vector_manager.get_vectors_for_analysis()
            
            if not vectors:
                print("❌ 분석할 벡터가 없습니다.")
                return None
            
            print(f"📊 사용할 벡터: {len(vectors)}개")
            print(f"📊 벡터 차원: {len(vectors[0])}차원")
            
            # CLOVA Chat API로 벡터 기반 답변 생성
            print("HyperCLOVA X로 벡터 기반 답변 생성 중...")
            
            answer = self.chat_client.create_vector_based_response(query, vectors, metadata)
            
            if answer:
                print("✅ CLOVA 벡터 기반 분석 완료")
                print(f"📝 응답 길이: {len(answer)} 문자")
                
                # 벡터 메타데이터 정보 출력
                if metadata:
                    print(f"📚 벡터 메타데이터: {len(metadata)}개")
                    for i, meta in enumerate(metadata[:3], 1):
                        filename = meta.get('filename', 'Unknown')
                        vector_type = meta.get('type', 'Unknown')
                        print(f"  {i}. {filename} ({vector_type})")
                
                return answer
            else:
                print("❌ CLOVA 벡터 기반 답변 생성 실패")
                return None
                
        except Exception as e:
            print(f"❌ CLOVA 벡터 기반 분석 오류: {e}")
            return None
    
    def save_analysis_result(self, result: str, filename: str = None) -> str:
        """분석 결과 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clova_analysis_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        try:
            # JSON 형태로 저장
            analysis_data = {
                "analysis_time": datetime.now().isoformat(),
                "analysis_method": "CLOVA Vector-based Analysis",
                "result": result
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 분석 결과 저장 완료: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ 분석 결과 저장 실패: {e}")
            return ""
    
    def run_analysis(self, rebuild_vectors: bool = False) -> bool:
        """전체 분석 프로세스 실행"""
        print("=" * 60)
        print("🚀 CLOVA 벡터 기반 데이터 분석 시스템")
        print("=" * 60)
        
        # 1. 벡터 처리
        print("\n1️⃣ CLOVA 벡터 처리 중...")
        vector_success = self.vector_manager.process_documents(rebuild=rebuild_vectors)
        
        if not vector_success:
            print("❌ CLOVA 벡터 처리 실패")
            return False
        
        # 벡터 정보 출력
        vector_info = self.vector_manager.get_vector_info()
        print(f"📊 벡터 정보: {vector_info['total_vectors']}개, {vector_info['vector_dimension']}차원")
        
        # 2. CLOVA 벡터 기반 분석 실행
        print("\n2️⃣ CLOVA 벡터 기반 분석 실행 중...")
        
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
        
        analysis_result = self.analyze_with_vectors(analysis_query)
        
        if analysis_result is None:
            print("❌ CLOVA 벡터 기반 분석 실패")
            return False
        
        # 3. 분석 결과 저장
        print("\n3️⃣ 분석 결과 저장 중...")
        saved_path = self.save_analysis_result(analysis_result)
        
        if saved_path:
            print(f"\n🎉 CLOVA 벡터 기반 분석 완료!")
            print(f"📁 결과 파일: {saved_path}")
            return True
        
        print("\n❌ 분석 결과 저장 실패")
        return False


def main():
    """메인 실행 함수"""
    analyzer = ClovaDataAnalyzer()
    success = analyzer.run_analysis(rebuild_vectors=True)
    
    if success:
        print("\n✅ 전체 CLOVA 벡터 기반 분석 프로세스 완료!")
    else:
        print("\n❌ CLOVA 벡터 기반 분석 프로세스 실패!")


if __name__ == "__main__":
    main() 