from predicttool.KerasLSTM import KerasLSTM
from predicttool.predicthelper import build_seq_dataset
import pandas as pd
from datacollection.logdataset import YMode

"""
No git change tracking
"""

filepath = "originaldata/tradeLog241121000802.csv"

seq_dataset = build_seq_dataset(
    data=pd.read_csv(filepath),
    ignore_col=[6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    x_size=10,
    offset=5,
    y_mode=YMode.BIN_LIMIT
)

model = KerasLSTM(
    seq_dataset=seq_dataset,
    classification=True,
    test_split=0.2,
    random_sample=False
)

model.model_build_compile(
    lstm_unit=64,
    dense_unit=32,
    activation='relu',
    learning_rate=0.001
)

model.fit(
    val_split=0.2,
    epochs=10,
    batch_size=256,
    early_stopping=True,
    early_stopping_patience=3,
    checkpoint=False
)

model.evaluate(plot_loss_history=True)
