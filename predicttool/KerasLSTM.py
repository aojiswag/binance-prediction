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

class KerasLSTM:
    def __init__(self):
        self.model = None
        self.history = None

        self.now_time = time.strftime("%y%m%d%H%M%S")

    def model_build_compile(self):
        pass

    def fit(self,
            seq_dataset: list,
            ):
        pass


