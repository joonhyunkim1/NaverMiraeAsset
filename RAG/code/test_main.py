#!/usr/bin/env python3
"""
통합 데이터 수집 및 분석 테스트 스크립트
- KRX 일일거래정보 수집
- 네이버 뉴스 수집
- CLOVA 분석 및 주식 종목 추출
- Function Calling을 통한 주가 데이터 수집
"""

from datetime import datetime
import subprocess
import time
import requests
import json
from pathlib import Path
from typing import List, Dict, Any
import os
from krx_api_client import KRXAPIClient
from naver_news_client import NaverNewsClient
from faiss_data_analyzer import FAISSDataAnalyzer
from stock_extractor import StockExtractor
from stock_news_collector import StockNewsCollector
from hybrid_vector_manager import HybridVectorManager
from clova_embedding import ClovaEmbeddingAPI
from clova_segmentation import ClovaSegmentationClient
from news_content_extractor import NewsContentExtractor

def start_faiss_api_server():
    """FAISS API 서버 시작"""
    print("\n" + "=" * 60)
    print("🚀 FAISS API 서버 시작")
    print("=" * 60)
    
    # 서버가 이미 실행 중인지 확인
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ FAISS API 서버가 이미 실행 중입니다")
            return True
    except:
        pass
    
    # 서버 시작
    try:
        print("🔧 FAISS API 서버를 시작합니다...")
        process = subprocess.Popen(
            ["python", "faiss_vector_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 서버 시작 대기
        for i in range(30):  # 최대 30초 대기
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ FAISS API 서버 시작 완료")
                    return True
            except:
                continue
        
        print("❌ FAISS API 서버 시작 실패")
        return False
        
    except Exception as e:
        print(f"❌ FAISS API 서버 시작 중 오류: {e}")
        return False

def start_vector_db1_api_server():
    """Vector DB1 FAISS API 서버 시작"""
    print("\n" + "=" * 60)
    print("🚀 Vector DB1 FAISS API 서버 시작")
    print("=" * 60)
    
    # 서버가 이미 실행 중인지 확인
    try:
        response = requests.get("http://localhost:8001/health", timeout=3)
        if response.status_code == 200:
            print("✅ Vector DB1 FAISS API 서버가 이미 실행 중입니다")
            return True
    except:
        pass
    
    # 서버 시작
    try:
        print("🔧 Vector DB1 FAISS API 서버를 시작합니다...")
        process = subprocess.Popen(
            ["python", "faiss_vector_db1_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 서버 시작 대기
        for i in range(30):  # 최대 30초 대기
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8001/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Vector DB1 FAISS API 서버 시작 완료")
                    return True
            except:
                continue
        
        print("❌ Vector DB1 FAISS API 서버 시작 실패")
        return False
        
    except Exception as e:
        print(f"❌ Vector DB1 FAISS API 서버 시작 중 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    # ===== 설정 =====
    # True: 새로운 데이터 수집 및 분석 수행
    # False: 기존 저장된 데이터만 사용하여 분석 수행
    ENABLE_DATA_COLLECTION = True  # 데이터 수집 기능 on/off
    
    print("=" * 60)
    print("🚀 통합 데이터 수집 테스트")
    print("📅 실행 시간:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("🔧 데이터 수집 모드:", "ON" if ENABLE_DATA_COLLECTION else "OFF")
    print("=" * 60)
    
    # ===== 뉴스 검색 파라미터 설정 =====
    # 최신순으로 30개 뉴스 수집
    NEWS_CONFIG = {
        "query": "국내 주식 주가",  # 검색어
        "display": 100,           # 가져올 뉴스 개수 (최대 100)
        "start": 1,               # 검색 시작 위치
        "sort": "date",           # 정렬 방법 ("sim": 관련도순, "date": 날짜순)
        "filter_by_date": True,   # 날짜 필터링 사용 여부
        "days_back": 1,           # 지난 몇 일 뉴스를 가져올지 (1 = 지난 1일)
        "target_count": 30        # 필터링 후 목표 뉴스 개수 (최신순 30개)
    }
    
    print(f"📰 뉴스 검색 설정: {NEWS_CONFIG}")
    
    # ===== 데이터 수집 (조건부 실행) =====
    if ENABLE_DATA_COLLECTION:
        print("\n" + "=" * 60)
        print("📊 새로운 데이터 수집 시작")
        print("=" * 60)
        
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
    else:
        print("\n" + "=" * 60)
        print("📊 기존 저장된 데이터 사용")
        print("=" * 60)
        print("✅ 데이터 수집 건너뛰기 - 기존 파일들 사용")
    
    # 4. FAISS API 서버 시작
    if not start_faiss_api_server():
        print("❌ FAISS API 서버 시작 실패로 인해 분석을 건너뜁니다.")
        return
    
    # 5. CLOVA 분석 및 주식 종목 추출
    print("\n" + "=" * 60)
    print("🤖 CLOVA 분석 및 주식 종목 추출")
    print("=" * 60)
    
    # FAISS 벡터 검색 기반 데이터 분석기 초기화
    analyzer = FAISSDataAnalyzer()
    
    # 첫 번째 데이터 변환 결과 확인
    print("\n" + "=" * 60)
    print("🔍 데이터 변환 결과 미리보기")
    print("=" * 60)
    
    # KRX 데이터 첫 번째 항목 변환 결과 확인
    print("\n📊 KRX 데이터 첫 번째 항목 변환 결과:")
    print("-" * 40)
    
    # KRX 파일 찾기
    import glob
    krx_files = glob.glob("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data/krx_daily_trading_*.csv")
    if krx_files:
        import pandas as pd
        df = pd.read_csv(krx_files[0])
        print(f"📄 파일: {krx_files[0]}")
        print(f"📊 전체 데이터: {len(df)}행, {len(df.columns)}컬럼")
        
        # 첫 번째 종목 정보 출력
        if len(df) > 0:
            first_row = df.iloc[0]
            print(f"\n🏢 첫 번째 종목 정보:")
            print(f"  종목명: {first_row.get('ISU_ABBRV', 'N/A')}")
            print(f"  종목코드: {first_row.get('ISU_CD', 'N/A')}")
            print(f"  시가: {first_row.get('TDD_OPNPRC', 'N/A')}")
            print(f"  고가: {first_row.get('TDD_HGPRC', 'N/A')}")
            print(f"  저가: {first_row.get('TDD_LWPRC', 'N/A')}")
            print(f"  종가: {first_row.get('TDD_CLSPRC', 'N/A')}")
            print(f"  거래대금: {first_row.get('ACC_TRDVAL', 'N/A')}")
            print(f"  등락률: {first_row.get('FLUC_RT', 'N/A')}")
    
    # 뉴스 데이터 첫 번째 항목 변환 결과 확인
    print("\n📰 뉴스 데이터 첫 번째 항목 변환 결과:")
    print("-" * 40)
    
    # 뉴스 파일 찾기
    news_files = glob.glob("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data/naver_news_*.json")
    if news_files:
        import json
        with open(news_files[0], 'r', encoding='utf-8') as f:
            news_data = json.load(f)
        
        print(f"📄 파일: {news_files[0]}")
        articles = news_data.get('items', [])
        print(f"📊 전체 뉴스: {len(articles)}개")
        
        if len(articles) > 0:
            first_article = articles[0]
            print(f"\n📰 첫 번째 뉴스 정보:")
            print(f"  제목: {first_article.get('title', 'N/A')}")
            print(f"  내용: {first_article.get('description', 'N/A')[:100]}...")
            print(f"  발행일: {first_article.get('pubDate', 'N/A')}")
    
    print("\n" + "=" * 60)
    
    print("🔍 FAISS 벡터 검색 기반 분석 시작...")
    # 데이터 수집 모드에 따라 벡터 재구축 여부 결정
    rebuild_vectors = ENABLE_DATA_COLLECTION  # 데이터 수집 시에만 벡터 재구축
    analysis_success = analyzer.run_analysis(rebuild_vectors=rebuild_vectors)
    
    if analysis_success:
        print("✅ FAISS 벡터 검색 기반 분석 완료")
        
        # ===== 주식 종목 추출 및 데이터 수집 (조건부 실행) =====
        if ENABLE_DATA_COLLECTION:
            # 주식 종목 추출
            print("\n📊 주식 종목 추출 시작...")
            extractor = StockExtractor()
            extraction_success = extractor.run_extraction()
            
            if extraction_success:
                print("✅ 주식 종목 추출 완료")
                
                # 5. 자동 주식 데이터 수집 (추출된 종목명 사용)
                print("\n" + "=" * 60)
                print("📈 자동 주식 데이터 수집")
                print("=" * 60)
                
                # stock_extractor에서 추출된 종목명을 가져와서 자동 수집
                extracted_stocks = extractor.get_extracted_stocks()
                
                if extracted_stocks:
                    from stock_data_collector import StockDataCollector
                    stock_collector = StockDataCollector()
                    auto_collection_success = stock_collector.run_auto_collection(extracted_stocks)
                    
                    if auto_collection_success:
                        print("✅ 자동 주식 데이터 수집 완료")
                    else:
                        print("❌ 자동 주식 데이터 수집 실패")
                else:
                    print("❌ 추출된 종목명이 없어 자동 수집을 건너뜁니다.")
                
                # 6. 개별 종목 뉴스 수집
                print("\n" + "=" * 60)
                print("📰 개별 종목 뉴스 수집")
                print("=" * 60)
                
                news_stocks = extracted_stocks
                news_collector = StockNewsCollector()
                news_success = news_collector.run_collection(news_stocks)
                
                if news_success:
                    print("✅ 개별 종목 뉴스 수집 완료")
                else:
                    print("❌ 개별 종목 뉴스 수집 실패")
            else:
                print("❌ 주식 종목 추출 및 데이터 수집 실패")
        else:
            print("✅ 데이터 수집 모드 OFF - 주식 종목 추출 및 데이터 수집 건너뛰기")
    else:
        print("❌ FAISS 벡터 검색 기반 분석 실패")
    
    # ===== data_1 폴더 임베딩 (조건부 실행) =====
    if ENABLE_DATA_COLLECTION:
        print("\n" + "=" * 60)
        print("🔍 data_1 폴더 파일들 임베딩")
        print("=" * 60)
        
        try:
            # vector_db_1 디렉토리 생성
            vector_db_1_path = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/vector_db_1")
            vector_db_1_path.mkdir(exist_ok=True)
            
            # data_1 폴더용 벡터 매니저 생성
            class Data1VectorManager(HybridVectorManager):
                def __init__(self, data_dir: str):
                    self.data_dir = Path(data_dir)
                    self.vector_dir = vector_db_1_path
                    self.vector_dir.mkdir(exist_ok=True)
                    
                    # CLOVA 클라이언트 초기화
                    self.embedding_client = ClovaEmbeddingAPI()
                    self.segmentation_client = ClovaSegmentationClient()
                    self.news_extractor = NewsContentExtractor()
                    
                    # 벡터 저장소
                    self.vectors_file = self.vector_dir / "hybrid_vectors.pkl"
                    self.metadata_file = self.vector_dir / "hybrid_metadata.json"
                    
                    # 벡터 데이터 로드
                    self.vectors = []
                    self.metadata = []
                    self._load_vectors()
                
                def _csv_to_summary_text(self, csv_file: Path) -> str:
                    """CSV 파일을 요약된 형태로 변환"""
                    try:
                        import pandas as pd
                        from datetime import datetime, timedelta
                        
                        # CSV 파일 읽기
                        df = pd.read_csv(csv_file)
                        
                        # Date 컬럼을 datetime으로 변환
                        df['Date'] = pd.to_datetime(df['Date'])
                        
                        # 종목명 추출 (파일명에서)
                        filename = csv_file.name
                        stock_name = filename.split('_')[0]  # 첫 번째 부분이 종목명
                        
                        # 현재 날짜 (가장 최근 날짜)
                        latest_date = df['Date'].max()
                        
                        # 전일 데이터
                        yesterday_data = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
                        
                        # 지난 일주일 데이터 (최근 7일)
                        week_ago = latest_date - timedelta(days=7)
                        week_data = df[df['Date'] >= week_ago]
                        
                        # 지난 3개월 데이터 (최근 90일)
                        three_months_ago = latest_date - timedelta(days=90)
                        three_months_data = df[df['Date'] >= three_months_ago]
                        
                        # 지난 6개월 데이터 (전체 데이터)
                        six_months_data = df
                        
                        # 요약 텍스트 생성
                        summary_parts = []
                        summary_parts.append(f"종목: {stock_name}")
                        summary_parts.append("")
                        
                        # 전일 데이터
                        summary_parts.append(f"전일 고가: {yesterday_data['High']:,.0f}, 저가: {yesterday_data['Low']:,.0f}, 시가: {yesterday_data['Open']:,.0f}, 종가: {yesterday_data['Close']:,.0f}, 거래량: {yesterday_data['Volume']:,.0f}, 등락률: {yesterday_data['Change']:.2f}%")
                        
                        # 지난 일주일 데이터
                        if len(week_data) > 0:
                            week_high = week_data['High'].max()
                            week_low = week_data['Low'].min()
                            week_change = ((week_data['Close'].iloc[-1] - week_data['Open'].iloc[0]) / week_data['Open'].iloc[0]) * 100
                            summary_parts.append(f"지난 일주일 고가: {week_high:,.0f}, 저가: {week_low:,.0f}, 등락률: {week_change:.2f}%")
                        else:
                            summary_parts.append("지난 일주일 고가: N/A, 저가: N/A, 등락률: N/A")
                        
                        # 지난 3개월 데이터
                        if len(three_months_data) > 0:
                            three_months_high = three_months_data['High'].max()
                            three_months_low = three_months_data['Low'].min()
                            three_months_change = ((three_months_data['Close'].iloc[-1] - three_months_data['Open'].iloc[0]) / three_months_data['Open'].iloc[0]) * 100
                            summary_parts.append(f"지난 3개월 고가: {three_months_high:,.0f}, 저가: {three_months_low:,.0f}, 등락률: {three_months_change:.2f}%")
                        else:
                            summary_parts.append("지난 3개월 고가: N/A, 저가: N/A, 등락률: N/A")
                        
                        # 지난 6개월 데이터
                        if len(six_months_data) > 0:
                            six_months_high = six_months_data['High'].max()
                            six_months_low = six_months_data['Low'].min()
                            six_months_change = ((six_months_data['Close'].iloc[-1] - six_months_data['Open'].iloc[0]) / six_months_data['Open'].iloc[0]) * 100
                            summary_parts.append(f"지난 6개월 고가: {six_months_high:,.0f}, 저가: {six_months_low:,.0f}, 등락률: {six_months_change:.2f}%")
                        else:
                            summary_parts.append("지난 6개월 고가: N/A, 저가: N/A, 등락률: N/A")
                        
                        return "\n".join(summary_parts)
                        
                    except Exception as e:
                        print(f"    ❌ CSV 요약 변환 실패: {csv_file.name} - {e}")
                        return f"파일명: {csv_file.name} (요약 변환 실패)"
                
                def _single_article_to_text(self, article: dict, article_index: int) -> str:
                    """개별 뉴스 기사를 텍스트로 변환 (vector_db 방식) - URL에서 전체 본문 추출"""
                    text_parts = []
                    
                    # 기사 제목
                    title = article.get('title', '')
                    if title:
                        # HTML 태그 제거
                        import re
                        clean_title = re.sub(r'<[^>]+>', '', title)
                        text_parts.append(f"제목: {clean_title}")
                    
                    # URL에서 전체 본문 추출 시도
                    full_content = None
                    url = article.get('originallink') or article.get('link')
                    
                    if url:
                        try:
                            full_content = self.news_extractor.extract_article_content(url)
                            if full_content and full_content.get('content'):
                                print(f"      ✅ 전체 본문 추출 성공: {len(full_content['content'])}자")
                            else:
                                print(f"      ⚠️ 전체 본문 추출 실패, 요약문 사용")
                        except Exception as e:
                            print(f"      ❌ 본문 추출 오류: {e}")
                    
                    # 전체 본문이 있으면 사용, 없으면 요약문 사용
                    if full_content and full_content.get('content'):
                        content = full_content['content']
                        # HTML 태그 제거
                        import re
                        clean_content = re.sub(r'<[^>]+>', '', content)
                        text_parts.append(f"본문: {clean_content}")
                    else:
                        # 요약문 사용
                        description = article.get('description', '')
                        if description:
                            # HTML 태그 제거
                            import re
                            clean_description = re.sub(r'<[^>]+>', '', description)
                            # ... 부분 제거
                            clean_description = clean_description.replace('...', '').strip()
                            text_parts.append(f"내용: {clean_description}")
                    
                    # 발행일
                    pub_date = article.get('pubDate', '')
                    if pub_date:
                        text_parts.append(f"발행일: {pub_date}")
                    
                    final_text = "\n".join(text_parts)
                    return final_text
            
            # data_1 폴더용 벡터 매니저 초기화
            vector_manager = Data1VectorManager(
                data_dir="/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1"
            )
            
            print("🔧 data_1 폴더 벡터 매니저 초기화 완료")
            print(f"📁 데이터 디렉토리: {vector_manager.data_dir}")
            print(f"📁 벡터 디렉토리: {vector_manager.vector_dir}")
            
            # data_1 폴더의 파일들 처리
            print("\n📊 data_1 폴더 파일 처리 중...")
            
            # 기존 메타데이터 초기화
            new_metadata = []
            
            # CSV 파일 처리 - 요약된 형태로 변환
            csv_files = list(Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1").glob("*.csv"))
            print(f"  📊 CSV 파일 {len(csv_files)}개 발견")
            for csv_file in csv_files:
                try:
                    print(f"    📊 CSV 파일 처리: {csv_file.name}")
                    # 요약된 형태로 변환
                    summary_text = vector_manager._csv_to_summary_text(csv_file)
                    print(f"      📝 요약 텍스트 길이: {len(summary_text)}자")
                    print(f"      📝 요약 텍스트 미리보기: {summary_text[:200]}...")
                    
                    # 요약 텍스트를 청킹 (보통 1개 청크가 될 것)
                    chunks = vector_manager._segment_text_with_clova(summary_text, max_length=2048)
                    print(f"      📝 청킹 결과: {len(chunks)}개 청크")
                    
                    for i, chunk in enumerate(chunks):
                        metadata_entry = {
                            "filename": csv_file.name,
                            "type": "csv",
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "text_content": chunk,
                            "text_length": len(chunk),
                            "created_at": "2025-01-31T00:00:00"
                        }
                        new_metadata.append(metadata_entry)
                        print(f"      📝 청크 {i+1}: {len(chunk)}자")
                        
                except Exception as e:
                    print(f"    ❌ CSV 파일 처리 오류: {e}")
            
            # JSON 파일 처리 (뉴스 데이터) - 개별 기사별 처리
            json_files = list(Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1").glob("*.json"))
            print(f"  📄 JSON 파일 {len(json_files)}개 발견")
            
            for json_file in json_files:
                print(f"    🔍 JSON 파일 처리: {json_file.name}")
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        news_data = json.load(f)
                    
                    # stocks 구조에서 개별 기사 추출
                    stocks = news_data.get('stocks', {})
                    all_articles = []
                    
                    for stock_name, stock_data in stocks.items():
                        articles = stock_data.get('items', [])
                        for article in articles:
                            article['stock_name'] = stock_name
                        all_articles.extend(articles)
                    
                    print(f"      📰 총 {len(all_articles)}개 뉴스 기사 발견")
                    
                    # 각 기사를 개별적으로 처리
                    for article_index, article in enumerate(all_articles):
                        print(f"        📰 기사 {article_index+1} 처리 시작")
                        
                        # 개별 기사를 텍스트로 변환
                        article_text = vector_manager._single_article_to_text(article, article_index)
                        print(f"          📝 기사 텍스트 길이: {len(article_text)}자")
                        
                        # 청킹
                        chunks = vector_manager._segment_text_with_clova(article_text, max_length=1024)
                        print(f"          🔄 세그멘테이션 결과: {len(chunks)}개 청크")
                        
                        # 메타데이터 생성
                        for chunk_index, chunk in enumerate(chunks):
                            metadata_entry = {
                                "filename": json_file.name,
                                "type": "news",
                                "article_index": article_index,
                                "chunk_index": chunk_index,
                                "total_articles": len(all_articles),
                                "total_chunks": len(chunks),
                                "title": article.get('title', ''),
                                "text_content": chunk,
                                "text_length": len(chunk),
                                "created_at": "2025-01-31T00:00:00"
                            }
                            new_metadata.append(metadata_entry)
                            print(f"          📝 청크 {chunk_index+1}: {len(chunk)}자")
                            
                except Exception as e:
                    print(f"    ❌ JSON 파일 처리 오류: {e}")
            
            # 새로운 메타데이터를 벡터 매니저에 저장
            vector_manager.metadata = new_metadata
            
            # 벡터 생성
            print(f"\n🔍 벡터 생성 시작...")
            new_vectors = []
            
            for i, metadata_entry in enumerate(new_metadata):
                try:
                    text_content = metadata_entry['text_content']
                    print(f"  📝 벡터 생성 중: {i+1}/{len(new_metadata)} - {len(text_content)}자")
                    
                    # 텍스트 임베딩
                    embedding = vector_manager.embedding_client.get_embedding(text_content)
                    if embedding:
                        new_vectors.append(embedding)
                        print(f"    ✅ 벡터 생성 성공")
                    else:
                        print(f"    ❌ 벡터 생성 실패")
                        
                except Exception as e:
                    print(f"    ❌ 벡터 생성 오류: {e}")
            
            vector_manager.vectors = new_vectors
            success = len(new_metadata) > 0 and len(new_vectors) > 0
            
            if success:
                print("✅ data_1 폴더 파일들 임베딩 완료")
                print(f"📊 생성된 벡터: {len(vector_manager.vectors)}개")
                print(f"📊 생성된 메타데이터: {len(vector_manager.metadata)}개")
                
                # 벡터 파일 저장
                vector_file = vector_db_1_path / "hybrid_vectors.pkl"
                metadata_file = vector_db_1_path / "hybrid_metadata.json"
                
                import pickle
                with open(vector_file, 'wb') as f:
                    pickle.dump(vector_manager.vectors, f)
                
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(vector_manager.metadata, f, ensure_ascii=False, indent=2)
                
                print(f"💾 벡터 파일 저장 완료: {vector_file}")
                print(f"💾 메타데이터 파일 저장 완료: {metadata_file}")
            else:
                print("❌ data_1 폴더 파일들 임베딩 실패")
                
        except Exception as e:
            print(f"❌ data_1 폴더 임베딩 중 오류: {e}")
    else:
        print("\n" + "=" * 60)
        print("🔍 data_1 폴더 임베딩 건너뛰기")
        print("=" * 60)
        print("✅ 데이터 수집 모드 OFF - data_1 폴더 임베딩 건너뛰기")
    
    # 8. Vector DB 기반 주식 시장 분석 보고서 생성
    print("\n" + "=" * 60)
    print("📊 Vector DB 기반 주식 시장 분석 보고서")
    print("=" * 60)
    
    try:
        # Vector DB 분석기 클래스 정의
        class VectorDBAnalyzer:
            """vector_db 벡터 기반 분석기 (FAISS API 사용)"""
            
            def __init__(self):
                self.api_base_url = "http://localhost:8000"  # 메인 FAISS API 서버
                
                # 새로운 CLOVA API 설정 (vector_db_1_analyzer와 동일)
                self.api_key = os.getenv("NEW_CLOVA_API_KEY", "")
                self.request_id = os.getenv("NEW_CLOVA_REQUEST_ID", "4997d0ab4e434139bd982084de885077")
                self.model_endpoint = os.getenv("NEW_CLOVA_MODEL_ENDPOINT", "/v3/tasks/yl1fvofj/chat-completions")
                
                # CLOVA 클라이언트 초기화
                self.clova_client = self._create_clova_client()
                
                print("🔧 VectorDBAnalyzer 초기화 완료")
                print(f"📡 FAISS API 서버: {self.api_base_url}")
            
            def _create_clova_client(self):
                """CLOVA 클라이언트 생성"""
                class CompletionExecutor:
                    def __init__(self, host, api_key, request_id, model_endpoint=None):
                        self._host = host
                        self._api_key = api_key
                        self._request_id = request_id
                        self._model_endpoint = model_endpoint or "/v3/tasks/yl1fvofj/chat-completions"

                    def _send_request(self, completion_request):
                        headers = {
                            'Content-Type': 'application/json; charset=utf-8',
                            'Authorization': self._api_key,
                            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
                        }

                        print(f"🔍 CLOVA API 요청 정보:")
                        print(f"   호스트: {self._host}")
                        print(f"   엔드포인트: {self._model_endpoint}")
                        print(f"   Request ID: {self._request_id}")
                        print(f"   API 키: {self._api_key[:20]}...")

                        import http.client
                        conn = http.client.HTTPSConnection(self._host)
                        conn.request('POST', self._model_endpoint, json.dumps(completion_request), headers)
                        response = conn.getresponse()
                        
                        print(f"📡 CLOVA API 응답:")
                        print(f"   상태 코드: {response.status}")
                        
                        result = json.loads(response.read().decode(encoding='utf-8'))
                        conn.close()
                        return result

                    def execute(self, completion_request):
                        res = self._send_request(completion_request)
                        if res['status']['code'] == '20000':
                            # 새로운 모델은 message.content 형식으로 응답
                            if 'result' in res and 'message' in res['result'] and 'content' in res['result']['message']:
                                return res['result']['message']['content']
                            # 기존 text 형식도 지원
                            elif 'result' in res and 'text' in res['result']:
                                return res['result']['text']
                            else:
                                print(f"❌ 예상치 못한 응답 형식: {res}")
                                return 'Error'
                        else:
                            return 'Error'
                
                return CompletionExecutor(
                    host='clovastudio.stream.ntruss.com',
                    api_key=f'Bearer {self.api_key}',
                    request_id=self.request_id,
                    model_endpoint=self.model_endpoint
                )
            
            def check_faiss_api_server(self) -> bool:
                """FAISS API 서버 상태 확인"""
                try:
                    response = requests.get(f"{self.api_base_url}/health", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ FAISS API 서버 연결 성공")
                        print(f"   벡터 로드: {data.get('total_vectors', 0)}개")
                        print(f"   메타데이터: {data.get('total_metadata', 0)}개")
                        return True
                    else:
                        print(f"❌ FAISS API 서버 응답 오류: {response.status_code}")
                        return False
                except Exception as e:
                    print(f"❌ FAISS API 서버 연결 실패: {e}")
                    return False
            
            def search_vectors(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
                """FAISS API를 통한 벡터 검색"""
                try:
                    response = requests.post(
                        f"{self.api_base_url}/search",
                        json={"query": query, "top_k": top_k},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('results', [])
                    else:
                        print(f"❌ 검색 요청 실패: {response.status_code}")
                        return []
                        
                except requests.exceptions.Timeout:
                    print(f"❌ 검색 타임아웃 (60초)")
                    return []
                except Exception as e:
                    print(f"❌ 검색 중 오류: {e}")
                    return []
            
            def analyze_vectors(self) -> str:
                """벡터 데이터를 분석하여 보고서 생성"""
                print("🔍 vector_db 벡터 데이터 분석 중...")
                
                # 검색 쿼리 설정
                search_query = "어제 하루 뉴스 및 일일 거래데이터 이슈 요약"
                
                # FAISS 벡터 검색 수행
                print(f"🔍 검색 쿼리: {search_query}")
                search_results = self.search_vectors(search_query, top_k=10)
                
                if not search_results:
                    print("❌ 검색 결과가 없습니다.")
                    return ""
                
                print(f"✅ 검색 완료: {len(search_results)}개 결과")
                
                # 검색 결과에서 텍스트 내용 추출
                text_contents = []
                for result in search_results:
                    text_content = result.get('text_content', '')
                    if text_content:
                        text_contents.append(text_content)
                
                # 분석용 프롬프트 구성
                analysis_prompt = self._create_analysis_prompt(text_contents)
                
                print("🤖 CLOVA 모델에게 보고서 요청 중...")
                
                # 새로운 CLOVA 모델 형식 사용 (messages 형식)
                request_data = {
                    "messages": [
                        {
                            "role": "user",
                            "content": analysis_prompt
                        }
                    ],
                    "maxTokens": 4000,  # 4000자 보고서
                    "temperature": 0.7,
                    "topP": 0.8
                }
                
                # CLOVA API 호출
                response_text = self.clova_client.execute(request_data)
                
                if response_text and response_text != 'Error':
                    print(f"✅ 보고서 생성 완료: {len(response_text)}자")
                    return response_text
                else:
                    print("❌ CLOVA API 호출 실패")
                    return ""
                
            def _create_analysis_prompt(self, text_contents: List[str]) -> str:
                """분석용 프롬프트 생성"""
                prompt = f"""
당신은 주식 시장 분석 전문가입니다. 제공된 데이터를 바탕으로 어제 하루의 뉴스 및 일일 거래데이터를 요약한 보고서를 최대한 자세히 작성해주세요.

다음은 분석할 데이터입니다:

{chr(15).join(text_contents[:15])}  # 처음 10개 텍스트만 사용

보고서 작성 요구사항:
1. 총 글자수: 4000자 정도
2. 구조:
   - 서론: 주요 증시 요약
   - 본론: 뉴스에 기반한 어제 하루의 주요 이슈 요약
   - 결론: 어제 하루의 종합적인 주식 시장 분석

3. 각 종목별 분석 내용:
   - 어제 거래 동향 (종목명, 시가, 고가, 저가, 종가, 거래량)
   - 관련 뉴스 및 이슈


4. 전문적이고 객관적인 톤으로 작성
5. 구체적인 데이터와 근거 제시
6. 어제 하루의 시장 전반적인 분위기 분석

위 데이터를 바탕으로 어제 하루의 종합적인 주식 시장 분석 보고서를 작성해주세요.
"""
                return prompt
            
            def save_report(self, report: str) -> str:
                """보고서를 파일로 저장"""
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    report_file = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_2") / f"vector_db_report_{timestamp}.txt"
                    
                    with open(report_file, 'w', encoding='utf-8') as f:
                        f.write(f"# Vector DB 기반 어제 하루 주식 시장 분석 보고서\n")
                        f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"분석 벡터 수: {len(report)}자\n")
                        f.write(f"=" * 60 + "\n\n")
                        f.write(report)
                    
                    print(f"💾 보고서 저장 완료: {report_file}")
                    return str(report_file)
                    
                except Exception as e:
                    print(f"❌ 보고서 저장 실패: {e}")
                    return ""
            
            def run_analysis(self) -> bool:
                """전체 분석 프로세스 실행"""
                print("\n" + "=" * 60)
                print("🔍 Vector DB 기반 어제 하루 주식 시장 분석")
                print("=" * 60)
                
                # 1. FAISS API 서버 상태 확인
                if not self.check_faiss_api_server():
                    return False
                
                # 2. 분석 실행
                report = self.analyze_vectors()
                if not report:
                    return False
                
                # 3. 보고서 저장
                report_file = self.save_report(report)
                if not report_file:
                    return False
                
                # 4. 결과 출력
                print("\n" + "=" * 60)
                print("📊 분석 결과 전체 보고서")
                print("=" * 60)
                print(report)
                
                return True
        
        # Vector DB 분석 실행
        analyzer = VectorDBAnalyzer()
        analysis_success = analyzer.run_analysis()
        
        if analysis_success:
            print("✅ Vector DB 기반 분석 보고서 생성 완료")
        else:
            print("❌ Vector DB 기반 분석 보고서 생성 실패")
            
    except Exception as e:
        print(f"❌ Vector DB 분석 중 오류: {e}")
    
    # 9. Vector DB1 FAISS API 서버 시작
    if not start_vector_db1_api_server():
        print("❌ Vector DB1 FAISS API 서버 시작 실패로 인해 분석을 건너뜁니다.")
    else:
        # 10. vector_db_1 기반 주식 시장 분석 보고서 생성
        print("\n" + "=" * 60)
        print("📊 Vector DB1 기반 주식 시장 분석 보고서")
        print("=" * 60)
        
        try:
            from vector_db_1_analyzer import VectorDB1Analyzer
            analyzer = VectorDB1Analyzer()
            analysis_success = analyzer.run_analysis()
            
            if analysis_success:
                print("✅ Vector DB1 기반 분석 보고서 생성 완료")
            else:
                print("❌ Vector DB1 기반 분석 보고서 생성 실패")
                
        except Exception as e:
            print(f"❌ Vector DB1 분석 중 오류: {e}")
    
    # 11. 두 보고서 합치기 및 저장
    print("\n" + "=" * 60)
    print("📋 두 보고서 합치기 및 저장")
    print("=" * 60)
    
    try:
        # daily_report 폴더 생성
        daily_report_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/daily_report")
        daily_report_dir.mkdir(exist_ok=True)
        print(f"📁 daily_report 폴더 생성/확인: {daily_report_dir}")
        
        # 최근 생성된 보고서 파일들 찾기
        data_2_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_2")
        
        # Vector DB 보고서 찾기
        vector_db_reports = list(data_2_dir.glob("vector_db_report_*.txt"))
        vector_db_report = None
        if vector_db_reports:
            # 가장 최근 파일 선택
            vector_db_report = max(vector_db_reports, key=lambda x: x.stat().st_mtime)
            print(f"📄 Vector DB 보고서 발견: {vector_db_report.name}")
        
        # Vector DB1 보고서 찾기
        vector_db1_reports = list(data_2_dir.glob("vector_db_1_report_*.txt"))
        vector_db1_report = None
        if vector_db1_reports:
            # 가장 최근 파일 선택
            vector_db1_report = max(vector_db1_reports, key=lambda x: x.stat().st_mtime)
            print(f"📄 Vector DB1 보고서 발견: {vector_db1_report.name}")
        
        # 보고서 내용 읽기
        combined_content = []
        combined_content.append("# 일일 주식 시장 종합 분석 보고서")
        combined_content.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        combined_content.append("=" * 80)
        combined_content.append("")
        
        # Vector DB 보고서 추가
        if vector_db_report:
            try:
                with open(vector_db_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_content.append("## 📊 어제 하루 주식 시장 분석")
                    combined_content.append("")
                    combined_content.append(content)
                    combined_content.append("")
                    combined_content.append("=" * 80)
                    combined_content.append("")
                    print(f"✅ Vector DB 보고서 내용 추가: {len(content)}자")
            except Exception as e:
                print(f"❌ Vector DB 보고서 읽기 실패: {e}")
        else:
            print("⚠️ Vector DB 보고서를 찾을 수 없습니다.")
        
        # Vector DB1 보고서 추가
        if vector_db1_report:
            try:
                with open(vector_db1_report, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_content.append("## 📈 오늘 이슈가 있을 것으로 예상되는 주목 종목 분석")
                    combined_content.append("")
                    combined_content.append(content)
                    print(f"✅ Vector DB1 보고서 내용 추가: {len(content)}자")
            except Exception as e:
                print(f"❌ Vector DB1 보고서 읽기 실패: {e}")
        else:
            print("⚠️ Vector DB1 보고서를 찾을 수 없습니다.")
        
        # 합쳐진 보고서 저장
        if len(combined_content) > 4:  # 기본 헤더 외에 내용이 있는 경우
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            combined_report_file = daily_report_dir / f"daily_combined_report_{timestamp}.txt"
            
            with open(combined_report_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(combined_content))
            
            combined_text = '\n'.join(combined_content)
            print(f"💾 합쳐진 보고서 저장 완료: {combined_report_file}")
            print(f"📊 총 길이: {len(combined_text)}자")
            
            # 요약 정보 출력
            print(f"\n📋 보고서 요약:")
            if vector_db_report:
                print(f"  📊 Vector DB 보고서: {vector_db_report.name}")
            if vector_db1_report:
                print(f"  📈 Vector DB1 보고서: {vector_db1_report.name}")
            print(f"  📄 합쳐진 보고서: {combined_report_file.name}")
            
        else:
            print("❌ 합칠 보고서가 없습니다.")
            
    except Exception as e:
        print(f"❌ 보고서 합치기 중 오류: {e}")
    
    print("\n🎉 통합 데이터 수집 및 분석 테스트 완료!")

if __name__ == "__main__":
    main() 