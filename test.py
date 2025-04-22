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
time.sleep(50)
