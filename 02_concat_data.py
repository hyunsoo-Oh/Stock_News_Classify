import pandas as pd
import glob

# 지정된 경로와 파일명을 가져오기
data_dir = './crawling_data/'

data_path1 = glob.glob(data_dir + 'top25_ticker_news_*.csv') # *.*
data_path2 = glob.glob(data_dir + '20250421_company_*.csv') # *.*
data_path3 = glob.glob(data_dir + '20250422_news_*.csv') # *.*

# 데이터 프레임 초기화
df1 = pd.DataFrame()
df2 = pd.DataFrame()
df3 = pd.DataFrame()

# news 데이터 합치기
for path in data_path1:
    df1_section = pd.read_csv(path)
    df1 = pd.concat([df1, pd.read_csv(path)], ignore_index=True)
df1.info()

# company 데이터 합치기
for path in data_path2:
    df2_section = pd.read_csv(path)
    df2 = pd.concat([df2, pd.read_csv(path)], ignore_index=True)
df2.info()

# sector news 데이터 합치기
for path in data_path3:
    df3_section = pd.read_csv(path)
    df3 = pd.concat([df3, pd.read_csv(path)], ignore_index=True)
df3.info()

print(df1.head(), df2.head(), df3.head())

df1.to_csv('./models/top25_ticker_all_news.csv', index=False)
df2.to_csv('./models/20250421_all_company.csv', index=False)
df3.to_csv('./models/20250422_all_news.csv', index=False)