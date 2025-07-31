#!/usr/bin/env python3
"""
Naver Cloud Outbound Mailer API를 이용한 이메일 발송 서비스
- 일일 주식 시장 분석 보고서를 이메일로 발송
- HTML 템플릿을 이용한 전문적인 보고서 형식
"""

import os
import json
import time
import hmac
import hashlib
import base64
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class NaverCloudMailer:
    """Naver Cloud Outbound Mailer API 클라이언트"""
    
    def __init__(self):
        """초기화"""
        self.access_key = os.getenv("NAVER_CLOUD_ACCESS_KEY")
        self.secret_key = os.getenv("NAVER_CLOUD_SECRET_KEY")
        self.endpoint = os.getenv("NAVER_CLOUD_MAIL_ENDPOINT", "https://mail.apigw.ntruss.com/api/v1")
        
        # 발송자 정보
        self.sender_address = os.getenv("EMAIL_SENDER_ADDRESS")
        self.sender_name = os.getenv("EMAIL_SENDER_NAME", "주식시장분석봇")
        
        # 수신자 정보
        recipients_str = os.getenv("EMAIL_RECIPIENTS", "")
        self.recipients = [email.strip() for email in recipients_str.split(",") if email.strip()]
        
        # API 키 검증
        if not self.access_key or not self.secret_key:
            raise ValueError("NAVER_CLOUD_ACCESS_KEY와 NAVER_CLOUD_SECRET_KEY가 설정되지 않았습니다.")
        
        if not self.sender_address:
            raise ValueError("EMAIL_SENDER_ADDRESS가 설정되지 않았습니다.")
        
        if not self.recipients:
            raise ValueError("EMAIL_RECIPIENTS가 설정되지 않았습니다.")
        
        print("✅ Naver Cloud Mailer 초기화 완료")
        print(f"📧 발송자: {self.sender_name} <{self.sender_address}>")
        print(f"📧 수신자: {len(self.recipients)}명")
    
    def _make_signature(self, method: str, url: str, timestamp: str) -> str:
        """API 서명 생성"""
        message = f"{method} {url}\n{timestamp}\n{self.access_key}"
        
        print(f"🔍 서명 생성 디버깅:")
        print(f"   메시지: {message}")
        print(f"   Secret Key 길이: {len(self.secret_key)}")
        
        # HMAC-SHA256으로 서명 생성
        signing_key = self.secret_key.encode('utf-8')
        mac = hmac.new(signing_key, message.encode('utf-8'), hashlib.sha256)
        signature = base64.b64encode(mac.digest()).decode('utf-8')
        
        return signature
    
    def _get_headers(self, method: str, url: str) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        timestamp = str(int(time.time() * 1000))
        signature = self._make_signature(method, url, timestamp)
        
        headers = {
            'Content-Type': 'application/json',
            'x-ncp-apigw-timestamp': timestamp,
            'x-ncp-iam-access-key': self.access_key,
            'x-ncp-apigw-signature-v2': signature,
            'x-ncp-lang': 'ko-KR'
        }
        
        # 디버깅용 헤더 정보 출력
        print(f"🔍 API 헤더 정보:")
        print(f"   타임스탬프: {timestamp}")
        print(f"   Access Key: {self.access_key[:10]}...")
        print(f"   서명: {signature[:20]}...")
        print(f"   URL: {url}")
        
        return headers
    
    def send_report_email(self, report_file_path: str, subject: str = None) -> bool:
        """보고서 이메일 발송"""
        try:
            print(f"\n📧 이메일 발송 시작: {report_file_path}")
            
            # 보고서 파일 읽기
            if not os.path.exists(report_file_path):
                print(f"❌ 보고서 파일을 찾을 수 없습니다: {report_file_path}")
                return False
            
            with open(report_file_path, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # 제목 설정
            if not subject:
                current_date = datetime.now().strftime("%Y년 %m월 %d일")
                subject = f"[주식시장분석] {current_date} 일일 주식 시장 종합 분석 보고서"
            
            # HTML 템플릿 생성
            html_content = self._create_html_template(report_content, subject)
            
            # 수신자 목록 생성
            recipients_list = []
            for email in self.recipients:
                recipients_list.append({
                    "address": email,
                    "name": email.split('@')[0],  # 이메일 앞부분을 이름으로 사용
                    "type": "R"  # 수신자
                })
            
            # API 요청 데이터
            request_data = {
                "senderAddress": self.sender_address,
                "senderName": self.sender_name,
                "title": subject,
                "body": html_content,
                "recipients": recipients_list,
                "individual": True,  # 개별 발송
                "advertising": False  # 광고성 메일 아님
            }
            
            # API 호출
            url = "/mails"
            headers = self._get_headers("POST", url)
            
            print(f"📡 API 요청 전송 중...")
            print(f"   제목: {subject}")
            print(f"   수신자: {len(self.recipients)}명")
            
            response = requests.post(
                f"{self.endpoint}{url}",
                headers=headers,
                json=request_data,
                timeout=30
            )
            
            print(f"📡 API 응답 상태: {response.status_code}")
            print(f"📡 응답 헤더: {dict(response.headers)}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ 이메일 발송 성공!")
                print(f"   요청 ID: {result.get('requestId', 'N/A')}")
                return True
            elif response.status_code == 401:
                print(f"❌ 인증 실패 (401)")
                print(f"   응답: {response.text}")
                print("💡 해결 방법:")
                print("   1. API 키가 올바른지 확인하세요")
                print("   2. Secret Key가 정확한지 확인하세요")
                print("   3. 서명 생성 로직을 확인하세요")
                return False
            elif response.status_code == 403:
                print(f"❌ 권한 없음 (403)")
                print(f"   응답: {response.text}")
                print("💡 해결 방법:")
                print("   1. Cloud Outbound Mailer 서비스가 활성화되어 있는지 확인하세요")
                print("   2. 발송자 이메일 주소가 인증되어 있는지 확인하세요")
                return False
            else:
                print(f"❌ 이메일 발송 실패: {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 이메일 발송 중 오류: {e}")
            return False
    
    def _create_html_template(self, report_content: str, subject: str) -> str:
        """HTML 이메일 템플릿 생성"""
        # 보고서 내용을 HTML로 변환
        html_report = report_content.replace('\n', '<br>')
        
        # 제목에서 날짜 추출
        current_date = datetime.now().strftime("%Y년 %m월 %d일")
        
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007bff;
            margin: 0;
            font-size: 24px;
        }}
        .header .date {{
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
        .content {{
            line-height: 1.8;
        }}
        .section {{
            margin-bottom: 25px;
        }}
        .section h2 {{
            color: #007bff;
            border-left: 4px solid #007bff;
            padding-left: 15px;
            margin: 20px 0 15px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        .disclaimer {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }}
        .highlight {{
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>📊 일일 주식 시장 분석 보고서</h1>
            <div class="date">{current_date}</div>
        </div>
        
        <div class="content">
            {html_report}
        </div>
        
        <div class="footer">
            <p>본 보고서는 AI 기반 주식 시장 분석 시스템에 의해 자동 생성되었습니다.</p>
            <p>© 2025 주식시장분석봇. All rights reserved.</p>
        </div>
        
        <div class="disclaimer">
            <strong>⚠️ 투자 유의사항</strong><br>
            본 보고서는 참고용으로만 제공되며, 투자 결정의 근거로 사용해서는 안 됩니다. 
            투자는 개인의 책임 하에 이루어져야 하며, 충분한 조사와 분석을 거친 후 신중하게 결정하시기 바랍니다.
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def send_daily_report(self) -> bool:
        """일일 보고서 자동 발송"""
        try:
            print("\n" + "=" * 60)
            print("📧 일일 보고서 이메일 발송")
            print("=" * 60)
            
            # 최신 보고서 파일 찾기
            # 현재 스크립트 위치를 기준으로 상대 경로 설정
            current_dir = Path(__file__).parent
            daily_report_dir = current_dir.parent / "daily_report"
            if not daily_report_dir.exists():
                print("❌ daily_report 폴더를 찾을 수 없습니다.")
                return False
            
            # 가장 최근 보고서 파일 찾기
            report_files = list(daily_report_dir.glob("daily_combined_report_*.txt"))
            if not report_files:
                print("❌ 발송할 보고서 파일을 찾을 수 없습니다.")
                return False
            
            # 가장 최근 파일 선택
            latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
            print(f"📄 발송할 보고서: {latest_report.name}")
            
            # 이메일 발송
            success = self.send_report_email(str(latest_report))
            
            if success:
                print("✅ 일일 보고서 이메일 발송 완료!")
                return True
            else:
                print("❌ 일일 보고서 이메일 발송 실패!")
                return False
                
        except Exception as e:
            print(f"❌ 일일 보고서 발송 중 오류: {e}")
            return False

def main():
    """메인 실행 함수"""
    try:
        # 이메일 발송기 초기화
        mailer = NaverCloudMailer()
        
        # 일일 보고서 발송
        success = mailer.send_daily_report()
        
        if success:
            print("\n🎉 이메일 발송 서비스 완료!")
        else:
            print("\n❌ 이메일 발송 서비스 실패!")
            
    except Exception as e:
        print(f"❌ 서비스 실행 중 오류: {e}")

if __name__ == "__main__":
    main() 