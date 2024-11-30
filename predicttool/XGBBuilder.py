from xgboost import XGBRegressor
from xgboost import plot_importance
import pandas as pd
import cupy
import time

from predicttool.tools.predicthelper import build_seq_dataset
from predicttool.tools.predicthelper import split_train_dataset
from datacollection.logdataset import YMode



class XGBBuilder:
    def __init(self,
               dataset: list,
               classification: bool = False,
               test_split: float = 0.2,
               random_sample: bool = False):
        self.model = None
        self.classification = classification
        self.train_x, self.train_y, self.test_x, self.test_y = \
            split_train_dataset(dataset, test_split, random_sample)
        self.now_time = time.strftime("%y%m%d%H%M%S")
        self.result_path = f"result/XGB_Result{self.now_time}.csv"


    def model_build_compile(self):
        pass

    def fit(self):
        pass

    def evaluate(self):
        pass