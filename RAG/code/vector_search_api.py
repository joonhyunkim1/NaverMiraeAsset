#!/usr/bin/env python3
"""
벡터 검색 API 서버
- FAISS를 사용한 벡터 검색
- FastAPI로 REST API 제공
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

class VectorSearchAPI:
    def __init__(self):
        self.app = FastAPI(title="Vector Search API", description="CLOVA Studio용 벡터 검색 API")
        self.vector_db_path = current_dir.parent / "vector_db_hybrid"
        self.vectors = []
        self.metadata = []
        self.embedding_client = None
        self.faiss_index = None
        
        # API 엔드포인트 등록
        self.setup_routes()
    
    def setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.get("/")
        async def root():
            return {"message": "Vector Search API", "status": "running"}
        
        @self.app.post("/search", response_model=SearchResponse)
        async def search_vectors(request: SearchRequest):
            """벡터 검색 API"""
            try:
                results = self.search_similar_vectors(request.query, request.top_k)
                return SearchResponse(results=results, total_found=len(results))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """헬스 체크"""
            return {"status": "healthy", "vectors_loaded": len(self.vectors)}
    
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
    
    def search_similar_vectors(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """질문과 유사한 벡터 검색"""
        if not self.embedding_client:
            raise Exception("임베딩 클라이언트가 초기화되지 않았습니다.")
        
        # 질문을 벡터로 변환
        query_vector = self.embedding_client.get_text_embedding(query)
        
        # 간단한 코사인 유사도 계산 (FAISS 없이)
        similarities = []
        for i, vector in enumerate(self.vectors):
            similarity = self.cosine_similarity(query_vector, vector)
            similarities.append((i, similarity))
        
        # 유사도 순으로 정렬
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 상위 k개 결과 반환
        results = []
        for idx, similarity in similarities[:top_k]:
            meta = self.metadata[idx]
            results.append({
                "index": idx,
                "similarity": float(similarity),
                "type": meta.get("type", "unknown"),
                "filename": meta.get("filename", ""),
                "title": meta.get("title", ""),
                "text_content": meta.get("text_content", ""),
                "text_length": meta.get("text_length", 0),
                "created_at": meta.get("created_at", "")
            })
        
        return results
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def run_server(self, host: str = "0.0.0.0", port: int = 8000):
        """API 서버 실행"""
        print(f"🚀 벡터 검색 API 서버 시작: http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

def main():
    """메인 함수"""
    api = VectorSearchAPI()
    
    # 벡터 데이터 로드
    if not api.load_vectors():
        print("❌ 벡터 데이터 로드 실패!")
        return
    
    # 임베딩 클라이언트 초기화
    if not api.initialize_embedding_client():
        print("❌ 임베딩 클라이언트 초기화 실패!")
        return
    
    # API 서버 실행
    api.run_server()

if __name__ == "__main__":
    main() 