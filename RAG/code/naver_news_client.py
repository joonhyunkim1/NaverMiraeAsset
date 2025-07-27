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
            filename = "naver_news_recent_3.json"
            # data 폴더 경로
            data_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data")
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