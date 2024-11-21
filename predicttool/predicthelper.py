import numpy as np
import pandas as pd
from datacollection.logdataset import YMode


def build_seq_dataset(data: pd.DataFrame,
                      x_size: int = 1,
                      offset: int = 0,
                      param_index: int = 18,
                      sym_n: int = 100,
                      y_mode: YMode = YMode.DIF,
                      buy_limit_criteria: float = 1.03,
                      sell_limit_criteria: float = 0.97,
                      bin_criteria: float = 1):

    x_data = data.iloc[:, 0:param_index].values

    x_index = [
        [x for x in range(i, i + (x_size * sym_n), sym_n)] for i in range(len(data) - (x_size - 1) * sym_n)
    ]

    x_seq = [x_data[x] for x in x_index]
    seq_df = pd.DataFrame({"x": x_seq})

    def df_shift_price(df):
        if pd.isna(df.iloc[1]):
            return np.nan

        dif = df.iloc[1] / df.iloc[0][-1]
        if y_mode == YMode.DIF:
            return dif
        if y_mode == YMode.BIN_LIMIT:
            return 1 if dif > bin_criteria else 0
        if y_mode == YMode.BUY_LIMIT:
            return 1 if dif > buy_limit_criteria else 0
        if y_mode == YMode.SELL_LIMIT:
            return 1 if dif < sell_limit_criteria else 0

    shift_data = data["last_price"][(x_size*sym_n)+(offset*sym_n):].reset_index(drop=True)

    x_last_value_list = [[i[2] for i in x] for x in seq_df["x"]]

    seq_df[y_mode] = pd.DataFrame(
        [x_last_value_list, shift_data]).apply(df_shift_price)
    seq_df = seq_df.dropna(axis=0)

    if y_mode == YMode.BIN_LIMIT or y_mode == YMode.BUY_LIMIT or y_mode == YMode.SELL_LIMIT:
        seq_df = seq_df.astype({y_mode: int})

    seq_df.to_csv("test.csv")

    return seq_df


def split_train_dataset(dataset: pd.DataFrame):
    pass


seq_dataset = build_seq_dataset(pd.read_csv("originaldata/tradeLog241118140145.csv"))

split_seq_dataset = split_train_dataset(seq_dataset)
