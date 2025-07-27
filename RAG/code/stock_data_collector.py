#!/usr/bin/env python3
"""
FinanceDataReader 기반 주식 데이터 수집 시스템
CLOVA Function Calling을 통한 지능형 데이터 수집
"""

import FinanceDataReader as fdr
import pandas as pd
import requests
import json
import uuid
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dateutil.parser import parse
from dotenv import load_dotenv

# 📌 .env 파일 로드
env_path = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/code/.env")
load_dotenv(env_path)

# 📌 CLOVA API 설정
API_KEY = os.getenv("CLOVA_API_KEY", "")
API_URL = "https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005"

# 📌 데이터 저장 경로
DATA_DIR = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/Individual_Stock_Search/data")

# 📌 Function Calling 정의
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_data",
            "description": "사용자의 질문에서 종목명이나 종목코드를 추출하여 해당 주식의 가격 데이터를 조회하고 CSV 파일로 저장합니다. 종목명(예: 삼성전자) 또는 종목코드(005930) 모두 인식 가능합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "사용자 질문에서 추출한 종목코드 또는 종목명입니다. 예: '005930' 또는 '삼성전자'. 사용자가 '삼성전자 주가를 알려줘'라고 하면 '삼성전자'를 추출합니다.KRX 종목만 지원합니다. KRX에 있는 종목명으로 변환 후 파라미터 설정을 해주세요."
                    },
                    "start_date": {
                        "type": "string",
                        "description": "조회 시작 날짜입니다. YYYY-MM-DD 형식으로 입력하세요. 기본값은 6개월 전입니다."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "조회 종료 날짜입니다. YYYY-MM-DD 형식으로 입력하세요. 기본값은 오늘입니다."
                    },

                },
                "required": ["ticker"]
            }
        }
    }
]

