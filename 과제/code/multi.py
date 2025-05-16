#날짜 요청 관련
from habanero import Crossref
import pandas as pd
import numpy as np
import multiprocessing as mp
#텍스트 전처리 관련
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

# Crossref 객체 생성 (User-Agent 설정)
cr = Crossref(
    ua_string="korean_undergraduate_project (mailto:topaz11100@gmail.com)",
    mailto="topaz11100@gmail.com"
)
# 날짜 요청 함수 (단락평가 포함, 실패 방지)
def fetch_date(doi):
    try:
        paper = cr.works(ids = doi)['message']

        if 'published-online' in paper and len(paper['published-online']['date-parts'][0]) >= 2:
            date = paper['published-online']['date-parts'][0]
        elif 'published-print' in paper and len(paper['published-print']['date-parts'][0]) >= 2:
            date = paper['published-print']['date-parts'][0]
        elif 'issued' in paper and len(paper['issued']['date-parts'][0]) >= 2:
            date = paper['issued']['date-parts'][0]
        else:
            return None
        return pd.Timestamp(year=date[0], month=date[1], day=1) 
    except:
        return None
# 발행날짜 추가
def add_date(chunk):
    chunk['Date'] = chunk['DOI'].apply(fetch_date)
    chunk = chunk.drop(columns = ['DOI'])
    chunk = chunk.dropna()
    return chunk

tokenizer  = TreebankWordTokenizer()
stop_words = stopwords.words('english')
lemmatizer = WordNetLemmatizer()
custom_stopwords = {'data', 'federate', 'model', 'learn'}
stop_words = set(stop_words) | custom_stopwords

def prep_apply(abst):
    #소문자화, 문장부호 제거
    abst = abst.lower()
    abst = re.sub(r'[^\w\s-]', ' ', abst)
    #nltk 토큰화 결과
    result = []
    for i in tokenizer.tokenize(abst):
        #표제어(동사 가정)
        i = lemmatizer.lemmatize(i, pos='v')
        #길이 2이하 제거
        if len(i) <= 2:
            continue
        #불용어 거름
        if i in stop_words:
            continue
        result.append(i)
    #tf-idf시 문장넣어야하므로 역토큰화
    return ' '.join(result)
#전처리
def text_prep(chunk):
    chunk['Abstract'] = chunk['Abstract'].apply(prep_apply)
    return chunk

# 병렬 처리 함수
def df_multi_process(df, apply, proc_n = 6):
    chunk_arr = np.array_split(df, proc_n)
    with mp.Pool(proc_n) as pool:
        result_arr = pool.map(apply, chunk_arr)
    return pd.concat(result_arr, ignore_index=True)