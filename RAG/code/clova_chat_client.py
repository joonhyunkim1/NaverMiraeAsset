#!/usr/bin/env python3
"""
HyperCLOVA X Chat Completion API 클라이언트
"""

import http.client
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

class ClovaChatClient:
    """HyperCLOVA X Chat Completion API 클라이언트"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("CLOVA_API_KEY", "")
        # Chat Completion 전용 Request ID (별도 환경변수 사용)
        self.request_id = os.getenv("CLOVA_CHAT_REQUEST_ID", "")
        
        # API 키에 Bearer 접두사 추가
        if not self.api_key.startswith('Bearer '):
            self.api_key = f'Bearer {self.api_key}'
        
        # HyperCLOVA X Chat Completion API 엔드포인트
        self.chat_url = "https://clovastudio.stream.ntruss.com/v3/chat-completions/HCX-005"
        
        self.headers = {
            "Authorization": self.api_key,
            "X-NCP-CLOVASTUDIO-REQUEST-ID": self.request_id,
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "text/event-stream"
        }
        
        print(f"HyperCLOVA X Chat API 클라이언트 초기화 완료")
        # print(f"API 키 설정: {'완료' if self.api_key else '미완료'}")
        # print(f"Chat Request ID 설정: {'완료' if self.request_id else '미완료'}")
    
    def create_chat_completion(self, 
                              messages: List[Dict[str, str]], 
                              max_tokens: int = 512,
                              temperature: float = 0.7,
                              top_p: float = 0.9) -> Optional[str]:
        """HyperCLOVA X Chat Completion API 호출"""
        try:
            # 요청 데이터 구성
            request_data = {
                "messages": messages,
                "maxTokens": max_tokens,
                "temperature": temperature,
                "topP": top_p,
                "topK": 0,
                "repetitionPenalty": 1.1,
                "stop": [],
                "includeAiFilters": True,
                "seed": 0
            }
            
            print(f"HyperCLOVA X Chat API 호출 중...")
            # print(f"Request ID: {self.request_id}")
            # print(f"API Key (처음 20자): {self.api_key[:20]}...")
            
            # HTTP 연결 및 요청
            conn = http.client.HTTPSConnection("clovastudio.stream.ntruss.com")
            conn.request('POST', '/v3/chat-completions/HCX-005', 
                        json.dumps(request_data), self.headers)
            
            response = conn.getresponse()
            
            print(f"응답 상태: {response.status} {response.reason}")
            
            if response.status == 200:
                final_answer = ""
                is_result_event = False
                print("🔍 응답 스트림 처리 중...")
                
                for line in response:
                    line_str = line.decode('utf-8').strip()
                    # print(f"📝 라인: {line_str}")  # 디버그 출력 주석처리

                    # event:result와 data:가 한 줄에 같이 있는 경우
                    if 'event:result' in line_str and 'data:' in line_str:
                        # data: 뒤의 JSON만 추출
                        data_idx = line_str.find('data:')
                        data_str = line_str[data_idx+5:].strip()
                        try:
                            data = json.loads(data_str)
                            if 'message' in data and 'content' in data['message']:
                                final_answer = data['message']['content']
                                print(f"✅ 최종 답변 추출: {final_answer[:100]}...")
                        except json.JSONDecodeError as e:
                            print(f"JSON 파싱 오류(한 줄): {e}")
                        break

                    # event:result만 있는 줄이면 다음 data:에서 추출
                    if line_str.startswith('event:result'):
                        is_result_event = True
                        print("📌 event:result 감지")
                        continue

                    # event:signal 또는 [DONE] 신호 감지 시 종료
                    if 'event:signal' in line_str or '"data":"[DONE]"' in line_str:
                        print("🛑 스트림 종료 신호 감지")
                        break

                    # event:result 다음의 data: 라인에서 최종 답변 추출
                    if is_result_event and line_str.startswith('data:'):
                        data_str = line_str[5:].strip()
                        try:
                            data = json.loads(data_str)
                            if 'message' in data and 'content' in data['message']:
                                final_answer = data['message']['content']
                                print(f"✅ 최종 답변 추출: {final_answer[:100]}...")
                        except json.JSONDecodeError as e:
                            print(f"JSON 파싱 오류(분리): {e}")
                        break

                conn.close()
                print(f"📊 최종 답변 길이: {len(final_answer)}")
                return final_answer.strip()
            else:
                print(f"Chat API 호출 실패: {response.status} {response.reason}")
                conn.close()
                return None
                
        except Exception as e:
            print(f"HyperCLOVA X Chat API 호출 오류: {e}")
            return None
    
    def create_rag_response(self, query: str, context_documents: List[Dict[str, Any]]) -> Optional[str]:
        """RAG용 응답 생성"""
        # 시스템 메시지
        system_message = """당신은 주식 시장 데이터에 대한 질문에 답변하는 전문가입니다. 
제공된 컨텍스트 정보를 바탕으로 금융 보고서 형태의 답변을 해주세요.
답변할 때는 한국어로 답변하고, 가능한 한 간결하고 명확하게 설명해주세요.
특히 주식 데이터를 답변할 때는 모든 관련 컬럼 정보를 포함하여 완전한 정보를 제공해주세요.
답변은 줄글로 작성해주세요."""

        # 컨텍스트 정보 구성
        context_text = "=== 참고 정보 ===\n"
        for i, doc in enumerate(context_documents, 1):
            context_text += f"[문서 {i}] {doc['content'][:1000]}...\n\n"
        
        # 사용자 메시지 구성
        user_message = f"{context_text}\n=== 질문 ===\n{query}\n\n위 정보를 바탕으로 답변해주세요."
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        return self.create_chat_completion(messages)
    
    def get_api_info(self) -> Dict[str, Any]:
        """API 정보를 반환합니다."""
        return {
            "api_key_set": bool(self.api_key),
            "request_id_set": bool(self.request_id),
            "chat_url": self.chat_url
        } 