class StockDataCollector:
    """주식 데이터 수집 클래스"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
        # KRX 종목 목록을 미리 로드
        self._load_stock_list()
        
    def _load_stock_list(self):
        """KRX 종목 목록 로드"""
        try:
            self.stock_df = fdr.StockListing('KRX')
            print(f"✅ KRX 종목 목록 로드 완료: {len(self.stock_df)}개 종목")
        except Exception as e:
            print(f"❌ KRX 종목 목록 로드 실패: {e}")
            self.stock_df = pd.DataFrame()
        
    def get_stock_code(self, ticker: str) -> Optional[Dict[str, str]]:
        """종목명을 종목코드로 변환하고 정확한 종목명도 반환"""
        try:
            if self.stock_df.empty:
                return None
            
            # 이미 종목코드인 경우
            if ticker.isdigit():
                match = self.stock_df[self.stock_df['Code'] == ticker]
                if not match.empty:
                    return {
                        "code": ticker,
                        "name": match.iloc[0]['Name'],
                        "original_input": ticker
                    }
                return None
            
            # 종목명으로 검색 (정확한 매칭)
            exact_match = self.stock_df[self.stock_df['Name'] == ticker]
            if not exact_match.empty:
                return {
                    "code": exact_match.iloc[0]['Code'],
                    "name": ticker,
                    "original_input": ticker
                }
            
            # 부분 일치 검색 (더 정확한 매칭)
            # 1. 시작 부분 일치
            start_match = self.stock_df[self.stock_df['Name'].str.startswith(ticker, na=False)]
            if not start_match.empty:
                return {
                    "code": start_match.iloc[0]['Code'],
                    "name": start_match.iloc[0]['Name'],
                    "original_input": ticker
                }
            
            # 2. 포함 일치 (더 유연한 검색)
            contains_match = self.stock_df[self.stock_df['Name'].str.contains(ticker, na=False)]
            if not contains_match.empty:
                return {
                    "code": contains_match.iloc[0]['Code'],
                    "name": contains_match.iloc[0]['Name'],
                    "original_input": ticker
                }
            
            # 3. 유사한 종목명 검색 (대소문자 무시)
            similar_match = self.stock_df[self.stock_df['Name'].str.lower().str.contains(ticker.lower(), na=False)]
            if not similar_match.empty:
                return {
                    "code": similar_match.iloc[0]['Code'],
                    "name": similar_match.iloc[0]['Name'],
                    "original_input": ticker
                }
            
            return None
            
        except Exception as e:
            print(f"종목코드 변환 오류: {e}")
            return None
    
    def get_stock_data(self, ticker: str, start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> Dict[str, Any]:
        """주식 데이터 조회 및 CSV 저장"""
        
        # 종목코드 변환
        stock_info = self.get_stock_code(ticker)
        if not stock_info:
            return {"error": f"'{ticker}'에 대한 종목코드를 찾을 수 없습니다."}
        
        stock_code = stock_info["code"]
        stock_name = stock_info["name"]
        original_input = stock_info["original_input"]
        
        try:
            # 기본 날짜 설정 (6개월 전 ~ 오늘)
            if not start_date:
                start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # 날짜 파싱
            start_dt = parse(start_date).date()
            end_dt = parse(end_date).date()
            
            # 데이터 조회
            print(f"📊 {stock_name}({stock_code}) 데이터 조회 중...")
            print(f"📅 기간: {start_date} ~ {end_date}")
            
            df = fdr.DataReader(stock_code, start_date, end_date)
            
            if df.empty:
                return {"error": f"해당 기간에 거래 데이터가 없습니다."}
            
            # 데이터 전처리
            df = self._preprocess_data(df)
            
            # CSV 파일 저장 (정확한 종목명 사용)
            filename = self._save_to_csv(df, stock_name, stock_code, start_date, end_date)
            
            # 결과 정보
            result = {
                "success": True,
                "ticker": stock_name,  # 정확한 종목명 사용
                "original_input": original_input,  # 원본 입력 보존
                "stock_code": stock_code,
                "start_date": start_date,
                "end_date": end_date,
                "filename": filename,
                "data_points": len(df),
                "file_path": str(self.data_dir / filename),
                "summary": self._get_data_summary(df)
            }
            
            print(f"✅ 데이터 수집 완료: {filename}")
            return result
            
        except Exception as e:
            return {"error": f"데이터 조회 중 오류 발생: {str(e)}"}
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 전처리"""
        # 날짜 인덱스를 컬럼으로 변환
        df = df.reset_index()
        
        # 컬럼명 정리 (첫 글자만 대문자로)
        df.columns = [col.capitalize() for col in df.columns]
        
        # 숫자 컬럼 정리
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # NaN 값 처리
        df = df.dropna()
        
        return df
    
    def _save_to_csv(self, df: pd.DataFrame, ticker: str, stock_code: str, 
                    start_date: str, end_date: str) -> str:
        """CSV 파일로 저장"""
        # 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{ticker}_{stock_code}_{start_date}_{end_date}_{timestamp}.csv"
        
        # 파일 저장
        file_path = self.data_dir / filename
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        return filename
    
    def _get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """데이터 요약 정보"""
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        first = df.iloc[0]
        
        return {
            "latest_close": float(latest['Close']),
            "latest_date": str(latest['Date']),
            "price_change": float(latest['Close'] - first['Close']),
            "price_change_pct": float((latest['Close'] - first['Close']) / first['Close'] * 100),
            "highest_price": float(df['High'].max()),
            "lowest_price": float(df['Low'].min()),
            "avg_volume": float(df['Volume'].mean()),
            "total_volume": int(df['Volume'].sum())
        }

def format_tool_result(result: Dict[str, Any]) -> str:
    """도구 실행 결과를 포맷팅"""
    if "error" in result:
        return f"❌ 오류 발생: {result['error']}"
    
    summary = result['summary']
    
    return f"""✅ 주식 데이터 수집 완료

📊 종목 정보:
- 종목명: {result['ticker']} (입력: {result['original_input']})
- 종목코드: {result['stock_code']}
- 조회기간: {result['start_date']} ~ {result['end_date']}
- 데이터 포인트: {result['data_points']:,}개

📈 가격 정보:
- 최신 종가: {summary['latest_close']:,}원 ({summary['latest_date']})
- 기간 내 변동: {summary['price_change']:+,.0f}원 ({summary['price_change_pct']:+.2f}%)
- 최고가: {summary['highest_price']:,}원
- 최저가: {summary['lowest_price']:,}원

📊 거래량 정보:
- 평균 거래량: {summary['avg_volume']:,.0f}주
- 총 거래량: {summary['total_volume']:,}주

💾 파일 정보:
- 파일명: {result['filename']}
- 저장경로: {result['file_path']}"""

