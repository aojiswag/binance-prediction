from xgboost import XGBRegressor, XGBClassifier, plot_importance
import xgboost as xgb
import pandas as pd
import numpy as np
import time

from predicttool.tools.predicthelper import split_train_dataset
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_squared_error, accuracy_score, r2_score, f1_score


class XGBBuilder:
    def __init__(self,
                 dataset: list,
                 columns: list,
                 classification: bool = False,
                 test_split: float = 0.2,
                 ):

        self.columns = columns
        self.model = None

        self.classification = classification

        train_x, train_y, test_x, test_y = \
            split_train_dataset(dataset, test_split)

        self.train_x = train_x.reshape(train_x.shape[0], train_x.shape[2])
        self.train_y = train_y.reshape(train_y.shape[0])

        self.test_x = test_x.reshape(test_x.shape[0], test_x.shape[2])
        self.test_y = test_y.reshape(test_y.shape[0])

        testoutx = pd.DataFrame(self.train_x)
        testoutx.to_csv("testoutx")

        testouty = pd.DataFrame(self.train_y)
        testouty.to_csv("testouty")

        self.d_train = xgb.DMatrix(data=self.train_x, label=self.train_y)
        self.d_test = xgb.DMatrix(data=self.test_x, label=self.test_y)

        self.now_time = time.strftime("%y%m%d%H%M%S")
        self.result_path = f"result/XGB_Result{self.now_time}.csv"

    def model_build_train(self,
                          num_boost_round: int = 1000,
                          learning_rate: float = 0.1,
                          max_depth: int = 6,
                          early_stopping=0,
                          ):
        param = {
            "learning_rate": learning_rate,
            "max_depth": max_depth,
        }

        if self.classification:
            param["objective"] = 'binary:logistic'
            param["eval_metric"] = 'logloss'
            self.model = xgb.train(
                params=param,
                dtrain=self.d_train,
                num_boost_round=num_boost_round,
                evals=[(self.d_train, 'train'), (self.d_test, 'test')],
                early_stopping_rounds=early_stopping,
                verbose_eval=True
            )
        else:
            def r2_score_metric(preds, dtrain):
                labels = dtrain.get_label()

                ss_res = np.sum((labels - preds) ** 2)
                ss_tot = np.sum((labels - np.mean(labels)) ** 2)
                r2 = 1 - (ss_res / ss_tot)

                return 'r2', r2

            param["objective"] = 'reg:squarederror'
            param["eval_metric"] = 'rmse'

            self.model = xgb.train(
                params=param,
                dtrain=self.d_train,
                num_boost_round=num_boost_round,
                evals=[(self.d_train, 'train'), (self.d_test, 'test')],
                early_stopping_rounds=early_stopping,
                verbose_eval=True,
                custom_metric=r2_score_metric
            )

    def evaluate(self):
        train_predict = self.model.predict(self.d_train)
        test_predict = self.model.predict(self.d_test)

        print(self.train_y)
        print(train_predict)

        if self.classification:
            result = pd.DataFrame({
                "real": self.test_y,
                "pred": test_predict,
                f"train_accuracy: {accuracy_score(self.train_y, train_predict)}": None,
                f"test_accuracy: {accuracy_score(self.test_y, test_predict)}": None,
                f"test_f1score: {f1_score(self.test_y, test_predict)}": None
            })

        else:
            result = pd.DataFrame({
                "real": self.test_y,
                "pred": test_predict,
                f"train_r2: {r2_score(self.train_y, train_predict)}": None,
                f"test_r2: {r2_score(self.test_y, test_predict)}": None,
                f"test_RMSE: {mean_squared_error(self.test_y, test_predict)}": None
            })

        print(result)
        result.to_csv(self.result_path)
