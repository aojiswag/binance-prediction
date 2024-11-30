from XGBBuilder import XGBBuilder
from predicttool.tools.predicthelper import build_seq_dataset
import pandas as pd
from datacollection.logdataset import YMode

filepath = "originaldata/tradeLog241121000802.csv"

dataset, labels = build_seq_dataset(
    data=pd.read_csv(filepath),
    ignore_col=[6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    x_size=1,
    offset=0,
    y_mode=YMode.BIN_LIMIT,
    return_labels=True
)

model = XGBBuilder(dataset=dataset,
                   columns=labels,
                   classification=False,
                   test_split=0.2,
                   random_sample=False)

model.model_build_compile(n_estimators=1000,
                          learning_rate=0.1)

model.fit()

model.evaluate()