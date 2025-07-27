
import FinanceDataReader as fdr
import pandas as pd
from datetime import timedelta
from dateutil.parser import parse
import requests
import json
import uuid

# 📌 Clova API 설정
API_KEY = "nv-ebdc692e9bc341dfbfefc1f145bbefb3FS3J"
API_URL = "https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005"

# 📌 Function Calling 정의
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_summary",
            "description": "특정 종목의 일간/주간/월간 주가 요약 정보를 조회할 수 있습니다. 종목명(예: 삼성전자) 또는 종목코드(005930) 모두 사용 가능합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "조회할 종목코드 또는 종목명입니다. 예: '005930' 또는 '삼성전자'"
                    },
                    "base_date": {
                        "type": "string",
                        "description": "기준 날짜입니다. YYYY-MM-DD 형식으로 입력하세요. 예: '2025-07-23'"
                    },
                    "period": {
                        "type": "string",
                        "enum": ["daily", "weekly", "monthly"],
                        "description": "조회 기간을 지정합니다. daily(일간), weekly(주간), monthly(월간) 중 선택"
                    }
                },
                "required": ["ticker", "base_date", "period"]
            }
        }
    }
]

# 📌 종목명 → 코드 변환
def get_stock_code(kor_name):
    try:
        df = fdr.StockListing('KRX')
        match = df[df['Name'] == kor_name]
        if not match.empty:
            return match.iloc[0]['Code']
    except Exception as e:
        print(f"[코드 변환 오류] {e}")
    return None

# 📌 최근 거래일 찾기 (휴장일 처리)
def find_last_trading_day(base_date, max_days_back=10):
    """
    주어진 날짜에서 최근 거래일을 찾는 함수
    max_days_back: 최대 몇 일 전까지 검색할지
    """
    current_date = base_date
    
    for i in range(max_days_back):
        # 주말이 아닌 경우에만 체크
        if current_date.weekday() < 5:  # 평일 (월=0, 화=1, ..., 금=4)
            try:
                # 간단한 데이터 존재 여부 체크 (KOSPI 지수로 확인)
                test_df = fdr.DataReader('KS11', current_date.strftime("%Y-%m-%d"), current_date.strftime("%Y-%m-%d"))
                if not test_df.empty:
                    return current_date
            except:
                pass
        
        current_date = current_date - timedelta(days=1)
    
    return None

