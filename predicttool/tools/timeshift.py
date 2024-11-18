import numpy as np
import pandas
import pandas as pd
import sys

import datetime
import time


def time_shift(f, shift_min: int = 5):
    shift_min = int(shift_min)
    log_df = pd.read_csv(f)
    copy_df = log_df.copy()
    print(copy_df.iloc[3]["price_dif"])
    log_df["now_time"] = log_df["now_time"].str.slice(0, 14)

    print(log_df)
    na_list = []
    for index, row in log_df.iterrows():
        now_time = datetime.datetime.strptime(row["now_time"], '%y-%m-%d %H:%M')
        symbol = row["symbol"]
        price = row["last_price"]

        shift_time = (now_time + datetime.timedelta(minutes=shift_min)).strftime('%y-%m-%d %H:%M')

        is_symbol = log_df["symbol"] == symbol
        is_shift_time = log_df["now_time"] == shift_time

        shift_price = log_df.loc[is_symbol & is_shift_time]["last_price"]
        shift_price_diff = shift_price / price

        if len(shift_price) < 1:
            na_list.append(index)
        else:
            copy_df.at[copy_df.index[index], 'price_dif'] = shift_price_diff

    print("drop na list:", na_list)
    copy_df.drop(na_list, inplace=True)
    copy_df.to_csv(f"{f}_timeshift.csv")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("\nusage: timeshift.py [filename] [shift_minute]\n"
              "Parameters:\n"
              " filename(require)\n"
              " shift_minute(optional, default value: 5)\n")
        exit(0)

    if sys.argv[1] == "?" or sys.argv[1] == "help":
        print("\nusage: timeshift.py [filename] [shift_minute]\n"
              "Parameters:\n"
              " filename(require)\n"
              " shift_minute(optional, default value: 5)\n")
    else:
        print(sys.argv[1:])
        time_shift(*sys.argv[1:])
