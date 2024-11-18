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

    # now_time을 datetime 형식으로 변환
    log_df["now_time"] = pd.to_datetime(log_df["now_time"].str.slice(0, 14), format='%y-%m-%d %H:%M')

    # shift_time 계산
    log_df["shift_time"] = log_df["now_time"] + datetime.timedelta(minutes=shift_min)

    # symbol과 now_time을 기준으로 정렬
    log_df.sort_values(by=["symbol", "now_time"], inplace=True)

    # Shifted prices를 사전에 계산
    shift_dict = {}
    for index, row in log_df.iterrows():
        shift_dict[(row["symbol"], row["now_time"])] = row["last_price"]

    # price_dif 계산 및 na_list 수집
    na_list = []
    for index, row in log_df.iterrows():
        symbol = row["symbol"]
        now_time = row["now_time"]
        shift_time = row["shift_time"]
        price = row["last_price"]

        shift_price = shift_dict.get((symbol, shift_time), None)

        if shift_price is None:
            na_list.append(index)
        else:
            copy_df.at[index, 'price_dif'] = shift_price / price

    print("drop na list:", na_list)

    # na_list를 drop한 DataFrame 생성
    copy_df.drop(index=na_list, inplace=True)

    # 결과를 CSV 파일로 저장
    copy_df.to_csv(f"{f}_timeshift.csv", index=False)


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