# 📌 주가 요약 함수 (개선된 휴장일 처리)
def get_stock_summary(ticker, base_date, period):
    # 종목명을 코드로 변환
    if not ticker.isdigit():
        code = get_stock_code(ticker)
        if code:
            ticker = code
        else:
            return {"error": f"'{ticker}'에 대한 종목코드를 찾을 수 없습니다."}

    try:
        base = parse(base_date).date()
        today = pd.Timestamp.now().date()
    except Exception:
        return {"error": f"날짜 형식을 인식할 수 없습니다: {base_date}"}

    # 📌 기간별 처리 로직
    if period == "daily":
        # 일간 조회 시 휴장일 처리
        if base.weekday() >= 5:  # 주말인 경우
            last_trading_day = find_last_trading_day(base)
            if last_trading_day:
                weekday_name = ['월요일', '화요일', '수요일', '목요일', '금요일'][last_trading_day.weekday()]
                print(f"🔄 휴장일 감지: {base_date} → {last_trading_day.strftime('%Y-%m-%d')} 로 조정")
                # 조정된 날짜로 재귀 호출
                adjusted_result = get_stock_summary(ticker, last_trading_day.strftime('%Y-%m-%d'), period)
                # 안내 메시지 추가
                if "error" not in adjusted_result:
                    adjusted_result["info_message"] = f"{base_date}은 주말(휴장일)입니다."
                    adjusted_result["suggestion"] = f"최근 거래일인 {last_trading_day.strftime('%Y-%m-%d')} ({weekday_name}) 데이터로 조회했습니다."
                return adjusted_result
            else:
                return {"error": "최근 10일 내 거래일을 찾을 수 없습니다."}
        
        start = end = base
        period_desc = "일간"
        
    elif period == "weekly":
        # 주간 처리: 해당 주의 월요일부터 금요일까지
        week_start = base - timedelta(days=base.weekday())  # 해당 주 월요일
        week_end = week_start + timedelta(days=4)  # 해당 주 금요일
        
        # 현재 날짜와 비교하여 실제 조회 끝날짜 결정
        if today >= week_end:
            # 해당 주가 완전히 지난 경우: 금요일까지
            actual_end = week_end
        else:
            # 해당 주가 진행 중인 경우: 오늘까지 (단, 주말이면 금요일까지)
            if today.weekday() >= 5:  # 주말
                actual_end = week_start + timedelta(days=4)  # 금요일
            else:
                actual_end = today
            
        start = week_start
        end = actual_end
        period_desc = f"주간 ({week_start.strftime('%m/%d')} ~ {actual_end.strftime('%m/%d')})"
        
        # 주말에 "이번주" 요청 시 안내 메시지
        weekend_info = None
        weekend_suggestion = None
        if base.weekday() >= 5:  # 주말에 요청한 경우
            weekend_info = f"주말에 이번주 주가를 요청하셨습니다."
            weekend_suggestion = f"이번주 거래일({week_start.strftime('%Y-%m-%d')} ~ {actual_end.strftime('%Y-%m-%d')}) 데이터로 조회했습니다."
        
    elif period == "monthly":
        # 월간 처리
        month_start = base.replace(day=1)
        month_end = (month_start + pd.DateOffset(months=1)) - pd.DateOffset(days=1)
        
        if base <= today:
            end = min(base, month_end.date())
        else:
            end = month_end.date()
            
        start = month_start
        period_desc = f"월간 ({month_start.strftime('%Y년 %m월')})"
    else:
        return {"error": "period는 daily, weekly, monthly 중 하나여야 합니다."}

    # 📌 안내 메시지가 있는 경우 재귀 호출 (제거됨 - 이미 위에서 처리)
        
    # 📌 주식 데이터 조회
    try:
        df = fdr.DataReader(ticker, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        if df.empty:
            # 휴장일 상세 안내
            if period == "daily":
                last_trading_day = find_last_trading_day(base)
                if last_trading_day:
                    suggestion_msg = f"최근 거래일 {last_trading_day.strftime('%Y-%m-%d')} 데이터를 확인해보세요."
                else:
                    suggestion_msg = "최근 거래일을 찾을 수 없습니다."
                return {"error": f"{base_date}은 휴장일입니다. {suggestion_msg}"}
            else:
                return {"error": f"해당 기간({start} ~ {end})에 거래 정보가 없습니다."}
    except Exception as e:
        return {"error": f"주식 데이터 조회 중 오류가 발생했습니다: {str(e)}"}

    # 📌 주요 지표 계산
    open_price = float(df.iloc[0]["Open"])
    close_price = float(df.iloc[-1]["Close"])
    high_price = float(df["High"].max())
    low_price = float(df["Low"].min())
    volume = int(df["Volume"].sum())
    value = int((df["Open"] * df["Volume"]).sum())
    change_rate = round((close_price - open_price) / open_price * 100, 2)

    result = {
        "ticker": ticker,
        "start_date": start.strftime('%Y-%m-%d'),
        "end_date": end.strftime('%Y-%m-%d'),
        "base_date": base.strftime('%Y-%m-%d'),
        "period": period,
        "period_desc": period_desc,
        "open": open_price,
        "close": close_price,
        "high": high_price,
        "low": low_price,
        "volume": volume,
        "value": value,
        "change_rate": change_rate,
        "trading_days": len(df)
    }
    
    # 📌 휴장일 처리 안내 메시지 추가
    if period == "weekly" and "weekend_info" in locals() and weekend_info:
        result["info_message"] = weekend_info
        result["suggestion"] = weekend_suggestion
        
    return result

# 📌 구조화된 텍스트 형태로 tool 결과 포맷팅 (개선)
def format_tool_result(result):
    if "error" in result:
        return f"❌ 오류 발생: {result['error']}"
    
    # 📌 휴장일 처리 안내 메시지
    info_text = ""
    if "info_message" in result:
        info_text += f"ℹ️ {result['info_message']}\n"
    if "suggestion" in result:
        info_text += f"💡 {result['suggestion']}\n"
    if info_text:
        info_text += "\n"
    
    start_date = result['start_date']
    end_date = result['end_date']
    period_desc = result['period_desc']
    trading_days = result['trading_days']
    
    # 기간 표시 방식 개선
    if start_date == end_date:
        date_range = f"{start_date}"
        period_info = f"{period_desc}"
    else:
        date_range = f"{start_date} ~ {end_date}"
        period_info = f"{period_desc} ({trading_days}일간 거래)"
    
    return f"""{info_text}📊 주식 정보 조회 결과

🏢 종목코드: {result['ticker']}
📅 조회기간: {date_range} ({period_info})
💰 시가: {result['open']:,}원 (첫 거래일)
💰 종가: {result['close']:,}원 (마지막 거래일)
📈 고가: {result['high']:,}원 (기간 내 최고가)
📉 저가: {result['low']:,}원 (기간 내 최저가)
📊 거래량: {result['volume']:,}주 (기간 합계)
💵 거래대금: {result['value']:,}원 (기간 합계)
{"📈" if result['change_rate'] > 0 else "📉" if result['change_rate'] < 0 else "➡️"} 등락률: {result['change_rate']:+.2f}% (시가 대비 종가)

⚠️ 중요 정보:
- 실제 거래일 기준: {start_date} ~ {end_date} ({trading_days}일)
- 주간 조회 시: 해당 주의 실제 거래된 날짜까지만 포함
- 월간 조회 시: 해당 월의 실제 거래된 날짜까지만 포함
- 연도: {parse(result['start_date']).year}년 데이터임을 명확히 표기하세요"""

# 📌 tool 호출 처리
def process_tool_calls(tool_name, arguments):
    tool_map = {
        "get_stock_summary": get_stock_summary,
    }
    func = tool_map.get(tool_name)
    if func:
        return func(**arguments)
    else:
        return {"error": f"알 수 없는 함수: {tool_name}"}

# 📌 Clova 요청 함수
def chat_completions(messages):
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
        print(f"🔍 요청 정보:")
        print(f"📡 URL: {API_URL}")
        print(f"🆔 REQUEST_ID: {request_id}")
        print(f"📝 Messages 수: {len(messages)}")
        
        # 요청 데이터 검증
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            print(f"  Message {i}: role={role}")
            
            if role == 'tool':
                if 'toolCallId' not in msg:
                    print(f"    ❌ toolCallId 누락!")
                    return {"error": "tool role 메시지에 toolCallId가 없습니다"}
            
            if role == 'assistant' and 'toolCalls' in msg:
                tool_calls = msg['toolCalls']
                if not isinstance(tool_calls, list):
                    print(f"    ❌ toolCalls가 리스트가 아님!")
                    return {"error": "toolCalls는 리스트여야 합니다"}
        
        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"📊 응답 상태: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ 오류 응답:")
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Body: {response.text}")
            
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 예외: {str(e)}")
        return {"error": f"API 요청 중 오류 발생: {str(e)}"}

