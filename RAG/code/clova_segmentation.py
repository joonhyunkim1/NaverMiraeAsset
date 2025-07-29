#!/usr/bin/env python3
"""
CLOVA Studio 세그멘테이션 API 클라이언트
"""

import requests
import json
import http.client
from typing import List, Dict, Any, Optional
from config import get_clova_api_key, get_clova_segmentation_request_id

class ClovaSegmentationClient:
    """CLOVA Studio 세그멘테이션 API 클라이언트"""
    
    def __init__(self):
        self.api_key = get_clova_api_key()
        self.request_id = get_clova_segmentation_request_id()
        
        # API 키에 Bearer 접두사 추가
        if not self.api_key.startswith('Bearer '):
            self.api_key = f'Bearer {self.api_key}'
        
        # CLOVA 세그멘테이션 API 엔드포인트
        self.segmentation_url = "https://clovastudio.stream.ntruss.com/v1/api-tools/segmentation"
        
        # 기본 헤더
        self.headers = {
            "Authorization": self.api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self.request_id,
            "Content-Type": "application/json; charset=utf-8"
        }
        
        print(f"CLOVA 세그멘테이션 API 클라이언트 초기화 완료")
        print(f"API 키 설정: {'완료' if self.api_key else '미완료'}")
        print(f"Request ID 설정: {'완료' if self.request_id else '미완료'}")
    
    def segment_text(self, text: str, max_length: int = 512, overlap: int = 50) -> Optional[List[str]]:
        """텍스트를 세그멘테이션(청킹)합니다."""
        try:
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': self.api_key,
                'X-NCP-CLOVASTUDIO-REQUEST-ID': self.request_id
            }
            
            # CLOVA 세그멘테이션 API 요청 데이터 (모델이 최적값 결정)
            body = {
                "postProcessMaxSize": max_length,
                "alpha": -100,  # 모델이 최적값으로 결정
                "segCnt": -1,   # 모델이 최적값으로 결정
                "postProcessMinSize": max_length // 4,  # 최소 크기는 최대 크기의 1/4
                "text": text,
                "postProcess": True  # 후처리 활성화
            }
            
            conn = http.client.HTTPSConnection("clovastudio.stream.ntruss.com")
            conn.request('POST', '/v1/api-tools/segmentation', json.dumps(body), headers)
            response = conn.getresponse()
            result = json.loads(response.read().decode('utf-8'))
            conn.close()
            
            if result['status']['code'] == '20000':
                # 세그멘테이션 결과 처리
                topic_segments = result['result'].get('topicSeg', [])
                if topic_segments:
                    # 각 세그먼트를 하나의 텍스트로 결합
                    return [' '.join(segment) for segment in topic_segments if segment]
                else:
                    print(f"topicSeg가 없습니다: {result}")
                    return None
            else:
                print(f"세그멘테이션 실패: {result}")
                return None
                
        except Exception as e:
            print(f"CLOVA 세그멘테이션 API 호출 오류: {e}")
            return None
    
    def get_api_info(self) -> Dict[str, Any]:
        """API 정보를 반환합니다."""
        return {
            "api_key_set": bool(self.api_key),
            "request_id_set": bool(self.request_id),
            "segmentation_url": self.segmentation_url
        } 