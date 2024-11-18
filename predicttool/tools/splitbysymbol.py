import numpy as np
import pandas
import pandas as pd
import sys


def split_symbol(f, model_percent: float = 0.7, skip_row: int = 5900):
    model_percent = float(model_percent)
    skip_row = int(skip_row)

    log_df = pd.read_csv(f)

    skip_df = log_df.iloc[skip_row:].copy()
    symbols = list(skip_df["symbol"].drop_duplicates())

    print(len(symbols))

    split_by_symbol = []

    for i in symbols:
        split_by_symbol.append(skip_df[skip_df["symbol"] == i])

    for i in split_by_symbol:
        symbol = i["symbol"].iloc[0]
        print(symbol)

        model_size = int(len(i) * model_percent)
        model_log = i.iloc[:model_size]
        test_log = i.iloc[model_size:]
        model_log.to_csv(f"{symbol}regmodel.csv", index=False)
        test_log.to_csv(f"{symbol}regtest.csv", index=False)
        print(symbol, "split done")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nusage: splitdata.py [filename] [model_percent] [skip_row]\n"
              "Parameters:\n"
              " filename(require)\n"
              " model_percent(optional, default value: 0.95)\n"
              " skip_row(optional, default value: 5900)\n")
        exit(0)

    if sys.argv[1] == "?" or sys.argv[1] == "help":
        print("\nusage: splitdata.py [filename] [model_percent] [skip_row]\n"
              "Parameters:\n"
              " filename(require)\n"
              " model_percent(optional, default value: 0.95)\n"
              " skip_row(optional, default value: 5900)\n")
    else:
        print("split_by_symbol...")
        split_symbol(*sys.argv[1:])
