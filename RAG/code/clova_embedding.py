#!/usr/bin/env python3
"""
CLOVA X Embedding API 직접 호출 클래스 (업데이트된 방식)
"""

import http.client
import json
import os
import time
from typing import List, Optional
from dotenv import load_dotenv
from llama_index.core.embeddings import BaseEmbedding

class EmbeddingExecutor:
    """CLOVA X Embedding API 직접 호출 클래스 (업데이트된 방식)"""
    
    def __init__(self, host, api_key, request_id):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id
        self._total_requests = 0
        self._completed_requests = 0
    
    def _send_request(self, completion_request):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }
        
        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', '/v1/api-tools/embedding/v2', json.dumps(completion_request), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result
    
    def execute(self, completion_request):
        # 진행상황 업데이트
        self._completed_requests += 1
        progress = (self._completed_requests / self._total_requests * 100) if self._total_requests > 0 else 0
        
        # API 요청 제한을 위한 지연
        print(f"⏳ 20초 지연 중... ({self._completed_requests}/{self._total_requests} - {progress:.1f}%)")
        time.sleep(20)  # 20초 지연 (rate limit 방지)
        print("지연 완료, 다음 요청 진행")
        
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']
        else:
            print(f"임베딩 API 응답 오류: {res}")
            return 'Error'

class ClovaEmbeddingAPI(BaseEmbedding):
    """CLOVA X Embedding API 래퍼 클래스 (LlamaIndex 호환)"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        load_dotenv()
        
        api_key = os.getenv("CLOVA_API_KEY", "")
        request_id = os.getenv("CLOVA_EMBEDDING_REQUEST_ID", "")
        
        # API 키에 Bearer 접두사 추가
        if not api_key.startswith('Bearer '):
            api_key = f'Bearer {api_key}'
        
        # EmbeddingExecutor 초기화 (Pydantic 필드 문제 회피)
        object.__setattr__(self, '_embedding_executor', EmbeddingExecutor(
            host='clovastudio.stream.ntruss.com',
            api_key=api_key,
            request_id=request_id
        ))
        
        print(f"CLOVA X Embedding API 클라이언트 초기화 완료")
        # print(f"API 키 설정: {'완료' if api_key else '미완료'}")
        # print(f"임베딩 Request ID 설정: {'완료' if request_id else '미완료'}")
    
    def _get_query_embedding(self, query: str) -> List[float]:
        """쿼리 텍스트의 임베딩 생성 (내부 메서드)"""
        try:
            request_data = {"text": query}
            result = self._embedding_executor.execute(request_data)
            if result == 'Error':
                print(f"임베딩 API 오류 - 요청 데이터: {request_data}")
                return [0.0] * 1024
            embedding = result.get('embedding', [0.0] * 1024)
            if not isinstance(embedding, list):
                print(f"임베딩 형태 오류: {type(embedding)}")
                return [0.0] * 1024  # CLOVA X 임베딩은 1024차원
            if len(embedding) != 1024:
                print(f"임베딩 길이 오류: {len(embedding)}, 기대값: 1024")
                return [0.0] * 1024
            return embedding
        except Exception as e:
            print(f"임베딩 생성 오류: {e}")
            return [0.0] * 1024
    
    def _get_text_embedding(self, text: str) -> List[float]:
        """텍스트의 임베딩 생성 (내부 메서드)"""
        return self._get_query_embedding(text)
    
    def _aget_query_embedding(self, query: str) -> List[float]:
        """비동기 쿼리 텍스트의 임베딩 생성 (내부 메서드)"""
        import asyncio
        return asyncio.run(self._get_query_embedding(query))
    
    def get_query_embedding(self, query: str) -> List[float]:
        """쿼리 텍스트의 임베딩 생성"""
        return self._get_query_embedding(query)
    
    def get_text_embedding(self, text: str) -> List[float]:
        """텍스트의 임베딩 생성"""
        return self._get_text_embedding(text)
    
    def get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """여러 텍스트의 임베딩 생성"""
        embeddings = []
        for text in texts:
            embedding = self.get_text_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    @property
    def dimension(self) -> int:
        """임베딩 차원"""
        return 1024  # CLOVA X 임베딩 차원 