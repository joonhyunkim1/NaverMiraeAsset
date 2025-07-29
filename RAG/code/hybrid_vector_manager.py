#!/usr/bin/env python3
"""
하이브리드 벡터 관리 시스템
- LlamaIndex의 문서 처리 파이프라인 유지
- CLOVA 세그멘테이션 API 사용
- CLOVA 임베딩 API로 직접 저장
"""

import json
import os
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import pandas as pd

from clova_embedding import ClovaEmbeddingAPI
from clova_segmentation import ClovaSegmentationClient
from news_content_extractor import NewsContentExtractor


class HybridVectorManager:
    """하이브리드 벡터 관리 시스템 (LlamaIndex + CLOVA)"""
    
    def __init__(self, data_dir: str = "/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data"):
        self.data_dir = Path(data_dir)
        self.vector_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/vector_db")
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
    
    def _load_vectors(self):
        """저장된 벡터 데이터 로드"""
        try:
            if self.vectors_file.exists():
                with open(self.vectors_file, 'rb') as f:
                    self.vectors = pickle.load(f)
                print(f"✅ 기존 벡터 로드 완료: {len(self.vectors)}개")
            
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"✅ 기존 메타데이터 로드 완료: {len(self.metadata)}개")
                
        except Exception as e:
            print(f"⚠️ 벡터 로드 오류: {e}")
            self.vectors = []
            self.metadata = []
    
    def _save_vectors(self):
        """벡터 데이터 저장"""
        try:
            with open(self.vectors_file, 'wb') as f:
                pickle.dump(self.vectors, f)
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                
            print(f"✅ 벡터 저장 완료: {len(self.vectors)}개")
            
        except Exception as e:
            print(f"❌ 벡터 저장 오류: {e}")
    
    def process_documents(self, rebuild: bool = False) -> bool:
        """문서들을 처리하여 벡터로 변환 (LlamaIndex 방식 + CLOVA 저장)"""
        if rebuild:
            print("🔄 벡터 재구축 모드")
            self.vectors = []
            self.metadata = []
        
        print("📚 문서 처리 시작...")
        
        # CSV 파일 처리
        csv_success = self._process_csv_files()
        
        # 뉴스 파일 처리
        news_success = self._process_news_files()
        
        if csv_success or news_success:
            self._save_vectors()
            print(f"🎉 문서 처리 완료: 총 {len(self.vectors)}개 벡터")
            return True
        
        print("❌ 문서 처리 실패")
        return False
    
    def _process_csv_files(self) -> bool:
        """CSV 파일들을 처리하여 벡터로 변환 (LlamaIndex 방식)"""
        csv_files = list(self.data_dir.glob("*.csv"))
        
        if not csv_files:
            print("📁 CSV 파일을 찾을 수 없습니다.")
            return False
        
        print(f"📊 CSV 파일 처리 중: {len(csv_files)}개")
        
        for csv_file in csv_files:
            try:
                print(f"  📄 처리 중: {csv_file.name}")
                
                # CSV 파일 읽기
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
                
                # DataFrame을 텍스트로 변환 (LlamaIndex 방식과 동일)
                text_content = self._dataframe_to_text(df, csv_file.stem)
                
                # 첫 번째 항목 변환 결과 출력 (디버그)
                print(f"  🔍 첫 번째 종목 변환 결과:")
                lines = text_content.split('\n')
                for i, line in enumerate(lines[:10]):  # 처음 10줄만 출력
                    if line.strip():
                        print(f"    {i+1:2d}: {line}")
                if len(lines) > 10:
                    print(f"    ... (총 {len(lines)}줄)")
                
                print(f"  🔧 CSV 데이터 - 최적화된 세그멘테이션 적용")
                chunks = self._segment_text_with_clova(text_content, max_length=2048)
                
                # 각 청크를 CLOVA 임베딩 API로 벡터화 (직접 저장)
                for i, chunk in enumerate(chunks):
                    vector = self.embedding_client.get_text_embedding(chunk)
                    
                    if vector:
                        self.vectors.append(vector)
                        self.metadata.append({
                            "filename": csv_file.name,
                            "type": "csv",
                            "chunk_index": i,
                            "total_chunks": len(chunks),
                            "rows": len(df),
                            "columns": list(df.columns),
                            "text_content": chunk,  # 실제 텍스트 내용 추가
                            "text_length": len(chunk),
                            "created_at": datetime.now().isoformat()
                        })
                        print(f"    ✅ 청크 {i+1}/{len(chunks)} 벡터화 완료")
                    else:
                        print(f"    ❌ 청크 {i+1} 벡터화 실패")
                
            except Exception as e:
                print(f"  ❌ {csv_file.name} 처리 실패: {e}")
        
        return True
    
    def _process_news_files(self) -> bool:
        """뉴스 파일들을 처리하여 벡터로 변환 (LlamaIndex 방식)"""
        news_files = list(self.data_dir.glob("*news*.json"))
        
        if not news_files:
            print("📰 뉴스 파일을 찾을 수 없습니다.")
            return False
        
        print(f"📰 뉴스 파일 처리 중: {len(news_files)}개")
        
        for news_file in news_files:
            try:
                print(f"  📄 처리 중: {news_file.name}")
                
                # JSON 파일 읽기
                with open(news_file, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
                
                # 뉴스 기사들을 텍스트로 변환 (LlamaIndex 방식과 동일)
                articles = news_data.get('items', [])
                
                for i, article in enumerate(articles):
                    # 본문 전체 추출 시도
                    full_content = self._get_full_article_content(article)
                    
                    if full_content:
                        # 본문 전체가 있는 경우
                        text_content = self._article_to_text_with_full_content(article, i, full_content)
                    else:
                        # 본문 추출 실패 시 기존 방식 사용
                        text_content = self._article_to_text(article, i)
                    
                    # 첫 번째 뉴스 기사 변환 결과 출력 (디버그)
                    if i == 0:
                        print(f"  🔍 첫 번째 뉴스 기사 변환 결과:")
                        lines = text_content.split('\n')
                        for j, line in enumerate(lines):
                            if line.strip():
                                print(f"    {j+1:2d}: {line}")
                    
                    # CLOVA 세그멘테이션 API로 청킹 (LlamaIndex 방식과 동일)
                    print(f"  📰 뉴스 데이터 - 기본 세그멘테이션 적용")
                    chunks = self._segment_text_with_clova(text_content, max_length=512)
                    
                    # 각 청크를 CLOVA 임베딩 API로 벡터화 (직접 저장)
                    for j, chunk in enumerate(chunks):
                        vector = self.embedding_client.get_text_embedding(chunk)
                        
                        if vector:
                            self.vectors.append(vector)
                            self.metadata.append({
                                "filename": news_file.name,
                                "type": "news",
                                "article_index": i,
                                "chunk_index": j,
                                "total_articles": len(articles),
                                "total_chunks": len(chunks),
                                "title": article.get('title', ''),
                                "text_content": chunk,  # 실제 텍스트 내용 추가
                                "text_length": len(chunk),
                                "created_at": datetime.now().isoformat()
                            })
                            print(f"    ✅ 기사 {i+1} 청크 {j+1}/{len(chunks)} 벡터화 완료")
                        else:
                            print(f"    ❌ 기사 {i+1} 청크 {j+1} 벡터화 실패")
                
            except Exception as e:
                print(f"  ❌ {news_file.name} 처리 실패: {e}")
        
        return True
    
    def _dataframe_to_text(self, df: pd.DataFrame, filename: str) -> str:
        """DataFrame을 텍스트로 변환 (LlamaIndex 방식과 동일)"""
        text_parts = []
        
        # 파일명 정보
        text_parts.append(f"파일명: {filename}")
        text_parts.append(f"총 {len(df)}행, {len(df.columns)}컬럼")
        text_parts.append("")
        
        # KRX 데이터인 경우 특별 처리
        if 'ISU_ABBRV' in df.columns and 'TDD_CLSPRC' in df.columns:
            text_parts.append("=== KRX 일일거래정보 (70% 기준 필터링) ===")
            text_parts.append("")
            
            # 전체 데이터에서 거래대금 하위 70%와 등락률 하위 70%에서 겹치는 주식 제외
            df_processed = df.copy()
            
            # FLUC_RT 컬럼을 등락률로 사용
            df_processed['등락률'] = df_processed['FLUC_RT']
            df_processed['등락률_절대값'] = df_processed['등락률'].abs()
            
            print(f"📊 전체 데이터: {len(df_processed)}개 종목")
            
            # 거래대금 기준 하위 70% 찾기
            df_trading_value_sorted = df_processed.sort_values('ACC_TRDVAL', ascending=True)
            bottom_70_percent_trading = int(len(df_trading_value_sorted) * 0.7)
            low_trading_stocks = set(df_trading_value_sorted.head(bottom_70_percent_trading)['ISU_ABBRV'].tolist())
            
            # 등락률 기준 하위 70% 찾기 (절대값 기준)
            df_change_rate_sorted = df_processed.sort_values('등락률_절대값', ascending=True)
            bottom_70_percent_change = int(len(df_change_rate_sorted) * 0.7)
            low_change_stocks = set(df_change_rate_sorted.head(bottom_70_percent_change)['ISU_ABBRV'].tolist())
            
            # 겹치는 주식들 찾기
            overlapping_stocks = low_trading_stocks.intersection(low_change_stocks)
            
            print(f"📊 거래대금 하위 70%: {len(low_trading_stocks)}개 종목")
            print(f"📊 등락률 하위 70%: {len(low_change_stocks)}개 종목")
            print(f"📊 겹치는 종목: {len(overlapping_stocks)}개")
            
            # 겹치는 주식들을 제외한 최종 필터링
            df_final_filtered = df_processed[~df_processed['ISU_ABBRV'].isin(overlapping_stocks)]
            
            print(f"📊 최종 필터링 결과: {len(df_processed)}개 → {len(df_final_filtered)}개")
            
            # 각 종목별로 읽기 쉬운 형태로 변환
            for idx, row in df_final_filtered.iterrows():
                stock_name = row.get('ISU_ABBRV', '')  # 실제 컬럼명
                stock_code = row.get('ISU_CD', '')     # 실제 컬럼명
                
                if stock_name and stock_code:
                    # 가격 정보
                    open_price = row.get('TDD_OPNPRC', 0)
                    high_price = row.get('TDD_HGPRC', 0)
                    low_price = row.get('TDD_LWPRC', 0)
                    close_price = row.get('TDD_CLSPRC', 0)
                    trading_value = row.get('ACC_TRDVAL', 0)
                    change_rate = row.get('등락률', 0.0)
                    
                    # 종목 정보를 읽기 쉬운 형태로 구성
                    stock_info = f"종목명: {stock_name}, 시가: {open_price}, 고가: {high_price}, 저가: {low_price}, 종가: {close_price}, 거래대금: {trading_value}, 등락률: {change_rate:.2f}"
                    text_parts.append(stock_info)
            
            text_parts.append("")
            text_parts.append(f"총 {len(df_final_filtered)}개 종목의 거래 정보 (70% 기준 필터링)")
        else:
            # 일반 CSV 파일 처리 (기존 방식)
            text_parts.append("컬럼명:")
            for col in df.columns:
                text_parts.append(f"  - {col}")
            text_parts.append("")
            
            # 데이터 샘플 (처음 10행)
            text_parts.append("데이터 샘플 (처음 10행):")
            sample_df = df.head(10)
            text_parts.append(sample_df.to_string(index=False))
        
        return "\n".join(text_parts)
    
    def _article_to_text(self, article: Dict, index: int) -> str:
        """뉴스 기사를 텍스트로 변환 (LlamaIndex 방식과 동일)"""
        text_parts = []
        
        # 기사 제목
        title = article.get('title', '')
        if title:
            text_parts.append(f"제목: {title}")
        
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
        
        return "\n".join(text_parts)
    
    def _segment_text_with_clova(self, text: str, max_length: int = 512) -> List[str]:
        """CLOVA 세그멘테이션 API로 텍스트를 청크로 분할 (LlamaIndex 방식과 동일)"""
        try:
            # CLOVA 세그멘테이션 API 사용 (LlamaIndex 방식과 동일)
            segments = self.segmentation_client.segment_text(text, max_length)
            if segments:
                print(f"    📝 CLOVA 세그멘테이션 완료: {len(segments)}개 청크")
                return segments
        except Exception as e:
            print(f"⚠️ 세그멘테이션 API 오류: {e}")
        
        # 폴백: 간단한 청킹 (LlamaIndex 방식과 동일)
        print(f"    📝 폴백 청킹 사용: {max_length}자 단위")
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # 공백 포함
            if current_length + word_length > max_length and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def get_vectors_for_analysis(self) -> tuple[List[List[float]], List[Dict[str, Any]]]:
        """분석용 벡터와 메타데이터 반환"""
        return self.vectors, self.metadata
    
    def get_vector_info(self) -> Dict[str, Any]:
        """벡터 정보 반환"""
        return {
            "total_vectors": len(self.vectors),
            "vector_dimension": len(self.vectors[0]) if self.vectors else 0,
            "metadata_count": len(self.metadata),
            "vector_file": str(self.vectors_file),
            "metadata_file": str(self.metadata_file)
        }

    def _get_full_article_content(self, article: Dict) -> Optional[str]:
        """뉴스 기사의 본문 전체를 가져오기"""
        try:
            # 원본 링크 우선, 없으면 네이버 링크 사용
            url = article.get('originallink') or article.get('link')
            if not url:
                return None
            
            # NewsContentExtractor를 사용해서 본문 추출
            content_data = self.news_extractor.extract_article_content(url)
            if content_data and content_data.get('content'):
                return content_data['content']
            
            return None
            
        except Exception as e:
            print(f"본문 추출 실패: {e}")
            return None
    
    def _article_to_text_with_full_content(self, article: Dict, index: int, full_content: str) -> str:
        """뉴스 기사를 텍스트로 변환 (본문 전체 포함)"""
        text_parts = []
        
        # 기사 제목
        title = article.get('title', '')
        if title:
            text_parts.append(f"제목: {title}")
        
        # 기사 본문 전체
        text_parts.append(f"본문: {full_content}")
        
        # 발행일
        pub_date = article.get('pubDate', '')
        if pub_date:
            text_parts.append(f"발행일: {pub_date}")
        
        return "\n".join(text_parts)


if __name__ == "__main__":
    # 테스트
    manager = HybridVectorManager()
    success = manager.process_documents(rebuild=True)
    
    if success:
        info = manager.get_vector_info()
        print(f"✅ 벡터 처리 완료: {info}")
    else:
        print("❌ 벡터 처리 실패") 