from predicttool.tools.predicthelper import split_train_dataset
from predicttool.tools.predicthelper import build_seq_dataset
from datacollection.logdataset import YMode
import pandas as pd

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import ModelCheckpoint
import matplotlib.pyplot as plt
import time

now_time = time.strftime("%y%m%d%H%M%S")
datafile = pd.read_csv("originaldata/tradeLog241121000802.csv")

data = build_seq_dataset(datafile, ignore_col=[6, 7], y_mode=YMode.BIN_LIMIT, x_size=5)

train_x, train_y, test_x, test_y = split_train_dataset(data=data, random_sample=False)

print(train_x.shape)
print(train_y.shape)
print(train_y)

print(test_x.shape)
print(test_y.shape)

# 2. 모델 설계
model = Sequential([
    LSTM(32, input_shape=(5, 13), return_sequences=False),  # Many-to-One 설정
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

checkpoint_path = f"checkpoint/best_lstm_model{now_time}.keras"
checkpoint = ModelCheckpoint(checkpoint_path, save_best_only=True, monitor='val_loss', mode='min')

history = model.fit(
    train_x, train_y,
    validation_split=0.2,
    epochs=30,
    batch_size=64,
    callbacks=[checkpoint]
)

saved_model = load_model(checkpoint_path)

predictions = saved_model.predict(test_x)

# 결과 출력
print("pred:", predictions[:10])
print("real:", test_y[:10])

result = pd.DataFrame({"real": test_y.flatten(), "pred": predictions.flatten()})
result.to_csv(f"result/lstmresult{now_time}.csv")

loss, accuracy = saved_model.evaluate(test_x, test_y)
print(f"loss: {loss}, accuracy: {accuracy}")

plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.show()
