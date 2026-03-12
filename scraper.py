import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib.parse

# 1. 오픈 커뮤니티 스크래퍼 (예: 디시인사이드 직접 크롤링)
class DCinsideScraper:
    def __init__(self, keyword):
        self.keyword = keyword
        # 봇 탐지 우회를 위한 User-Agent 위장
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 디시인사이드 통합검색 URL (검색어 인코딩 적용)
        self.base_url = f"https://search.dcinside.com/post/q/{urllib.parse.quote(keyword)}"

    async def fetch(self, session):
        print(f"[DCinside] '{self.keyword}' 검색 시작...")
        results = []
        # 현재 시간 기준 24시간 전 타임스탬프 계산
        time_limit = datetime.now() - timedelta(hours=24)

        try:
            # 비동기 HTTP GET 요청
            async with session.get(self.base_url, headers=self.headers, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # HTML 파싱 (아래 선택자는 가상의 구조이며, 실제 사이트 구조 변동 시 수정 필요)
                    posts = soup.select('ul.sch_result_list > li')
                    for post in posts:
                        title_el = post.select_one('a.tit_txt')
                        date_el = post.select_one('span.date_time')
                        
                        if title_el and date_el:
                            title = title_el.text.strip()
                            try:
                                # 문자열을 datetime 객체로 변환하여 24시간 이내인지 검증
                                post_time = datetime.strptime(date_el.text.strip(), '%Y-%m-%d %H:%M:%S')
                                if post_time >= time_limit:
                                    results.append({
                                        'platform': 'DCinside',
                                        'title': title,
                                        'timestamp': post_time.isoformat()
                                    })
                            except ValueError:
                                continue
                else:
                    print(f"[DCinside] HTTP 에러 발생: {response.status}")
        except Exception as e:
            print(f"[DCinside] 수집 중 예외 발생: {e}")
        
        return results

# 2. 네이버 오픈 API 스크래퍼 (안정적인 대량 수집)
class NaverAPIScraper:
    def __init__(self, keyword, client_id, client_secret):
        self.keyword = keyword
        self.client_id = client_id
        self.client_secret = client_secret
        # 네이버 블로그 검색 API (sort=date 속성으로 최신순 정렬)
        self.url = f"https://openapi.naver.com/v1/search/blog.json?query={urllib.parse.quote(keyword)}&display=100&sort=date"

    async def fetch(self, session):
        print(f"[Naver API] '{self.keyword}' 검색 시작...")
        results = []
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        time_limit = datetime.now() - timedelta(hours=24)

        try:
            async with session.get(self.url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json() # JSON 응답 파싱
                    items = data.get('items', [])
                    
                    for item in items:
                        # API 응답의 <b> 태그 등 불필요한 HTML 요소 1차 제거
                        raw_title = item.get('title', '')
                        clean_title = BeautifulSoup(raw_title, "html.parser").text
                        
                        post_date = item.get('postdate', '') # YYYYMMDD 형태 반환
                        if post_date:
                            post_time = datetime.strptime(post_date, '%Y%m%d')
                            # 날짜 비교 로직 적용
                            # API 데이터에 시간 정보가 없으므로(00:00 기준), 날짜(date)만 비교하여 어제/오늘 데이터를 모두 포함
                            if post_time.date() >= time_limit.date():
                                results.append({
                                    'platform': 'Naver Blog',
                                    'title': clean_title,
                                    'timestamp': post_time.isoformat()
                                })
                else:
                    print(f"[Naver API] 상태 코드 에러: {response.status}")
        except Exception as e:
            print(f"[Naver API] 통신 오류: {e}")
        
        return results

# 3. 비동기 실행을 통제하는 코어 함수
async def run_collectors(keyword, naver_id, naver_secret):
    print(f"\n=== '{keyword}' 관련 24시간 내 데이터 수집 프로세스 가동 ===")
    
    # 단일 aiohttp 세션을 생성하여 여러 스크래퍼가 자원을 효율적으로 공유하게 함
    async with aiohttp.ClientSession() as session:
        dc_scraper = DCinsideScraper(keyword)
        naver_scraper = NaverAPIScraper(keyword, naver_id, naver_secret)
        
        # asyncio.gather를 통해 두 스크래퍼를 동시에(병렬로) 실행 대기열에 올림
        # 추후 에펨코리아, 보배드림 등 새로운 클래스를 만들면 이 리스트에 추가만 하면 됨
        tasks = [
            dc_scraper.fetch(session),
            naver_scraper.fetch(session)
        ]
        
        # 병렬 작업이 모두 끝날 때까지 대기 후 결과 병합
        collected_results = await asyncio.gather(*tasks)
        
        # 2차원 리스트 형태의 결과를 1차원으로 평탄화(Flatten)
        all_data = []
        for res in collected_results:
            all_data.extend(res)
            
        return all_data
