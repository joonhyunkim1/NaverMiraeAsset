#!/usr/bin/env python3
"""
네이버 뉴스 API 테스트 스크립트
"""

from naver_news_client import NaverNewsClient

def test_naver_news():
    """네이버 뉴스 API 테스트"""
    print("=" * 50)
    print("네이버 뉴스 API 테스트")
    print("=" * 50)
    
    # 네이버 뉴스 클라이언트 초기화
    news_client = NaverNewsClient()
    
    # API 정보 확인
    api_info = news_client.get_api_info()
    print(f"\nAPI 정보:")
    print(f"  Client ID 설정: {'완료' if api_info['client_id_set'] else '미완료'}")
    print(f"  Client Secret 설정: {'완료' if api_info['client_secret_set'] else '미완료'}")
    
    if not api_info['client_id_set'] or not api_info['client_secret_set']:
        print("\n❌ 네이버 API 키가 설정되지 않았습니다!")
        print("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 .env 파일에 설정하세요.")
        return
    
    # '금융' 관련 최신 뉴스 가져오기
    print(f"\n'금융' 관련 최신 뉴스 가져오기...")
    success = news_client.get_latest_finance_news()
    
    if success:
        print("✅ 뉴스 데이터 가져오기 및 저장 성공!")
    else:
        print("❌ 뉴스 데이터 가져오기 실패!")
    
    print("\n테스트 완료!")

if __name__ == "__main__":
    test_naver_news() 