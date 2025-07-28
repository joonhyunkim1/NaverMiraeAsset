#!/usr/bin/env python3
"""
주식 종목 추출 및 주가 데이터 수집 시스템
- CLOVA 분석 결과에서 이슈 종목 추출
- Function Calling을 통해 주가 데이터 수집
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd

# 주식 데이터 수집기
from stock_data_collector import StockDataCollector, chat_completions, process_tool_calls

# 환경변수 로드
env_path = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/code/.env")
load_dotenv(env_path)

# 📌 종목명 추출용 Function Calling 정의
extraction_tools = [
    {
        "type": "function",
        "function": {
            "name": "extract_stock_names",
            "description": "분석 결과에서 이슈가 된 주식 종목명들을 추출합니다. 정확한 KRX 종목명으로 추출해주세요.",
            "parameters": {
                "type": "object",
                "properties": {
                    "extracted_stocks": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "분석 결과에서 추출된 주식 종목명들의 배열입니다. 정확한 KRX 종목명으로 추출해주세요."
                    }
                },
                "required": ["extracted_stocks"]
            }
        }
    }
]

class StockExtractor:
    """주식 종목 추출 및 데이터 수집 클래스"""
    
    def __init__(self):
        self.data_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1")
        self.output_dir = Path("/Users/Chris/Desktop/JH/MiraeassetNaver/RAG/data_1")
        self.output_dir.mkdir(exist_ok=True)
        
        # 주식 데이터 수집기 초기화
        self.stock_collector = StockDataCollector()
        
        # KRX 종목 목록 로드
        self._load_stock_list()
        
        print("🔧 StockExtractor 초기화 완료")
        print(f"📁 데이터 디렉토리: {self.data_dir}")
        print(f"📁 출력 디렉토리: {self.output_dir}")
    
    def _load_stock_list(self):
        """KRX 종목 목록 로드"""
        try:
            import finance_datareader as fdr
            self.stock_df = fdr.StockListing('KRX')
            print(f"✅ KRX 종목 목록 로드 완료: {len(self.stock_df)}개 종목")
        except ImportError:
            print("❌ finance_datareader 모듈이 설치되지 않았습니다.")
            print("💡 pip install finance-datareader 명령으로 설치하세요.")
            self.stock_df = pd.DataFrame()
        except Exception as e:
            print(f"❌ KRX 종목 목록 로드 실패: {e}")
            self.stock_df = pd.DataFrame()
    
    def get_stock_code(self, ticker: str) -> Optional[Dict[str, str]]:
        """종목명을 종목코드로 변환하고 정확한 종목명도 반환 (stock_data_collector와 동일한 로직)"""
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
    
    def _chat_completions_with_extraction_tools(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """종목명 추출용 CLOVA API 요청"""
        import requests
        import uuid
        
        API_KEY = os.getenv('CLOVA_API_KEY')
        API_URL = "https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005"
        
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
            "tools": extraction_tools,
            "toolChoice": "auto"
        }

        try:
            print(f"🔍 종목명 추출용 CLOVA API 요청:")
            print(f"📡 REQUEST_ID: {request_id}")
            
            response = requests.post(API_URL, headers=headers, json=payload)
            print(f"📊 응답 상태: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ 오류 응답: {response.text}")
                return {"error": f"API 오류: {response.status_code}"}
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 요청 예외: {str(e)}")
            return {"error": f"API 요청 중 오류 발생: {str(e)}"}
    
    def load_clova_analysis(self) -> Optional[Dict]:
        """CLOVA 분석 결과 로드"""
        try:
            # 가장 최근 분석 결과 파일 찾기
            analysis_files = list(self.data_dir.glob("clova_analysis_*.json"))
            if not analysis_files:
                print("❌ CLOVA 분석 결과 파일을 찾을 수 없습니다.")
                return None
            
            latest_file = max(analysis_files, key=lambda x: x.stat().st_mtime)
            print(f"📊 CLOVA 분석 결과 파일 로드: {latest_file.name}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            print(f"✅ CLOVA 분석 결과 로드 완료")
            return analysis_data
            
        except Exception as e:
            print(f"❌ CLOVA 분석 결과 로드 실패: {e}")
            return None
    
    def extract_stock_names(self, analysis_result: str) -> List[str]:
        """CLOVA Function Calling을 사용하여 분석 결과에서 주식 종목명 추출"""
        stock_names = []
        
        try:
            # CLOVA Function Calling을 사용하여 종목명 추출
            extraction_prompt = f"""
