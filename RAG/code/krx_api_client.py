#!/usr/bin/env python3
"""
KRX API 클라이언트 모듈
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from config import API_BASE_URL, DEFAULT_HEADERS, get_api_key

class KRXAPIClient:
    """KRX API 클라이언트"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.headers = DEFAULT_HEADERS.copy()
        self.api_key = get_api_key()
        
        # API 키가 설정되어 있다면 헤더에 추가
        if self.api_key and self.api_key != "your_krx_api_key_here":
            self.headers['Authorization'] = f'Bearer {self.api_key}'
            print("✅ KRX API 키가 설정되었습니다.")
        else:
            print("⚠️ KRX API 키가 설정되지 않았습니다. 공개 API로 시도합니다.")
    
    def get_previous_business_day(self) -> str:
        """이전 영업일을 계산합니다."""
        today = datetime.now()
        
        # 월요일인 경우 전 주 금요일로 설정
        if today.weekday() == 0:  # 월요일
            previous_day = today - timedelta(days=3)
        # 일요일인 경우 전 주 금요일로 설정
        elif today.weekday() == 6:  # 일요일
            previous_day = today - timedelta(days=2)
        else:
            # 다른 평일인 경우 하루 전으로 설정
            previous_day = today - timedelta(days=1)
        
        return previous_day.strftime('%Y%m%d')
    
    def get_daily_trading_data(self, target_date: str) -> Optional[pd.DataFrame]:
        """
        특정 날짜의 일일 매매 정보를 가져옵니다.
        
        Args:
            target_date (str): 'YYYYMMDD' 형식의 날짜
            
        Returns:
            pandas.DataFrame: 일일 매매 데이터
        """
        # KRX 일일 매매 정보 API 파라미터
        params = {
            'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
            'mktId': 'ALL',  # 전체 시장
            'trdDd': target_date,
            'share': '1',
            'money': '1',
            'csvxls_isNo': 'false'
        }
        
        try:
            print(f"📊 {target_date} 일일 매매 데이터를 가져오는 중...")
            
            response = requests.post(self.base_url, headers=self.headers, data=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'OutBlock_1' in data:
                df = pd.DataFrame(data['OutBlock_1'])
                print(f"✅ 데이터 가져오기 성공: {len(df)}개 종목")
                return df
            else:
                print("❌ 데이터가 없습니다.")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ API 요청 오류: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 오류: {e}")
            return None
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {e}")
            return None
    
    def get_daily_trading_data_alternative(self, target_date: str) -> Optional[pd.DataFrame]:
        """
        대체 방법: KRX 일일 매매 정보를 가져옵니다.
        """
        # 대체 API 엔드포인트
        params = {
            'bld': 'dbms/MDC/STAT/standard/MDCSTAT01501',
            'mktId': 'STK',  # 주식시장
            'trdDd': target_date,
            'share': '1',
            'money': '1',
            'csvxls_isNo': 'false'
        }
        
        try:
            print(f"📊 {target_date} 일일 매매 데이터를 가져오는 중... (대체 방법)")
            
            response = requests.post(self.base_url, headers=self.headers, data=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'OutBlock_1' in data:
                df = pd.DataFrame(data['OutBlock_1'])
                print(f"✅ 데이터 가져오기 성공: {len(df)}개 종목")
                return df
            else:
                print("❌ 데이터가 없습니다.")
                return None
                
        except Exception as e:
            print(f"❌ 대체 방법도 실패: {e}")
            return None
    
    def save_to_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """
        DataFrame을 CSV 파일로 저장합니다.
        
        Args:
            df (pandas.DataFrame): 저장할 데이터
            filename (str): 저장할 파일명
            
        Returns:
            bool: 저장 성공 여부
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ CSV 파일 저장 완료: {filename}")
            return True
        except Exception as e:
            print(f"❌ CSV 저장 오류: {e}")
            return False
    
    def collect_and_save_daily_data(self, target_date: str = None) -> Optional[str]:
        """
        일일거래정보를 수집하고 저장합니다.
        
        Args:
            target_date (str): 대상 날짜 (None이면 이전 영업일)
            
        Returns:
            str: 저장된 파일 경로 또는 None
        """
        if target_date is None:
            target_date = self.get_previous_business_day()
        
        print(f"📅 대상 날짜: {target_date}")
        
        # 첫 번째 방법으로 데이터 가져오기
        df = self.get_daily_trading_data(target_date)
        
        # 첫 번째 방법이 실패하면 대체 방법 시도
        if df is None or df.empty:
            print("🔄 첫 번째 방법 실패, 대체 방법 시도...")
            df = self.get_daily_trading_data_alternative(target_date)
        
        if df is not None and not df.empty:
            # 데이터 전처리
            print("\n🔧 데이터 전처리 중...")
            print(f"📊 원본 데이터 형태: {df.shape}")
            print(f"📋 컬럼명: {list(df.columns)}")
            
            # 숫자 컬럼의 쉼표 제거 및 숫자 변환
            numeric_columns = ['TDD_CLSPRC', 'CMPPREVDD_PRC', 'FLUC_RT', 'TDD_OPNPRC', 
                              'TDD_HGPRC', 'TDD_LWPRC', 'ACC_TRDVOL', 'ACC_TRDVAL', 
                              'MKTCAP', 'LIST_SHRS']
            
            for col in numeric_columns:
                if col in df.columns:
                    # 쉼표 제거 후 숫자로 변환
                    df[col] = df[col].astype(str).str.replace(',', '').str.replace('-', '0')
                    # 숫자가 아닌 값은 0으로 처리
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # CSV 파일을 지정된 경로에 저장
            current_dir = Path(__file__).parent
            data_dir = current_dir.parent / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = data_dir / f"krx_daily_trading_{target_date}.csv"
            
            # 전체 종목 저장 (거래량이 있는 종목들 포함)
            if self.save_to_csv(df, str(filename)):
                # 데이터 샘플 출력
                print("\n📊 데이터 샘플 (전체 종목):")
                print(df.head())
                
                # 기본 통계 정보
                print("\n📈 기본 통계 정보:")
                print(f"총 종목 수: {len(df)}개")
                if 'TDD_CLSPRC' in df.columns:
                    print(f"평균 종가: {df['TDD_CLSPRC'].mean():.2f}")
                if 'ACC_TRDVOL' in df.columns:
                    print(f"총 거래량: {df['ACC_TRDVOL'].sum():,}")
                    
                    # 거래량이 있는 종목 수 계산
                    trading_stocks = df[df['ACC_TRDVOL'] > 0]
                    print(f"거래량 있는 종목 수: {len(trading_stocks)}개")
                
                return str(filename)
            else:
                return None
                
        else:
            print("❌ 데이터를 가져올 수 없습니다.")
            print("다음 사항을 확인해주세요:")
            print("1. 인터넷 연결 상태")
            print("2. KRX 웹사이트 접근 가능 여부")
            print("3. 요청한 날짜에 거래 데이터 존재 여부")
            return None 