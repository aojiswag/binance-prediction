from binance.client import Client
import time


import binancehelper as bh
import logdataset
from env import settings
import talib
from talib import MA_Type
import numpy as np

import requests.exceptions
import urllib3.exceptions
import traceback


@bh.retry(count=40, sleep_sec=1,
          exceptions=(ConnectionResetError, urllib3.exceptions.ProtocolError, requests.exceptions.ConnectionError, Exception))
def get_ticker(api: settings.ApiInfo):
    client = Client(api_key=api.key, api_secret=api.secret)
    tkr = client.futures_ticker()
    client.close_connection()

    return tkr


@bh.retry(count=40, sleep_sec=1,
          exceptions=(ConnectionResetError, urllib3.exceptions.ProtocolError, requests.exceptions.ConnectionError, Exception))
def get_candle(api: settings.ApiInfo, symbols: iter):
    client = Client(api_key=api.key, api_secret=api.secret)
    candles = bh.get_last_1m_candle(cl=client, symbols=symbols)
    client.close_connection()

    return candles


error_log_path = "./tradelog/errorlog.txt"


def main():
    authkey = settings.ApiInfo()

    futures_ticker = get_ticker(authkey)

    candle_update_delay_offset_sec = 8
    top_volume_ticker_length = 30

    price_window_size = 720
    day_init_window_size = price_window_size
    day_init_count = 0

    delist_filter_ms = 86400000 * 2

    now_time = time.strftime("%y%m%d%H%M%S")
    trade_log_path = "./tradelog/tradeLog{0}.csv".format(now_time)
    correl_log_path = "./tradelog/correlLog{0}.csv".format(now_time)

    log_header = (logdataset.LogDataSet().get_log_header())

    bh.write_log(trade_log_path, log_header)
    bh.write_log(correl_log_path, log_header)

    now_unix_time = round(time.time() * 1000)

    futures_symbol_volume = [[x["symbol"], float(x["quoteVolume"])]
                             for x in futures_ticker
                             if x["symbol"][-4:] == "USDT" and now_unix_time - x["openTime"] < delist_filter_ms]
    print(futures_symbol_volume)

    futures_symbol_volume_sort = sorted(futures_symbol_volume, key=lambda x: x[1], reverse=True)[0:top_volume_ticker_length]
    top_volume_symbol = [x[0] for x in futures_symbol_volume_sort]

    data = []
    lower_price_data = {}
    sec_trigger_flag = False

    period_rsi = 12
    period_macd_fast = 12
    period_macd_slow = 26
    period_macd_sig = 9
    period_mfi = 21
    period_stoch_rsi_fast = 14
    period_stoch_rsi_slow = 3
    ma_score_target = (5, 10, 15, 20, 30, 45, 60)

    while True:
        # 60sec candle update timer
        while True:
            now_sec = time.localtime(time.time()).tm_sec
            if now_sec == 0 + candle_update_delay_offset_sec:
                sec_trigger_flag = True
            if now_sec == 1 + candle_update_delay_offset_sec and sec_trigger_flag is True:
                sec_trigger_flag = False
                break
            time.sleep(0.1)

        candle = get_candle(authkey, top_volume_symbol)
        futures_ticker = get_ticker(authkey)
        prev_data = data
        data = []

        # delisted symbol update
        now_unix_time = round(time.time() * 1000)
        delist_symbol = [x["symbol"] for x in futures_ticker if now_unix_time - x["openTime"] > delist_filter_ms]
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

            # MA Score
            ma_score = 0
            if max(ma_score_target) < len(price_window):
                for i in ma_score_target:
                    ma_result = sum(price_window[-i:]) / i
                    if ma_result < last_price:
                        ma_score = ma_score + 1

            # Calc. Volume change
            prev_base_asset_volume = bh.get_value_by_key_in_symbol(prev_data, "baseAssetVolume", symbol) or 0
            volume_change = base_asset_volume / prev_base_asset_volume if prev_base_asset_volume else 0

            # Buy - sell volume ratio
            sell_volume = (base_asset_volume - taker_buy_base_asset_volume) or 1
            prev_buy_volume_ratio = bh.get_value_by_key_in_symbol(prev_data, "buyVolumeRatio", symbol) or 0
            buy_volume_ratio = taker_buy_base_asset_volume / sell_volume
            buy_volume_ratio_change = buy_volume_ratio / prev_buy_volume_ratio if prev_buy_volume_ratio else 0

            # Calc. RSI
            if len(price_window) > period_rsi:
                rsi = talib.RSI(np.array(price_window), timeperiod=period_rsi)[-1]
                prev_rsi = bh.get_value_by_key_in_symbol(prev_data, "rsi", symbol) or 0
                rsi_window = bh.get_value_by_key_in_symbol(prev_data, "rsiWindow", symbol) or []
                prev_day_rsi_avg = bh.get_value_by_key_in_symbol(prev_data, "prevDayRsiAvg", symbol) or 0

                rsi_window, rsi_change, prev_day_rsi_avg_per = bh.process_ind_wcap(
                    ind=rsi,
                    prev_ind=prev_rsi,
                    prev_window=rsi_window,
                    prev_window_avg=prev_day_rsi_avg,
                    window_size=day_init_window_size
                )
            else:
                rsi = 0
                rsi_window = []
                rsi_change = 0
                prev_day_rsi_avg = 0
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
                macd = macd[-1]
                prev_macd = bh.get_value_by_key_in_symbol(prev_data, "macd", symbol) or 0
                macd_window = bh.get_value_by_key_in_symbol(prev_data, "macdWindow", symbol) or []
                prev_day_macd_avg = bh.get_value_by_key_in_symbol(prev_data, "prevDayMacdAvg", symbol) or 0

                macd_window, macd_change, prev_day_macd_avg_per = bh.process_ind_wcap(
                    ind=macd,
                    prev_ind=prev_macd,
                    prev_window=macd_window,
                    prev_window_avg=prev_day_macd_avg,
                    window_size=day_init_window_size
                )

                # MACD hist
                macd_hist = macd_hist[-1]
                prev_macd_hist = bh.get_value_by_key_in_symbol(prev_data, "macdHist", symbol) or 0
                macd_hist_window = bh.get_value_by_key_in_symbol(prev_data, "macdHistWindow", symbol) or []
                prev_day_macd_hist_avg = bh.get_value_by_key_in_symbol(prev_data, "prevDayMacdHistAvg", symbol) or 0

                macd_hist_window, macd_hist_change, prev_day_macd_hist_avg_per = bh.process_ind_wcap(
                    ind=macd_hist,
                    prev_ind=prev_macd_hist,
                    prev_window=macd_hist_window,
                    prev_window_avg=prev_day_macd_hist_avg,
                    window_size=day_init_window_size
                )
            else:
                macd = 0
                macd_window = []
                macd_change = 0
                prev_day_macd_avg = 0
                prev_day_macd_avg_per = 0

                macd_hist = 0
                macd_hist_window = []
                macd_hist_change = 0
                prev_day_macd_hist_avg = 0
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
                prev_day_mfi_avg = bh.get_value_by_key_in_symbol(prev_data, "prevDayMfiAvg", symbol) or 0

                mfi_window, mfi_change, prev_day_mfi_avg_per = bh.process_ind_wcap(
                    ind=mfi,
                    prev_ind=prev_mfi,
                    prev_window=mfi_window,
                    prev_window_avg=prev_day_mfi_avg,
                    window_size=day_init_window_size
                )
            else:
                mfi = 0
                mfi_window = []
                mfi_change = 0
                prev_day_mfi_avg = 0
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
                prev_day_ssd_avg = bh.get_value_by_key_in_symbol(prev_data, "prevDaySsdAvg", symbol) or 0

                ssd_window, ssd_change, prev_day_ssd_avg_per = bh.process_ind_wcap(
                    ind=ssd,
                    prev_ind=prev_ssd,
                    prev_window=ssd_window,
                    prev_window_avg=prev_day_ssd_avg,
                    window_size=day_init_window_size
                )
            else:
                ssd = 0
                ssd_window = []
                ssd_change = 0
                prev_day_ssd_avg = 0
                prev_day_ssd_avg_per = 0

            lower_price = min(price_window)
            prev_lower_price = bh.get_value_by_key_in_symbol(prev_data, "lowerPrice", symbol) or 0
            lower_price_per_now_price = last_price / lower_price

            ticker_dict = {
                "symbol": symbol,
                "baseAssetVolume": base_asset_volume,
                "buyVolumeRatio": buy_volume_ratio,
                "lastPrice": last_price,
                "lowerPrice": lower_price,
                "candleWindow": candle_window,
                "priceWindow": price_window,
                "rsi": rsi,
                "rsiWindow": rsi_window,
                "prevDayRsiAvg": prev_day_rsi_avg,
                "macd": macd,
                "macdWindow": macd_window,
                "prevDayMacdAvg": prev_day_macd_avg,
                "macdHist": macd_hist,
                "macdHistWindow": macd_hist_window,
                "prevDayMacdHistAvg": prev_day_macd_hist_avg,
                "mfi": mfi,
                "mfiWindow": mfi_window,
                "prevDayMfiAvg": prev_day_mfi_avg,
                "ssd": ssd,
                "ssdWindow": ssd_window,
                "prevDaySsdAvg": prev_day_ssd_avg
            }
            data.append(ticker_dict)

            now_time = time.strftime("%y-%m-%d %H:%M:%S")
            logging_data = logdataset.CorrelDataSet(
                nowTime=now_time,
                symbol=symbol,
                lastPrice=last_price,
                lowerPrice=lower_price,
                lowerPricePerNowPrice=lower_price_per_now_price,
                baseAssetVolume=base_asset_volume,
                volumeChange=volume_change,
                buyVolumeRatio=buy_volume_ratio,
                buyVolumeRatioChange=buy_volume_ratio_change,
                maScore=ma_score,
                rsi=rsi,
                rsiChange=rsi_change,
                prevDayRsiAvgPer=prev_day_rsi_avg_per,
                macd=macd,
                macdChange=macd_change,
                prevDayMacdAvgPer=prev_day_macd_avg_per,
                macdHist=macd_hist,
                macdHistChange=macd_hist_change,
                prevDayMacdHistAvgPer=prev_day_macd_hist_avg_per,
                mfi=mfi,
                mfiChange=mfi_change,
                prevDayMfiAvgPer=prev_day_mfi_avg_per,
                ssd=ssd,
                ssdChange=ssd_change,
                prevDaySsdAvgPer=prev_day_ssd_avg_per
            )

            if lower_price != prev_lower_price:
                lower_price_data[symbol] = logging_data

            bh.write_log(trade_log_path, logging_data)

        day_init_count += 1
        # Day init and write correlation analysis log
        if day_init_count == day_init_window_size:
            day_init_count = 0
            for vals in lower_price_data.values():
                vals.update_last_price(bh.get_value_by_key_in_symbol(data, "lastPrice", vals.symbol))
                vals.recalc_lower_price_per_now_price()
                bh.write_log(correl_log_path, vals)

            for i in data:
                i["prevDayRsiAvg"] = sum(i["rsiWindow"]) / len(i["rsiWindow"])
                i["prevDayMacdAvg"] = sum(i["macdWindow"]) / len(i["macdWindow"])
                i["prevDayMacdHistAvg"] = sum(i["macdHistWindow"]) / len(i["macdHistWindow"])
                i["prevDayMfiAvg"] = sum(i["mfiWindow"]) / len(i["mfiWindow"])
                i["prevDaySsdAvg"] = sum(i["ssdWindow"]) / len(i["ssdWindow"])

        now_time = time.strftime("%y-%m-%d %H:%M:%S")
        print("log updated" + now_time)


if __name__ == "__main__":
    try:
        t = time.strftime("%y-%m-%d %H:%M:%S")
        bh.write_log(error_log_path, ("A: ", t, "start program"))
        main()
    except Exception as e:
        t = time.strftime("%y-%m-%d %H:%M:%S")
        bh.write_log(error_log_path, ("E: ", t, e, traceback.format_exc()))
        exit()
