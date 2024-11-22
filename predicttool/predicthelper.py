import numpy as np
import pandas as pd
from datacollection.logdataset import YMode
import random
import predicttool.tools.printlog as pl


def build_seq_dataset(data: pd.DataFrame,
                      ignore_col=None,
                      x_size: int = 1,
                      offset: int = 0,
                      param_index: tuple = (4, 19),
                      sym_n: int = 100,
                      y_mode: YMode = YMode.DIF,
                      buy_limit_criteria: float = 1.03,
                      sell_limit_criteria: float = 0.97,
                      bin_criteria: float = 1,):
    """
    No support Many-To-Many model.
    """

    if ignore_col is None:
        ignore_col = []

    x_data = data.iloc[:, 0: param_index[1]].values
    x_index = [
        [x for x in range(i, i + (x_size * sym_n), sym_n)] for i in range(len(data) - (x_size - 1) * sym_n)
    ]

    pl.log("build seq dataset size= " + str(len(data)))
    x_seq = [x_data[x] for x in x_index]
    seq_df = pd.DataFrame({"x": x_seq})

    ignored_col = [x for x in range(param_index[0], param_index[1]) if x not in ignore_col]
    out_x_seq = [x_data[x][0][ignored_col] for x in x_index]

    out_seq_df = pd.DataFrame({"x": out_x_seq})

    def df_shift_price(df):
        if pd.isna(df.iloc[1]):
            return np.nan
        dif = df.iloc[1] / df.iloc[0][-1]

        if y_mode == YMode.DIF:
            return dif
        elif y_mode == YMode.BIN_LIMIT:
            return 1 if dif > bin_criteria else 0
        elif y_mode == YMode.BUY_LIMIT:
            return 1 if dif > buy_limit_criteria else 0
        elif y_mode == YMode.SELL_LIMIT:
            return 1 if dif < sell_limit_criteria else 0

    shift_data = data["last_price"][(x_size*sym_n)+(offset*sym_n):].reset_index(drop=True)

    x_last_value_list = [[i[2] for i in x] for x in seq_df["x"]]

    out_seq_df[y_mode] = pd.DataFrame(
        [x_last_value_list, shift_data]).apply(df_shift_price)
    out_seq_df = out_seq_df.dropna(axis=0)

    if y_mode == YMode.BIN_LIMIT or y_mode == YMode.BUY_LIMIT or y_mode == YMode.SELL_LIMIT:
        out_seq_df = out_seq_df.astype({y_mode: int})

    pl.log("build seq dataset processed\n")

    return out_seq_df


def split_train_dataset(dataset: pd.DataFrame, train_ratio: float = 0.9, random_sample: bool = False):
    dataset_size = len(dataset)
    pl.log("split size= " + str((int(dataset_size*train_ratio), int(dataset_size * (1-train_ratio)))))
    pl.log("random sample= " + str(random_sample))

    if random_sample:
        sample = random.sample(range(0, dataset_size), int(dataset_size * (1 - train_ratio)))

        train = dataset.drop(sample, inplace=False)
        train_x = train.iloc[:, 0].reset_index(drop=True)
        train_y = train.iloc[:, 1].reset_index(drop=True)

        test = dataset.loc[sample, :]
        test_x = test.iloc[:, 0].reset_index(drop=True)
        test_y = test.iloc[:, 1].reset_index(drop=True)

        pl.log("split seq processed\n")
        return train_x, train_y, test_x, test_y

    train_index = int(dataset_size*train_ratio)

    train_x = dataset.iloc[0:train_index, 0]
    train_y = dataset.iloc[0:train_index, 1]

    test_x = dataset.iloc[train_index:, 0].reset_index(drop=True)
    test_y = dataset.iloc[train_index:, 1].reset_index(drop=True)

    pl.log("split seq processed\n")
    return train_x, train_y, test_x, test_y