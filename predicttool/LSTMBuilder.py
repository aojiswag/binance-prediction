from predicttool.tools.predicthelper import split_train_dataset
import pandas as pd

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
import time

import tensorflow as tf


def r_squared(y_true, y_pred):
    ss_res = tf.reduce_sum(tf.square(y_true - y_pred))
    ss_tot = tf.reduce_sum(tf.square(y_true - tf.reduce_mean(y_true)))
    return 1 - ss_res / (ss_tot + tf.keras.backend.epsilon())


class LSTMBuilder:
    def __init__(self,
                 seq_dataset: list,
                 classification: bool = False,
                 test_split: float = 0.2,
                 ):
        self.model = None
        self.history = None

        self.classification = classification
        self.train_x, self.train_y, self.test_x, self.test_y \
            = split_train_dataset(seq_dataset, test_split)
        self.now_time = time.strftime("%y%m%d%H%M%S")
        self.checkpoint_path = f"checkpoint/model_{self.now_time}.keras"
        self.result_path = f"result/LSTM_Result{self.now_time}.csv"

    def model_build_compile(self,
                            lstm_unit: int = 64,
                            dense_unit: int = 32,
                            activation: str = 'relu',
                            learning_rate: float = 0.001
                            ):

        input_shape = (self.train_x.shape[1], self.train_x.shape[2])

        if self.classification:
            self.model = Sequential([
                LSTM(lstm_unit, input_shape=input_shape, return_sequences=False),
                Dense(dense_unit, activation=activation),
                Dense(1, activation='sigmoid')
            ])
            self.model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

        else:
            self.model = Sequential([
                LSTM(lstm_unit, input_shape=input_shape, return_sequences=False),
                Dense(dense_unit, activation=activation),
                Dense(1)
            ])
            self.model.compile(optimizer=Adam(learning_rate=learning_rate), loss='mse', metrics=['mae', r_squared])

        self.model.summary()

    def fit(self,
            val_split: float = 0.2,
            epochs: int = 10,
            batch_size: int = 64,
            early_stopping: bool = True,
            early_stopping_patience: int = 10,
            checkpoint: bool = True,
            ):

        callbacks = []

        if checkpoint:
            checkpoint = ModelCheckpoint(self.checkpoint_path, save_best_only=True, monitor='val_loss', mode='min')
            callbacks.append(checkpoint)

        if early_stopping:
            early_stopping = EarlyStopping(monitor='val_loss', patience=early_stopping_patience, restore_best_weights=True)
            callbacks.append(early_stopping)

        self.history = self.model.fit(
            self.train_x, self.train_y,
            validation_split=val_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks
        )

        if checkpoint:
            self.model = load_model(self.checkpoint_path, custom_objects={"r_squared": r_squared})

    def evaluate(self, plot_loss_history: bool = True):

        predictions = self.model.predict(self.test_x)

        evaluate = self.model.evaluate(self.test_x, self.test_y)

        if self.classification:
            predictions = [1 if x > 0.5 else 0 for x in predictions.flatten()]
            result = pd.DataFrame({
                "real": self.test_y.flatten(),
                "pred": predictions,
                f"loss: {evaluate[0]}": None,
                f"accuracy: {evaluate[1]}": None,
            })
        else:
            result = pd.DataFrame({
                "real": self.test_y.flatten(),
                "pred": predictions.flatten(),
                f"loss: {evaluate[0]}": None,
                f"mae: {evaluate[1]}": None,
                f"r_sq: {evaluate[2]}": None,
            })

        result.to_csv(self.result_path)

        if plot_loss_history:
            plt.plot(self.history.history['loss'], label='Train Loss')
            plt.plot(self.history.history['val_loss'], label='Validation Loss')
            plt.legend()
            plt.show()


