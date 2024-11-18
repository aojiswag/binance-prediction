from xgboost import XGBRegressor
import pandas as pd
import cupy
import os


total_score = []
for i in os.listdir("util/"):
    if i[-12:] == "regmodel.csv":
        symbol = i[:-12]

        model_dataset = pd.read_csv("util/" + i, delimiter=",")

        print(symbol, "start")
        x = cupy.array(model_dataset.iloc[:, 3:33])
        y = model_dataset.iloc[:, 33]

        test_filename = "util/" + symbol + "regtest.csv"
        test_dataset = pd.read_csv(test_filename, delimiter=",")

        test_x = cupy.array(test_dataset.iloc[:, 3:33])
        test_y = test_dataset.iloc[:, 33]

        model = XGBRegressor(device="cuda", n_estimators=8000, learning_rate=0.05)
        model.fit(x, y)

        seen_data_score = model.score(x, y)
        unseen_data_score = model.score(test_x, test_y)

        pred = model.predict(test_x)

        result = pd.DataFrame({"real": test_y, "pred": pred})
        result.to_csv("result/" + symbol + "result.csv")

        total_score.append({"symbol": symbol, "seen_score": seen_data_score, "unseen_score": unseen_data_score})

total_score = pd.DataFrame(total_score)

total_score.to_csv("result/" + "total_score.csv")
