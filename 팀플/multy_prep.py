from concurrent.futures import ProcessPoolExecutor
from bs4 import BeautifulSoup
import re

STOPWORD = ['강좌운영팀', 
            '교수소개', '교수', '교수팀',
            '참고교재', '교재소개', '교재',
            '평가 방법', '평가방법', '이수 기준', '평가점수', '이수증', '이수정보', '이수 정보', '이수기준',
            '운영일정', '강좌계획',
            '수강기간', '등록기간', '수강 방법', '수강방법']

def prep_single_data(name, summary):
    #이름 특문 제거
    name = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()

    #본문 html 파싱
    summary = BeautifulSoup(summary, 'html.parser').get_text(separator=' ', strip=True)
    #특수문자 제거, 공백 단일화
    summary = re.sub(r'[^가-힣a-zA-Z0-9\s.,!?]', ' ', summary)
    summary = re.sub(r'\s+', ' ', summary).strip()
    #불용어 제거
    for i in STOPWORD:
        summary = summary.partition(i)[0].strip()

    return name, summary

def prep_data(name_list, summary_list, worker=6):
    
    output = {'name':[], 'summary':[]}

    with ProcessPoolExecutor(max_workers=worker) as executor:
        result = executor.map(prep_single_data, name_list, summary_list)
        for name, summary in result:
            output['name'].append(name)
            output['summary'].append(summary)
    
    return output