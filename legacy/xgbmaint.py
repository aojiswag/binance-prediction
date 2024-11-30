from xgboost import XGBRegressor
from xgboost import plot_importance
import pandas as pd

import cupy
from predicttool.tools.predicthelper import build_seq_dataset
from predicttool.tools.predicthelper import split_train_dataset
from datacollection.logdataset import YMode


original_data = pd.read_csv("originaldata/tradeLog241121000802.csv")

dataset = build_seq_dataset(data=original_data, y_mode=YMode.DIF, ignore_col=[6, 7])
train_x, train_y, test_x, test_y = split_train_dataset(dataset, train_ratio=0.9, random_sample=True)

x_col = ["prev_day_ma_vol_per_vol",
         "volume_change",
         # "buy_volume_ratio",
         # "buy_volume_ratio_change",
         "ma_score",
         "rsi_change",
         "prev_day_rsi_avg_per",
         "macd_change",
         "prev_day_macd_avg_per",
         "macd_hist_change",
         "prev_day_macd_hist_avg_per",
         "mfi_change",
         "prev_day_mfi_avg_per",
         "ssd_change",
         "prev_day_ssd_avg_per"]


train_x = pd.DataFrame(train_x.tolist(), columns=x_col)
test_x = pd.DataFrame(test_x.tolist(), columns=x_col)

x = cupy.array(train_x)
y = train_y
test_x = cupy.array(test_x)

model = XGBRegressor(device="cuda", n_estimators=100000, learning_rate=0.1)
model.fit(x, y)

print(model.score(x, y))
print(model.score(test_x, test_y))

pred = model.predict(test_x)
plot_importance(model)

result = pd.DataFrame({"real": test_y, "pred": pred})
result.to_csv("result/xgbresult.csv")