다음은 CLOVA가 분석한 주식 시장 데이터입니다. 이 분석 결과에서 이슈가 된 주식 종목명들을 추출해주세요.

분석 결과:
{analysis_result}

위 분석 결과에서 언급된 모든 주식 종목명을 정확히 추출하여 JSON 형태로 반환해주세요.
예시:
```json
{{
    "extracted_stocks": ["종목명1", "종목명2", "종목명3"]
}}
```

종목명은 정확한 KRX 종목명으로 추출해주세요.
"""
            
            # CLOVA Function Calling을 통한 종목명 추출
            messages = [{"role": "user", "content": extraction_prompt}]
            response = self._chat_completions_with_extraction_tools(messages)
            
            if "error" in response:
                print(f"❌ CLOVA Function Calling 실패: {response['error']}")
                return []
            
            # 응답 구조 확인
            result_message = response.get("result", {}).get("message", {})
            tool_calls = result_message.get("toolCalls", [])
            
            if tool_calls:
                tool_call = tool_calls[0]
                tool_name = tool_call["function"]["name"]
                arguments = tool_call["function"]["arguments"]
                
                # arguments가 문자열인 경우 파싱
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        print("❌ 함수 매개변수 파싱 오류")
                        return []
                
                # 추출된 종목명들 처리
                if tool_name == "extract_stock_names":
                    extracted_stocks = arguments.get("extracted_stocks", [])
                    if isinstance(extracted_stocks, list):
                        stock_names = extracted_stocks
                        print(f"✅ CLOVA Function Calling으로 종목명 추출 완료: {stock_names}")
                        return stock_names
            
            # Function Calling이 실패한 경우 텍스트에서 직접 추출 (백업 방법)
            print("⚠️ CLOVA Function Calling 실패, 텍스트에서 직접 추출 시도...")
            
            # JSON 형태의 결과에서 종목명 추출
            json_match = re.search(r'```json\s*(\[.*?\])\s*```', analysis_result, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                try:
                    data = json.loads(json_str)
                    
                    # 배열 형태의 데이터에서 종목명 추출
                    for item in data:
                        if isinstance(item, dict):
                            # 다양한 키 이름으로 종목명 찾기
                            for key in ['종목명', '종목 명', 'stock_name', 'name']:
                                if key in item:
                                    stock_names.append(item[key])
                                    print(f"✅ JSON에서 종목명 추출: {item[key]}")
                                    break
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 파싱 실패: {e}")
            
            # 텍스트에서도 종목명 추출 (추가 백업 방법)
            if not stock_names:
                # 다양한 패턴으로 종목명 찾기
                patterns = [
                    r'"종목명":\s*"([^"]+)"',
                    r'"종목 명":\s*"([^"]+)"',
                    r'"stock_name":\s*"([^"]+)"',
                    r'"name":\s*"([^"]+)"'
                ]
                
                for pattern in patterns:
                    stock_matches = re.findall(pattern, analysis_result)
                    if stock_matches:
                        stock_names.extend(stock_matches)
                        print(f"✅ 정규식으로 종목명 추출: {stock_matches}")
                        break
            
            # 중복 제거
            stock_names = list(set(stock_names))
            
            # 추출된 종목명들을 stock_data_collector와 동일한 방식으로 매칭
            validated_stock_names = []
            for stock_name in stock_names:
                stock_info = self.get_stock_code(stock_name)
                if stock_info:
                    validated_stock_names.append(stock_info["name"])
                    print(f"✅ 종목명 검증 완료: '{stock_name}' → '{stock_info['name']}' (코드: {stock_info['code']})")
                else:
                    print(f"❌ 종목명 검증 실패: '{stock_name}' (KRX에 존재하지 않음)")
            
            print(f"📈 최종 검증된 종목명: {validated_stock_names}")
            return validated_stock_names
            
        except Exception as e:
            print(f"❌ 종목명 추출 실패: {e}")
            return []
    
    def collect_stock_data(self, stock_names: List[str]) -> List[Dict[str, Any]]:
        """추출된 종목들의 주가 데이터 수집"""
        collected_data = []
        
        for stock_name in stock_names:
            try:
                print(f"\n📊 {stock_name} 주가 데이터 수집 중...")
                
                # Function Calling을 통한 데이터 수집
                messages = [{"role": "user", "content": f"{stock_name}의 최근 6개월 주가 데이터를 가져와줘"}]
                
                response = chat_completions(messages)
                
                if "error" in response:
                    print(f"❌ {stock_name} 데이터 수집 실패: {response['error']}")
                    continue
                
                # 응답 구조 확인
                result_message = response.get("result", {}).get("message", {})
                tool_calls = result_message.get("toolCalls", [])
                
                if tool_calls:
                    tool_call = tool_calls[0]
                    tool_name = tool_call["function"]["name"]
                    arguments = tool_call["function"]["arguments"]
                    
                    # arguments가 문자열인 경우 파싱
                    if isinstance(arguments, str):
                        try:
                            arguments = json.loads(arguments)
                        except json.JSONDecodeError:
                            print(f"❌ {stock_name} 함수 매개변수 파싱 오류")
                            continue
                    
                    # 실제 함수 실행
                    tool_result = process_tool_calls(tool_name, arguments)
                    
                    if "error" not in tool_result:
                        collected_data.append({
                            "stock_name": stock_name,
                            "data": tool_result,
                            "collection_time": datetime.now().isoformat()
                        })
                        print(f"✅ {stock_name} 데이터 수집 완료")
                    else:
                        print(f"❌ {stock_name} 데이터 수집 실패: {tool_result['error']}")
                else:
                    print(f"❌ {stock_name} Function Calling 실패")
                    
            except Exception as e:
                print(f"❌ {stock_name} 처리 중 오류: {e}")
                continue
        
        return collected_data
    
    def save_collected_data(self, collected_data: List[Dict[str, Any]]) -> str:
        """수집된 데이터 저장"""
        if not collected_data:
            print("❌ 저장할 데이터가 없습니다.")
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"collected_stock_data_{timestamp}.json"
        file_path = self.output_dir / filename
        
        try:
            # 저장할 데이터 구성
            save_data = {
                "collection_time": datetime.now().isoformat(),
                "total_stocks": len(collected_data),
                "stocks": collected_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 수집된 데이터 저장 완료: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"❌ 데이터 저장 실패: {e}")
            return ""
    
    def run_extraction(self) -> bool:
        """전체 추출 프로세스 실행"""
        print("=" * 60)
        print("🚀 주식 종목 추출 및 데이터 수집 시스템")
        print("=" * 60)
        
        # 1. CLOVA 분석 결과 로드
        print("\n1️⃣ CLOVA 분석 결과 로드 중...")
        analysis_data = self.load_clova_analysis()
        
        if analysis_data is None:
            print("❌ CLOVA 분석 결과 로드 실패")
            return False
        
        # 2. 종목명 추출
        print("\n2️⃣ 종목명 추출 중...")
        stock_names = self.extract_stock_names(analysis_data['result'])
        
        if not stock_names:
            print("❌ 추출된 종목이 없습니다.")
            return False
        
        print(f"📈 추출된 종목 수: {len(stock_names)}개")
        
        # 3. 주가 데이터 수집
        print("\n3️⃣ 주가 데이터 수집 중...")
        collected_data = self.collect_stock_data(stock_names)
        
        if not collected_data:
            print("❌ 수집된 데이터가 없습니다.")
            return False
        
        # 4. 데이터 저장
        print("\n4️⃣ 수집된 데이터 저장 중...")
        saved_path = self.save_collected_data(collected_data)
        
        if saved_path:
            print(f"\n🎉 추출 및 수집 완료!")
            print(f"📁 결과 파일: {saved_path}")
            print(f"📊 수집된 종목 수: {len(collected_data)}개")
            return True
        
        print("\n❌ 데이터 저장 실패")
        return False

def main():
    """메인 실행 함수"""
    extractor = StockExtractor()
    success = extractor.run_extraction()
    
    if success:
        print("\n✅ 전체 프로세스 완료!")
    else:
        print("\n❌ 프로세스 실패!")

if __name__ == "__main__":
    main() 