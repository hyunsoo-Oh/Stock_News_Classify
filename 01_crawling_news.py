from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
import datetime

# 섹터 목록
categories_url = ['financial-services', 'technology', 'utilities']
categories = ['Financial Services', 'Technology', 'Utilities'] # 섹터 목록

# Chrome 옵션 설정
options = ChromeOptions()

# Chrome 드라이버 설정
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# WebDriverWait 초기화
wait = WebDriverWait(driver, 10)

# Yahoo Finance 스크리너 URL
for sector_id in range(len(categories)):
    url = 'https://finance.yahoo.com/sectors/{}/'.format(categories_url[sector_id])
    driver.get(url)
    print(f"\n=== {categories[sector_id]} 섹터 뉴스창 스크롤 시작 ===")
    time.sleep(2)

    # 스크롤 반복
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 각 행에서 뉴스 데이터 추출
    news_items = driver.find_elements(By.XPATH,
                                      '//*[@id="nimbus-app"]/section/section/section/article/section[6]/div[2]/div/div/div/ul/li')
    print(f"총 항목 수: {len(news_items)}")
    titles = []
    summaries = []
    for idx in range(1, len(news_items) + 1):
        title_path = '//*[@id="nimbus-app"]/section/section/section/article/section[6]/div[2]/div/div/div/ul/li[{}]/section/div/a/h3'.format(idx)
        summary_path = '//*[@id="nimbus-app"]/section/section/section/article/section[6]/div[2]/div/div/div/ul/li[{}]/section/div/a/p'.format(idx)
        try:
            title = driver.find_element(By.XPATH, title_path).text
            summary = driver.find_element(By.XPATH, summary_path).text
            if title and summary:
                titles.append(title)
                summaries.append(summary)
                print(f"[{idx}] {title} | {summary}")
        except:
            print(f"인덱스 {idx}에서 오류 발생")
            continue # 오류 발생 시 현재 페이지 종료

    # 전체 데이터프레임 초기화
    df_news = pd.DataFrame(columns=['title', 'summary', 'category'])

    # 데이터프레임에 추가
    df_news = pd.concat([df_news, pd.DataFrame({'title': titles, 'summary': summaries, 'category': categories[sector_id]})], ignore_index=True)
    df_news.info()
    print(f"=== {categories[sector_id]} 섹터 뉴스창 스크롤 완료 ===\n")

    # 데이터프레임 저장
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    filename = f'./crawling_data/{timestamp}_news_{categories[sector_id]}.csv'
    df_news.to_csv(filename, index=False)