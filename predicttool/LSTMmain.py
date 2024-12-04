from predicttool.LSTMBuilder import LSTMBuilder
from predicttool.tools.predicthelper import build_seq_dataset
import pandas as pd
from datacollection.logdataset import YMode

"""
No git change tracking
"""

filepath = "originaldata/tradeLog241121000802.csv"

seq_dataset = build_seq_dataset(
    data=pd.read_csv(filepath),
    ignore_col=[6, 7],
    x_size=10,
    offset=5,
    y_mode=YMode.DIF,
    single_symbol=True,
    symbol_name="BTCUSDT"
)

model = LSTMBuilder(
    seq_dataset=seq_dataset,
    classification=False,
    test_split=0.2,
)

model.model_build_compile(
    lstm_unit=128,
    dense_unit=64,
    activation='relu',
    learning_rate=0.001
)

model.fit(
    val_split=0.2,
    epochs=100,
    batch_size=128,
    early_stopping=False,
    early_stopping_patience=3,
    checkpoint=False
)

model.evaluate(plot_loss_history=True)
