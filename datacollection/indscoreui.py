import webbrowser


from binance.client import Client
import numpy as np
import time
import os
import sys
from env import settings
import binancehelper as bh

from PyQt5.uic.properties import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

import urllib3.exceptions
import requests.exceptions

import talib
from talib import MA_Type

@bh.retry(count=30, sleep_sec=1,
          exceptions=(ConnectionResetError, urllib3.exceptions.ProtocolError, requests.exceptions.ConnectionError, Exception))
def get_ticker(api: settings.ApiInfo):
    client = Client(api_key=api.key, api_secret=api.secret)
    tkr = client.futures_ticker()
    client.close_connection()

    return tkr


@bh.retry(count=30, sleep_sec=1,
          exceptions=(ConnectionResetError, urllib3.exceptions.ProtocolError, requests.exceptions.ConnectionError, Exception))
def get_candle(api: settings.ApiInfo, symbols: iter):
    client = Client(api_key=api.key, api_secret=api.secret)
    candles = bh.get_last_1m_candle(cl=client, symbols=symbols)
    client.close_connection()

    return candles


class ResultDataSet:
    def __init__(self, **data):
        self.now_time = data.get("nowTime", 0)
        self.symbol = data.get("symbol", 0)
        self.last_price = data.get("lastPrice", 0)

        self.ind_score = data.get("indScore", 0)

        self.price_dif = 0

    def __iter__(self):
        for _, val in self.__dict__.items():
            yield val

    def get_log_header(self):
        return [x for x, _ in self.__dict__.items()]


UI_PATH = os.path.dirname(os.path.realpath(__file__)) + "/ui/main.ui"


def is_nan(x: float):
    if x == 0 or np.isnan(x):
        return True
    else:
        return False

