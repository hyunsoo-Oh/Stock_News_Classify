import numpy as np
import matplotlib.pyplot as plt
from attr.setters import validate
from keras.models import *
from keras.layers import *
from tensorflow.python.keras.saving.saved_model.load import metrics

x_train = np.load('./models/news_x_train_wordsize14293.npy', allow_pickle=True)
x_test = np.load('./models/news_x_test_wordsize14293.npy', allow_pickle=True)
y_train = np.load('./models/news_y_train_wordsize14293.npy', allow_pickle=True)
y_test = np.load('./models/news_y_test_wordsize14293.npy', allow_pickle=True)

print(x_train.shape, y_train.shape)
print(x_test.shape, y_test.shape)

model = Sequential()
model.add(Embedding(14293, 300))
model.build(input_shape=(None, 14293))
model.add(Conv1D(32, kernel_size=5, padding='same', activation='relu'))
model.add(MaxPooling1D(pool_size=1))
model.add(LSTM(128, activation='tanh', return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(64, activation='tanh', return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(32, activation='tanh'))
model.add(Dropout(0.3))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(3, activation='softmax'))
model.summary()

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
fit_hist = model.fit(x_train, y_train, batch_size=128, epochs=10, validation_data=(x_test, y_test))

score = model.evaluate(x_test, y_test, verbose=0)
model.save('./models/news_section_classification_model_{:.2f}.h5'.format(score[1]))

# 정확도 그래프
plt.subplot(1, 2, 1)
plt.plot(fit_hist.history['accuracy'], 'b-', label='accuracy')
plt.plot(fit_hist.history['val_accuracy'], 'r--', label='val_accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()

# 손실 그래프
plt.subplot(1, 2, 2)
plt.plot(fit_hist.history['loss'], 'g-', label='loss')
plt.plot(fit_hist.history['val_loss'], 'k--', label='val_loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.tight_layout()
plt.show()