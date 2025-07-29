#!/usr/bin/env python3
"""
토큰 사용량 분석 스크립트
"""

import pandas as pd
import json
from pathlib import Path

def analyze_krx_tokens():
    """KRX 데이터 토큰 사용량 분석"""
    print("=" * 60)
    print("📊 KRX 데이터 토큰 사용량 분석")
    print("=" * 60)
    
    # KRX CSV 파일 읽기
    csv_path = Path("../data/krx_daily_trading_20250725.csv")
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    
    print(f"📈 원본 데이터: {len(df)}행, {len(df.columns)}컬럼")
    print(f"📏 원본 파일 크기: {csv_path.stat().st_size:,} 바이트")
    
    # 현재 코드 방식으로 텍스트 변환
    text_parts = []
    
    # 파일명 정보
    text_parts.append(f"파일명: krx_daily_trading_20250725")
    text_parts.append(f"총 {len(df)}행, {len(df.columns)}컬럼")
    text_parts.append("")
    
    # KRX 데이터 특별 처리
    text_parts.append("=== KRX 일일거래정보 (등락률 상위 50%) ===")
    text_parts.append("")
    
    # 전체 데이터에서 거래대금 하위 60%와 등락률 하위 60%에서 겹치는 주식 제외
    df_processed = df.copy()
    
    # FLUC_RT 컬럼을 등락률로 사용
    df_processed['등락률'] = df_processed['FLUC_RT']
    df_processed['등락률_절대값'] = df_processed['등락률'].abs()
    
    print(f"📊 전체 데이터: {len(df_processed)}개 종목")
    
    # 거래대금 기준 하위 70% 찾기
    df_trading_value_sorted = df_processed.sort_values('ACC_TRDVAL', ascending=True)
    bottom_70_percent_trading = int(len(df_trading_value_sorted) * 0.7)
    low_trading_stocks = set(df_trading_value_sorted.head(bottom_70_percent_trading)['ISU_ABBRV'].tolist())
    
    # 등락률 기준 하위 70% 찾기 (절대값 기준)
    df_change_rate_sorted = df_processed.sort_values('등락률_절대값', ascending=True)
    bottom_70_percent_change = int(len(df_change_rate_sorted) * 0.7)
    low_change_stocks = set(df_change_rate_sorted.head(bottom_70_percent_change)['ISU_ABBRV'].tolist())
    
    # 겹치는 주식들 찾기
    overlapping_stocks = low_trading_stocks.intersection(low_change_stocks)
    
    print(f"📊 거래대금 하위 70%: {len(low_trading_stocks)}개 종목")
    print(f"📊 등락률 하위 70%: {len(low_change_stocks)}개 종목")
    print(f"📊 겹치는 종목: {len(overlapping_stocks)}개")
    
    # 겹치는 주식들을 제외한 최종 필터링
    df_final_filtered = df_processed[~df_processed['ISU_ABBRV'].isin(overlapping_stocks)]
    
    print(f"📊 최종 필터링 결과: {len(df_processed)}개 → {len(df_final_filtered)}개")
    
    # 각 종목별로 읽기 쉬운 형태로 변환
    processed_count = 0
    for idx, row in df_final_filtered.iterrows():
        stock_name = row.get('ISU_ABBRV', '')  # 실제 컬럼명
        stock_code = row.get('ISU_CD', '')     # 실제 컬럼명
        
        # 디버깅: 처음 몇 개만 출력
        if processed_count < 5:
            print(f"  디버깅: 종목명='{stock_name}', 종목코드='{stock_code}'")
        
        # 조건 수정: 종목명만 있으면 처리
        if stock_name:
            # 가격 정보
            open_price = row.get('TDD_OPNPRC', 0)
            high_price = row.get('TDD_HGPRC', 0)
            low_price = row.get('TDD_LWPRC', 0)
            close_price = row.get('TDD_CLSPRC', 0)
            trading_value = row.get('ACC_TRDVAL', 0)
            change_rate = row.get('등락률', 0.0)
            
            # 종목 정보를 읽기 쉬운 형태로 구성
            stock_info = f"종목명: {stock_name}, 시가: {open_price}, 고가: {high_price}, 저가: {low_price}, 종가: {close_price}, 거래대금: {trading_value}, 등락률: {change_rate:.2f}"
            text_parts.append(stock_info)
            processed_count += 1
    
    print(f"📊 실제 처리된 종목 수: {processed_count}개")
    
    text_parts.append("")
    text_parts.append(f"총 {len(df_final_filtered)}개 종목의 거래 정보 (등락률 상위 50%)")
    
    # 최종 텍스트 생성
    final_text = "\n".join(text_parts)
    
    print(f"📏 변환된 텍스트 크기: {len(final_text):,} 문자")
    print(f"📊 예상 토큰 수: {int(len(final_text) * 1.3):,} 토큰 (한글 기준)")
    
    return len(final_text), len(df_final_filtered)

