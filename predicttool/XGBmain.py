from XGBBuilder import XGBBuilder
from predicttool.tools.predicthelper import build_seq_dataset
import pandas as pd
from predicttool.tools.predicthelper import YMode

filepath = "originaldata/tradeLog241121000802.csv"

dataset, labels = build_seq_dataset(
    data=pd.read_csv(filepath),
    ignore_col=[6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    x_size=1,
    offset=10,
    y_mode=YMode.DIF,
    return_labels=True
)

model = XGBBuilder(dataset=dataset,
                   columns=labels,
                   classification=False,
                   test_split=0.2)

model.model_build_train(num_boost_round=1000,
                        learning_rate=0.2,
                        max_depth=3)

model.evaluate()
