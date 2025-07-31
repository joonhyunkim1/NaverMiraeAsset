#!/usr/bin/env python3
"""
단일 뉴스 기사 본문 추출 테스트
"""

from news_content_extractor import NewsContentExtractor
import json

def test_single_article():
    """단일 뉴스 기사 본문 추출 테스트"""
    print("=" * 60)
    print("🔍 단일 뉴스 기사 본문 추출 테스트")
    print("=" * 60)
    
    # NewsContentExtractor 초기화
    extractor = NewsContentExtractor()
    
    # 테스트할 URL (씨이랩 기사)
    test_url = "https://zdnet.co.kr/view/?no=20250729123501"
    
    print(f"📰 테스트 URL: {test_url}")
    print("\n" + "=" * 60)
    
    # 본문 추출
    result = extractor.extract_article_content(test_url)
    
    if result:
        print("✅ 본문 추출 성공!")
        print(f"📊 본문 길이: {result['length']}자")
        print("\n📝 전체 본문 내용:")
        print("-" * 60)
        print(result['content'])
        print("-" * 60)
        
        # 본문이 잘리는지 확인
        if "..." in result['content'] or result['content'].endswith("..."):
            print("\n⚠️ 본문이 잘렸습니다!")
        else:
            print("\n✅ 본문이 완전합니다!")
            
    else:
        print("❌ 본문 추출 실패")

if __name__ == "__main__":
    test_single_article() 