class TickerUpdater(QThread):
    emit_signal = pyqtSignal(list)
    def __init__(self):
        super().__init__()

    def run(self):
        data=[]
        authkey = settings.ApiInfo()
        candle_update_delay_offset_sec = 8
        top_volume_ticker_length = 100
        sec_trigger_flag = False

        delist_filter_ms = 360000

        price_window_size = 1440
        day_init_window_size = 1440

        period_rsi = 12
        period_macd_fast = 12
        period_macd_slow = 26
        period_macd_sig = 9
        period_mfi = 21
        period_stoch_rsi_fast = 14
        period_stoch_rsi_slow = 3

        past_data_window = {}
        past_data_window_length = 1440

        futures_ticker = get_ticker(authkey)
        now_unix_time = round(time.time() * 1000)

        futures_symbol_volume = [[x["symbol"], float(x["quoteVolume"])]
                                 for x in futures_ticker
                                 if x["symbol"][-4:] == "USDT" and now_unix_time - x["closeTime"] < delist_filter_ms]

        futures_symbol_volume_sort = sorted(futures_symbol_volume, key=lambda x: x[1], reverse=True)[
                                     0:top_volume_ticker_length]
        top_volume_symbol = [x[0] for x in futures_symbol_volume_sort]

        log_path_10m = "./tradelog/tradeLog10m{0}.csv".format(time.strftime("%y%m%d%H%M%S"))
        log_path_30m = "./tradelog/tradeLog30m{0}.csv".format(time.strftime("%y%m%d%H%M%S"))
        log_path_1h = "./tradelog/tradeLog1h{0}.csv".format(time.strftime("%y%m%d%H%M%S"))
        log_path_4h = "./tradelog/tradeLog4h{0}.csv".format(time.strftime("%y%m%d%H%M%S"))

        log_header = (ResultDataSet().get_log_header())

        bh.write_log(log_path_10m, log_header)
        bh.write_log(log_path_30m, log_header)
        bh.write_log(log_path_1h, log_header)
        bh.write_log(log_path_4h, log_header)

        while True:
            # 60sec candle update timer
            while True:
                now_sec = time.localtime(time.time()).tm_sec
                if now_sec == 0 + candle_update_delay_offset_sec:
                    sec_trigger_flag = True
                if now_sec == 1 + candle_update_delay_offset_sec and sec_trigger_flag is True:
                    sec_trigger_flag = False
                    now_time = time.strftime("%y-%m-%d %H:%M:%S")
                    print("in progress: " + now_time)
                    break
                time.sleep(0.1)

            candle = get_candle(authkey, top_volume_symbol)
            futures_ticker = get_ticker(authkey)
            prev_data = data
            data = []
            emit_data = []

            # delisted symbol update
            now_unix_time = round(time.time() * 1000)
            delist_symbol = [x["symbol"] for x in futures_ticker if now_unix_time - x["closeTime"] > delist_filter_ms]
            for i in delist_symbol:
                if i in top_volume_symbol:
                    top_volume_symbol.remove(i)
            top_volume_ticker = [x for x in candle if x["symbol"] in top_volume_symbol]

            for ticker in top_volume_ticker:
                symbol = ticker["symbol"]
                base_asset_volume = float(ticker["baseAssetVolume"])
                taker_buy_base_asset_volume = float(ticker["takerBuyBaseAssetVolume"])
                last_price = float(ticker["lastPrice"])
                open_price = float(ticker["openPrice"])
                high_price = float(ticker["highPrice"])
                low_price = float(ticker["lowPrice"])

                # candlestick data init and update
                candle_window = bh.get_value_by_key_in_symbol(prev_data, "candleWindow", symbol) or {
                    "openPrice": np.array([]),
                    "highPrice": np.array([]),
                    "lowPrice": np.array([]),
                    "lastPrice": np.array([]),
                    "baseAssetVolume": np.array([])
                }
                candle_window["openPrice"] = np.append(candle_window["openPrice"], open_price)
                candle_window["highPrice"] = np.append(candle_window["highPrice"], high_price)
                candle_window["lowPrice"] = np.append(candle_window["lowPrice"], low_price)
                candle_window["lastPrice"] = np.append(candle_window["lastPrice"], last_price)
                candle_window["baseAssetVolume"] = np.append(candle_window["baseAssetVolume"], base_asset_volume)

                if len(candle_window["openPrice"]) > price_window_size:
                    for key in candle_window.keys():
                        candle_window[key] = np.delete(candle_window[key], 0)

                price_window = bh.get_value_by_key_in_symbol(prev_data, "priceWindow", symbol) or []
                price_window.append(last_price)
                if len(price_window) > price_window_size:
                    del price_window[0]

                # Calc. RSI
                if len(price_window) > period_rsi:
                    rsi = talib.RSI(np.array(price_window), timeperiod=period_rsi)[-1]

                    prev_rsi = bh.get_value_by_key_in_symbol(prev_data, "rsi", symbol) or 0
                    rsi_window = bh.get_value_by_key_in_symbol(prev_data, "rsiWindow", symbol) or []

                    rsi_window, rsi_change, prev_day_rsi_avg_per = bh.process_ind_wcap_reg(
                        ind=rsi,
                        prev_ind=prev_rsi,
                        prev_window=rsi_window,
                        window_size=day_init_window_size
                    )
                else:
                    rsi = 0
                    rsi_window = []
                    rsi_change = 0
                    prev_day_rsi_avg_per = 0

                # Calc. MACD
                if len(price_window) > period_macd_slow:
                    macd, _, macd_hist = talib.MACD(
                        np.array(price_window),
                        fastperiod=period_macd_fast,
                        slowperiod=period_macd_slow,
                        signalperiod=period_macd_sig
                    )

                    # MACD
                    macd = macd[-1] / last_price

                    prev_macd = bh.get_value_by_key_in_symbol(prev_data, "macd", symbol) or 0
                    macd_window = bh.get_value_by_key_in_symbol(prev_data, "macdWindow", symbol) or []

                    macd_window, macd_change, prev_day_macd_avg_per = bh.process_ind_wcap_reg(
                        ind=macd,
                        prev_ind=prev_macd,
                        prev_window=macd_window,
                        window_size=day_init_window_size
                    )

                    # MACD hist
                    macd_hist = macd_hist[-1] / last_price

                    prev_macd_hist = bh.get_value_by_key_in_symbol(prev_data, "macdHist", symbol) or 0
                    macd_hist_window = bh.get_value_by_key_in_symbol(prev_data, "macdHistWindow", symbol) or []

                    macd_hist_window, macd_hist_change, prev_day_macd_hist_avg_per = bh.process_ind_wcap_reg(
                        ind=macd_hist,
                        prev_ind=prev_macd_hist,
                        prev_window=macd_hist_window,
                        window_size=day_init_window_size
                    )
                else:
                    macd = 0
                    macd_window = []
                    macd_change = 0
                    prev_day_macd_avg_per = 0

                    macd_hist = 0
                    macd_hist_window = []
                    macd_hist_change = 0
                    prev_day_macd_hist_avg_per = 0

                # Calc MFI21
                if len(price_window) > period_mfi:
                    mfi = talib.MFI(
                        high=candle_window["highPrice"],
                        low=candle_window["lowPrice"],
                        close=candle_window["lastPrice"],
                        volume=candle_window["baseAssetVolume"],
                        timeperiod=period_mfi
                    )[-1]

                    prev_mfi = bh.get_value_by_key_in_symbol(prev_data, "mfi", symbol) or 0
                    mfi_window = bh.get_value_by_key_in_symbol(prev_data, "mfiWindow", symbol) or []

                    mfi_window, mfi_change, prev_day_mfi_avg_per = bh.process_ind_wcap_reg(
                        ind=mfi,
                        prev_ind=prev_mfi,
                        prev_window=mfi_window,
                        window_size=day_init_window_size
                    )
                else:
                    mfi = 0
                    mfi_window = []
                    mfi_change = 0
                    prev_day_mfi_avg_per = 0

                # Calc Stochastic RSI
                if len(price_window) > period_stoch_rsi_fast:
                    stoch_len_rsi = talib.RSI(real=np.array(price_window), timeperiod=period_stoch_rsi_fast)

                    # ssd = stochastic slow d
                    _, ssd = talib.STOCH(
                        high=stoch_len_rsi,
                        low=stoch_len_rsi,
                        close=stoch_len_rsi,
                        fastk_period=period_stoch_rsi_fast,
                        slowk_period=period_stoch_rsi_slow,
                        slowk_matype=MA_Type.SMA,
                        slowd_period=period_stoch_rsi_slow,
                        slowd_matype=MA_Type.SMA
                    )
                    ssd = ssd[-1]

                    prev_ssd = bh.get_value_by_key_in_symbol(prev_data, "ssd", symbol) or 0
                    ssd_window = bh.get_value_by_key_in_symbol(prev_data, "ssdWindow", symbol) or []

                    ssd_window, ssd_change, prev_day_ssd_avg_per = bh.process_ind_wcap_reg(
                        ind=ssd,
                        prev_ind=prev_ssd,
                        prev_window=ssd_window,
                        window_size=day_init_window_size
                    )
                else:
                    ssd = 0
                    ssd_window = []
                    ssd_change = 0
                    prev_day_ssd_avg_per = 0

                ticker_dict = {
                    "symbol": symbol,
                    "baseAssetVolume": base_asset_volume,
                    "lastPrice": last_price,
                    "candleWindow": candle_window,
                    "priceWindow": price_window,
                    "rsi": rsi,
                    "rsiWindow": rsi_window,
                    "macd": macd,
                    "macdWindow": macd_window,
                    "macdHist": macd_hist,
                    "macdHistWindow": macd_hist_window,
                    "mfi": mfi,
                    "mfiWindow": mfi_window,
                    "ssd": ssd,
                    "ssdWindow": ssd_window,
                }
                data.append(ticker_dict)
                is_nan_ind = list(map(is_nan, (rsi, mfi, ssd)))
                if is_nan_ind == [False, False, False]:
                    print(is_nan_ind)
                    ind_score_1 = float(rsi) + float(mfi) + float(ssd)
                else:
                    print(is_nan_ind)
                    ind_score_1 = 0

                ind_score_2 = (float(rsi) + float(mfi) + float(ssd)) * float(prev_day_macd_avg_per)
                emit_data.append(
                    (symbol, last_price, ind_score_1, ind_score_2)
                )

                now_time = time.strftime("%y-%m-%d %H:%M:%S")

                logging_data = ResultDataSet(
                    nowTime=now_time,
                    symbol=symbol,
                    lastPrice=last_price,
                    indScore=ind_score_1
                )

                if past_data_window.get(symbol, None) is None:
                    past_data_window[symbol] = []

                past_data_window[symbol].append(logging_data)

                # 10m
                if len(past_data_window[symbol]) >= 10:
                    compare_data = past_data_window[symbol][-10]
                    if compare_data.ind_score != 0 and not np.isnan(compare_data.ind_score):
                        compare_data.price_dif = last_price / compare_data.last_price
                        bh.write_log(log_path_10m, compare_data)

                if len(past_data_window[symbol]) >= 30:
                    compare_data = past_data_window[symbol][-30]
                    if compare_data.ind_score != 0 and not np.isnan(compare_data.ind_score):
                        compare_data.price_dif = last_price / compare_data.last_price
                        bh.write_log(log_path_30m, compare_data)

                if len(past_data_window[symbol]) >= 60:
                    compare_data = past_data_window[symbol][-60]
                    if compare_data.ind_score != 0 and not np.isnan(compare_data.ind_score):
                        compare_data.price_dif = last_price / compare_data.last_price
                        bh.write_log(log_path_1h, compare_data)

                if len(past_data_window[symbol]) >= 360:
                    compare_data = past_data_window[symbol][-360]
                    if compare_data.ind_score != 0 and not np.isnan(compare_data.ind_score):
                        compare_data.price_dif = last_price / compare_data.last_price
                        bh.write_log(log_path_4h, compare_data)

                    del past_data_window[symbol][0]

            self.emit_signal.emit(emit_data)


class MainWindow(QMainWindow, uic.loadUiType(UI_PATH)[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init_ui()
        self.ticker_updater = TickerUpdater()
        self.ticker_updater.start()
        self.ticker_updater.emit_signal.connect(self.emit_signal)
        self.tableWidget.itemDoubleClicked.connect(self.open_binance)

    def open_binance(self, item):
        if item.column() == 0:
            webbrowser.open("www.binance.com/en/futures/" + item.text())

    def init_ui(self):
        pass

    def emit_signal(self, data):
        row_count = (len(data))
        column_count = (len(data[0]))
        self.tableWidget.setColumnCount(column_count)
        self.tableWidget.setRowCount(row_count)
        self.tableWidget.setHorizontalHeaderLabels(["symbol", "lastPrice", "indScore1", "indScore2"])
        self.tableWidget.setSortingEnabled(False)
        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem()
                item.setData(Qt.EditRole, data[row][col])
                self.tableWidget.setItem(row, col, item)
        self.tableWidget.setSortingEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myApp = MainWindow()
    myApp.show()
    sys.exit(app.exec_())