# -*- coding: utf-8 -*-

import http.client
import json
import os
from dotenv import load_dotenv


class CompletionExecutor:
    def __init__(self, host, api_key, request_id):
        self._host = host
        self._api_key = api_key
        self._request_id = request_id

    def _send_request(self, completion_request):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': self._api_key,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id
        }

        conn = http.client.HTTPSConnection(self._host)
        conn.request('POST', '/v1/api-tools/embedding/v2', json.dumps(completion_request), headers)
        response = conn.getresponse()
        result = json.loads(response.read().decode(encoding='utf-8'))
        conn.close()
        return result

    def execute(self, completion_request):
        res = self._send_request(completion_request)
        if res['status']['code'] == '20000':
            return res['result']
        else:
            return 'Error'


if __name__ == '__main__':
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
    api_key = os.getenv("CLOVA_API_KEY", "")
    request_id = os.getenv("CLOVA_REQUEST_ID", "")

    # API 키에 Bearer 접두사 추가
    if not api_key.startswith('Bearer '):
        api_key = f'Bearer {api_key}'

    completion_executor = CompletionExecutor(
        host='clovastudio.stream.ntruss.com',
        api_key=api_key,
        request_id=request_id
    )

    request_data = json.loads("""{
  "text" : "input text"
}""", strict=False)

    response_text = completion_executor.execute(request_data)
    print("요청 데이터:")
    print(request_data)
    print("\n응답 결과:")
    print(response_text) 