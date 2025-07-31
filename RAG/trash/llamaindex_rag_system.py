#!/usr/bin/env python3
"""
LlamaIndex 기반 RAG 시스템 (CLOVA API + 한국어 LLaMA)
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from dotenv import load_dotenv

# LlamaIndex 관련 import
from llama_index.core import (
    VectorStoreIndex, 
    SimpleDirectoryReader, 
    Document,
    Settings,
    StorageContext,
    load_index_from_storage
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.retrievers import VectorIndexRetriever

# CLOVA API 클라이언트들
from clova_chat_client import ClovaChatClient
from clova_embedding import ClovaEmbeddingAPI
from clova_segmentation import ClovaSegmentationClient

# 데이터 처리
import pandas as pd
import numpy as np
import http.client
import json

class LlamaIndexRAGSystem:
    """LlamaIndex 기반 RAG 시스템"""
    
    def __init__(self, data_dir: str = "/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data"):
        self.data_dir = Path(data_dir)
        self.index = None
        self.retriever = None
        self.storage_context = None
        
        # 환경변수 로드
        load_dotenv()
        
        # 설정 초기화
        self._setup_embedding()
        self._setup_chat_client()
        self._setup_segmentation()
        
    def _setup_chat_client(self):
        """HyperCLOVA X Chat API 클라이언트 설정"""
        print("HyperCLOVA X Chat API 클라이언트 설정 중...")
        
        self.chat_client = ClovaChatClient()
        
        # API 정보 확인
        api_info = self.chat_client.get_api_info()
        if not api_info["api_key_set"]:
            print("경고: CLOVA API 키가 설정되지 않았습니다!")
        if not api_info["request_id_set"]:
            print("경고: CLOVA Request ID가 설정되지 않았습니다!")
        
    def _setup_embedding(self):
        """CLOVA X Embedding API 설정"""
        print("CLOVA X Embedding API 설정 중...")
        
        self.embed_model = ClovaEmbeddingAPI()
        
        # 전역 설정
        Settings.embed_model = self.embed_model
    
    def _setup_segmentation(self):
        """CLOVA 세그멘테이션 API 설정"""
        print("CLOVA 세그멘테이션 API 설정 중...")
        
        self.segmentation_client = ClovaSegmentationClient()
        
        # API 정보 확인
        api_info = self.segmentation_client.get_api_info()
        if not api_info["api_key_set"]:
            print("경고: CLOVA API 키가 설정되지 않았습니다!")
        if not api_info["request_id_set"]:
            print("경고: CLOVA Request ID가 설정되지 않았습니다!")
    

        
    def _load_documents(self) -> List[Document]:
        """모든 데이터 파일들을 LlamaIndex Document로 변환"""
        documents = []
        
        if not self.data_dir.exists():
            print(f"데이터 디렉토리가 존재하지 않습니다: {self.data_dir}")
            return documents
        
        # CSV 파일 처리
        csv_documents = self._csv_to_documents()
        documents.extend(csv_documents)
        
        # 뉴스 본문 JSON 파일 처리
        news_documents = self._news_articles_to_documents()
        documents.extend(news_documents)
        
        return documents
    
    def _csv_to_documents(self) -> List[Document]:
        """CSV 파일들을 LlamaIndex Document로 변환"""
        documents = []
        
        csv_files = list(self.data_dir.glob("*.csv"))
        
        if not csv_files:
            print(f"CSV 파일을 찾을 수 없습니다: {self.data_dir}")
            return documents
            
        print(f"발견된 CSV 파일: {len(csv_files)}개")
        
        for csv_file in csv_files:
            try:
                print(f"처리 중: {csv_file.name}")
                
                # CSV 파일 읽기
                df = pd.read_csv(csv_file, encoding='utf-8-sig')
                
                # DataFrame을 텍스트로 변환
                text_content = self._dataframe_to_text(df, csv_file.stem)
                
                # Document 생성
                doc = Document(
                    text=text_content,
                    metadata={
                        "source": str(csv_file),
                        "filename": csv_file.name,
                        "type": "csv",
                        "rows": len(df),
                        "columns": list(df.columns)
                    }
                )
                
                documents.append(doc)
                print(f"  - {csv_file.name}: {len(df)}행, {len(df.columns)}컬럼")
                
            except Exception as e:
                print(f"오류: {csv_file} 처리 실패 - {e}")
                
        return documents
    
    def _dataframe_to_text(self, df: pd.DataFrame, filename: str) -> str:
        """DataFrame을 텍스트로 변환"""
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
    
    def _news_articles_to_documents(self) -> List[Document]:
        """뉴스 기사들을 LlamaIndex Document로 변환"""
        documents = []
        
        # naver_news_*.json 파일들 찾기
        news_files = list(self.data_dir.glob("naver_news_*.json"))
        
        if not news_files:
            print(f"뉴스 JSON 파일을 찾을 수 없습니다: {self.data_dir}")
            return documents
            
        print(f"발견된 뉴스 파일: {len(news_files)}개")
        
        for news_file in news_files:
            try:
                print(f"처리 중: {news_file.name}")
                
                # JSON 파일 읽기
                with open(news_file, 'r', encoding='utf-8') as f:
                    news_data = json.load(f)
                
                # 뉴스 기사 목록 추출
                articles = []
                if 'items' in news_data:
                    articles = news_data['items']
                elif 'articles' in news_data:
                    articles = news_data['articles']
                
                print(f"  - {len(articles)}개 뉴스 기사 처리")
                
                # 각 뉴스 기사를 Document로 변환
                for i, article in enumerate(articles):
                    text_content = self._article_to_text(article, i+1)
                    
                    doc = Document(
                        text=text_content,
                        metadata={
                            "source": str(news_file),
                            "filename": news_file.name,
                            "type": "news_article",
                            "article_index": i+1,
                            "title": article.get('title', ''),
                            "url": article.get('link', ''),
                            "publish_date": article.get('pubDate', '')
                        }
                    )
                    documents.append(doc)
                
            except Exception as e:
                print(f"오류: {news_file} 처리 실패 - {e}")
                
        return documents
    
    def _article_to_text(self, article: Dict, index: int) -> str:
        """뉴스 기사를 텍스트로 변환"""
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
    

        
    def build_index(self, rebuild: bool = False) -> bool:
        """벡터 인덱스 구축"""
        try:
            # 절대 경로로 vector_db 디렉토리 설정
            storage_path = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/vector_db")
            
            # 기존 인덱스가 있고 rebuild가 False인 경우 로드
            if not rebuild and storage_path.exists():
                print("기존 인덱스 로드 중...")
                self.storage_context = StorageContext.from_defaults(persist_dir=str(storage_path))
                self.index = load_index_from_storage(self.storage_context)
                print("기존 인덱스 로드 완료!")
                return True
            
            print("새로운 인덱스 구축 중...")
            
            # vector_store 디렉토리 생성
            storage_path.mkdir(exist_ok=True)
            
            # 모든 데이터 파일들을 Document로 변환
            documents = self._load_documents()
            
            if not documents:
                print("처리할 문서가 없습니다!")
                return False
            
            print(f"총 {len(documents)}개의 문서를 처리합니다.")
            
            # 문서 청킹
            print("문서 청킹 중...")
            chunked_documents = []
            
            for doc in documents:
                # 문서 크기 로깅
                print(f"📄 문서 처리 중: {doc.metadata.get('filename', 'unknown')} ({len(doc.text):,}자)")
                
                # 문서 타입에 따른 세그멘테이션 설정
                doc_type = doc.metadata.get('type', 'unknown')
                
                if doc_type == 'csv':
                    # KRX CSV 데이터: 최적화된 설정 사용
                    print(f"  🔧 CSV 데이터 - 최적화된 세그멘테이션 적용")
                    chunks = self.segmentation_client.segment_text(
                        doc.text, 
                        max_length=2048  # 큰 청크 크기
                    )
                else:
                    # 뉴스 데이터: 원래 설정 사용
                    print(f"  📰 뉴스 데이터 - 기본 세그멘테이션 적용")
                    chunks = self.segmentation_client.segment_text(
                        doc.text, 
                        max_length=512  # 작은 청크 크기 (뉴스에 적합)
                    )
                
                if chunks:
                    # 각 청크를 별도의 Document로 생성
                    for i, chunk in enumerate(chunks):
                        chunk_doc = Document(
                            text=chunk,
                            metadata={
                                **doc.metadata,
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                                "original_document": doc.metadata.get("filename", "unknown")
                            }
                        )
                        chunked_documents.append(chunk_doc)
                else:
                    # 세그멘테이션 실패 시 원본 문서 사용
                    print(f"세그멘테이션 실패, 원본 문서 사용: {doc.metadata.get('filename', 'unknown')}")
                    chunked_documents.append(doc)
            
            print(f"총 {len(chunked_documents)}개의 청크로 분할 완료")
            
            # 임베딩 진행상황 추적을 위한 총 요청 수 설정
            if hasattr(self.embed_model, '_embedding_executor'):
                self.embed_model._embedding_executor._total_requests = len(chunked_documents)
                self.embed_model._embedding_executor._completed_requests = 0
                print(f"📊 임베딩 진행상황 추적 설정: 총 {len(chunked_documents)}개 청크")
            
            # 벡터 인덱스 생성 (청킹된 문서들 사용)
            print("벡터 인덱스 생성 중...")
            try:
                self.index = VectorStoreIndex.from_documents(
                    chunked_documents,
                    show_progress=True
                )
                print("벡터 인덱스 생성 완료!")
            except Exception as e:
                print(f"벡터 인덱스 생성 중 오류: {e}")
                import traceback
                traceback.print_exc()
                raise
            
            # 인덱스 저장
            print("인덱스 저장 중...")
            try:
                # 새로운 인덱스의 경우 직접 저장
                self.index.storage_context.persist(persist_dir=str(storage_path))
                print("인덱스 저장 완료!")
            except Exception as e:
                print(f"인덱스 저장 중 오류: {e}")
                import traceback
                traceback.print_exc()
                # 저장 실패해도 인덱스는 사용 가능하므로 계속 진행
                print("인덱스 저장 실패했지만 계속 진행합니다...")
            
            print("인덱스 구축 및 저장 완료!")
            return True
            
        except Exception as e:
            print(f"인덱스 구축 실패: {e}")
            return False
            
    def setup_retriever(self) -> bool:
        """리트리버 설정"""
        if self.index is None:
            print("인덱스가 구축되지 않았습니다!")
            return False
            
        try:
            # 리트리버 설정
            self.retriever = VectorIndexRetriever(
                index=self.index,
                similarity_top_k=5
            )
            
            print("리트리버 설정 완료!")
            return True
            
        except Exception as e:
            print(f"리트리버 설정 실패: {e}")
            return False
            
    def ask(self, query: str) -> Dict[str, Any]:
        """질문에 답변"""
        if self.retriever is None:
            return {
                "success": False,
                "error": "리트리버가 설정되지 않았습니다."
            }
            
        try:
            print(f"질문: {query}")
            print("관련 문서 검색 중...")
            
            # 관련 문서 검색
            retrieved_nodes = self.retriever.retrieve(query)
            
            if not retrieved_nodes:
                return {
                    "success": False,
                    "error": "관련된 문서를 찾을 수 없습니다.",
                    "query": query
                }
            
            print(f"검색된 문서: {len(retrieved_nodes)}개")
            
            # 검색된 문서를 HyperCLOVA X에 전달
            print("HyperCLOVA X로 답변 생성 중...")
            
            # 문서 정보 구성
            context_documents = []
            for node in retrieved_nodes:
                context_documents.append({
                    "content": node.text,
                    "metadata": node.metadata,
                    "score": node.score if hasattr(node, 'score') else None
                })
            
            # HyperCLOVA X로 답변 생성
            answer = self.chat_client.create_rag_response(query, context_documents)
            
            if answer:
                return {
                    "success": True,
                    "query": query,
                    "answer": answer,
                    "source_nodes": context_documents
                }
            else:
                return {
                    "success": False,
                    "error": "HyperCLOVA X 답변 생성 실패",
                    "query": query
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"답변 생성 실패: {e}",
                "query": query
            }
    
    def ask_with_vectors(self, query: str) -> Dict[str, Any]:
        """임베딩 벡터를 직접 사용하여 질문에 답변"""
        if self.index is None:
            return {
                "success": False,
                "error": "인덱스가 구축되지 않았습니다."
            }
            
        try:
            print(f"질문: {query}")
            print("임베딩 벡터 정보 수집 중...")
            
            # 모든 노드의 임베딩 벡터 수집
            all_nodes = list(self.index.docstore.docs.values())
            embedding_vectors = []
            vector_metadata = []
            
            print(f"총 {len(all_nodes)}개의 노드에서 벡터 정보 수집 중...")
            
            for i, node in enumerate(all_nodes):
                try:
                    # 노드의 임베딩 벡터 가져오기
                    if hasattr(node, 'embedding') and node.embedding is not None:
                        embedding_vectors.append(node.embedding)
                        vector_metadata.append({
                            "filename": node.metadata.get('filename', 'Unknown'),
                            "type": node.metadata.get('type', 'Unknown'),
                            "node_index": i,
                            "vector_dimension": len(node.embedding)
                        })
                    else:
                        print(f"노드 {i}에 임베딩 벡터가 없습니다.")
                except Exception as e:
                    print(f"노드 {i} 벡터 수집 오류: {e}")
            
            if not embedding_vectors:
                return {
                    "success": False,
                    "error": "임베딩 벡터를 찾을 수 없습니다.",
                    "query": query
                }
            
            print(f"수집된 벡터: {len(embedding_vectors)}개")
            print(f"벡터 차원: {len(embedding_vectors[0])}차원")
            
            # 임베딩 벡터를 HyperCLOVA X에 전달
            print("HyperCLOVA X로 벡터 기반 답변 생성 중...")
            
            answer = self.chat_client.create_vector_based_response(query, embedding_vectors, vector_metadata)
            
            if answer:
                return {
                    "success": True,
                    "query": query,
                    "answer": answer,
                    "vector_count": len(embedding_vectors),
                    "vector_dimension": len(embedding_vectors[0]) if embedding_vectors else 0,
                    "vector_metadata": vector_metadata
                }
            else:
                return {
                    "success": False,
                    "error": "HyperCLOVA X 벡터 기반 답변 생성 실패",
                    "query": query
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"벡터 기반 답변 생성 실패: {e}",
                "query": query
            }
            
    def get_system_info(self) -> Dict[str, Any]:
        """시스템 정보 반환"""
        info = {
            "data_directory": str(self.data_dir),
            "index_built": self.index is not None,
            "retriever_setup": self.retriever is not None,
            "llm_model": "HyperCLOVA X",
            "embedding_model": "CLOVA X Embedding",
            "segmentation_model": "CLOVA Segmentation",
            "clova_api_key_set": bool(os.getenv("CLOVA_API_KEY")),
            "clova_embedding_request_id_set": bool(os.getenv("CLOVA_EMBEDDING_REQUEST_ID")),
            "clova_chat_request_id_set": bool(os.getenv("CLOVA_CHAT_REQUEST_ID"))
        }
        
        if self.index:
            info["index_info"] = {
                "total_nodes": len(self.index.docstore.docs),
                "vector_store_type": type(self.index.vector_store).__name__
            }
            
        return info
        
    def interactive_chat(self):
        """대화형 채팅 모드"""
        if self.retriever is None:
            print("리트리버를 먼저 설정해주세요.")
            return
            
        print("\n" + "=" * 50)
        print("LlamaIndex RAG 대화형 채팅")
        print("종료하려면 'quit', 'exit', '종료'를 입력하세요.")
        print("=" * 50)
        
        conversation = []
        
        while True:
            try:
                query = input("\n질문을 입력하세요: ").strip()
                
                if query.lower() in ['quit', 'exit', '종료']:
                    break
                    
                if not query:
                    continue
                    
                result = self.ask(query)
                
                if result["success"]:
                    print(f"\n답변: {result['answer']}")
                    
                    # 소스 정보 출력
                    if result.get("source_nodes"):
                        print(f"\n참고한 문서: {len(result['source_nodes'])}개")
                        for i, node in enumerate(result["source_nodes"][:3], 1):
                            print(f"  {i}. {node['metadata'].get('filename', 'Unknown')}")
                            print(f"     내용: {node['content'][:100]}...")
                    
                    conversation.append({
                        "query": query,
                        "answer": result["answer"],
                        "sources_count": len(result.get("source_nodes", []))
                    })
                else:
                    print(f"\n오류: {result['error']}")
                    
            except KeyboardInterrupt:
                print("\n\n채팅을 종료합니다.")
                break
            except Exception as e:
                print(f"\n오류가 발생했습니다: {e}")
        
        # 대화 내용 저장
        if conversation:
            self._save_conversation(conversation)
            
    def _save_conversation(self, conversation: List[Dict[str, Any]], filename: str = "llamaindex_conversation.json"):
        """대화 내용 저장"""
        conversation_path = Path(filename)
        
        with open(conversation_path, 'w', encoding='utf-8') as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)
        
        print(f"\n대화 내용 저장 완료: {conversation_path}")
        print(f"총 {len(conversation)}개의 대화가 저장되었습니다.") 

 