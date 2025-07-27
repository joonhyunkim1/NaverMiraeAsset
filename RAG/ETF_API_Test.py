import requests
import pandas as pd
import json
from datetime import datetime
import time
from config import get_api_key

class ETFKRXAPI:
    def __init__(self):
        self.base_url = "http://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'http://data.krx.co.kr',
            'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020101'
        }
        self.api_key = get_api_key()
        
        # API 키가 설정되어 있다면 헤더에 추가
        if self.api_key and self.api_key != "your_krx_api_key_here":
            self.headers['Authorization'] = f'Bearer {self.api_key}'
            print("API 키가 설정되었습니다.")
        else:
            print("API 키가 설정되지 않았습니다. 공개 API로 시도합니다.")
    
    def get_etf_daily_trading_data(self, target_date):
        """
        특정 날짜의 ETF 일일 매매 정보를 가져옵니다.
        
        Args:
            target_date (str): 'YYYYMMDD' 형식의 날짜
            
        Returns:
            pandas.DataFrame: ETF 일일 매매 데이터
        """
        # ETF 일일 매매 정보 API 파라미터 (스펙에 따라 basDd 사용)
        params = {
            'basDd': target_date
        }
        
        try:
            print(f"{target_date} ETF 일일 매매 데이터를 가져오는 중...")
            
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            print(f"응답 상태 코드: {response.status_code}")
            print(f"응답 헤더: {dict(response.headers)}")
            print(f"응답 내용 (처음 500자): {response.text[:500]}")
            
            # JSONP 응답 처리
            response_text = response.text.strip()
            if response_text.startswith('callback(') and response_text.endswith(');'):
                # JSONP 형식에서 JSON 부분만 추출
                json_str = response_text[9:-2]  # 'callback(' 제거하고 ');' 제거
                data = json.loads(json_str)
            else:
                data = response.json()
            
            if 'OutBlock_1' in data:
                df = pd.DataFrame(data['OutBlock_1'])
                print(f"데이터 가져오기 성공: {len(df)}개 ETF")
                return df
            elif isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                print(f"데이터 가져오기 성공: {len(df)}개 ETF")
                return df
            else:
                print("데이터가 없습니다.")
                return pd.DataFrame()
                
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return pd.DataFrame()
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"예상치 못한 오류: {e}")
            return pd.DataFrame()
    
    def get_etf_daily_trading_data_alternative(self, target_date):
        """
        대체 방법: POST 요청으로 ETF 일일 매매 정보를 가져옵니다.
        """
        # POST 요청으로 시도 (스펙에 따라 basDd 사용)
        payload = {
            'basDd': target_date
        }
        
        try:
            print(f"{target_date} ETF 일일 매매 데이터를 가져오는 중... (POST 방법)")
            
            response = requests.post(current_url, headers=self.headers, data=payload)
            response.raise_for_status()
            
            print(f"POST 응답 상태 코드: {response.status_code}")
            print(f"POST 응답 내용 (처음 500자): {response.text[:500]}")
            
            # JSONP 응답 처리
            response_text = response.text.strip()
            if response_text.startswith('callback(') and response_text.endswith(');'):
                # JSONP 형식에서 JSON 부분만 추출
                json_str = response_text[9:-2]  # 'callback(' 제거하고 ');' 제거
                data = json.loads(json_str)
            else:
                data = response.json()
            
            if 'OutBlock_1' in data:
                df = pd.DataFrame(data['OutBlock_1'])
                print(f"데이터 가져오기 성공: {len(df)}개 ETF")
                return df
            elif isinstance(data, list) and len(data) > 0:
                df = pd.DataFrame(data)
                print(f"데이터 가져오기 성공: {len(df)}개 ETF")
                return df
            else:
                print("데이터가 없습니다.")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"POST 방법도 실패: {e}")
            return pd.DataFrame()

def save_to_csv(df, filename):
    """
    DataFrame을 CSV 파일로 저장합니다.
    
    Args:
        df (pandas.DataFrame): 저장할 데이터
        filename (str): 저장할 파일명
    """
    try:
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"CSV 파일 저장 완료: {filename}")
    except Exception as e:
        print(f"CSV 저장 오류: {e}")

def main():
    # ETF KRX API 인스턴스 생성
    etf_api = ETFKRXAPI()
    
    # 2024년 7월 22일 데이터 요청 (월요일)
    target_date = "20250724"
    
    print("=" * 50)
    print("KRX ETF 일일 매매 정보 수집")
    print("=" * 50)
    
    # 첫 번째 방법으로 데이터 가져오기 (GET 요청)
    df = etf_api.get_etf_daily_trading_data(target_date)
    
    # 첫 번째 방법이 실패하면 대체 방법 시도 (POST 요청)
    if df.empty:
        print("첫 번째 방법 실패, 대체 방법 시도...")
        df = etf_api.get_etf_daily_trading_data_alternative(target_date)
    
    if not df.empty:
        # 데이터 전처리
        print("\n데이터 전처리 중...")
        print(f"원본 데이터 형태: {df.shape}")
        print(f"컬럼명: {list(df.columns)}")
        
        # 숫자 컬럼의 쉼표 제거 및 숫자 변환 (일반적인 컬럼명들)
        numeric_columns = ['TDD_CLSPRC', 'CMPPREVDD_PRC', 'FLUC_RT', 'TDD_OPNPRC', 
                          'TDD_HGPRC', 'TDD_LWPRC', 'ACC_TRDVOL', 'ACC_TRDVAL', 
                          'MKTCAP', 'LIST_SHRS', 'NAV', 'TDD_NAV', 'SPREAD']
        
        for col in numeric_columns:
            if col in df.columns:
                # 쉼표 제거 후 숫자로 변환
                df[col] = df[col].astype(str).str.replace(',', '').str.replace('-', '0')
                # 숫자가 아닌 값은 0으로 처리
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # CSV 파일을 지정된 경로에 저장
        import os
        data_dir = "/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data"
        filename = os.path.join(data_dir, f"krx_etf_daily_trading_{target_date}.csv")
        save_to_csv(df, filename)
        
        # 데이터 샘플 출력
        print("\n데이터 샘플:")
        print(df.head())
        
        # 기본 통계 정보
        print("\n기본 통계 정보:")
        print(f"총 ETF 수: {len(df)}")
        
        # 주요 컬럼이 있는 경우 통계 출력
        if 'TDD_CLSPRC' in df.columns:
            print(f"평균 종가: {df['TDD_CLSPRC'].mean():.2f}")
        if 'ACC_TRDVOL' in df.columns:
            print(f"총 거래량: {df['ACC_TRDVOL'].sum():,}")
        if 'NAV' in df.columns:
            print(f"평균 NAV: {df['NAV'].mean():.2f}")
            
    else:
        print("데이터를 가져올 수 없습니다.")
        print("다음 사항을 확인해주세요:")
        print("1. 인터넷 연결 상태")
        print("2. KRX ETF API 접근 가능 여부")
        print("3. 요청한 날짜에 ETF 거래 데이터 존재 여부")
        print("4. API 키 설정 여부 (필요한 경우)")

if __name__ == "__main__":
    main() 