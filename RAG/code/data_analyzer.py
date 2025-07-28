#!/usr/bin/env python3
"""
데이터 분석 및 CLOVA 통합 시스템
- KRX 일일 주가 데이터 및 뉴스 데이터를 CLOVA Segmentation과 Embedding으로 처리
- CLOVA 모델에게 데이터를 전달하여 이슈 종목 추출
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

# CLOVA API 클라이언트들
from clova_segmentation import ClovaSegmentationClient
from clova_embedding import ClovaEmbeddingAPI
from clova_chat_client import ClovaChatClient

# 환경변수 로드
env_path = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/code/.env")
load_dotenv(env_path)

class DataAnalyzer:
    """데이터 분석 및 CLOVA 통합 클래스"""
    
    def __init__(self):
        self.data_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data")
        self.output_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1")
        self.output_dir.mkdir(exist_ok=True)
        
        # CLOVA API 클라이언트들 초기화
        self.segmentation_client = ClovaSegmentationClient()
        self.embedding_client = ClovaEmbeddingAPI()
        self.chat_client = ClovaChatClient()
        
        print("🔧 DataAnalyzer 초기화 완료")
        print(f"📁 데이터 디렉토리: {self.data_dir}")
        print(f"📁 출력 디렉토리: {self.output_dir}")
    
    def load_krx_data(self) -> Optional[pd.DataFrame]:
        """KRX 일일 주가 데이터 로드"""
        try:
            # 가장 최근 KRX CSV 파일 찾기
            krx_files = list(self.data_dir.glob("krx_daily_trading_*.csv"))
            if not krx_files:
                print("❌ KRX 데이터 파일을 찾을 수 없습니다.")
                return None
            
            latest_file = max(krx_files, key=lambda x: x.stat().st_mtime)
            print(f"📊 KRX 데이터 파일 로드: {latest_file.name}")
            
            df = pd.read_csv(latest_file, encoding='utf-8-sig')
            print(f"✅ KRX 데이터 로드 완료: {len(df)}개 종목")
            return df
            
        except Exception as e:
            print(f"❌ KRX 데이터 로드 실패: {e}")
            return None
    
    def load_news_data(self) -> Optional[Dict]:
        """뉴스 데이터 로드"""
        try:
            # 가장 최근 뉴스 JSON 파일 찾기
            news_files = list(self.data_dir.glob("naver_news_*.json"))
            if not news_files:
                print("❌ 뉴스 데이터 파일을 찾을 수 없습니다.")
                return None
            
            latest_file = max(news_files, key=lambda x: x.stat().st_mtime)
            print(f"📰 뉴스 데이터 파일 로드: {latest_file.name}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            print(f"✅ 뉴스 데이터 로드 완료: {len(news_data.get('items', []))}개 기사")
            return news_data
            
        except Exception as e:
            print(f"❌ 뉴스 데이터 로드 실패: {e}")
            return None
    
    def prepare_krx_text(self, df: pd.DataFrame) -> str:
        """KRX 데이터를 텍스트로 변환"""
        text_parts = []
        
        text_parts.append("=== KRX 일일 주가 데이터 ===")
        text_parts.append(f"총 종목 수: {len(df)}개")
        text_parts.append(f"데이터 수집 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        text_parts.append("")
        
        # 상위 종목들의 정보 (거래량 기준으로 정렬)
        df_sorted = df.sort_values('ACC_TRDVOL', ascending=False)
        
        # 상위 20개 종목만 포함 (임베딩 한도 고려)
        for idx, row in df_sorted.head(20).iterrows():
            stock_info = []
            stock_info.append(f"종목 {idx+1}: {row.get('ISU_ABBRV', 'N/A')}")
            stock_info.append(f"  종목코드: {row.get('ISU_CD', 'N/A')}")
            stock_info.append(f"  종가: {row.get('TDD_CLSPRC', 'N/A')}원")
            stock_info.append(f"  전일대비: {row.get('CMPPREVDD_PRC', 'N/A')}원 ({row.get('FLUC_RT', 'N/A')}%)")
            stock_info.append(f"  거래량: {row.get('ACC_TRDVOL', 'N/A')}주")
            stock_info.append(f"  거래대금: {row.get('ACC_TRDVAL', 'N/A')}원")
            stock_info.append(f"  시가총액: {row.get('MKTCAP', 'N/A')}원")
            stock_info.append("")
            
            text_parts.extend(stock_info)
        
        return "\n".join(text_parts)
    
    def prepare_news_text(self, news_data: Dict) -> str:
        """뉴스 데이터를 텍스트로 변환"""
        text_parts = []
        
        text_parts.append("=== 최신 뉴스 데이터 ===")
        text_parts.append(f"총 뉴스 수: {len(news_data.get('items', []))}개")
        text_parts.append(f"검색어: {news_data.get('query', 'N/A')}")
        text_parts.append("")
        
        # 뉴스 기사들
        for idx, item in enumerate(news_data.get('items', []), 1):
            news_info = []
            news_info.append(f"뉴스 {idx}:")
            news_info.append(f"  제목: {item.get('title', 'N/A')}")
            news_info.append(f"  설명: {item.get('description', 'N/A')}")
            news_info.append(f"  발행일: {item.get('pubDate', 'N/A')}")
            news_info.append(f"  링크: {item.get('link', 'N/A')}")
            news_info.append("")
            
            text_parts.extend(news_info)
        
        return "\n".join(text_parts)
    
    def segment_data(self, text: str) -> List[str]:
        """CLOVA Segmentation으로 텍스트 분할"""
        try:
            print("🔪 CLOVA Segmentation으로 텍스트 분할 중...")
            chunks = self.segmentation_client.segment_text(
                text=text,
                max_length=512,
                overlap=50
            )
            
            if chunks:
                print(f"✅ 텍스트 분할 완료: {len(chunks)}개 청크")
                return chunks
            else:
                print("❌ 텍스트 분할 실패")
                return [text]  # 실패 시 원본 텍스트 반환
                
        except Exception as e:
            print(f"❌ Segmentation 오류: {e}")
            return [text]
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """CLOVA Embedding으로 벡터 생성"""
        try:
            print("🔢 CLOVA Embedding으로 벡터 생성 중...")
            embeddings = self.embedding_client.get_text_embeddings(texts)
            
            if embeddings:
                print(f"✅ 벡터 생성 완료: {len(embeddings)}개")
                return embeddings
            else:
                print("❌ 벡터 생성 실패")
                return []
                
        except Exception as e:
            print(f"❌ Embedding 오류: {e}")
            return []
    
    def analyze_with_clova(self, krx_text: str, news_text: str) -> Optional[str]:
        """CLOVA 모델에게 데이터를 전달하여 이슈 종목 분석"""
        try:
            print("🤖 CLOVA 모델에게 데이터 전달 중...")
            
            # 분석 요청 메시지 구성
            analysis_prompt = f"""
