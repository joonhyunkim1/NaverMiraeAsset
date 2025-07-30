#!/usr/bin/env python3
"""
뉴스 본문 추출 클라이언트
"""

import json
import requests
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from llama_index.core import Document
from llama_index.readers.web import NewsArticleReader
import time

class NewsContentExtractor:
    """뉴스 본문 추출 클라이언트"""
    
    def __init__(self):
        self.data_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data")
        
        # 웹 페이지 로더 초기화
        try:
            self.web_loader = NewsArticleReader()
            print("뉴스 기사 로더 초기화 완료")
        except Exception as e:
            print(f"뉴스 기사 로더 초기화 실패: {e}")
            self.web_loader = None
    
    def load_news_json(self, filename: str) -> Optional[Dict]:
        """뉴스 JSON 파일 로드"""
        try:
            file_path = self.data_dir / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"JSON 파일 로드 실패: {e}")
            return None
    
    def extract_urls_from_news(self, news_data: Dict) -> List[str]:
        """뉴스 데이터에서 URL 추출"""
        urls = []
        if 'items' in news_data:
            for item in news_data['items']:
                # 원본 링크 우선, 없으면 네이버 링크 사용
                url = item.get('originallink') or item.get('link')
                if url:
                    urls.append(url)
        return urls
    
    def extract_article_content(self, url: str) -> Optional[Dict]:
        """URL에서 뉴스 본문 추출"""
        try:
            print(f"본문 추출 중: {url}")
            
            # 웹 페이지 로더로 본문 가져오기
            documents = self.web_loader.load_data(urls=[url])
            
            if documents and len(documents) > 0:
                content = documents[0].text
                
                # 간단한 텍스트 정제 (HTML 태그 제거 등)
                content = self._clean_content(content)
                
                if content and len(content) > 20:  # 최소 20자 이상으로 완화
                    return {
                        'url': url,
                        'content': content,
                        'length': len(content)
                    }
                else:
                    print(f"본문이 너무 짧거나 없음: {url}")
                    return None
            else:
                print(f"본문 추출 실패: {url}")
                return None
                
        except Exception as e:
            print(f"본문 추출 오류 ({url}): {e}")
            return None
    
    def _clean_content(self, content: str) -> str:
        """텍스트 정제 - 내용이 잘리지 않도록 개선"""
        if not content:
            return ""
        
        # HTML 태그 제거
        import re
        content = re.sub(r'<[^>]+>', '', content)
        
        # 기본적인 정제 작업 (너무 짧은 줄 제거 기준 완화)
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # 빈 줄 제거, 너무 짧은 줄 제거 기준을 5자로 완화
            if line and len(line) > 5:
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        
        # 최소 길이 확인 (20자 이상으로 완화)
        if len(result) < 20:
            return ""
        
        return result
    
    def process_news_json(self, filename: str) -> List[Dict]:
        """뉴스 JSON 파일을 처리하여 본문 추출"""
        # JSON 파일 로드
        news_data = self.load_news_json(filename)
        if not news_data:
            return []
        
        # URL 추출
        urls = self.extract_urls_from_news(news_data)
        print(f"추출된 URL 개수: {len(urls)}")
        
        # 각 URL에서 본문 추출
        articles = []
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 본문 추출 중...")
            
            article = self.extract_article_content(url)
            if article:
                articles.append(article)
                print(f"본문 길이: {article['length']}자")
            
            # 요청 간격 조절 (서버 부하 방지)
            time.sleep(1)
        
        return articles
    
    def save_articles_to_json(self, articles: List[Dict], filename: str = None) -> bool:
        """추출된 본문을 JSON으로 저장"""
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"finance_articles_{timestamp}.json"
            
            file_path = self.data_dir / filename
            
            # 저장할 데이터 구성
            save_data = {
                'extraction_time': datetime.now().isoformat(),
                'total_articles': len(articles),
                'articles': articles
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"본문 데이터 저장 완료: {file_path}")
            return True
            
        except Exception as e:
            print(f"본문 데이터 저장 실패: {e}")
            return False
    
    def extract_and_save_articles(self, news_filename: str) -> bool:
        """뉴스 JSON에서 본문 추출하여 저장"""
        print("=" * 50)
        print("뉴스 본문 추출 시작")
        print("=" * 50)
        
        # 본문 추출
        articles = self.process_news_json(news_filename)
        
        if not articles:
            print("추출된 본문이 없습니다.")
            return False
        
        # JSON으로 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        articles_filename = f"finance_articles_{timestamp}.json"
        
        success = self.save_articles_to_json(articles, articles_filename)
        
        if success:
            print(f"\n✅ 본문 추출 완료!")
            print(f"총 {len(articles)}개 기사의 본문을 추출했습니다.")
        
        return success 