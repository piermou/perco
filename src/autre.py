import json

from curl_cffi import requests

urls = [
    "https://www.vinted.fr/api/v2/catalog/items?page=1&per_page=12&time=1756774865&search_text=&catalog_ids=5&order=newest_first&brand_ids=218132,47829,3354969,51445,2441307",
    "https://www.vinted.fr/api/v2/catalog/items?page=1&per_page=96&time=1756774865&search_text=&catalog_ids=5&order=newest_first&brand_ids=2367131,2318552,5589958,609050,461946,72138",
]

cookies = {
    "access_token_web": "eyJraWQiOiJFNTdZZHJ1SHBsQWp1MmNObzFEb3JIM2oyN0J1NS1zX09QNVB3UGlobjVNIiwiYWxnIjoiUFMyNTYifQ.eyJhY2NvdW50X2lkIjoxMDYyNjAxNjgsImFwcF9pZCI6NCwiYXVkIjoiZnIuY29yZS5hcGkiLCJjbGllbnRfaWQiOiJ3ZWIiLCJleHAiOjE3NTY3NzY3NDAsImlhdCI6MTc1Njc2OTU0MCwiaXNzIjoidmludGVkLWlhbS1zZXJ2aWNlIiwicHVycG9zZSI6ImFjY2VzcyIsInNjb3BlIjoidXNlciIsInNpZCI6IjEzZTY5NzM3LTE3NTYzMjE5MDciLCJzdWIiOiIxNTUwODkwNjQiLCJhY3QiOnsic3ViIjoiMTU1MDg5MDY0In19.wmqkL0qJZ99R9frKjNgZF-xHiTd1p7N8cPqrbodJR7sem4pH4-ZIFX1zKJvgNzzxU4vuukSr_Q9_tB49wBhWr2AB896r_uKmhL3NEdWwc4mKxBXAkcEcxQbIt0q0WxLcaDeSKr2pkdkMGKErL7LGiScLoPtZgrWAk-D9GdJglp3GOQr8RNAEspOzaPk43B1FqAfiTXZLGT4M9znTe4RCyL2HMM846AkMRJlFtt4Mu1I7oQG2uKl9BBIEVmZpfnaNs3S8_DCDBNVuVHc8K8gqcvvGmNyeM7pjowY2Vei4KKfsbwM7sj39TiLaIMtIM2xirM8ErymTVwd_mTUombIs_Q"
}

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/11.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36",
]

mama = [1, 2]

for url, i in zip(urls, mama):
    response = requests.get(url=url, cookies=cookies)
    print(response.status_code)
    data = response.json()  # dict ou list

    with open(f"json{i}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
