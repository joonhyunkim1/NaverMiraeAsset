#!/usr/bin/env python3
"""
네이버 뉴스 검색 API 클라이언트
"""

import requests
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from config import get_naver_client_id, get_naver_client_secret

class NaverNewsClient:
    """네이버 뉴스 검색 API 클라이언트"""
    
    def __init__(self):
        self.client_id = get_naver_client_id()
        self.client_secret = get_naver_client_secret()
        self.base_url = "https://openapi.naver.com/v1/search/news.json"
        
        # API 키 확인
        if not self.client_id or not self.client_secret:
            print("경고: 네이버 API 키가 설정되지 않았습니다!")
            print("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET을 .env 파일에 설정하세요.")
        
        print(f"네이버 뉴스 API 클라이언트 초기화 완료")
        print(f"Client ID 설정: {'완료' if self.client_id else '미완료'}")
        print(f"Client Secret 설정: {'완료' if self.client_secret else '미완료'}")
    
    def search_news(self, query: str, display: int = 1, start: int = 1, sort: str = "date") -> Optional[Dict]:
        """
        네이버 뉴스 검색 API 호출
        
        Args:
            query: 검색어
            display: 한 번에 표시할 검색 결과 개수 (기본값: 1, 최댓값: 100)
            start: 검색 시작 위치 (기본값: 1, 최댓값: 1000)
            sort: 정렬 방법 ("sim": 정확도순, "date": 날짜순)
        
        Returns:
            API 응답 결과 (Dict) 또는 None (실패 시)
        """
        try:
            # 헤더 설정
            headers = {
                "X-Naver-Client-Id": self.client_id,
                "X-Naver-Client-Secret": self.client_secret
            }
            
            # 파라미터 설정
            params = {
                "query": query,
                "display": display,
                "start": start,
                "sort": sort
            }
            
            print(f"네이버 뉴스 검색 중...")
            print(f"검색어: {query}")
            print(f"결과 개수: {display}")
            print(f"정렬: {sort}")
            
            # API 호출
            response = requests.get(self.base_url, headers=headers, params=params)
            
            print(f"응답 상태: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"검색 결과: {result.get('total', 0)}개 중 {len(result.get('items', []))}개 반환")
                return result
            else:
                print(f"API 호출 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                return None
                
        except Exception as e:
            print(f"네이버 뉴스 API 호출 오류: {e}")
            return None
    
    def save_news_to_json(self, news_data: Dict, filename: str = None) -> bool:
        """
        뉴스 데이터를 JSON 파일로 저장
        
        Args:
            news_data: 네이버 뉴스 API 응답 데이터
            filename: 저장할 파일명 (None이면 자동 생성)
        
        Returns:
            저장 성공 여부
        """
        try:
            # 파일명 자동 생성
            # if filename is None:
            #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            #     filename = f"naver_news_{timestamp}.json"
            filename = "naver_news_recent_30.json"
            # data 폴더 경로
            current_dir = Path(__file__).parent
            data_dir = current_dir.parent / "data"
            data_dir.mkdir(exist_ok=True)
            
            file_path = data_dir / filename
            
            # JSON 파일로 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=2)
            
            print(f"뉴스 데이터 저장 완료: {file_path}")
            return True
            
        except Exception as e:
            print(f"뉴스 데이터 저장 실패: {e}")
            return False
    
    def get_custom_news(self, query: str, display: int = 10, start: int = 1, sort: str = "sim", 
                       filter_by_date: bool = False, days_back: int = 1, target_count: int = None) -> bool:
        """
        사용자 정의 검색어로 뉴스를 가져와서 JSON으로 저장
        
        Args:
            query: 검색어
            display: 가져올 뉴스 개수 (기본값: 10, 최댓값: 100)
            start: 검색 시작 위치 (기본값: 1)
            sort: 정렬 방법 ("sim": 관련도순, "date": 날짜순)
            filter_by_date: 날짜 필터링 사용 여부 (기본값: False)
            days_back: 몇 일 전까지의 뉴스를 가져올지 (기본값: 1)
            target_count: 필터링 후 목표 뉴스 개수 (None이면 display 사용)
        
        Returns:
            성공 여부
        """
        # 목표 개수 설정
        if target_count is None:
            target_count = display
        
        # 현재 쿼리를 인스턴스 변수로 저장 (필터링 함수에서 사용)
        self._current_query = query
        
        # 사용자 정의 검색어로 뉴스 검색
        news_data = self.search_news(
            query=query,
            display=display,
            start=start,
            sort=sort
        )
        
        if news_data is None:
            print("뉴스 검색 실패")
            return False
        
        # 날짜 필터링 적용
        if filter_by_date:
            news_data = self._filter_news_by_date_with_target(news_data, days_back, target_count)
            print(f"📅 날짜 필터링 적용: 지난 {days_back}일 뉴스만 포함, 목표 {target_count}개")
            # 목표 개수만큼만 유지
            if len(news_data.get('items', [])) > target_count:
                news_data['items'] = news_data['items'][:target_count]
                news_data['total'] = target_count
                print(f"📊 뉴스 개수 최종 조정: {target_count}개로 제한")
        else:
            # 필터링 없이도 목표 개수만큼만 유지
            if len(news_data.get('items', [])) > target_count:
                news_data['items'] = news_data['items'][:target_count]
                news_data['total'] = target_count
                print(f"📊 뉴스 개수 조정: {target_count}개로 제한")
        
        # JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"naver_news_{query.replace(' ', '_')}_{timestamp}.json"
        
        return self.save_news_to_json(news_data, filename)
    

    def _filter_news_by_date(self, news_data: Dict, days_back: int) -> Dict:
        """
        뉴스 데이터를 날짜로 필터링합니다.
        
        Args:
            news_data: 네이버 뉴스 API 응답 데이터
            days_back: 몇 일 전까지의 뉴스를 포함할지
        
        Returns:
            필터링된 뉴스 데이터
        """
        from datetime import datetime, timedelta
        import pytz
        
        # 한국 시간대 설정
        korea_tz = pytz.timezone('Asia/Seoul')
        
        # 기준 날짜 계산 (한국 시간 기준, 현재 시간에서 days_back일 전)
        now_korea = datetime.now(korea_tz)
        cutoff_date = now_korea - timedelta(days=days_back)
        
        print(f"📅 필터링 기준 시간: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        # 필터링된 아이템들
        filtered_items = []
        
        for item in news_data.get('items', []):
            try:
                # pubDate 파싱 (예: "Mon, 25 Dec 2023 10:30:00 +0900")
                pub_date_str = item.get('pubDate', '')
                if pub_date_str:
                    # 다양한 날짜 형식 처리
                    pub_date = self._parse_news_date(pub_date_str)
                    if pub_date:
                        # 시간대 정보가 없는 경우 한국 시간으로 가정
                        if pub_date.tzinfo is None:
                            pub_date = korea_tz.localize(pub_date)
                        
                        if pub_date >= cutoff_date:
                            filtered_items.append(item)
                        else:
                            print(f"🔍 제외된 뉴스: {item.get('title', 'N/A')[:30]}... ({pub_date.strftime('%Y-%m-%d %H:%M')})")
                    else:
                        # 파싱 실패한 경우 포함 (최신 뉴스일 가능성)
                        filtered_items.append(item)
                else:
                    # pubDate가 없는 경우 포함 (최신 뉴스일 가능성)
                    filtered_items.append(item)
            except Exception as e:
                print(f"날짜 파싱 오류: {e}, 아이템 포함")
                filtered_items.append(item)
        
        # 필터링된 데이터로 업데이트
        filtered_data = news_data.copy()
        filtered_data['items'] = filtered_items
        filtered_data['total'] = len(filtered_items)
        
        print(f"📊 날짜 필터링 결과: {len(news_data.get('items', []))}개 → {len(filtered_items)}개")
        
        return filtered_data
    
    def _filter_news_by_date_with_target(self, news_data: Dict, days_back: int, target_count: int) -> Dict:
        """
        뉴스 데이터를 날짜로 필터링하고 목표 개수만큼 유지합니다.
        display=100으로 시작해서 목표 개수에 도달하지 못하면 start를 늘려가며 추가 검색합니다.
        
        Args:
            news_data: 네이버 뉴스 API 응답 데이터
            days_back: 몇 일 전까지의 뉴스를 포함할지
            target_count: 목표 뉴스 개수
        
        Returns:
            필터링된 뉴스 데이터
        """
        from datetime import datetime, timedelta
        import pytz
        
        # 한국 시간대 설정
        korea_tz = pytz.timezone('Asia/Seoul')
        
        # 기준 날짜 계산 (한국 시간 기준, 현재 시간에서 days_back일 전)
        now_korea = datetime.now(korea_tz)
        cutoff_date = now_korea - timedelta(days=days_back)
        
        print(f"📅 필터링 기준 시간: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"🎯 목표 뉴스 개수: {target_count}개")
        
        # 필터링된 아이템들
        filtered_items = []
        current_start = 1
        max_attempts = 10  # 최대 10번까지 시도 (start=1, 101, 201, ..., 901)
        
        while len(filtered_items) < target_count and current_start <= 1000 and max_attempts > 0:
            print(f"🔍 검색 시도 {11-max_attempts}/10: start={current_start}, display=100")
            
            # 현재 start 위치에서 뉴스 검색 (원본 정렬 방식 유지)
            # 원본 쿼리 사용 (news_data에는 쿼리 정보가 없을 수 있음)
            original_query = getattr(self, '_current_query', news_data.get('query', ''))
            current_news_data = self.search_news(
                query=original_query,
                display=100,  # 최대 100개씩 가져오기
                start=current_start,
                sort="date"  # 시간순 정렬 유지
            )
            
            if not current_news_data or 'items' not in current_news_data:
                print(f"❌ start={current_start}에서 뉴스를 가져올 수 없습니다.")
                break
            
            # 현재 배치에서 날짜 필터링
            batch_filtered = 0
            for item in current_news_data['items']:
                try:
                    pub_date_str = item.get('pubDate', '')
                    if pub_date_str:
                        pub_date = self._parse_news_date(pub_date_str)
                        if pub_date:
                            if pub_date.tzinfo is None:
                                pub_date = korea_tz.localize(pub_date)
                            
                            if pub_date >= cutoff_date:
                                filtered_items.append(item)
                                batch_filtered += 1
                                if len(filtered_items) >= target_count:
                                    break
                            else:
                                print(f"🔍 제외된 뉴스: {item.get('title', 'N/A')[:30]}... ({pub_date.strftime('%Y-%m-%d %H:%M')})")
                        else:
                            # 파싱 실패한 경우 포함 (최신 뉴스일 가능성)
                            filtered_items.append(item)
                            batch_filtered += 1
                            if len(filtered_items) >= target_count:
                                break
                    else:
                        # pubDate가 없는 경우 포함 (최신 뉴스일 가능성)
                        filtered_items.append(item)
                        batch_filtered += 1
                        if len(filtered_items) >= target_count:
                            break
                except Exception as e:
                    print(f"날짜 파싱 오류: {e}, 아이템 포함")
                    filtered_items.append(item)
                    batch_filtered += 1
                    if len(filtered_items) >= target_count:
                        break
            
            print(f"📊 현재 배치 결과: {len(current_news_data['items'])}개 중 {batch_filtered}개 필터링 통과")
            print(f"📊 누적 필터링 결과: {len(filtered_items)}개 / {target_count}개")
            
            # 다음 검색을 위해 start 위치 업데이트
            current_start += 100
            max_attempts -= 1
            
            # 목표 개수에 도달했으면 중단
            if len(filtered_items) >= target_count:
                break
        
        # 필터링된 데이터로 업데이트
        filtered_data = news_data.copy()
        filtered_data['items'] = filtered_items[:target_count]  # 목표 개수만큼만 유지
        filtered_data['total'] = len(filtered_data['items'])
        
        print(f"📊 최종 필터링 결과: {len(filtered_data['items'])}개 (목표: {target_count}개)")
        
        return filtered_data
    
    def _parse_news_date(self, date_str: str) -> Optional[datetime]:
        """
        뉴스 날짜 문자열을 파싱합니다.
        
        Args:
            date_str: 날짜 문자열
        
        Returns:
            파싱된 datetime 객체 또는 None
        """
        try:
            # 다양한 날짜 형식 시도
            formats = [
                "%a, %d %b %Y %H:%M:%S %z",  # "Mon, 25 Dec 2023 10:30:00 +0900"
                "%Y-%m-%d %H:%M:%S",         # "2023-12-25 10:30:00"
                "%Y년 %m월 %d일",             # "2023년 12월 25일"
                "%Y.%m.%d",                  # "2023.12.25"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # 마지막 시도: dateutil.parser 사용
            from dateutil import parser
            return parser.parse(date_str)
            
        except Exception as e:
            print(f"날짜 파싱 실패: {date_str}, 오류: {e}")
            return None
    
    def get_latest_finance_news(self, count: int = 3) -> bool:
        """
        '금융' 관련 최신 뉴스 여러 개를 가져와서 JSON으로 저장
        
        Args:
            count: 가져올 뉴스 개수 (기본값: 3)
        
        Returns:
            성공 여부
        """
        # '금융' 관련 최신 뉴스 검색
        news_data = self.search_news(
            query="금융",
            display=count,  # 최신 뉴스 여러 개
            start=1,
            sort="date"  # 날짜순 정렬 (최신순)
        )
        
        if news_data is None:
            print("뉴스 검색 실패")
            return False
        
        # JSON 파일로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"finance_news_{timestamp}.json"
        
        return self.save_news_to_json(news_data, filename)
    
    def get_api_info(self) -> Dict[str, bool]:
        """API 정보를 반환합니다."""
        return {
            "client_id_set": bool(self.client_id),
            "client_secret_set": bool(self.client_secret)
        } 