import pickle
import re
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# NLTK 리소스 다운로드
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# 불용어 설정
stop_words = set(stopwords.words('english'))  # 영어 기준

# CSV 로딩
df = pd.read_csv('./models/top25_ticker_all_news.csv')

# X, Y 정의
X = (df.title + ' ' + df.summary).astype(str)
Y = df.category

# 라벨 인코딩
encoder = LabelEncoder()
labeled_y = encoder.fit_transform(Y)
onehot_y = to_categorical(labeled_y)

# 인코더 저장
with open('./models/encoder.pickle', 'wb') as f:
    pickle.dump(encoder, f)

# 전처리 함수 정의
def preprocess_text(text):
    text = text.lower()
    # 영문자(대 소문자)와 공백만 남김 + 제거한 문자-숫자 공백으로 대체
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    tokens = text.split()
    filtered_tokens = [word for word in tokens if word not in stop_words and len(word) > 1]
    return ' '.join(filtered_tokens)

# 전체 데이터 전처리
X = X.apply(preprocess_text)

# 토크나이징
tokenizer = Tokenizer()
tokenizer.fit_on_texts(X)
tokened_x = tokenizer.texts_to_sequences(X)

# 단어 집합 크기
wordsize = len(tokenizer.word_index) + 1

# 최대 문장 길이
max_len = max(len(x) for x in tokened_x)

# 토크나이저 저장
with open(f'./models/token_max_{max_len}.pickle', 'wb') as f:
    pickle.dump(tokenizer, f)

# 패딩
x_pad = pad_sequences(tokened_x, maxlen=max_len)

# 학습/테스트 데이터 분리
x_train, x_test, y_train, y_test = train_test_split(x_pad, onehot_y, test_size=0.2)

# 저장
np.save(f'./models/news_x_train_wordsize{wordsize}.npy', x_train)
np.save(f'./models/news_x_test_wordsize{wordsize}.npy', x_test)
np.save(f'./models/news_y_train_wordsize{wordsize}.npy', y_train)
np.save(f'./models/news_y_test_wordsize{wordsize}.npy', y_test)
