import asyncio
from nlp_processor import process_nlp

# 동일한 폴더에 있는 scraper.py 파일에서 수집 실행 함수를 가져옵니다.
from scraper import run_collectors

from analytics import analyze_and_print


def main():
    print("=" * 50)
    print("  SNS/커뮤니티 실시간 키워드 트렌드 분석기")
    print("=" * 50)
    
    # 1. 사용자 입력 받기
    keyword = input("\n분석할 키워드를 입력하세요: ").strip()
    
    if not keyword:
        print("키워드가 입력되지 않았습니다. 프로그램을 종료합니다.")
        return

    # [주의] 실제 사용 시에는 소스 코드에 직접 키를 넣기보다, 
    # .env 파일이나 config.json 같은 별도의 설정 파일로 분리하는 것이 안전합니다.
    NAVER_CLIENT_ID = "YlLT2bOR4jH1nhxGwdU0e"         
    NAVER_CLIENT_SECRET = "u2r82Yh4j8" 
    
    print(f"\n▶ '{keyword}' 관련 최근 24시간 데이터를 수집합니다. 잠시만 기다려주세요...")
    
    # 2. 비동기 수집 모듈(scraper.py) 가동
    try:
        # asyncio.run()을 통해 비동기 함수를 동기적 흐름에서 실행합니다.
        raw_data = asyncio.run(run_collectors(keyword, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET))
        
        if not raw_data:
            print("\n수집된 데이터가 없습니다. 다른 키워드로 시도해 보세요.")
            return

        # 3. 수집 결과 요약 출력
        print(f"\n✔ 수집 완료! (총 {len(raw_data)}건)")
        print("-" * 50)
        
        # 데이터가 잘 들어왔는지 상위 5개만 샘플로 확인
        for i, data in enumerate(raw_data[:5], 1):
            print(f"{i}. [{data['platform']}] {data['title']} ({data['timestamp']})")
            
        print("-" * 50)
        
        # =================================================================
        print("\n[선택] 분석 결과에서 제외하고 싶은 단어가 있다면 입력해 주세요.")
        print("💡 팁: 검색어 자체나 너무 뻔한 단어를 제외하면 숨겨진 트렌드가 잘 보입니다.")
        print("(예: 해킹, 피싱, 뉴스 / 뺄 단어가 없다면 그냥 엔터를 누르세요)")
        
        stopword_input = input("▶ 제외할 단어: ").strip()
        
        custom_stopwords = []
        if stopword_input:
            # 쉼표(,)나 띄어쓰기를 기준으로 단어를 쪼개서 리스트로 만듭니다.
            import re
            custom_stopwords = [word.strip() for word in re.split(r'[,\s]+', stopword_input) if word.strip()]
            print(f"[*] 적용된 제외 단어 필터: {custom_stopwords}")
        
        # 4. NLP 정제 모듈 가동
        extracted_nouns = process_nlp(raw_data, custom_stopwords)
        
        # 5. [추가된 부분] 통계 분석 및 최종 리포트 출력 모듈 가동
        # top_n 변수를 조절하면 10위, 20위 등 원하는 만큼 순위를 볼 수 있습니다.
        analyze_and_print(raw_data, extracted_nouns, top_n=15)
        print(f"\n✔ 텍스트 정제 완료! (총 {len(extracted_nouns)}개의 유의미한 단어 추출)")        
        # =================================================================
        
    except Exception as e:
        print(f"\n[오류 발생] 프로그램 실행 중 문제가 발생했습니다: {e}")

# 파이썬 스크립트가 직접 실행될 때만 main() 함수를 호출합니다.
if __name__ == "__main__":
    main()