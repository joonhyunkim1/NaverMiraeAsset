#!/usr/bin/env python3
"""
이메일 발송 기능 테스트 스크립트
- Naver Cloud Outbound Mailer API 연결 테스트
- 보고서 이메일 발송 테스트
"""

import os
from pathlib import Path
from email_sender import NaverCloudMailer

def test_email_sender():
    """이메일 발송 기능 테스트"""
    print("=" * 60)
    print("📧 이메일 발송 기능 테스트")
    print("=" * 60)
    
    # 1. 환경 변수 확인
    print("\n1️⃣ 환경 변수 확인")
    print("-" * 40)
    
    required_vars = [
        "NAVER_CLOUD_ACCESS_KEY",
        "NAVER_CLOUD_SECRET_KEY", 
        "EMAIL_SENDER_ADDRESS",
        "EMAIL_RECIPIENTS"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: 설정됨")
        else:
            print(f"❌ {var}: 설정되지 않음")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️ 다음 환경 변수들을 .env 파일에 설정해주세요:")
        for var in missing_vars:
            print(f"   {var}")
        return False
    
    # 2. 이메일 발송기 초기화 테스트
    print("\n2️⃣ 이메일 발송기 초기화 테스트")
    print("-" * 40)
    
    try:
        mailer = NaverCloudMailer()
        print("✅ 이메일 발송기 초기화 성공")
    except Exception as e:
        print(f"❌ 이메일 발송기 초기화 실패: {e}")
        return False
    
    # 3. 보고서 파일 확인
    print("\n3️⃣ 보고서 파일 확인")
    print("-" * 40)
    
    # 현재 스크립트 위치를 기준으로 상대 경로 설정
    current_dir = Path(__file__).parent
    daily_report_dir = current_dir.parent / "daily_report"
    if not daily_report_dir.exists():
        print("❌ daily_report 폴더가 존재하지 않습니다.")
        return False
    
    report_files = list(daily_report_dir.glob("daily_combined_report_*.txt"))
    if not report_files:
        print("❌ 발송할 보고서 파일을 찾을 수 없습니다.")
        return False
    
    latest_report = max(report_files, key=lambda x: x.stat().st_mtime)
    print(f"✅ 최신 보고서 발견: {latest_report.name}")
    print(f"   파일 크기: {latest_report.stat().st_size:,} bytes")
    
    # 4. 이메일 발송 테스트
    print("\n4️⃣ 이메일 발송 테스트")
    print("-" * 40)
    
    try:
        success = mailer.send_daily_report()
        
        if success:
            print("✅ 이메일 발송 테스트 성공!")
            return True
        else:
            print("❌ 이메일 발송 테스트 실패!")
            return False
            
    except Exception as e:
        print(f"❌ 이메일 발송 테스트 중 오류: {e}")
        return False

def main():
    """메인 실행 함수"""
    success = test_email_sender()
    
    if success:
        print("\n🎉 이메일 발송 테스트 완료!")
    else:
        print("\n❌ 이메일 발송 테스트 실패!")

if __name__ == "__main__":
    main() 