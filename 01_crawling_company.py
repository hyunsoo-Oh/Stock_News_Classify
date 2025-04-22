from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import datetime

# 섹터 목록
categories = ['Financial Services', 'Technology', 'Utilities']

# Chrome 옵션 설정
options = ChromeOptions()
options.add_argument('lang=ko_KR')

# Chrome 드라이버 설정
service = ChromeService(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# WebDriverWait 초기화
wait = WebDriverWait(driver, 10)

# Yahoo Finance 스크리너 URL
url = 'https://finance.yahoo.com/research-hub/screener/sec-ind_ind-largest-equities_software-infrastructure/?start=0&count=100'
driver.get(url)


# 팝업 제거 함수
def close_popups():
    popup_xpaths = [
        '//*[@id="nimbus-app"]/section/section/section/article/section/div/div[1]/div[3]/span/div[3]/div[2]/span/button',
        '//*[@id="nimbus-app"]/section/section/section/article/section/div/div[3]/div/span/div/span/button'
    ]
    for xpath in popup_xpaths:
        try:
            driver.find_element(By.XPATH, xpath).click()
            time.sleep(0.5)
            print("팝업 제거 완료")
        except:
            pass  # 팝업이 없으면 무시


# 초기 팝업 제거
close_popups()

# 필터 제거 버튼
remove_btn_1 = '//*[@id="nimbus-app"]/section/section/section/article/section/div/div[3]/div/div[5]/button'
remove_btn_2 = '//*[@id="nimbus-app"]/section/section/section/article/section/div/div[3]/div/div[4]/button'
sector_btn = '//*[@id="nimbus-app"]/section/section/section/article/section/div/div[3]/div/div[3]/div/button'

try:
    driver.find_element(By.XPATH, remove_btn_1).click()
    time.sleep(0.5)
    print('필터 제거 1')
    driver.find_element(By.XPATH, remove_btn_2).click()
    time.sleep(0.5)
    print('필터 제거 2')
except Exception as e:
    print(f"필터 제거 중 오류: {str(e)}")

# 각 섹터에 대해 반복
for sector_id in range(len(categories)):
    print(f"\n=== {categories[sector_id]} 섹터 크롤링 시작 ===")
    driver.execute_script("window.scrollTo(0, 0);")  # 페이지 상단으로 스크롤
    try:
        driver.find_element(By.XPATH, sector_btn).click()  # 섹터 필터 버튼 클릭
        time.sleep(0.5)
        print('섹터 버튼 클릭')
    except Exception as e:
        print(f"섹터 버튼 클릭 오류: {str(e)}")
        continue

    # 리셋 버튼 클릭
    reset_btn = '//button[text()="Reset" and not(@disabled)]'
    try:
        driver.find_element(By.XPATH, reset_btn).click()
        time.sleep(2)
    except Exception as e:
        print(f"리셋 버튼 클릭 오류: {str(e)}")
        continue

    # 섹터 체크박스 선택
    check_btn = f'//*[@id="{categories[sector_id]}"]'
    try:
        driver.find_element(By.XPATH, check_btn).click()
        time.sleep(0.5)
    except Exception as e:
        print(f"섹터 체크박스 선택 오류: {str(e)}")
        continue

    # 적용 버튼 클릭
    apply_btn = '//button[text()="Apply" and not(@disabled)]'
    try:
        driver.find_element(By.XPATH, apply_btn).click()
        time.sleep(2)
    except Exception as e:
        print(f"적용 버튼 클릭 오류: {str(e)}")
        continue

    # 테이블이 로드될 때까지 대기
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section/div/div[5]/div[1]/table')))
        print(f"{categories[sector_id]} 테이블 로드 완료")
    except Exception as e:
        print(f"테이블 로드 실패: {str(e)}")
        continue
    tickers = [] # ticker 목록 저장
    companies = []  # 회사 목록 저장
    k = 1  # 회사 인덱스
    page_num = 1  # 페이지 번호 추적
    while True:
        print(f"\n페이지 {page_num} 크롤링 시작")
        time.sleep(2)

        # 각 행에서 회사명 추출
        for i in range(1, 100 + 1):
            ticker_xpath = f'//*[@id="nimbus-app"]/section/section/section/article/section/div/div[5]/div[1]/table/tbody/tr[{i}]/td[2]/div/span/a/div/span'
            company_xpath = f'//*[@id="nimbus-app"]/section/section/section/article/section/div/div[5]/div[1]/table/tbody/tr[{i}]/td[3]/div'
            try:
                ticker = driver.find_element(By.XPATH, ticker_xpath).text
                tickers.append(ticker)
                company_name = driver.find_element(By.XPATH, company_xpath).text
                companies.append(company_name)
                print(f"[{k}] {ticker} - {company_name}")
                k += 1
            except Exception as e:
                print(f'인덱스 {i}에서 오류 발생: {str(e)}')
                break  # 오류 발생 시 현재 페이지 종료

        # "다음" 버튼 확인
        next_btn = '//*[@id="nimbus-app"]/section/section/section/article/section/div/div[5]/div[2]/div[3]/button[3]'
        try:
            next_button = driver.find_element(By.XPATH, next_btn)
            if next_button.get_attribute('disabled'):
                print(f"{categories[sector_id]}의 페이지가 더 이상 없습니다")
                break
            next_button.click()
            page_num += 1
            # 다음 페이지 테이블 로드 대기
            wait.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="nimbus-app"]/section/section/section/article/section/div/div[5]/div[1]/table')))
        except Exception as e:
            print(f"다음 버튼을 찾을 수 없거나 오류 발생: {str(e)}")
            break

    # 데이터프레임 생성 및 저장
    if companies:  # 회사 데이터가 있을 경우에만 처리
        # 전체 데이터프레임 초기화
        df_company = pd.DataFrame(columns=['ticker', 'company', 'category'])

        # 데이터프레임에 추가
        df_news = pd.concat(
            [df_company, pd.DataFrame({'ticker': tickers, 'company': companies,
                                    'category': categories[sector_id]})], ignore_index=True)
        df_news.info()
        print(f"=== {categories[sector_id]} 섹터 뉴스창 스크롤 완료 ===\n")

        # 데이터프레임 저장
        timestamp = datetime.datetime.now().strftime('%Y%m%d')
        filename = f'./crawling_data/{timestamp}_company_{categories[sector_id]}.csv'
        df_news.to_csv(filename, index=False)

        # 전체 데이터프레임 정보 출력
        print("\n현재 df_titles 데이터프레임:")
        print(df_company.head())
        print("\ndf_titles 정보:")
        df_company.info()
        print("\n카테고리별 데이터 수:")
        print(df_company['category'].value_counts())
    else:
        print(f"{categories[sector_id]} 섹터에서 데이터를 수집하지 못했습니다")

# 브라우저 종료
driver.quit()

# Financal Servies 3290
# Technology 1987
# Utilities 414