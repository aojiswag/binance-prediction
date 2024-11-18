import numpy as np
import pandas as pd
import sys
import random


def split_log(f, split_percent: float = 0.9, skip_row: int = 0):
    split_percent = float(split_percent)
    skip_row = int(skip_row)

    print("file read...")

    log_df = pd.read_csv(f)
    skip_df = log_df.iloc[skip_row:].copy()
    print(skip_df)

    print("sort...")
    sample = random.sample(range(0, len(skip_df)), int(len(skip_df) * (1-split_percent)))

    model_log = skip_df.drop(sample, inplace=False)
    test_log = skip_df.loc[sample, :]
    print(sample)
    print(len(sample))

    print("file save...")
    model_log.to_csv("regmodel.csv", index=False)
    test_log.to_csv("regtest.csv", index=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nusage: splitdata.py [filename] [model_percent] [skip_row]\n"
              "Parameters:\n"
              " filename(require)\n"
              " model_percent(optional, default value: 0.9)\n"
              " skip_row(optional, default value: 0)\n")
        exit(0)

    if sys.argv[1] == "?" or sys.argv[1] == "help":
        print("\nusage: splitdata.py [filename] [model_percent] [skip_row]\n"
              "Parameters:\n"
              " filename(require)\n"
              " model_percent(optional, default value: 0.9)\n"
              " skip_row(optional, default value: 0)\n")
    else:
        print(sys.argv[1:])
        split_log(*sys.argv[1:])
