#!/usr/bin/env python3
"""
뉴스 시간 분석 테스트 스크립트
"""

from datetime import datetime
from naver_news_client import NaverNewsClient
import pytz

def analyze_news_timeline():
    """뉴스 시간대 분석"""
    print("=" * 60)
    print("📰 '주가 국내 주식' 키워드 시간대 분석")
    print("=" * 60)
    
    # 네이버 뉴스 클라이언트 초기화
    news_client = NaverNewsClient()
    
    # API 정보 확인
    api_info = news_client.get_api_info()
    if not api_info['client_id_set'] or not api_info['client_secret_set']:
        print("❌ 네이버 API 키가 설정되지 않았습니다!")
        return
    
    print("✅ 네이버 API 키 설정 완료")
    
    # '주가 국내 주식' 키워드로 시간순 정렬하여 50개 검색
    print("\n🔍 '주가 국내 주식' 키워드로 시간순 정렬하여 50개 검색 중...")
    
    news_data = news_client.search_news(
        query="주가 국내 주식",
        display=50,
        start=1,
        sort="date"  # 시간순 정렬
    )
    
    if not news_data or 'items' not in news_data:
        print("❌ 뉴스 검색 실패!")
        return
    
    print(f"✅ 뉴스 검색 완료: {len(news_data['items'])}개")
    
    # 한국 시간대 설정
    korea_tz = pytz.timezone('Asia/Seoul')
    now_korea = datetime.now(korea_tz)
    
    print(f"\n📅 현재 시간: {now_korea.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print("\n" + "=" * 60)
    print("📊 뉴스 시간대 분석 결과")
    print("=" * 60)
    
    # 각 뉴스의 시간 분석
    time_analysis = []
    
    for i, item in enumerate(news_data['items'], 1):
        try:
            pub_date_str = item.get('pubDate', '')
            if pub_date_str:
                pub_date = news_client._parse_news_date(pub_date_str)
                if pub_date:
                    # 시간대 정보가 없는 경우 한국 시간으로 가정
                    if pub_date.tzinfo is None:
                        pub_date = korea_tz.localize(pub_date)
                    
                    # 시간 차이 계산
                    time_diff = now_korea - pub_date
                    hours_diff = time_diff.total_seconds() / 3600
                    
                    time_analysis.append({
                        'index': i,
                        'title': item.get('title', 'N/A')[:50],
                        'pub_date': pub_date,
                        'hours_ago': hours_diff,
                        'time_diff_str': str(time_diff)
                    })
                    
                    print(f"{i:2d}. {item.get('title', 'N/A')[:40]:40} | "
                          f"{pub_date.strftime('%m-%d %H:%M'):10} | "
                          f"{hours_diff:6.1f}시간 전")
                else:
                    print(f"{i:2d}. {item.get('title', 'N/A')[:40]:40} | 날짜 파싱 실패")
            else:
                print(f"{i:2d}. {item.get('title', 'N/A')[:40]:40} | pubDate 없음")
                
        except Exception as e:
            print(f"{i:2d}. {item.get('title', 'N/A')[:40]:40} | 오류: {e}")
    
    if time_analysis:
        # 통계 계산
        hours_list = [item['hours_ago'] for item in time_analysis]
        
        print("\n" + "=" * 60)
        print("📈 시간대 통계")
        print("=" * 60)
        print(f"총 뉴스 수: {len(time_analysis)}개")
        print(f"가장 최신: {min(hours_list):.1f}시간 전")
        print(f"가장 오래된: {max(hours_list):.1f}시간 전")
        print(f"평균: {sum(hours_list)/len(hours_list):.1f}시간 전")
        
        # 시간대별 분포
        print("\n📊 시간대별 분포:")
        ranges = [
            (0, 1, "1시간 이내"),
            (1, 3, "1-3시간 전"),
            (3, 6, "3-6시간 전"),
            (6, 12, "6-12시간 전"),
            (12, 24, "12-24시간 전"),
            (24, float('inf'), "24시간 이상")
        ]
        
        for min_hours, max_hours, label in ranges:
            count = sum(1 for hours in hours_list if min_hours <= hours < max_hours)
            percentage = (count / len(hours_list)) * 100
            print(f"  {label}: {count}개 ({percentage:.1f}%)")
    
    print("\n" + "=" * 60)
    print("✅ 시간대 분석 완료!")
    print("=" * 60)

if __name__ == "__main__":
    analyze_news_timeline() 