다음은 지난 24시간의 국내 주식 시장 데이터입니다.

=== 주가 데이터 ===
{krx_text}

=== 뉴스 데이터 ===
{news_text}

위 데이터를 분석하여 지난 24시간 동안 이슈가 되었던 주식 종목들을 추출해주세요.
각 종목에 대해 다음 정보를 포함해주세요:
1. 종목명
2. 이슈가 된 이유 (뉴스 내용 기반)
3. 주가 변동 상황
4. 향후 전망

분석 결과는 JSON 형태로 반환해주세요.
"""
            
            # CLOVA Chat API로 분석 요청
            response = self.chat_client.create_chat_completion(
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=1000,
                temperature=0.7
            )
            
            if response:
                print("✅ CLOVA 분석 완료")
                print(f"📝 응답 길이: {len(response)} 문자")
                return response
            else:
                print("❌ CLOVA 분석 실패 - 응답이 비어있음")
                return None
                
        except Exception as e:
            print(f"❌ CLOVA 분석 오류: {e}")
            return None
    
    def save_analysis_result(self, result: str, filename: str = None) -> str:
        """분석 결과 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"clova_analysis_{timestamp}.json"
        
        file_path = self.output_dir / filename
        
        try:
            # JSON 형태로 저장
            analysis_data = {
                "analysis_time": datetime.now().isoformat(),
                "result": result
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 분석 결과 저장 완료: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ 분석 결과 저장 실패: {e}")
            return ""
    
    def run_analysis(self) -> bool:
        """전체 분석 프로세스 실행"""
        print("=" * 60)
        print("🚀 데이터 분석 및 CLOVA 통합 시스템")
        print("=" * 60)
        
        # 1. 데이터 로드
        print("\n1️⃣ 데이터 로드 중...")
        krx_df = self.load_krx_data()
        news_data = self.load_news_data()
        
        if krx_df is None or news_data is None:
            print("❌ 데이터 로드 실패")
            return False
        
        # 2. 텍스트 변환
        print("\n2️⃣ 텍스트 변환 중...")
        krx_text = self.prepare_krx_text(krx_df)
        news_text = self.prepare_news_text(news_data)
        
        # 3. 뉴스 데이터 먼저 Segmentation 및 Embedding (한도 우선 처리)
        print("\n3️⃣ 뉴스 데이터 CLOVA Segmentation 중...")
        news_chunks = self.segment_data(news_text)
        
        print("\n4️⃣ 뉴스 데이터 CLOVA Embedding 중...")
        news_embeddings = self.create_embeddings(news_chunks)
        
        # 4. KRX 데이터 Segmentation 및 Embedding
        print("\n5️⃣ KRX 데이터 CLOVA Segmentation 중...")
        krx_chunks = self.segment_data(krx_text)
        
        print("\n6️⃣ KRX 데이터 CLOVA Embedding 중...")
        krx_embeddings = self.create_embeddings(krx_chunks)
        
        # 5. CLOVA 분석
        print("\n7️⃣ CLOVA 모델 분석 중...")
        analysis_result = self.analyze_with_clova(krx_text, news_text)
        
        if analysis_result:
            # 6. 결과 저장
            print("\n8️⃣ 분석 결과 저장 중...")
            saved_path = self.save_analysis_result(analysis_result)
            
            if saved_path:
                print(f"\n🎉 분석 완료!")
                print(f"📁 결과 파일: {saved_path}")
                return True
        
        print("\n❌ 분석 실패")
        return False

def main():
    """메인 실행 함수"""
    analyzer = DataAnalyzer()
    success = analyzer.run_analysis()
    
    if success:
        print("\n✅ 전체 프로세스 완료!")
    else:
        print("\n❌ 프로세스 실패!")

if __name__ == "__main__":
    main() 