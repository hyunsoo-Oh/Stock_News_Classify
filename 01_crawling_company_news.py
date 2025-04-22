from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# 1. 크롬 옵션 설정
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# 2. CSV에서 티커 목록 불러오기
categories = ['Financial Services', 'Technology', 'Utilities'] # 섹터 목록

for sector_id in range(len(categories)):
    # CSV 파일 로드
    df = pd.read_csv(f'./crawling_data/20250421_company_{categories[sector_id]}.csv')

    # company 기준으로 중복 제거 (첫 번째 ticker 유지)
    df_unique_companies = df.drop_duplicates(subset=['company'], keep='first')
    companies = df_unique_companies['company'].tolist()
    print(f"{categories[sector_id]} : {len(companies)}개 기업이 로드됨")

    # 상위 25개 company와 ticker 선택
    df_top_25 = df_unique_companies[['company', 'ticker']].dropna().head(25)

    # ticker 리스트 생성
    tickers = df_top_25['ticker'].tolist()
    print(f"{categories[sector_id]} : {len(tickers)}개 티커가 로드됨")
    print(tickers)
    # 3. 크롤링 결과 저장 리스트
    news_data = []

    # 4. 각 티커별 뉴스 페이지 크롤링
    for ticker in tickers:
        print(f"{ticker} 뉴스 수집 시작")
        url = f'https://finance.yahoo.com/quote/{ticker}/news'
        driver.get(url)
        time.sleep(3)  # 로딩 대기

        # 스크롤 내려서 뉴스 더 로딩
        for _ in range(35):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

        # 뉴스 기사 카드들 가져오기 (h3 포함된 기사 링크 기준)
        try:
            articles = driver.find_elements(By.XPATH, '//ul/li//h3/ancestor::a')
            if len(articles) == 0:
                raise Exception("뉴스 없음")
        except:
            print(f"{ticker} 뉴스 로딩 실패")
            continue

        print(f"{ticker} 뉴스 {len(articles)}개 탐지됨")

        for article in articles[:200]:
            try:
                title = article.find_element(By.TAG_NAME, 'h3').text
                summary = article.find_element(By.TAG_NAME, 'p').text

                if len(summary) > 150:
                    summary = summary[:150] + "..."

                news_data.append({
                    'symbol' : ticker,
                    'title': title,
                    'summary': summary,
                    'category': categories[sector_id]
                })

            except Exception:
                continue

    # 5. 데이터프레임으로 변환 & 저장
    df_news = pd.DataFrame(news_data)
    df_news.to_csv(f'./crawling_data/top25_ticker_news_{categories[sector_id]}.csv', index=False, encoding='utf-8-sig')
    print(f"전체 뉴스 CSV 저장 완료: top25_ticker_news_{categories[sector_id]}.csv")

driver.quit()