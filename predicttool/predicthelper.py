import numpy as np
import pandas as pd
from datacollection.logdataset import YMode
import random
import predicttool.tools.printlog as pl


def build_seq_dataset(data: pd.DataFrame,
                      ignore_col=None,
                      x_size: int = 5,
                      offset: int = 0,
                      param_index: tuple = (4, 19),
                      sym_n: int = 100,
                      y_mode: YMode = YMode.DIF,
                      buy_limit_criteria: float = 1.03,
                      sell_limit_criteria: float = 0.97,
                      bin_criteria: float = 1):
    """
    No support Many-To-Many model.

    :return out_seq[] -> [x_data, y_data]
    """
    out_seq = [[], []]

    if ignore_col is None:
        ignore_col = []

    x_data = data.iloc[:, 0: param_index[1]].values

    x_index = [
        [x for x in range(i, i + (x_size * sym_n), sym_n)] for i in range(len(data) - (x_size - 1) * sym_n)
    ]

    pl.log("build seq dataset size= " + str(len(data)))
    ignored_col = [x for x in range(param_index[0], param_index[1]) if x not in ignore_col]
    out_x_seq = [x_data[x][:, ignored_col] for x in x_index]
    out_seq[0] = np.array(out_x_seq[:-(sym_n+(sym_n*offset))], dtype=np.float32)

    def compare_price(now_price, prev_price):
        dif = now_price / prev_price

        if y_mode == YMode.DIF:
            return [(dif-1) * 100]
        elif y_mode == YMode.BIN_LIMIT:
            return [1] if dif > bin_criteria else [0]
        elif y_mode == YMode.BUY_LIMIT:
            return [1] if dif > buy_limit_criteria else [0]
        elif y_mode == YMode.SELL_LIMIT:
            return [1] if dif < sell_limit_criteria else [0]

    shift_data = data["last_price"][(x_size*sym_n)+(offset*sym_n):].reset_index(drop=True)
    last_x_data = data["last_price"][((x_size-1)*sym_n):].reset_index(drop=True)

    out_seq[1] = np.array(list(map(compare_price, shift_data, last_x_data)), dtype=np.float32)

    pl.log("x_data_shape" + str(out_seq[0].shape))
    pl.log("y_data_shape" + str(out_seq[1].shape))

    return out_seq


def split_train_dataset(data: list, train_ratio: float = 0.9, random_sample: bool = False):
    dataset_size = len(data[0])
    pl.log("split_dataset")
    pl.log("random sample= " + str(random_sample))

    if random_sample:
        sample = random.sample(range(0, dataset_size), int(dataset_size * (1 - train_ratio)))

        train_x = np.delete(data[0], sample, axis=0)
        train_y = np.delete(data[1], sample, axis=0)

        test_x = data[0][sample]
        test_y = data[1][sample]

        pl.log("split seq processed\n")

        return train_x, train_y, test_x, test_y

    train_index = int(dataset_size*train_ratio)

    train_x = data[0][0:train_index]
    train_y = data[1][0:train_index]

    test_x = data[0][train_index:]
    test_y = data[1][train_index:]

    pl.log("split seq processed\n")

    return train_x, train_y, test_x, test_y


"""original_data = pd.read_csv("originaldata/tradeLog241118140145.csv")

dataset = build_seq_dataset(data=original_data, y_mode=YMode.DIF, ignore_col=[6, 7])
a, b, c, d = split_train_dataset(data=dataset, random_sample=False)

print(a[0][0])
print(b[0][0])
"""
