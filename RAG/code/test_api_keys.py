#!/usr/bin/env python3
"""
Naver Cloud API 키 테스트 스크립트
"""

import os
import time
import hmac
import hashlib
import base64
import requests
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_api_keys():
    """API 키 테스트"""
    print("=" * 60)
    print("🔑 Naver Cloud API 키 테스트")
    print("=" * 60)
    
    # 환경 변수 로드
    access_key = os.getenv("NAVER_CLOUD_ACCESS_KEY")
    secret_key = os.getenv("NAVER_CLOUD_SECRET_KEY")
    
    print(f"📋 API 키 정보:")
    print(f"   Access Key: {access_key}")
    print(f"   Secret Key: {secret_key[:10]}..." if secret_key else "   Secret Key: None")
    print(f"   Access Key 길이: {len(access_key) if access_key else 0}")
    print(f"   Secret Key 길이: {len(secret_key) if secret_key else 0}")
    
    if not access_key or not secret_key:
        print("❌ API 키가 설정되지 않았습니다.")
        return False
    
    # 간단한 API 호출 테스트 (health check 또는 다른 간단한 엔드포인트)
    try:
        # 타임스탬프 생성
        timestamp = str(int(time.time() * 1000))
        
        # 서명 생성
        method = "GET"
        url = "/api/v1/health"  # 또는 다른 간단한 엔드포인트
        
        message = f"{method} {url}\n{timestamp}\n{access_key}"
        signing_key = secret_key.encode('utf-8')
        mac = hmac.new(signing_key, message.encode('utf-8'), hashlib.sha256)
        signature = base64.b64encode(mac.digest()).decode('utf-8')
        
        headers = {
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': access_key,
            'x-ncp-apigw-signature-v2': signature,
            'x-ncp-lang': 'ko-KR'
        }
        
        print(f"\n🔍 API 연결 테스트:")
        print(f"   엔드포인트: https://mail.apigw.ntruss.com{url}")
        print(f"   메서드: {method}")
        print(f"   타임스탬프: {timestamp}")
        print(f"   서명: {signature[:20]}...")
        
        response = requests.get(
            f"https://mail.apigw.ntruss.com{url}",
            headers=headers,
            timeout=10
        )
        
        print(f"📡 응답 상태: {response.status_code}")
        print(f"📡 응답 내용: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ API 연결 성공!")
            return True
        elif response.status_code == 401:
            print("❌ 인증 실패 - API 키를 확인하세요.")
            return False
        elif response.status_code == 403:
            print("❌ 권한 없음 - Cloud Outbound Mailer 서비스를 활성화하세요.")
            return False
        else:
            print(f"❌ 기타 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API 테스트 중 오류: {e}")
        return False

if __name__ == "__main__":
    success = test_api_keys()
    
    if success:
        print("\n🎉 API 키 테스트 성공!")
    else:
        print("\n❌ API 키 테스트 실패!")
        print("\n💡 해결 방법:")
        print("1. Naver Cloud Platform에서 API 키를 다시 확인하세요")
        print("2. Cloud Outbound Mailer 서비스가 활성화되어 있는지 확인하세요")
        print("3. 발송자 이메일 주소가 인증되어 있는지 확인하세요") 