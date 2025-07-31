#!/usr/bin/env python3
"""
FAISS 기반 벡터 검색 API 서버
- FastAPI + uvicorn으로 REST API 제공
- 로컬 벡터를 FAISS로 검색
- CLOVA Studio에서 호출 가능
"""

import os
import sys
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import faiss

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from clova_embedding import ClovaEmbeddingAPI

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_found: int
    query: str

class FAISSVectorAPI:
    def __init__(self):
        self.app = FastAPI(
            title="FAISS Vector Search API", 
            description="CLOVA Studio용 FAISS 벡터 검색 API",
            version="1.0.0"
        )
        self.vector_db_path = current_dir.parent / "vector_db"
        self.vectors = []
        self.metadata = []
        self.embedding_client = None
        self.faiss_index = None
        self.dimension = 1024  # CLOVA X 임베딩 차원
        
        # API 엔드포인트 등록
        self.setup_routes()
    
    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": "FAISS Vector Search API", 
                "status": "running",
                "vectors_loaded": len(self.vectors),
                "faiss_index_built": self.faiss_index is not None
            }
        
        @self.app.post("/search", response_model=SearchResponse)
        async def search_vectors(request: SearchRequest):
            """벡터 검색 API"""
            try:
                results = self.search_similar_vectors(request.query, request.top_k)
                return SearchResponse(
                    results=results, 
                    total_found=len(results),
                    query=request.query
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """헬스 체크"""
            return {
                "status": "healthy", 
                "vectors_loaded": len(self.vectors),
                "faiss_index_built": self.faiss_index is not None,
                "embedding_client_ready": self.embedding_client is not None
            }
        
        @self.app.get("/test")
        async def test_search():
            """테스트 검색"""
            test_queries = [
                "삼성전자 주가",
                "하이브 세무조사", 
                "거래대금 많은 종목",
                "주식 시장 이슈"
            ]
            
            test_results = {}
            for query in test_queries:
                try:
                    results = self.search_similar_vectors(query, top_k=3)
                    test_results[query] = {
                        "found": len(results),
                        "top_result": results[0] if results else None
                    }
                except Exception as e:
                    test_results[query] = {"error": str(e)}
            
            return {"test_results": test_results}
    
    def load_vectors(self):
        """저장된 벡터와 메타데이터 로드"""
        print("🔍 벡터 데이터 로드 중...")
        
        # 벡터 파일 로드
        vectors_file = self.vector_db_path / "hybrid_vectors.pkl"
        if vectors_file.exists():
            with open(vectors_file, 'rb') as f:
                self.vectors = pickle.load(f)
            print(f"✅ 벡터 로드 완료: {len(self.vectors)}개")
        else:
            print("❌ 벡터 파일을 찾을 수 없습니다!")
            return False
        
        # 메타데이터 파일 로드
        metadata_file = self.vector_db_path / "hybrid_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"✅ 메타데이터 로드 완료: {len(self.metadata)}개")
        else:
            print("❌ 메타데이터 파일을 찾을 수 없습니다!")
            return False
        
        return True
    
    def initialize_embedding_client(self):
        """임베딩 클라이언트 초기화"""
        try:
            self.embedding_client = ClovaEmbeddingAPI()
            print("✅ 임베딩 클라이언트 초기화 완료")
            return True
        except Exception as e:
            print(f"❌ 임베딩 클라이언트 초기화 실패: {e}")
            return False
    
    def build_faiss_index(self):
        """FAISS 인덱스 구축"""
        if not self.vectors:
            print("❌ 벡터가 로드되지 않았습니다!")
            return False
        
        print("🔧 FAISS 인덱스 구축 중...")
        
        try:
            # 벡터를 numpy 배열로 변환
            vectors_array = np.array(self.vectors, dtype=np.float32)
            
            # FAISS 인덱스 생성 (FlatIP 사용 - 내적 기반)
            self.faiss_index = faiss.IndexFlatIP(self.dimension)
            
            # 벡터 추가
            self.faiss_index.add(vectors_array)
            
            print(f"✅ FAISS 인덱스 구축 완료: {self.faiss_index.ntotal}개 벡터")
            return True
            
        except Exception as e:
            print(f"❌ FAISS 인덱스 구축 실패: {e}")
            return False
    
    def search_similar_vectors(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """질문과 유사한 벡터 검색"""
        if not self.embedding_client:
            raise Exception("임베딩 클라이언트가 초기화되지 않았습니다.")
        
        if not self.faiss_index:
            raise Exception("FAISS 인덱스가 구축되지 않았습니다.")
        
        # 질문을 벡터로 변환
        query_vector = self.embedding_client.get_text_embedding(query)
        query_array = np.array([query_vector], dtype=np.float32)
        
        # FAISS로 검색
        similarities, indices = self.faiss_index.search(query_array, top_k)
        
        # 결과 반환
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx != -1:  # 유효한 결과인 경우
                meta = self.metadata[idx]
                results.append({
                    "index": int(idx),
                    "similarity": float(similarity),
                    "type": meta.get("type", "unknown"),
                    "filename": meta.get("filename", ""),
                    "title": meta.get("title", ""),
                    "text_content": meta.get("text_content", ""),
                    "text_length": meta.get("text_length", 0),
                    "created_at": meta.get("created_at", "")
                })
        
        return results
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000):
        """API 서버 실행"""
        print(f"🚀 FAISS 벡터 검색 API 서버 시작: http://{host}:{port}")
        print(f"📊 API 문서: http://{host}:{port}/docs")
        print(f"🔍 테스트: http://{host}:{port}/test")
        uvicorn.run(self.app, host=host, port=port)

def main():
    """메인 함수"""
    api = FAISSVectorAPI()
    
    # 벡터 데이터 로드
    if not api.load_vectors():
        print("❌ 벡터 데이터 로드 실패!")
        return
    
    # 임베딩 클라이언트 초기화
    if not api.initialize_embedding_client():
        print("❌ 임베딩 클라이언트 초기화 실패!")
        return
    
    # FAISS 인덱스 구축
    if not api.build_faiss_index():
        print("❌ FAISS 인덱스 구축 실패!")
        return
    
    # API 서버 실행
    api.run_server()

if __name__ == "__main__":
    main() 