def analyze_news_tokens():
    """뉴스 데이터 토큰 사용량 분석 (30개 기사 시뮬레이션)"""
    print("\n" + "=" * 60)
    print("📰 뉴스 데이터 토큰 사용량 분석 (30개 기사)")
    print("=" * 60)
    
    # 뉴스 JSON 파일 읽기
    json_path = Path("../data/naver_news_recent_3.json")
    with open(json_path, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    print(f"📈 원본 데이터: {len(news_data.get('items', []))}개 뉴스 기사")
    print(f"📏 원본 파일 크기: {json_path.stat().st_size:,} 바이트")
    
    # 현재 코드 방식으로 텍스트 변환 (30개 기사 시뮬레이션)
    total_text_length = 0
    article_count = 0
    
    articles = news_data.get('items', [])
    
    # 30개 기사로 확장 시뮬레이션
    expanded_articles = []
    for i in range(30):
        if i < len(articles):
            # 기존 기사 사용
            expanded_articles.append(articles[i])
        else:
            # 기존 기사를 복제하여 시뮬레이션
            base_article = articles[i % len(articles)]
            simulated_article = {
                'title': f"{base_article.get('title', '')} (기사 {i+1})",
                'description': f"{base_article.get('description', '')} - 추가 분석 내용이 포함된 확장된 뉴스 기사입니다.",
                'pubDate': base_article.get('pubDate', '')
            }
            expanded_articles.append(simulated_article)
    
    print(f"📰 확장된 뉴스 기사: {len(expanded_articles)}개")
    
    for i, article in enumerate(expanded_articles):
        # 기사 제목
        title = article.get('title', '')
        title_text = f"제목: {title}" if title else ""
        
        # 기사 내용 (설명)
        description = article.get('description', '')
        if description:
            # HTML 태그 제거
            import re
            clean_description = re.sub(r'<[^>]+>', '', description)
            content_text = f"내용: {clean_description}"
        else:
            content_text = ""
        
        # 발행일
        pub_date = article.get('pubDate', '')
        date_text = f"발행일: {pub_date}" if pub_date else ""
        
        # 전체 텍스트
        article_text = "\n".join([title_text, content_text, date_text])
        total_text_length += len(article_text)
        article_count += 1
    
    print(f"📏 변환된 텍스트 총 크기: {total_text_length:,} 문자")
    print(f"📊 예상 토큰 수: {int(total_text_length * 1.3):,} 토큰 (한글 기준)")
    print(f"📰 처리된 기사 수: {article_count}개")
    
    return total_text_length, article_count

def main():
    """메인 분석 함수"""
    print("🚀 토큰 사용량 분석 시작")
    print("=" * 60)
    
    # KRX 데이터 분석
    krx_chars, krx_stocks = analyze_krx_tokens()
    
    # 뉴스 데이터 분석
    news_chars, news_articles = analyze_news_tokens()
    
    # 전체 분석
    print("\n" + "=" * 60)
    print("📋 전체 토큰 사용량 요약")
    print("=" * 60)
    
    total_chars = krx_chars + news_chars
    total_tokens = total_chars * 1.3  # 한글 기준 토큰 수 추정
    
    print(f"📊 KRX 데이터: {krx_chars:,} 문자 ({krx_stocks}개 종목)")
    print(f"📰 뉴스 데이터: {news_chars:,} 문자 ({news_articles}개 기사)")
    print(f"📏 전체 텍스트: {total_chars:,} 문자")
    print(f"🎯 예상 토큰 수: {int(total_tokens):,} 토큰")
    
    # CLOVA API 제한 확인
    clova_limit = 120000  # 12만자 제한
    
    print(f"\n🔍 CLOVA API 제한 분석:")
    print(f"📏 CLOVA 제한: {clova_limit:,} 문자")
    print(f"📊 현재 사용량: {total_chars:,} 문자")
    
    if total_chars > clova_limit:
        excess = total_chars - clova_limit
        print(f"⚠️ 제한 초과: {excess:,} 문자 ({excess/clova_limit*100:.1f}% 초과)")
        print(f"💡 청크 분할 필요: {excess//100000 + 1}개 청크로 분할")
    else:
        remaining = clova_limit - total_chars
        print(f"✅ 제한 내 사용: {remaining:,} 문자 여유")
    
    print("\n🎉 토큰 사용량 분석 완료!")

if __name__ == "__main__":
    main() 