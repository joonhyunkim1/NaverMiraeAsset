import requests
import json
import base64
import http.client
from typing import List, Dict, Any, Optional
from config import get_clova_api_key, get_clova_request_id

class ClovaEmbeddingClient:
    """CLOVA X 임베딩 API 클라이언트 (LLaMA 모델과 조합 사용)"""
    
    def __init__(self):
        self.api_key = get_clova_api_key()
        self.request_id = get_clova_request_id()
        
        # API 키에 Bearer 접두사 추가 (성공한 테스트 코드와 동일하게)
        if not self.api_key.startswith('Bearer '):
            self.api_key = f'Bearer {self.api_key}'
        
        # CLOVA 임베딩 API 엔드포인트 (올바른 엔드포인트)
        self.embedding_url = "https://clovastudio.stream.ntruss.com/v1/api-tools/embedding/v2"
        
        # 기본 헤더 (테스트 코드와 동일하게)
        self.headers = {
            "Authorization": self.api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self.request_id,
            "Content-Type": "application/json; charset=utf-8"
        }
        
        print(f"CLOVA 임베딩 API 클라이언트 초기화 완료")
        print(f"API 키 설정: {'완료' if self.api_key else '미완료'}")
        # print(f"API 키 (처음 20자): {self.api_key[:20]}..." if self.api_key else "없음")
        # print(f"API 키 (전체): {self.api_key}" if self.api_key else "없음")
        print(f"Request ID 설정: {'완료' if self.request_id else '미완료'}")
        # print(f"Request ID: {self.request_id}" if self.request_id else "없음")
    

    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """CLOVA X Embedding API 호출"""
        try:
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': self.api_key,
                'X-NCP-CLOVASTUDIO-REQUEST-ID': self.request_id
            }
            body = json.dumps({"text": text})
            
            conn = http.client.HTTPSConnection("clovastudio.stream.ntruss.com")
            conn.request('POST', '/v1/api-tools/embedding/v2', body, headers)
            response = conn.getresponse()
            result = json.loads(response.read().decode('utf-8'))
            conn.close()
            
            if result['status']['code'] == '20000':
                return result['result']['embedding']
            else:
                print(f"임베딩 실패: {result}")
                return None
                
        except Exception as e:
            print(f"CLOVA 임베딩 API 호출 오류: {e}")
            return None
    

    
    def get_api_info(self) -> Dict[str, Any]:
        """API 정보를 반환합니다."""
        return {
            "api_key_set": bool(self.api_key),
            "request_id_set": bool(self.request_id),
            "embedding_url": self.embedding_url
        } 