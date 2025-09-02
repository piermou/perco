import time

from curl_cffi import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

url = "https://www.vinted.fr/catalog?search_text=&catalog[]=5&brand_ids[]=218132&brand_ids[]=47829&brand_ids[]=3354969&brand_ids[]=51445&brand_ids[]=2441307&search_id=24743460970&order=newest_first&time=1756751200"
url1 = "https://www.vinted.fr/api/v2/catalog/items?page=1&per_page=96&time=1756762652&search_text=&catalog_ids=5&order=newest_first&brand_ids=218132,47829,3354969,51445,2441307"

cookies = {
    "access_token_web": "eyJraWQiOiJFNTdZZHJ1SHBsQWp1MmNObzFEb3JIM2oyN0J1NS1zX09QNVB3UGlobjVNIiwiYWxnIjoiUFMyNTYifQ.eyJhY2NvdW50X2lkIjoxMDYyNjAxNjgsImFwcF9pZCI6NCwiYXVkIjoiZnIuY29yZS5hcGkiLCJjbGllbnRfaWQiOiJ3ZWIiLCJleHAiOjE3NTY3Njk4NDAsImlhdCI6MTc1Njc2MjY0MCwiaXNzIjoidmludGVkLWlhbS1zZXJ2aWNlIiwicHVycG9zZSI6ImFjY2VzcyIsInNjb3BlIjoidXNlciIsInNpZCI6IjEzZTY5NzM3LTE3NTYzMjE5MDciLCJzdWIiOiIxNTUwODkwNjQiLCJhY3QiOnsic3ViIjoiMTU1MDg5MDY0In19.TXEVSxB84_O5va-4MatrUc6BypmQSj3heTA7wAlXTvEI6izpuvCKQjyxtEvLQGMcVfvfAq2ouv3sTOWBrWH87ge_-Xq4GbzSvaMwtAmNf4Isg-_BXCGdFW8vs_C-jv6qgwnrwZBqyobvm2nEI7hORQ3TQJh9PQS_OILs0jq_vgpZCeNewbV0kY63wJ19ui9dXR6om5200ocBvN3r6IRLYYi-TsPutXpD-hIk6PWJ7JoJiXNh5j99ht_VJXfifWjusW7Ysb6PUGa_L24Vsb7CvtRP0DGg1uvPU8TDYoFnriXhCnYnsUkjPtev2npzg5dTFEVgh5j1rFp5QhfbnaSnyQ"
}


def get_all():
    options = Options()
    # options.add_argument("--headless=new")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")

    service = Service(executable_path="/Users/piermou/zed/perco/src/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)

        time.sleep(5)

        hrefs = driver.find_elements(
            By.CSS_SELECTOR, "a.new-item-box__overlay.new-item-box__overlay--clickable"
        )
        links = [href.get_attribute("href") for href in hrefs]
        print(len(links))
        for nana in links:
            print(nana)

    finally:
        driver.quit()


response = requests.get(url=url1, cookies=cookies)
print(response.status_code)
print(response.json())
