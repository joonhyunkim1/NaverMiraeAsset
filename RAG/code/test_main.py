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
    print("=" * 60)
    print("🚀 통합 데이터 수집 테스트")
    print("📅 실행 시간:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
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
    analysis_success = analyzer.run_analysis(rebuild_vectors=True)  # 벡터 재구축
    
    if analysis_success:
        print("✅ FAISS 벡터 검색 기반 분석 완료")
        
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
        print("❌ FAISS 벡터 검색 기반 분석 실패")
    
    # 7. data_1 폴더 파일들 임베딩하여 vector_db_1에 저장
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
        
        # data_1 폴더용 벡터 매니저 초기화
        vector_manager = Data1VectorManager(
            data_dir="/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1"
        )
        
        print("🔧 data_1 폴더 벡터 매니저 초기화 완료")
        print(f"📁 데이터 디렉토리: {vector_manager.data_dir}")
        print(f"📁 벡터 디렉토리: {vector_manager.vector_dir}")
        
        # data_1 폴더의 파일들 처리
        print("\n📊 data_1 폴더 파일 처리 중...")
        success = vector_manager.process_documents()
        
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
    
    # 8. Vector DB1 FAISS API 서버 시작
    if not start_vector_db1_api_server():
        print("❌ Vector DB1 FAISS API 서버 시작 실패로 인해 분석을 건너뜁니다.")
    else:
        # 9. vector_db_1 기반 주식 시장 분석 보고서 생성
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
    
    print("\n🎉 통합 데이터 수집 및 분석 테스트 완료!")

if __name__ == "__main__":
    main() 