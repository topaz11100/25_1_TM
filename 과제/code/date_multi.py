from habanero import Crossref
import pandas as pd
import numpy as np
import multiprocessing as mp

# Crossref 객체 생성 (User-Agent 설정)
cr = Crossref(
    ua_string="korean_undergraduate_project (mailto:topaz11100@gmail.com)",
    mailto="topaz11100@gmail.com"
)

# 슬로우 요청 함수 (단락평가 포함, 실패 방지)
def fetch_metadata(doi):
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

# 청크별로 apply
def process_chunk(df_chunk):
    df_chunk['Date'] = df_chunk['DOI'].apply(fetch_metadata)
    df_chunk = df_chunk.drop(columns = ['DOI'])
    df_chunk = df_chunk.dropna()
    return df_chunk

# 병렬 처리 함수
def parallel_fetch(df, n_proc = 4):
    chunks = np.array_split(df, n_proc)
    with mp.Pool(n_proc) as pool:
        results = pool.map(process_chunk, chunks)
    return pd.concat(results, ignore_index=True)