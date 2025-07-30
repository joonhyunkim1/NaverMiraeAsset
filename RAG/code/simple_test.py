#!/usr/bin/env python3
"""
기존 파일들만 사용하는 간단한 테스트 스크립트
- 기존 벡터 파일들 사용
- 새로운 CLOVA 모델로 분석
"""

import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime

def start_faiss_api_server():
    """FAISS API 서버 시작"""
    print("\n" + "=" * 60)
    print("🚀 FAISS API 서버 시작")
    print("=" * 60)
    
    # 서버가 이미 실행 중인지 확인
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        if response.status_code == 200:
            print("✅ FAISS API 서버가 이미 실행 중입니다")
            return True
    except:
        pass
    
    # 서버 시작
    try:
        print("🔧 FAISS API 서버를 시작합니다...")
        process = subprocess.Popen(
            ["python", "faiss_vector_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 서버 시작 대기
        for i in range(30):  # 최대 30초 대기
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ FAISS API 서버 시작 완료")
                    return True
            except:
                continue
        
        print("❌ FAISS API 서버 시작 실패")
        return False
        
    except Exception as e:
        print(f"❌ FAISS API 서버 시작 중 오류: {e}")
        return False

def start_vector_db1_api_server():
    """Vector DB1 FAISS API 서버 시작"""
    print("\n" + "=" * 60)
    print("🚀 Vector DB1 FAISS API 서버 시작")
    print("=" * 60)
    
    # 서버가 이미 실행 중인지 확인
    try:
        response = requests.get("http://localhost:8001/health", timeout=3)
        if response.status_code == 200:
            print("✅ Vector DB1 FAISS API 서버가 이미 실행 중입니다")
            return True
    except:
        pass
    
    # 서버 시작
    try:
        print("🔧 Vector DB1 FAISS API 서버를 시작합니다...")
        process = subprocess.Popen(
            ["python", "faiss_vector_db1_api.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 서버 시작 대기
        for i in range(30):  # 최대 30초 대기
            time.sleep(1)
            try:
                response = requests.get("http://localhost:8001/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Vector DB1 FAISS API 서버 시작 완료")
                    return True
            except:
                continue
        
        print("❌ Vector DB1 FAISS API 서버 시작 실패")
        return False
        
    except Exception as e:
        print(f"❌ Vector DB1 FAISS API 서버 시작 중 오류: {e}")
        return False

def check_existing_files():
    """기존 파일들 확인"""
    print("\n" + "=" * 60)
    print("📁 기존 파일들 확인")
    print("=" * 60)
    
    # 벡터 파일들 확인
    vector_files = {
        "vector_db": Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/vector_db"),
        "vector_db_1": Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/vector_db_1"),
    }
    
    for name, path in vector_files.items():
        vectors_file = path / "hybrid_vectors.pkl"
        metadata_file = path / "hybrid_metadata.json"
        
        if vectors_file.exists() and metadata_file.exists():
            print(f"✅ {name}: 벡터 파일 존재")
        else:
            print(f"❌ {name}: 벡터 파일 없음")
    
    # data_2 파일들 확인
    data_2_path = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_2")
    if data_2_path.exists():
        files = list(data_2_path.glob("*"))
        print(f"📁 data_2 폴더: {len(files)}개 파일")
    else:
        print("❌ data_2 폴더 없음")

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("🚀 간단한 테스트 실행")
    print("📅 실행 시간:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    # 1. 기존 파일들 확인
    check_existing_files()
    
    # 2. FAISS API 서버 시작
    if not start_faiss_api_server():
        print("❌ FAISS API 서버 시작 실패")
        return
    
    # 3. Vector DB1 API 서버 시작
    if not start_vector_db1_api_server():
        print("❌ Vector DB1 API 서버 시작 실패")
        return
    
    # 4. Vector DB1 분석 실행
    print("\n" + "=" * 60)
    print("📊 Vector DB1 기반 분석")
    print("=" * 60)
    
    try:
        from vector_db_1_analyzer import VectorDB1Analyzer
        analyzer = VectorDB1Analyzer()
        analysis_success = analyzer.run_analysis()
        
        if analysis_success:
            print("✅ Vector DB1 기반 분석 완료")
        else:
            print("❌ Vector DB1 기반 분석 실패")
            
    except Exception as e:
        print(f"❌ Vector DB1 분석 중 오류: {e}")
    
    print("\n🎉 간단한 테스트 완료!")

if __name__ == "__main__":
    main() 