# 📌 메인 실행
if __name__ == "__main__":
    user_input = input("📥 사용자 질문을 입력하세요: ")
    messages = [{"role": "user", "content": user_input}]

    print(f"👤 사용자: {user_input}")
    print("🤖 처리 중...")

    # Step 1: 첫 번째 요청 (Function Calling 판단)
    first_response = chat_completions(messages)
    
    if "error" in first_response:
        print(f"🛑 API 오류: {first_response['error']}")
        exit()

    # 응답 구조 확인
    result_message = first_response.get("result", {}).get("message", {})
    tool_calls = result_message.get("toolCalls", [])

    if tool_calls:
        print("🔧 함수 호출이 필요한 요청으로 판단됨")
        
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
                exit()

        print(f"⚙️  함수 실행: {tool_name}")
        print(f"📝 매개변수: {arguments}")

        # 실제 함수 실행
        tool_result = process_tool_calls(tool_name, arguments)

        if "error" in tool_result:
            print(f"🛑 함수 실행 오류: {tool_result['error']}")
            exit()

        # 결과를 구조화된 텍스트로 포맷팅
        formatted_result = format_tool_result(tool_result)
        print(f"\n✅ 함수 실행 결과:")
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
            "content": formatted_result[:2000]  # 내용 길이 제한 (2000자)
        }
        
        # 메시지 유효성 검사
        print(f"🔍 Assistant 메시지 검증:")
        print(f"  toolCall ID: {tool_call['id']}")
        print(f"  toolCall 함수: {tool_call['function']['name']}")
        
        print(f"🔍 Tool 메시지 검증:")
        print(f"  toolCallId: {tool_message['toolCallId']}")
        print(f"  content 길이: {len(tool_message['content'])}")
        
        messages.append(assistant_message)
        messages.append(tool_message)

        # Step 4: 최종 응답 생성 (개선된 시스템 프롬프트)
        print("\n🤖 최종 응답 생성 중...")
        
        # 개선된 시스템 프롬프트
        system_message = {
            "role": "system",
            "content": """당신은 주식 분석 전문가입니다. 다음 규칙을 따라 응답하세요:

1. 날짜와 연도를 정확히 표기하세요. 특히 2025년 데이터는 반드시 2025년으로 명시하세요.
2. 주간 데이터의 경우 "YYYY년 MM월 DD일 ~ YYYY년 MM월 DD일 주간 주가 요약" 형식으로 표현하세요.
3. 월간 데이터의 경우 "YYYY년 MM월 월간 주가 요약" 형식으로 표현하세요.
4. 제공된 데이터의 연도를 절대 변경하지 마세요.
5. 휴장일 처리 안내 메시지가 있다면 반드시 언급해주세요.
6. 주말에 주간 데이터를 요청한 경우, 해당 주의 거래일 범위를 명확히 설명해주세요.
7. **중요**: 조회기간(start_date ~ end_date)을 반드시 첫 번째 줄에 명시하세요. 예: "2025년 7월 21일 ~ 2025년 7월 25일 주간"
8. 간결하고 정확한 정보 전달에 집중하세요."""
        }
        
        # 시스템 메시지를 첫 번째로 추가
        final_messages = [system_message] + messages
        final_response = chat_completions(final_messages)

        if "error" in final_response:
            print(f"🛑 최종 응답 생성 오류: {final_response['error']}")
            exit()

        # 최종 응답 출력
        final_result = final_response.get("result", {})
        if "message" in final_result and "content" in final_result["message"]:
            print(f"\n🎯 클로바의 최종 응답:")
            print(final_result["message"]["content"])
        else:
            print("🛑 최종 응답을 받을 수 없습니다:")
            print(json.dumps(final_response, indent=2, ensure_ascii=False))

    else:
        # Function Calling이 불필요한 일반 응답
        final_result = first_response.get("result", {})
        if "message" in final_result and "content" in final_result["message"]:
            print(f"\n🎯 클로바의 응답:")
            print(final_result["message"]["content"])
        else:
            print("🛑 응답을 처리할 수 없습니다:")
            print(json.dumps(first_response, indent=2, ensure_ascii=False))