import pickle
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from keras.utils import to_categorical
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model

# NLTK 리소스 다운로드
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

# 데이터 로딩
df = pd.read_csv('./models/20250422_all_news.csv')
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)
print(df.head())
df.info()
print(df['category'].value_counts())

X = (df.title + ' ' + df.summary).astype(str)
Y = df['category']

# 라벨 인코딩
with open('./models/encoder.pickle', 'rb') as f:
    encoder = pickle.load(f)

label = encoder.classes_
print(label)

labeled_y = encoder.transform(Y)
onehot_y = to_categorical(labeled_y)
print(onehot_y)

# 텍스트 전처리 함수 (NLTK 사용)
stop_words = set(stopwords.words('english'))
def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)  # 영문자와 공백만 남김
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words and len(word) > 1]
    return ' '.join(tokens)

X = X.apply(preprocess)
print(X[:10])

# 토크나이저 로드 및 시퀀스 변환
with open('./models/token_max_40.pickle', 'rb') as f:
    token = pickle.load(f)

# 토큰 사전 정보 확인
print(f"단어 개수 (vocab size): {len(token.word_index)}")

tokened_x = token.texts_to_sequences(X)
print(tokened_x[:10])

# 길이 자르고 패딩
for i in range(len(tokened_x)):
    tokened_x[i] = tokened_x[i][:40]
x_pad = pad_sequences(tokened_x, 40)
print(x_pad[:10])

# 모델 로드 및 예측
model = load_model('./models/news_section_classification_model_0.89.h5')
preds = model.predict(x_pad)
print(preds[:10])

# 예측 카테고리 추출
predict_section = []
for pred in preds:
    most = label[np.argmax(pred)]
    pred[np.argmax(pred)] = 0
    second = label[np.argmax(pred)]
    predict_section.append([most, second])
print(predict_section[:10])

df['predict'] = predict_section
print(df[['category', 'predict']].head(30))

# 정확도 평가
score = model.evaluate(x_pad, onehot_y)
print(f"Accuracy: {score[1]:.2f}")

# 맞았는지 확인
df['OX'] = (df['category'] == df['predict'].apply(lambda x: x[0])).astype(int)
print("정확도 (맞춘 비율):", df['OX'].mean())
