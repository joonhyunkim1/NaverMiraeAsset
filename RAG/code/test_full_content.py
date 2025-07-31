#!/usr/bin/env python3
"""
전체 본문과 세그멘테이션 결과 비교 테스트
"""

from news_content_extractor import NewsContentExtractor
from clova_segmentation import ClovaSegmentationClient
import json

def test_full_content_vs_segmentation():
    """씨이랩 기사의 전체 본문과 세그멘테이션 결과 비교"""
    print("=" * 80)
    print("🔍 씨이랩 기사 전체 본문 vs 세그멘테이션 결과 비교")
    print("=" * 80)
    
    # 1. URL에서 전체 본문 추출
    url = "https://zdnet.co.kr/view/?no=20250729123501"
    extractor = NewsContentExtractor()
    
    print(f"📰 URL: {url}")
    print("\n" + "=" * 80)
    print("1️⃣ 전체 본문 추출")
    print("=" * 80)
    
    result = extractor.extract_article_content(url)
    
    if result:
        full_content = result['content']
        print(f"✅ 전체 본문 추출 성공: {len(full_content)}자")
        print("\n📝 전체 본문 내용:")
        print("-" * 80)
        print(full_content)
        print("-" * 80)
        
        # 2. 세그멘테이션 테스트
        print("\n" + "=" * 80)
        print("2️⃣ CLOVA 세그멘테이션 결과")
        print("=" * 80)
        
        segmentation_client = ClovaSegmentationClient()
        segments = segmentation_client.segment_text(full_content, max_length=1024)
        
        if segments:
            print(f"✅ 세그멘테이션 완료: {len(segments)}개 세그먼트")
            
            for i, segment in enumerate(segments):
                print(f"\n📄 세그먼트 {i+1} (길이: {len(segment)}자):")
                print("-" * 80)
                print(segment)
                print("-" * 80)
            
            # 3. 비교 분석
            print("\n" + "=" * 80)
            print("3️⃣ 비교 분석")
            print("=" * 80)
            
            total_segment_length = sum(len(segment) for segment in segments)
            print(f"📊 전체 본문 길이: {len(full_content)}자")
            print(f"📊 세그먼트 총 길이: {total_segment_length}자")
            
            if total_segment_length < len(full_content):
                print(f"❌ 데이터 손실 발생: {len(full_content) - total_segment_length}자")
                
                # 손실된 부분 찾기
                print("\n🔍 손실된 부분 확인:")
                print("전체 본문에서 세그먼트에 포함되지 않은 부분:")
                remaining_text = full_content
                for segment in segments:
                    if segment in remaining_text:
                        remaining_text = remaining_text.replace(segment, "", 1)
                
                if remaining_text.strip():
                    print(f"손실된 텍스트: {remaining_text.strip()}")
                else:
                    print("손실된 텍스트를 정확히 찾을 수 없습니다.")
            else:
                print("✅ 데이터 손실 없음")
        else:
            print("❌ 세그멘테이션 실패")
    else:
        print("❌ 본문 추출 실패")

if __name__ == "__main__":
    test_full_content_vs_segmentation() 