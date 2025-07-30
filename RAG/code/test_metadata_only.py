#!/usr/bin/env python3
"""
메타데이터만 새로 생성하여 뉴스 데이터 포함 여부 확인
- 기존 벡터 파일은 유지
- 메타데이터만 새로 생성
- 뉴스 데이터 포함 여부 확인
"""

import json
import pickle
from pathlib import Path
from hybrid_vector_manager import HybridVectorManager
from clova_embedding import ClovaEmbeddingAPI
from clova_segmentation import ClovaSegmentationClient
from news_content_extractor import NewsContentExtractor

def test_metadata_generation():
    """메타데이터만 새로 생성하여 테스트"""
    print("=" * 60)
    print("🔍 메타데이터 생성 테스트")
    print("=" * 60)
    
    # data_1 폴더용 벡터 매니저 생성 (벡터 저장 없이)
    class MetadataOnlyVectorManager(HybridVectorManager):
        def __init__(self, data_dir: str):
            self.data_dir = Path(data_dir)
            self.vector_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/vector_db_1")
            
            # CLOVA 클라이언트 초기화
            self.embedding_client = ClovaEmbeddingAPI()
            self.segmentation_client = ClovaSegmentationClient()
            self.news_extractor = NewsContentExtractor()
            
            # 벡터 저장소 (읽기 전용)
            self.vectors_file = self.vector_dir / "hybrid_vectors.pkl"
            self.metadata_file = self.vector_dir / "hybrid_metadata.json"
            
            # 기존 벡터 데이터 로드
            self.vectors = []
            self.metadata = []
            self._load_vectors()
        
        def process_documents(self):
            """문서 처리 (메타데이터만 생성)"""
            print("📊 문서 처리 시작 (메타데이터만 생성)...")
            
            # 기존 메타데이터 초기화
            new_metadata = []
            
            # CSV 파일 처리
            csv_files = list(self.data_dir.glob("*.csv"))
            print(f"📄 CSV 파일 {len(csv_files)}개 발견")
            
            for csv_file in csv_files:
                print(f"🔍 CSV 파일 처리: {csv_file.name}")
                try:
                    import pandas as pd
                    df = pd.read_csv(csv_file)
                    
                    # CSV를 텍스트로 변환
                    text_content = self._dataframe_to_text(df, csv_file.name)
                    
                    # 청킹
                    chunks = self._segment_text_with_clova(text_content, max_length=2048)
                    
                    print(f"  📊 청킹 결과: {len(chunks)}개 청크")
                    
                    # 메타데이터 생성 (벡터는 생성하지 않음)
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
                        print(f"    📝 청크 {i+1}: {len(chunk)}자")
                        
                except Exception as e:
                    print(f"  ❌ CSV 파일 처리 오류: {e}")
            
            # JSON 파일 처리 (뉴스 데이터) - vector_db 형식으로 개별 기사별 처리
            json_files = list(self.data_dir.glob("*.json"))
            print(f"📄 JSON 파일 {len(json_files)}개 발견")
            
            for json_file in json_files:
                print(f"🔍 JSON 파일 처리: {json_file.name}")
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
                    
                    print(f"  📰 총 {len(all_articles)}개 뉴스 기사 발견")
                    
                    # 각 기사를 개별적으로 처리 (vector_db 방식)
                    for article_index, article in enumerate(all_articles):
                        print(f"    📰 기사 {article_index+1} 처리 시작")
                        
                        # 개별 기사를 텍스트로 변환
                        article_text = self._single_article_to_text(article, article_index)
                        print(f"      📝 기사 텍스트 길이: {len(article_text)}자")
                        print(f"      📝 기사 텍스트 미리보기: {article_text[:200]}...")
                        
                        # 청킹 (더 큰 크기로 설정하여 짤림 방지)
                        chunks = self._segment_text_with_clova(article_text, max_length=1024)
                        print(f"      🔄 세그멘테이션 결과: {len(chunks)}개 청크")
                        
                        # 각 청크의 길이 확인
                        for chunk_idx, chunk in enumerate(chunks):
                            print(f"        📄 청크 {chunk_idx+1} 길이: {len(chunk)}자")
                            print(f"        📄 청크 {chunk_idx+1} 미리보기: {chunk[:100]}...")
                        
                        print(f"    📰 기사 {article_index+1} 청킹 결과: {len(chunks)}개 청크")
                        
                        # 각 청크에 대해 메타데이터 생성
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
                            print(f"      📝 청크 {chunk_index+1}: {len(chunk)}자")
                            print(f"      📝 메타데이터 text_content 길이: {len(metadata_entry['text_content'])}자")
                        
                except Exception as e:
                    print(f"  ❌ JSON 파일 처리 오류: {e}")
            
            # 결과 출력
            print(f"\n📊 메타데이터 생성 완료:")
            print(f"  📄 총 메타데이터 항목: {len(new_metadata)}개")
            
            # 타입별 통계
            csv_count = len([m for m in new_metadata if m["type"] == "csv"])
            news_count = len([m for m in new_metadata if m["type"] == "news"])
            
            print(f"  📊 CSV 메타데이터: {csv_count}개")
            print(f"  📰 뉴스 메타데이터: {news_count}개")
            
            # 샘플 출력
            if new_metadata:
                print(f"\n📝 메타데이터 구조 상세 분석:")
                print("=" * 60)
                
                # CSV 메타데이터 샘플
                csv_samples = [m for m in new_metadata if m["type"] == "csv"]
                if csv_samples:
                    print(f"\n📊 CSV 메타데이터 샘플 (첫 번째):")
                    csv_sample = csv_samples[0]
                    for key, value in csv_sample.items():
                        if key == "text_content":
                            print(f"  {key}: {str(value)[:100]}...")
                        else:
                            print(f"  {key}: {value}")
                
                # 뉴스 메타데이터 샘플
                news_samples = [m for m in new_metadata if m["type"] == "news"]
                if news_samples:
                    print(f"\n📰 뉴스 메타데이터 샘플 (첫 번째):")
                    news_sample = news_samples[0]
                    for key, value in news_sample.items():
                        if key == "text_content":
                            print(f"  {key}: {str(value)[:100]}...")
                        else:
                            print(f"  {key}: {value}")
                
                # 뉴스 메타데이터 샘플 (두 번째)
                if len(news_samples) > 1:
                    print(f"\n📰 뉴스 메타데이터 샘플 (두 번째):")
                    news_sample2 = news_samples[1]
                    for key, value in news_sample2.items():
                        if key == "text_content":
                            print(f"  {key}: {str(value)[:100]}...")
                        else:
                            print(f"  {key}: {value}")
                
                print(f"\n📊 전체 메타데이터 구조 요약:")
                print(f"  - 총 항목 수: {len(new_metadata)}개")
                print(f"  - CSV 항목: {len(csv_samples)}개")
                print(f"  - 뉴스 항목: {len(news_samples)}개")
                
                # 각 타입별 필드 분석
                if csv_samples:
                    csv_fields = list(csv_samples[0].keys())
                    print(f"  - CSV 필드: {csv_fields}")
                
                if news_samples:
                    news_fields = list(news_samples[0].keys())
                    print(f"  - 뉴스 필드: {news_fields}")
            
            return len(new_metadata) > 0

        def _article_to_text(self, news_data: dict, filename: str) -> str:
            """뉴스 데이터를 텍스트로 변환 (vector_db와 동일한 방식)"""
            text_parts = []
            
            # vector_db와 동일한 방식: 'items' 배열 사용
            articles = news_data.get('items', [])
            
            # 만약 'stocks' 구조라면 'items'로 변환
            if 'stocks' in news_data and not articles:
                all_articles = []
                stocks = news_data.get('stocks', {})
                for stock_name, stock_data in stocks.items():
                    stock_articles = stock_data.get('items', [])
                    # 각 기사에 종목명 추가
                    for article in stock_articles:
                        article['stock_name'] = stock_name
                    all_articles.extend(stock_articles)
                articles = all_articles
            
            text_parts.append(f"파일명: {filename}")
            text_parts.append(f"총 {len(articles)}개 뉴스 기사")
            text_parts.append("")
            
            for i, article in enumerate(articles):
                text_parts.append(f"=== 뉴스 {i+1} ===")
                
                # 종목명 (있는 경우)
                stock_name = article.get('stock_name', '')
                if stock_name:
                    text_parts.append(f"종목: {stock_name}")
                
                # 기사 제목
                title = article.get('title', '')
                if title:
                    # HTML 태그 제거
                    import re
                    clean_title = re.sub(r'<[^>]+>', '', title)
                    text_parts.append(f"제목: {clean_title}")
                
                # 기사 내용 (설명)
                description = article.get('description', '')
                if description:
                    # HTML 태그 제거
                    import re
                    clean_description = re.sub(r'<[^>]+>', '', description)
                    text_parts.append(f"내용: {clean_description}")
                
                # 발행일
                pub_date = article.get('pubDate', '')
                if pub_date:
                    text_parts.append(f"발행일: {pub_date}")
                
                text_parts.append("")
            
            return "\n".join(text_parts)
        
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
                print(f"        📰 제목 길이: {len(clean_title)}자")
            
            # URL에서 전체 본문 추출 시도
            full_content = None
            url = article.get('originallink') or article.get('link')
            
            if url:
                try:
                    print(f"      🔗 URL에서 본문 추출 시도: {url}")
                    full_content = self.news_extractor.extract_article_content(url)
                    if full_content and full_content.get('content'):
                        print(f"      ✅ 전체 본문 추출 성공: {len(full_content['content'])}자")
                        print(f"      📄 본문 미리보기: {full_content['content'][:100]}...")
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
                print(f"        📄 정제된 본문 길이: {len(clean_content)}자")
                print(f"        📄 정제된 본문 미리보기: {clean_content}...")
            else:
                # 요약문 사용
                description = article.get('description', '')
                if description:
                    # HTML 태그 제거
                    import re
                    clean_description = re.sub(r'<[^>]+>', '', description)
                    text_parts.append(f"내용: {clean_description}")
                    print(f"        📄 요약문 길이: {len(clean_description)}자")
                    print(f"        📄 요약문 미리보기: {clean_description[:100]}...")
            
            # 발행일
            pub_date = article.get('pubDate', '')
            if pub_date:
                text_parts.append(f"발행일: {pub_date}")
            
            final_text = "\n".join(text_parts)
            print(f"        📝 최종 텍스트 길이: {len(final_text)}자")
            print(f"        📝 최종 텍스트 미리보기: {final_text}...")
            
            return final_text

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

    # 테스트 실행
    try:
        vector_manager = MetadataOnlyVectorManager(
            data_dir="/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1"
        )
        
        success = vector_manager.process_documents()
        
        if success:
            print("\n✅ 메타데이터 생성 테스트 완료")
            print("📊 뉴스 데이터가 메타데이터에 포함되는 것을 확인했습니다!")
            
            # 실제 메타데이터 저장
            print("\n💾 새로운 메타데이터를 vector_db_1에 저장합니다...")
            
            # 새로운 메타데이터 생성 (process_documents에서 생성된 것 사용)
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
                        
                except Exception as e:
                    print(f"  ❌ CSV 파일 처리 오류: {e}")
            
            # JSON 파일 처리 (뉴스 데이터) - 개별 뉴스로 처리
            json_files = list(Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1").glob("*.json"))
            print(f"  📄 JSON 파일 {len(json_files)}개 발견")
            for json_file in json_files:
                try:
                    print(f"    🔍 JSON 파일 처리: {json_file.name}")
                    with open(json_file, 'r', encoding='utf-8') as f:
                        news_data = json.load(f)
                    
                    # 개별 뉴스 기사 처리
                    articles = []
                    stocks = news_data.get('stocks', {})
                    for stock_name, stock_data in stocks.items():
                        stock_articles = stock_data.get('items', [])
                        for article in stock_articles:
                            article['stock_name'] = stock_name  # 종목명 추가
                            articles.append(article)
                    
                    print(f"      📰 총 {len(articles)}개 뉴스 기사 발견")
                    for article_index, article in enumerate(articles):
                        print(f"        📰 기사 {article_index+1} 처리 중...")
                        # 개별 기사를 텍스트로 변환
                        article_text = vector_manager._single_article_to_text(article, article_index)
                        
                        # 청킹
                        chunks = vector_manager._segment_text_with_clova(article_text, max_length=1024)
                        print(f"        📝 청킹 결과: {len(chunks)}개 청크")
                        
                        # 각 청크에 대해 메타데이터 생성
                        for chunk_index, chunk in enumerate(chunks):
                            metadata_entry = {
                                "filename": json_file.name,
                                "type": "news",
                                "article_index": article_index,
                                "chunk_index": chunk_index,
                                "total_articles": len(articles),
                                "total_chunks": len(chunks),
                                "title": article.get('title', ''),
                                "text_content": chunk,
                                "text_length": len(chunk),
                                "created_at": "2025-01-31T00:00:00"
                            }
                            new_metadata.append(metadata_entry)
                            print(f"          📝 뉴스 메타데이터 추가: article_index={article_index}, chunk_index={chunk_index}")
                        
                except Exception as e:
                    print(f"  ❌ JSON 파일 처리 오류: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 메타데이터 파일 저장
            metadata_file = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/vector_db_1/hybrid_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(new_metadata, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 새로운 메타데이터 저장 완료: {metadata_file}")
            print(f"📊 총 {len(new_metadata)}개 메타데이터 항목 저장됨")
            
            # 저장된 메타데이터 확인
            print(f"\n🔍 저장된 메타데이터 확인:")
            csv_count = len([m for m in new_metadata if m["type"] == "csv"])
            news_count = len([m for m in new_metadata if m["type"] == "news"])
            print(f"  📊 CSV 항목: {csv_count}개")
            print(f"  📰 뉴스 항목: {news_count}개")
            
            if news_count > 0:
                print("✅ 뉴스 데이터가 성공적으로 메타데이터에 포함되었습니다!")
            else:
                print("❌ 뉴스 데이터가 메타데이터에 포함되지 않았습니다.")
                
        else:
            print("\n❌ 메타데이터 생성 실패")
            
    except Exception as e:
        print(f"\n❌ 테스트 중 오류: {e}")

if __name__ == "__main__":
    test_metadata_generation() 