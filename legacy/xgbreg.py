import numpy as np
from matplotlib import pyplot
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.metrics import r2_score
from pycaret.regression import *



data = pd.read_csv("BTCUSDTregmodel.csv_timeshift.csv", delimiter=",")
data = data.iloc[:, 3:34]
#print(data)

test_data = pd.read_csv("BTCUSDTregtest.csv_timeshift.csv", delimiter=",")
test_y = test_data.iloc[:, 33]
test_data = test_data.iloc[:, 3:33]
#print(test_y)

caret_model = setup(session_id=1, data=data, target='price_dif', use_gpu=True, train_size=0.9)

xgb = create_model('xgboost')
tuned_xgb = tune_model(xgb, n_iter=10, optimize="r2")

pred_unseen = predict_model(tuned_xgb, data=test_data)
print(pred_unseen)

print(finalize_model(estimator=tuned_xgb))


result = pd.DataFrame({"real": test_y, "pred": pred_unseen["prediction_label"]})
result.to_csv("result.csv")

