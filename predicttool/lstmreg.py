from predicttool.predicthelper import split_train_dataset
from predicttool.predicthelper import build_seq_dataset
from datacollection.logdataset import YMode
import numpy as np
import pandas as pd

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import time

import tensorflow as tf

print(tf.config.list_physical_devices('GPU'))
now_time = time.strftime("%y%m%d%H%M%S")
datafile = pd.read_csv("originaldata/tradeLog241121000802.csv")

data = build_seq_dataset(datafile,
                         ignore_col=[6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
                         y_mode=YMode.DIF,
                         x_size=5,
                         offset=5)

train_x, train_y, test_x, test_y = split_train_dataset(data=data, random_sample=False)

print(train_x)

print(train_x.shape)
print(train_y.shape)

print(test_x.shape)
print(test_y.shape)


model = Sequential([
    LSTM(64, input_shape=(5, 3), return_sequences=False),  # Many-to-One 설정
    Dense(32, activation='relu'),
    Dense(1)
])

model.compile(optimizer=Adam(learning_rate=0.0005), loss='mse', metrics=['mae'])
model.summary()

checkpoint_path = f"checkpoint/best_lstm_model{now_time}.keras"
checkpoint = ModelCheckpoint(checkpoint_path, save_best_only=True, monitor='val_loss', mode='min')

early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

history = model.fit(
    train_x, train_y,
    validation_split=0.2,
    epochs=20,
    batch_size=64,
    callbacks=[checkpoint, early_stopping]
)

saved_model = load_model(checkpoint_path)

predictions = saved_model.predict(test_x)

# 결과 출력
print("예측 값 예시:", predictions[:10])
print("실제 값 예시:", test_y[:10])

result = pd.DataFrame({"real": test_y.flatten(), "pred": predictions.flatten()})
result.to_csv(f"result/lstmresult{now_time}.csv")

print(model.evaluate(test_x, test_y))

plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.show()
