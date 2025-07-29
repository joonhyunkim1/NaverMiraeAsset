#!/usr/bin/env python3
"""
vector_db_hybrid 기반 CLOVA Chat API 테스트
- 저장된 임베딩 벡터를 로드
- CLOVA Chat API로 분석 요청
- 벡터 데이터 기반 답변 확인
"""

import os
import sys
import json
import pickle
from datetime import datetime
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from clova_chat_client import ClovaChatClient

class VectorChatTester:
    def __init__(self):
        self.chat_client = ClovaChatClient()
        self.vector_db_path = current_dir.parent / "vector_db_hybrid"
        self.vectors = []
        self.metadata = []
    
    def load_vectors(self):
        """저장된 벡터와 메타데이터 로드"""
        print("🔍 벡터 데이터 로드 중...")
        
        # 벡터 파일 로드
        vectors_file = self.vector_db_path / "hybrid_vectors.pkl"
        if vectors_file.exists():
            with open(vectors_file, 'rb') as f:
                self.vectors = pickle.load(f)
            print(f"✅ 벡터 로드 완료: {len(self.vectors)}개")
        else:
            print("❌ 벡터 파일을 찾을 수 없습니다!")
            return False
        
        # 메타데이터 파일 로드
        metadata_file = self.vector_db_path / "hybrid_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"✅ 메타데이터 로드 완료: {len(self.metadata)}개")
        else:
            print("❌ 메타데이터 파일을 찾을 수 없습니다!")
            return False
        
        return True
    
    def create_content_based_prompt(self, query: str) -> str:
        """메타데이터에서 실제 텍스트 내용을 추출하여 프롬프트 생성"""
        print("📝 실제 텍스트 내용 기반 프롬프트 생성 중...")
        
        # CSV 데이터와 뉴스 데이터 분리
        csv_contents = []
        news_contents = []
        
        for i, meta in enumerate(self.metadata):
            if meta.get('type') == 'csv':
                # CSV 데이터는 실제 종목 정보 포함
                text_content = meta.get('text_content', '')
                if text_content:
                    csv_contents.append(f"종목 데이터 {i+1}:\n{text_content}")
            elif meta.get('type') == 'news':
                # 뉴스 데이터는 제목과 실제 내용 포함
                title = meta.get('title', 'N/A')
                text_content = meta.get('text_content', '')
                if text_content:
                    news_contents.append(f"뉴스 {i+1} - {title}:\n{text_content}")
        
        # 프롬프트 구성
        prompt = f"""
다음은 한국 주식 시장의 최신 데이터입니다:

=== KRX 일일거래정보 (전 영업일) ===
총 {len([m for m in self.metadata if m.get('type') == 'csv'])}개 종목 데이터:
"""
        
        # CSV 데이터 (처음 5개만 - 너무 길어질 수 있으므로)
        for i, content in enumerate(csv_contents[:5]):
            prompt += f"\n{content}\n"
        
        if len(csv_contents) > 5:
            prompt += f"\n... 및 {len(csv_contents) - 5}개 더\n"
        
        prompt += f"""
=== 네이버 뉴스 기사 (지난 24시간) ===
총 {len([m for m in self.metadata if m.get('type') == 'news'])}개 뉴스 기사:
"""
        
        # 뉴스 데이터 (처음 5개만)
        for i, content in enumerate(news_contents[:5]):
            prompt += f"\n{content}\n"
        
        if len(news_contents) > 5:
            prompt += f"\n... 및 {len(news_contents) - 5}개 더\n"
        
        prompt += f"""
=== 질문 ===
{query}

위 데이터를 바탕으로 구체적인 종목명, 수치, 이슈를 포함하여 답변해주세요.
"""
        
        return prompt
    
    def analyze_vectors(self):
        """벡터 데이터 기반 분석 요청"""
        if not self.vectors or not self.metadata:
            print("❌ 벡터 데이터가 로드되지 않았습니다!")
            return False
        
        print("\n" + "=" * 60)
        print("🤖 CLOVA 벡터 기반 분석 테스트")
        print("=" * 60)
        
        # 분석 프롬프트
        query = """
다음을 분석해주세요:

1. 현재 주식 시장의 주요 이슈는 무엇인가요?
2. 거래량이나 등락률이 두드러지는 종목들은 어떤 것들이 있나요?
3. 뉴스에서 언급된 주요 종목이나 이슈는 무엇인가요?
4. 투자자들이 주목해야 할 포인트는 무엇인가요?

구체적인 종목명과 수치를 포함해서 답변해주세요.
"""
        
        # 실제 텍스트 내용 기반 프롬프트 생성
        prompt = self.create_content_based_prompt(query)
        
        print("📝 분석 요청 중...")
        print(f"📊 벡터 수: {len(self.vectors)}개")
        print(f"📋 메타데이터 수: {len(self.metadata)}개")
        
        try:
            # 일반 Chat API 호출 (벡터 통계 대신 실제 내용 사용)
            messages = [
                {"role": "system", "content": "당신은 주식 시장 데이터 분석 전문가입니다. 제공된 데이터를 바탕으로 구체적이고 정확한 분석을 제공해주세요."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.chat_client.create_chat_completion(messages)
            
            print("\n" + "=" * 60)
            print("✅ CLOVA 분석 결과")
            print("=" * 60)
            print(response)
            
            return True
            
        except Exception as e:
            print(f"❌ 분석 중 오류 발생: {e}")
            return False
    
    def test_simple_query(self):
        """간단한 질문으로 테스트"""
        if not self.vectors or not self.metadata:
            print("❌ 벡터 데이터가 로드되지 않았습니다!")
            return False
        
        print("\n" + "=" * 60)
        print("🔍 간단한 질문 테스트")
        print("=" * 60)
        
        simple_query = "이 데이터에서 가장 거래대금이 많은 종목 5개를 알려주세요."
        
        # 실제 텍스트 내용 기반 프롬프트 생성
        prompt = self.create_content_based_prompt(simple_query)
        
        try:
            messages = [
                {"role": "system", "content": "당신은 주식 시장 데이터 분석 전문가입니다. 제공된 데이터를 바탕으로 구체적이고 정확한 답변을 제공해주세요."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.chat_client.create_chat_completion(messages)
            
            print("📝 질문:", simple_query)
            print("\n💬 답변:")
            print(response)
            
            return True
            
        except Exception as e:
            print(f"❌ 테스트 중 오류 발생: {e}")
            return False
    
    def show_vector_info(self):
        """벡터 정보 요약"""
        print("\n" + "=" * 60)
        print("📊 벡터 데이터 정보")
        print("=" * 60)
        
        # 파일 타입별 통계
        file_types = {}
        for meta in self.metadata:
            file_type = meta.get('type', 'unknown')
            if file_type not in file_types:
                file_types[file_type] = 0
            file_types[file_type] += 1
        
        print("📁 파일 타입별 벡터 수:")
        for file_type, count in file_types.items():
            print(f"  - {file_type}: {count}개")
        
        print(f"\n📈 총 벡터 수: {len(self.vectors)}개")
        print(f"📋 총 메타데이터 수: {len(self.metadata)}개")
        
        # 샘플 메타데이터 출력
        if self.metadata:
            print("\n📄 샘플 메타데이터:")
            sample = self.metadata[0]
            print(f"  - 파일: {sample.get('filename', 'N/A')}")
            print(f"  - 타입: {sample.get('type', 'N/A')}")
            print(f"  - 제목: {sample.get('title', 'N/A')}")
            print(f"  - 텍스트 길이: {sample.get('text_length', 'N/A')}")

def main():
    """메인 실행 함수"""
    print("🚀 벡터 기반 CLOVA Chat 테스트")
    print("📅 실행 시간:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    tester = VectorChatTester()
    
    # 1. 벡터 데이터 로드
    if not tester.load_vectors():
        print("❌ 벡터 데이터 로드 실패")
        return
    
    # 2. 벡터 정보 표시
    tester.show_vector_info()
    
    # 3. 간단한 질문 테스트
    if not tester.test_simple_query():
        print("❌ 간단한 질문 테스트 실패")
        return
    
    # 4. 상세 분석 테스트
    if not tester.analyze_vectors():
        print("❌ 상세 분석 테스트 실패")
        return
    
    print("\n🎉 모든 테스트 완료!")

if __name__ == "__main__":
    main() 