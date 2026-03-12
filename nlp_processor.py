import re
from konlpy.tag import Okt

def clean_text(text):
    """
    정규표현식을 사용하여 URL, 특수문자 등 불필요한 노이즈를 제거합니다.
    """
    # 1. URL 제거 (http:// 또는 https:// 로 시작하는 문자열)
    text = re.sub(r'http\S+', '', text)
    # 2. 한글, 영문, 숫자, 공백을 제외한 모든 특수문자 제거
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    # 3. 여러 개의 공백을 하나의 공백으로 압축
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def process_nlp(raw_data, extra_stopwords=None):
    """
    수집된 원시 데이터에서 텍스트를 정제하고 유의미한 명사만 추출합니다.
    """
    print("\n[NLP] 텍스트 정제 및 형태소 분석을 시작합니다...")
    
    # Okt(Open Korean Text) 분석기 초기화
    # 설치 및 설정이 비교적 간편하여 널리 쓰이는 분석기입니다.
    okt = Okt()
    
    # 분석 가치를 흐리는 기본 불용어(Stopwords) 사전
    stopwords = ['진짜', '너무', '오늘', '그냥', '이거', '있는', '합니다', '입니다', 'ㅋㅋ', 'ㅎㅎ']
    if extra_stopwords:
        stopwords.extend(extra_stopwords)
        
    final_words = []
    
    for item in raw_data:
        # 현재는 제목(title)만 수집했으므로 제목을 대상으로 분석
        # 추후 본문(content)을 수집한다면 text = item['title'] + " " + item['content'] 로 확장 가능
        text = item.get('title', '')
        
        if not text:
            continue
            
        # 1차: 노이즈 제거
        cleaned_text = clean_text(text)
        
        # 2차: 형태소 분석을 통해 명사(Noun) 리스트 추출
        nouns = okt.nouns(cleaned_text)
        
        # 3차: 필터링 (1글자 단어 제거 및 불용어 제거)
        for noun in nouns:
            if len(noun) > 1 and noun not in stopwords:
                final_words.append(noun)
                
    return final_words