def process_tool_calls(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """도구 호출 처리"""
    tool_map = {
        "get_stock_data": StockDataCollector().get_stock_data,
    }
    
    func = tool_map.get(tool_name)
    if func:
        return func(**arguments)
    else:
        return {"error": f"알 수 없는 함수: {tool_name}"}

def chat_completions(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """CLOVA API 요청"""
    # 매번 새로운 REQUEST_ID 생성
    request_id = str(uuid.uuid4()).replace('-', '')
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-NCP-CLOVASTUDIO-REQUEST-ID": request_id,
        "Content-Type": "application/json"
    }

    payload = {
        "model": "command-naver",
        "messages": messages,
        "tools": tools,
        "toolChoice": "auto"
    }

    try:
        print(f"🔍 CLOVA API 요청:")
        print(f"📡 REQUEST_ID: {request_id}")
        print(f"📝 Messages 수: {len(messages)}")
        
        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"📊 응답 상태: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 오류 응답: {response.text}")
            return {"error": f"API 오류: {response.status_code}"}
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 예외: {str(e)}")
        return {"error": f"API 요청 중 오류 발생: {str(e)}"}

def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("📈 FinanceDataReader 기반 주식 데이터 수집 시스템")
    print("🤖 CLOVA Function Calling 통합")
    print("=" * 60)
    
    # API 키 확인
    if not API_KEY:
        print("❌ CLOVA API 키가 설정되지 않았습니다!")
        print("📁 .env 파일 경로: /Users/Chris/Desktop/JH/MiraeassetNaver/RAG/code/.env")
        print("🔑 CLOVA_API_KEY 환경변수를 설정해주세요.")
        return
    else:
        print(f"✅ CLOVA API 키 로드 완료: {API_KEY[:10]}...")
    
    # StockDataCollector 인스턴스 생성
    collector = StockDataCollector()
    
    while True:
        try:
            user_input = input("\n📥 종목명 또는 종목코드를 입력하세요 (종료: quit): ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료']:
                print("👋 시스템을 종료합니다.")
                break
            
            if not user_input:
                continue
            
            print(f"👤 사용자: {user_input}")
            print("🤖 CLOVA AI가 질문을 분석하고 주식 데이터를 수집합니다...")
            
            # Step 1: 첫 번째 요청 (Function Calling 판단)
            messages = [{"role": "user", "content": user_input}]
            first_response = chat_completions(messages)
            
            if "error" in first_response:
                print(f"🛑 API 오류: {first_response['error']}")
                continue
            
            # 응답 구조 확인
            result_message = first_response.get("result", {}).get("message", {})
            tool_calls = result_message.get("toolCalls", [])
            
            if tool_calls:
                print("🔧 CLOVA AI가 주식 데이터 수집 함수를 호출합니다")
                
                # Step 2: 함수 호출 및 실행
                tool_call = tool_calls[0]
                tool_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]
                
                # arguments가 문자열인 경우 파싱
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        print("🛑 함수 매개변수 파싱 오류")
                        continue
                
                print(f"📊 종목: {arguments.get('ticker', 'N/A')}")
                if arguments.get('start_date'):
                    print(f"📅 시작일: {arguments['start_date']}")
                if arguments.get('end_date'):
                    print(f"📅 종료일: {arguments['end_date']}")
                
                # 실제 함수 실행
                tool_result = process_tool_calls(tool_name, arguments)
                
                if "error" in tool_result:
                    print(f"🛑 데이터 수집 오류: {tool_result['error']}")
                    continue
                
                # 결과를 구조화된 텍스트로 포맷팅
                formatted_result = format_tool_result(tool_result)
                print(f"\n✅ 데이터 수집 완료:")
                print(formatted_result)
                
                # Step 3: 대화 기록 업데이트
                assistant_message = {
                    "role": "assistant", 
                    "content": "", 
                    "toolCalls": [tool_call]
                }
                tool_message = {
                    "role": "tool",
                    "toolCallId": tool_call["id"], 
                    "content": formatted_result[:2000]  # 내용 길이 제한
                }
                
                messages.append(assistant_message)
                messages.append(tool_message)
                
                print(f"\n🎉 주식 데이터 수집이 성공적으로 완료되었습니다!")
                print(f"📁 CSV 파일 저장 위치: {tool_result['file_path']}")
            
            else:
                # Function Calling이 불필요한 경우
                print("❌ 주식 데이터 수집이 필요하지 않은 요청입니다.")
                print("💡 예시: '삼성전자 주가 데이터를 가져와줘', '005930 2024년 데이터', 'SK하이닉스 최근 6개월 주가'")
        
        except KeyboardInterrupt:
            print("\n\n👋 시스템을 종료합니다.")
            break
        except Exception as e:
            print(f"\n❌ 오류가 발생했습니다: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # 바로 실행 (테스트 없이)
    main() 