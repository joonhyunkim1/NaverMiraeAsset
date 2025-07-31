#!/usr/bin/env python3
"""
새로운 CLOVA 모델 테스트 스크립트
"""

import http.client
import json
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class NewModelTester:
    def __init__(self):
        self.host = 'clovastudio.stream.ntruss.com'
        self.api_key = os.getenv("NEW_CLOVA_API_KEY", "")
        self.request_id = os.getenv("NEW_CLOVA_REQUEST_ID", "4997d0ab4e434139bd982084de885077")
        self.model_endpoint = os.getenv("NEW_CLOVA_MODEL_ENDPOINT", "/v3/tasks/yl1fvofj/chat-completions")
        
        print(f"🔧 테스트 설정:")
        print(f"   호스트: {self.host}")
        print(f"   엔드포인트: {self.model_endpoint}")
        print(f"   Request ID: {self.request_id}")
        print(f"   API 키: {self.api_key[:20]}..." if self.api_key else "❌ API 키 없음")
    
    def test_simple_request(self):
        """간단한 요청 테스트"""
        print("\n" + "=" * 60)
        print("🧪 간단한 요청 테스트")
        print("=" * 60)
        
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f'Bearer {self.api_key}',
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self.request_id
        }
        
        # 테스트용 간단한 요청
        request_data = {
            'text': '안녕하세요. 간단한 테스트입니다.',
            'start': '',
            'restart': '',
            'includeTokens': True,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 100,
            'temperature': 0.5,
            'repeatPenalty': 1.1,
            'stopBefore': [],
            'includeAiFilters': True
        }
        
        print(f"📤 요청 데이터: {request_data}")
        
        try:
            conn = http.client.HTTPSConnection(self.host)
            conn.request('POST', self.model_endpoint, json.dumps(request_data), headers)
            response = conn.getresponse()
            
            print(f"📡 응답 상태: {response.status} {response.reason}")
            print(f"📡 응답 헤더: {response.getheaders()}")
            
            result = json.loads(response.read().decode(encoding='utf-8'))
            print(f"📡 응답 내용: {result}")
            
            conn.close()
            
            if response.status == 200:
                print("✅ 테스트 성공!")
                return True
            else:
                print("❌ 테스트 실패!")
                return False
                
        except Exception as e:
            print(f"❌ 테스트 중 오류: {e}")
            return False
    
    def test_messages_format(self):
        """messages 형식으로 테스트"""
        print("\n" + "=" * 60)
        print("🧪 messages 형식 테스트")
        print("=" * 60)
        
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f'Bearer {self.api_key}',
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self.request_id
        }
        
        # messages 형식으로 요청
        request_data = {
            "messages": [
                {
                    "role": "user",
                    "content": "안녕하세요. 간단한 테스트입니다."
                }
            ],
            "maxTokens": 100,
            "temperature": 0.5,
            "topP": 0.8,
            "topK": 0,
            "repetitionPenalty": 1.1,
            "stop": [],
            "includeAiFilters": True,
            "seed": 0
        }
        
        print(f"📤 요청 데이터: {request_data}")
        
        try:
            conn = http.client.HTTPSConnection(self.host)
            conn.request('POST', self.model_endpoint, json.dumps(request_data), headers)
            response = conn.getresponse()
            
            print(f"📡 응답 상태: {response.status} {response.reason}")
            print(f"📡 응답 헤더: {response.getheaders()}")
            
            result = json.loads(response.read().decode(encoding='utf-8'))
            print(f"📡 응답 내용: {result}")
            
            conn.close()
            
            if response.status == 200:
                print("✅ messages 형식 테스트 성공!")
                return True
            else:
                print("❌ messages 형식 테스트 실패!")
                return False
                
        except Exception as e:
            print(f"❌ messages 형식 테스트 중 오류: {e}")
            return False

def main():
    print("=" * 60)
    print("🚀 새로운 CLOVA 모델 테스트")
    print("=" * 60)
    
    tester = NewModelTester()
    
    # 1. 간단한 요청 테스트
    success1 = tester.test_simple_request()
    
    # 2. messages 형식 테스트
    success2 = tester.test_messages_format()
    
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    print(f"간단한 요청 테스트: {'✅ 성공' if success1 else '❌ 실패'}")
    print(f"messages 형식 테스트: {'✅ 성공' if success2 else '❌ 실패'}")
    
    if success1 or success2:
        print("\n🎉 최소 하나의 테스트가 성공했습니다!")
    else:
        print("\n❌ 모든 테스트가 실패했습니다.")

if __name__ == "__main__":
    main() 