from collections import Counter

def analyze_and_print(raw_data, extracted_nouns, top_n=10):
    """
    수집된 원본 데이터와 추출된 명사 리스트를 바탕으로 통계를 내고 출력합니다.
    """
    if not raw_data:
        print("분석할 데이터가 없습니다.")
        return

    # 1. 전체 수집 건수 및 플랫폼별 통계 계산
    total_count = len(raw_data)
    
    # 리스트 컴프리헨션을 이용해 플랫폼 이름만 모은 뒤 Counter로 개수 집계
    platform_list = [item['platform'] for item in raw_data]
    platform_counts = Counter(platform_list)

    # ==========================================
    # 결과 화면 출력 포맷팅
    # ==========================================
    print("\n" + "=" * 50)
    print(" 📊 [실시간 키워드 분석 리포트]")
    print("=" * 50)
    print(f"▶ 총 분석 대상: {total_count}건의 게시물")
    
    # 플랫폼별 점유율 출력
    print("\n[플랫폼별 수집 현황]")
    for platform, count in platform_counts.most_common():
        percentage = (count / total_count) * 100
        print(f" - {platform}: {count}건 ({percentage:.1f}%)")

    # 2. 키워드 빈도 분석 (Top N)
    if not extracted_nouns:
        print("\n[알림] 형태소 분석 결과, 유의미한 단어가 추출되지 않았습니다.")
        print("=" * 50)
        return

    # 추출된 명사들의 등장 횟수를 계산하고 가장 많이 나온 순으로 정렬
    word_counts = Counter(extracted_nouns)
    top_words = word_counts.most_common(top_n)

    print(f"\n[연관 핵심 키워드 Top {top_n}]")
    for i, (word, count) in enumerate(top_words, 1):
        # 텍스트 길이에 맞춰 깔끔하게 정렬되도록 포맷팅
        print(f" {i:2d}위 | {word:<10} | {count}회 언급")
        
    print("=" * 50)