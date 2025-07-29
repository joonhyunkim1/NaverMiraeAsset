#!/usr/bin/env python3
"""
선정된 개별 종목들의 네이버 뉴스 수집 시스템
- CLOVA 분석 결과에서 추출된 종목들의 관련 뉴스 수집
- 관련도 순으로 각 종목별 3개씩 뉴스 수집
"""

import json
import requests
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# 환경변수 로드
env_path = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/code/.env")
load_dotenv(env_path)

class StockNewsCollector:
    """개별 종목 뉴스 수집 클래스"""
    
    def __init__(self):
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        self.output_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1")
        self.output_dir.mkdir(exist_ok=True)
        
        print("🔧 StockNewsCollector 초기화 완료")
        print(f"📁 출력 디렉토리: {self.output_dir}")
        
        # API 키 확인
        if not self.client_id or not self.client_secret:
            print("❌ 네이버 API 키가 설정되지 않았습니다!")
            print("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 .env 파일에 설정하세요.")
    
    def get_api_info(self) -> Dict[str, bool]:
        """API 정보 확인"""
        return {
            'client_id_set': bool(self.client_id),
            'client_secret_set': bool(self.client_secret)
        }
    
    def search_news(self, query: str, display: int = 100, start: int = 1, sort: str = "sim") -> Optional[Dict[str, Any]]:
        """네이버 뉴스 검색 API 호출"""
        if not self.client_id or not self.client_secret:
            print("❌ 네이버 API 키가 설정되지 않았습니다.")
            return None
        
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        params = {
            "query": query,
            "display": display,
            "start": start,
            "sort": sort  # "sim": 관련도순, "date": 최신순
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API 오류: {response.status_code}")
                print(f"오류 내용: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 요청 오류: {e}")
            return None
    
    def collect_stock_news(self, stock_names: List[str]) -> Dict[str, Any]:
        """각 종목별로 관련 뉴스 수집"""
        collected_news = {}
        
        for stock_name in stock_names:
            try:
                print(f"\n📰 {stock_name} 관련 뉴스 수집 중...")
                
                # 종목명으로 뉴스 검색
                news_data = self.search_news(
                    query=stock_name,
                    display=100,
                    start=1,
                    sort="sim"  # 관련도순
                )
                
                if news_data and 'items' in news_data:
                    # 상위 3개 뉴스만 선택
                    top_news = news_data['items'][:3]
                    
                    collected_news[stock_name] = {
                        "query": stock_name,
                        "total": len(top_news),
                        "items": top_news,
                        "collection_time": datetime.now().isoformat()
                    }
                    
                    print(f"✅ {stock_name} 뉴스 수집 완료: {len(top_news)}개")
                    
                    # 각 뉴스 제목 출력
                    for i, news in enumerate(top_news, 1):
                        title = news.get('title', '').replace('<b>', '').replace('</b>', '')
                        print(f"  {i}. {title}")
                        
                else:
                    print(f"❌ {stock_name} 뉴스 수집 실패")
                    collected_news[stock_name] = {
                        "query": stock_name,
                        "total": 0,
                        "items": [],
                        "collection_time": datetime.now().isoformat(),
                        "error": "뉴스 수집 실패"
                    }
                    
            except Exception as e:
                print(f"❌ {stock_name} 처리 중 오류: {e}")
                collected_news[stock_name] = {
                    "query": stock_name,
                    "total": 0,
                    "items": [],
                    "collection_time": datetime.now().isoformat(),
                    "error": str(e)
                }
        
        return collected_news
    
    def save_news_data(self, collected_news: Dict[str, Any]) -> str:
        """수집된 뉴스 데이터 저장"""
        if not collected_news:
            print("❌ 저장할 뉴스 데이터가 없습니다.")
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_news_data_{timestamp}.json"
        file_path = self.output_dir / filename
        
        try:
            # 저장할 데이터 구성
            save_data = {
                "collection_time": datetime.now().isoformat(),
                "total_stocks": len(collected_news),
                "stocks": collected_news
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 뉴스 데이터 저장 완료: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ 뉴스 데이터 저장 실패: {e}")
            return ""
    
    def run_collection(self, stock_names: List[str]) -> bool:
        """전체 뉴스 수집 프로세스 실행"""
        print("=" * 60)
        print("📰 개별 종목 뉴스 수집 시스템")
        print("=" * 60)
        
        # API 정보 확인
        api_info = self.get_api_info()
        if not api_info['client_id_set'] or not api_info['client_secret_set']:
            print("❌ 네이버 API 키가 설정되지 않았습니다!")
            print("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 .env 파일에 설정하세요.")
            return False
        
        print("✅ 네이버 API 키 설정 완료")
        print(f"📊 수집 대상 종목: {stock_names}")
        
        # 뉴스 수집
        print("\n🔍 뉴스 수집 시작...")
        collected_news = self.collect_stock_news(stock_names)
        
        if not collected_news:
            print("❌ 수집된 뉴스가 없습니다.")
            return False
        
        # 데이터 저장
        print("\n💾 뉴스 데이터 저장 중...")
        saved_path = self.save_news_data(collected_news)
        
        if saved_path:
            print(f"\n🎉 뉴스 수집 완료!")
            print(f"📁 결과 파일: {saved_path}")
            print(f"📊 수집된 종목 수: {len(collected_news)}개")
            
            # 요약 정보 출력
            for stock_name, news_data in collected_news.items():
                total = news_data.get('total', 0)
                print(f"  📰 {stock_name}: {total}개 뉴스")
            
            return True
        
        print("\n❌ 뉴스 데이터 저장 실패")
        return False

def main():
    """메인 실행 함수"""
    # 테스트용 종목명들
    test_stocks = ["미투온", "뉴로핏", "광명전기"]
    
    collector = StockNewsCollector()
    success = collector.run_collection(test_stocks)
    
    if success:
        print("\n✅ 전체 뉴스 수집 프로세스 완료!")
    else:
        print("\n❌ 뉴스 수집 프로세스 실패!")

if __name__ == "__main__":
    main() 