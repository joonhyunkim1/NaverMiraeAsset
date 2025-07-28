#!/usr/bin/env python3
"""
통합 데이터 수집 및 분석 테스트 스크립트
- KRX 일일거래정보 수집
- 네이버 뉴스 수집
- CLOVA 분석 및 주식 종목 추출
- Function Calling을 통한 주가 데이터 수집
"""

from datetime import datetime
from krx_api_client import KRXAPIClient
from naver_news_client import NaverNewsClient
from data_analyzer import DataAnalyzer
from stock_extractor import StockExtractor
from stock_news_collector import StockNewsCollector

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 통합 데이터 수집 테스트")
    print("📅 실행 시간:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    # ===== 뉴스 검색 파라미터 설정 =====
    # 테스트용: 뉴스 3개 (관련도순), KRX 데이터 상위 10개
    NEWS_CONFIG = {
        "query": "국내 주식 주가",  # 검색어
        "display": 100,           # 가져올 뉴스 개수 (최대 100)
        "start": 1,               # 검색 시작 위치
        "sort": "sim",            # 정렬 방법 ("sim": 관련도순, "date": 날짜순)
        "filter_by_date": True,   # 날짜 필터링 사용 여부
        "days_back": 1,           # 지난 몇 일 뉴스를 가져올지 (1 = 지난 1일)
        "target_count": 3         # 필터링 후 목표 뉴스 개수 (테스트용: 3개)
    }
    
    print(f"📰 뉴스 검색 설정: {NEWS_CONFIG}")
    
    # 1. KRX 일일거래정보 수집
    print("\n" + "=" * 60)
    print("📈 KRX 일일거래정보 수집")
    print("=" * 60)
    
    krx_client = KRXAPIClient()
    krx_filename = krx_client.collect_and_save_daily_data()
    
    # 2. 네이버 뉴스 수집
    print("\n" + "=" * 60)
    print("📰 네이버 뉴스 수집")
    print("=" * 60)
    
    news_client = NaverNewsClient()
    
    # API 정보 확인
    api_info = news_client.get_api_info()
    if not api_info['client_id_set'] or not api_info['client_secret_set']:
        print("❌ 네이버 API 키가 설정되지 않았습니다!")
        print("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 .env 파일에 설정하세요.")
        news_filename = None
    else:
        print("✅ 네이버 API 키 설정 완료")
        print(f"🔍 '{NEWS_CONFIG['query']}' 키워드로 뉴스 검색 중...")
        
        # 사용자 정의 파라미터로 뉴스 수집
        success = news_client.get_custom_news(
            query=NEWS_CONFIG["query"],
            display=NEWS_CONFIG["display"],
            start=NEWS_CONFIG["start"],
            sort=NEWS_CONFIG["sort"],
            filter_by_date=NEWS_CONFIG["filter_by_date"],
            days_back=NEWS_CONFIG["days_back"],
            target_count=NEWS_CONFIG["target_count"]
        )
        
        if success:
            print("✅ 뉴스 수집 완료")
            # 파일명은 naver_news_client에서 자동 생성됨
            news_filename = "수집 완료"
        else:
            print("❌ 뉴스 수집 실패")
            news_filename = None
    
    # 3. 결과 요약
    print("\n" + "=" * 60)
    print("📋 수집 결과 요약")
    print("=" * 60)
    
    if krx_filename:
        print(f"✅ KRX 데이터: {krx_filename}")
    else:
        print("❌ KRX 데이터 수집 실패")
    
    if news_filename:
        print(f"✅ 네이버 뉴스: {news_filename}")
    else:
        print("❌ 네이버 뉴스 수집 실패")
    
    # 4. CLOVA 분석 및 주식 종목 추출
    print("\n" + "=" * 60)
    print("🤖 CLOVA 분석 및 주식 종목 추출")
    print("=" * 60)
    
    # 데이터 분석기 초기화
    analyzer = DataAnalyzer()
    
    print("🔍 CLOVA 분석 시작...")
    analysis_success = analyzer.run_analysis()
    
    if analysis_success:
        print("✅ CLOVA 분석 완료")
        
        # 주식 종목 추출 및 데이터 수집
        print("\n📊 주식 종목 추출 및 데이터 수집 시작...")
        extractor = StockExtractor()
        extraction_success = extractor.run_extraction()
        
        if extraction_success:
            print("✅ 주식 종목 추출 및 데이터 수집 완료")
            
            # 5. 개별 종목 뉴스 수집
            print("\n" + "=" * 60)
            print("📰 개별 종목 뉴스 수집")
            print("=" * 60)
            
            # 추출된 종목명들을 가져와서 뉴스 수집
            # 실제로는 stock_extractor에서 추출된 종목명을 사용해야 함
            # 임시로 테스트용 종목명 사용
            extracted_stocks = ["미투온", "뉴로핏", "광명전기"]
            
            news_collector = StockNewsCollector()
            news_success = news_collector.run_collection(extracted_stocks)
            
            if news_success:
                print("✅ 개별 종목 뉴스 수집 완료")
            else:
                print("❌ 개별 종목 뉴스 수집 실패")
        else:
            print("❌ 주식 종목 추출 및 데이터 수집 실패")
    else:
        print("❌ CLOVA 분석 실패")
    
    print("\n🎉 통합 데이터 수집 및 분석 테스트 완료!")

if __name__ == "__main__":
    main() 