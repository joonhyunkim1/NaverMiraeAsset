#!/usr/bin/env python3
"""
CLOVA 세그멘테이션 API 테스트 스크립트
"""

from clova_segmentation import ClovaSegmentationClient

def test_segmentation():
    """CLOVA 세그멘테이션 API 테스트"""
    print("=" * 50)
    print("CLOVA 세그멘테이션 API 테스트")
    print("=" * 50)
    
    # 세그멘테이션 클라이언트 초기화
    segmentation_client = ClovaSegmentationClient()
    
    # API 정보 확인
    api_info = segmentation_client.get_api_info()
    print(f"\nAPI 정보:")
    print(f"  API 키 설정: {'완료' if api_info['api_key_set'] else '미완료'}")
    print(f"  Request ID 설정: {'완료' if api_info['request_id_set'] else '미완료'}")
    
    if not api_info['api_key_set'] or not api_info['request_id_set']:
        print("❌ API 키 또는 Request ID가 설정되지 않았습니다!")
        return
    
    # 테스트 텍스트
    test_text = """
    삼성전자는 2024년 1분기 실적을 발표했다. 매출은 전년 동기 대비 12% 증가한 71조원을 기록했다.
    영업이익은 6.6조원으로 전년 동기 대비 15% 증가했다. 메모리 반도체 시장의 회복과 AI 관련 수요 증가가 주요 성장 동력이었다.
    특히 HBM(고대역폭 메모리)과 DDR5 수요가 급증하면서 메모리 사업부의 실적이 크게 개선되었다.
    시스템 반도체 사업부도 AI 칩과 자동차 반도체 수요 증가로 양호한 실적을 보였다.
    향후 AI 시장 확대와 메모리 시장 회복세가 지속될 것으로 전망된다.
    """
    
    print(f"\n테스트 텍스트:")
    print(f"길이: {len(test_text)}자")
    print(f"내용: {test_text[:100]}...")
    
    # 세그멘테이션 테스트
    print(f"\n세그멘테이션 테스트 (max_length=200, overlap=30)...")
    
    chunks = segmentation_client.segment_text(
        text=test_text,
        max_length=200,
        overlap=30
    )
    
    if chunks:
        print(f"✅ 세그멘테이션 성공!")
        print(f"총 {len(chunks)}개의 청크로 분할됨")
        
        for i, chunk in enumerate(chunks, 1):
            print(f"\n청크 {i}:")
            print(f"길이: {len(chunk)}자")
            print(f"내용: {chunk}")
    else:
        print("❌ 세그멘테이션 실패!")
    
    print("\n테스트 완료!")

if __name__ == "__main__":
    test_segmentation() 