#!/usr/bin/env python3
"""
Vector DB1용 FAISS 벡터 검색 API 서버
- vector_db_1의 벡터를 로드하여 FAISS 인덱스 구축
- FastAPI를 통한 벡터 검색 API 제공
"""

import pickle
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import faiss
from datetime import datetime

app = FastAPI(title="Vector DB1 FAISS API", version="1.0.0")

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_results: int
    query: str

class VectorDB1Manager:
    """Vector DB1 관리자"""
    
    def __init__(self):
        # 현재 스크립트 위치를 기준으로 상대 경로 설정
        current_dir = Path(__file__).parent
        self.vector_dir = current_dir.parent / "vector_db_1"
        self.vectors = []
        self.metadata = []
        self.index = None
        self.is_loaded = False
        
        print("🔧 Vector DB1 매니저 초기화 완료")
        print(f"📁 벡터 디렉토리: {self.vector_dir}")
    
    def load_vectors(self) -> bool:
        """vector_db_1의 벡터와 메타데이터 로드"""
        try:
            vectors_file = self.vector_dir / "vector_db_1_vectors.pkl"
            metadata_file = self.vector_dir / "vector_db_1_metadata.json"
            
            if not vectors_file.exists():
                print("❌ vector_db_1의 벡터 파일을 찾을 수 없습니다.")
                return False
            
            if not metadata_file.exists():
                print("❌ vector_db_1의 메타데이터 파일을 찾을 수 없습니다.")
                return False
            
            # 벡터 로드
            with open(vectors_file, 'rb') as f:
                self.vectors = pickle.load(f)
            
            # 메타데이터 로드
            with open(metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            print(f"✅ vector_db_1 벡터 로드 완료: {len(self.vectors)}개")
            print(f"✅ vector_db_1 메타데이터 로드 완료: {len(self.metadata)}개")
            
            # FAISS 인덱스 구축
            if self.vectors:
                vectors_array = np.array(self.vectors, dtype=np.float32)
                dimension = vectors_array.shape[1]
                
                # FAISS 인덱스 생성 (L2 거리)
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(vectors_array)
                
                print(f"✅ FAISS 인덱스 구축 완료: {self.index.ntotal}개 벡터")
                self.is_loaded = True
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 벡터 로드 실패: {e}")
            return False
    
    def search_vectors(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """벡터 검색 수행"""
        if not self.is_loaded or not self.index:
            return []
        
        try:
            # 쿼리 벡터를 numpy 배열로 변환
            query_array = np.array([query_vector], dtype=np.float32)
            
            # FAISS 검색 수행
            distances, indices = self.index.search(query_array, top_k)
            
            # 결과 구성
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.metadata):
                    result = {
                        "rank": i + 1,
                        "distance": float(distance),
                        "metadata": self.metadata[idx],
                        "text_content": self.metadata[idx].get('text_content', ''),
                        "filename": self.metadata[idx].get('filename', ''),
                        "type": self.metadata[idx].get('type', ''),
                        "title": self.metadata[idx].get('title', '')
                    }
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"❌ 벡터 검색 실패: {e}")
            return []

# 전역 매니저 인스턴스
vector_manager = VectorDB1Manager()

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 벡터 로드"""
    print("🚀 Vector DB1 FAISS API 서버 시작 중...")
    success = vector_manager.load_vectors()
    if success:
        print("✅ 서버 시작 완료")
    else:
        print("❌ 서버 시작 실패")

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "vectors_loaded": vector_manager.is_loaded,
        "total_vectors": len(vector_manager.vectors),
        "total_metadata": len(vector_manager.metadata),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/info")
async def get_info():
    """벡터 정보 조회"""
    return {
        "vector_dir": str(vector_manager.vector_dir),
        "vectors_loaded": vector_manager.is_loaded,
        "total_vectors": len(vector_manager.vectors),
        "total_metadata": len(vector_manager.metadata),
        "faiss_index_built": vector_manager.index is not None,
        "index_size": vector_manager.index.ntotal if vector_manager.index else 0
    }

@app.post("/search", response_model=SearchResponse)
async def search_vectors(request: SearchRequest):
    """벡터 검색 API"""
    try:
        # 여기서는 간단히 쿼리 텍스트를 기반으로 검색
        # 실제로는 쿼리 텍스트를 벡터로 변환해야 함
        # 임시로 첫 번째 벡터를 사용
        if not vector_manager.vectors:
            raise HTTPException(status_code=404, detail="벡터가 로드되지 않았습니다")
        
        # 임시 쿼리 벡터 (실제로는 텍스트를 벡터로 변환해야 함)
        query_vector = vector_manager.vectors[0]  # 임시
        
        results = vector_manager.search_vectors(query_vector, request.top_k)
        
        return SearchResponse(
            results=results,
            total_results=len(results),
            query=request.query
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류: {str(e)}")

@app.get("/test")
async def test_endpoint():
    """테스트 엔드포인트"""
    return {
        "message": "Vector DB1 FAISS API 서버가 정상적으로 실행 중입니다.",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Vector DB1 FAISS API 서버 시작...")
    uvicorn.run(app, host="0.0.0.0", port=8001)  # 8001 포트 사용 