#!/usr/bin/env python3
"""
주식 데이터 수집 시스템 테스트 스크립트
"""

from stock_data_collector import StockDataCollector, format_tool_result
import pandas as pd

def test_stock_data_collector():
    """주식 데이터 수집 테스트"""
    print("=" * 60)
    print("📈 주식 데이터 수집 시스템 테스트")
    print("=" * 60)
    
    # StockDataCollector 인스턴스 생성
    collector = StockDataCollector()
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "삼성전자 (종목명)",
            "ticker": "삼성전자",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        },
        {
            "name": "005930 (종목코드)",
            "ticker": "005930",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        },
        {
            "name": "기본값 테스트 (2년간)",
            "ticker": "SK하이닉스"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 테스트 {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # 종목코드 변환 테스트
            stock_code = collector.get_stock_code(test_case['ticker'])
            print(f"종목코드 변환: {test_case['ticker']} → {stock_code}")
            
            if not stock_code:
                print(f"❌ 종목코드를 찾을 수 없습니다: {test_case['ticker']}")
                continue
            
            # 데이터 수집 테스트
            result = collector.get_stock_data(
                ticker=test_case['ticker'],
                start_date=test_case.get('start_date'),
                end_date=test_case.get('end_date')
            )
            
            if "error" in result:
                print(f"❌ 데이터 수집 실패: {result['error']}")
            else:
                print(f"✅ 데이터 수집 성공!")
                print(f"파일명: {result['filename']}")
                print(f"데이터 포인트: {result['data_points']:,}개")
                
                # CSV 파일 읽기 테스트
                try:
                    df = pd.read_csv(result['file_path'])
                    print(f"CSV 파일 읽기 성공: {df.shape}")
                    print(f"컬럼: {list(df.columns)}")
                    print(f"샘플 데이터:")
                    print(df.head(3))
                except Exception as e:
                    print(f"❌ CSV 파일 읽기 실패: {e}")
        
        except Exception as e:
            print(f"❌ 테스트 실패: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 테스트 완료!")

def test_format_tool_result():
    """도구 결과 포맷팅 테스트"""
    print("\n" + "=" * 60)
    print("📝 도구 결과 포맷팅 테스트")
    print("=" * 60)
    
    # 성공 케이스
    success_result = {
        "success": True,
        "ticker": "삼성전자",
        "stock_code": "005930",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "period": "daily",
        "filename": "삼성전자_005930_2024-01-01_2024-12-31_20250127_143022.csv",
        "data_points": 252,
        "file_path": "/Users/Chris/Desktop/JH/MiraeassetNaver/Individual_Stock_Search/data/삼성전자_005930_2024-01-01_2024-12-31_20250127_143022.csv",
        "summary": {
            "latest_close": 75000.0,
            "latest_date": "2024-12-31",
            "price_change": 5000.0,
            "price_change_pct": 7.14,
            "highest_price": 80000.0,
            "lowest_price": 65000.0,
            "avg_volume": 15000000.0,
            "total_volume": 3780000000
        }
    }
    
    formatted = format_tool_result(success_result)
    print("✅ 성공 케이스:")
    print(formatted)
    
    # 오류 케이스
    error_result = {
        "error": "종목코드를 찾을 수 없습니다: 존재하지않는종목"
    }
    
    formatted_error = format_tool_result(error_result)
    print("\n❌ 오류 케이스:")
    print(formatted_error)

if __name__ == "__main__":
    # 도구 결과 포맷팅 테스트
    test_format_tool_result()
    
    # 주식 데이터 수집 테스트 (실제 API 호출)
    print("\n" + "=" * 60)
    print("🧪 실제 데이터 수집 테스트 시작")
    print("=" * 60)
    test_stock_data_collector() 