import aiohttp
import asyncio

# 세마포어와 지연 시간 설정
semaphore = asyncio.Semaphore(10)  # 동시에 최대 10개까지
REQUEST_DELAY = 0.2  # 각 요청 사이 0.2초 → 초당 약 5건으로 제한

async def fetch_course_detail(session, cid, url, user_key):
    params = {'ServiceKey': user_key, 'CourseId': cid}
    async with semaphore:
        await asyncio.sleep(REQUEST_DELAY)
        async with session.get(url, params=params) as response:
            if 'application/json' in response.headers.get('Content-Type', ''):
                    json_result = await response.json()
                    result = json_result['results']
                    return result['name'], result['summary']
            else:
                text = await response.text()
                print(f"[{cid}] XML 응답 (에러): {text[:150]}")
                raise
        
async def fetch_all_courses(id_list, url, user_key):
    result = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_course_detail(session, cid, url, user_key) for cid in id_list]
        result = await asyncio.gather(*tasks)
    name_list = [i[0] for i in result]
    summary_list = [i[1] for i in result]
    return name_list, summary_list

