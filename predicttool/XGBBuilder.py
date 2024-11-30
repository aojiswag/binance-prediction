from xgboost import XGBRegressor, XGBClassifier, plot_importance
import pandas as pd
import numpy as np
import cupy
import time

from predicttool.tools.predicthelper import build_seq_dataset
from predicttool.tools.predicthelper import split_train_dataset
from datacollection.logdataset import YMode



class XGBBuilder:
    def __init__(self,
               dataset: list,
               columns: list,
               classification: bool = False,
               test_split: float = 0.2,
               random_sample: bool = False):
        self.model = None
        self.classification = classification
        train_x, train_y, test_x, test_y = \
            split_train_dataset(dataset, test_split, random_sample)

        self.train_x = cupy.array(
            pd.DataFrame(
                train_x.reshape(train_x.shape[0], train_x.shape[2]),
                columns=columns)
        )
        self.train_y = pd.DataFrame(train_y.reshape(train_y.shape[0]), columns=["train_y"])

        self.test_x = cupy.array(
            pd.DataFrame(
                test_x.reshape(test_x.shape[0], test_x.shape[2]),
                columns=columns)
        )
        self.test_y = pd.DataFrame(test_y.reshape(test_y.shape[0]), columns=["test_y"])

        self.now_time = time.strftime("%y%m%d%H%M%S")
        self.result_path = f"result/XGB_Result{self.now_time}.csv"


    def model_build_compile(self,
                            n_estimators:int = 1000,
                            learning_rate: float = 0.1,
                            ):
        param = {
            "device": "cuda",
            "n_estimators": n_estimators,
            "learning_rate": learning_rate
        }

        if self.classification:
            self.model = XGBClassifier(**param)
        else:
            self.model = XGBRegressor(**param)


    def fit(self):
        self.model.fit(self.train_x, self.train_y)

    def evaluate(self):
        train_score = self.model.score(self.train_x, self.train_y)
        test_score = self.model.score(self.test_x, self.test_y)
        print(f"model score of train: {train_score}")
        print(f"model score of test: {test_score}")

        predict = self.model.predict(self.test_x)

        result = pd.DataFrame({
            "real": self.test_y,
            "pred": predict,
            f"train_score: {train_score}" : None,
            f"test_score: {test_score}" : None,
        })

        result.to_csv(self.result_path)