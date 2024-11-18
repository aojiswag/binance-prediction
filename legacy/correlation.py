import numpy as np
from xgboost import XGBRegressor
from xgboost import plot_importance
from matplotlib import pyplot
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.ensemble import RandomForestRegressor
import cupy


model_dataset = pd.read_csv("util/regmodel.csv", delimiter=",")
x = cupy.array(model_dataset.iloc[:, 3:33])
y = model_dataset.iloc[:, 33]
print(y)

test_dataset = pd.read_csv("util/regtest.csv", delimiter=",")
test_x = cupy.array(test_dataset.iloc[:, 3:33])
test_y = test_dataset.iloc[:, 33]
print(test_y)

model = XGBRegressor(device="cuda")
model.fit(x, y)

print(model.score(x, y))
print(model.score(test_x, test_y))

pred = model.predict(test_x)
print(pred)
plot_importance(model)

result = pd.DataFrame({"real": test_y, "pred": pred})
result.to_csv("result.csv")

