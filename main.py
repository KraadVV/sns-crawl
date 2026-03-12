import asyncio
# 동일한 폴더에 있는 scraper.py 파일에서 수집 실행 함수를 가져옵니다.
from scraper import run_collectors

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
        # TODO: 3번(NLP 텍스트 정제) 및 4번(통계 분석/시각화) 모듈 호출 영역
        # 예: cleaned_words = process_nlp(raw_data)
        #     show_statistics(cleaned_words)
        # =================================================================
        
    except Exception as e:
        print(f"\n[오류 발생] 프로그램 실행 중 문제가 발생했습니다: {e}")

# 파이썬 스크립트가 직접 실행될 때만 main() 함수를 호출합니다.
if __name__ == "__main__":
    main()