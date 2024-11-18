import functools
import time

import binance.exceptions
import binance.enums
from datetime import datetime


def write_log(path: str, data: iter):
    data = map(str, data)
    with open(path, "a") as log:
        log.write(",".join(data) + "\n")


def retry(count=5, sleep_sec=5, exceptions=()):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for cnt in range(count):
                try:
                    result = func(*args, **kwargs)
                    if result:
                        return result
                except exceptions as e:
                    error_log_path = "./tradelog/errorlog.txt"
                    write_log(error_log_path, ("R: ", e))
                    print("retry for ",e)
                    pass
                except Exception as e:
                    error_log_path = "./tradelog/errorlog.txt"
                    write_log(error_log_path, ("RF: ", e))
                    raise e

                time.sleep(sleep_sec)

        return wrapper

    return decorator


def unix_ms_time_to_datetime(ts):
    return datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d %H:%M:%S')


def process_ind_wcap(ind: float,
                     prev_ind: float,
                     prev_window: list,
                     prev_window_avg: float,
                     window_size: int) -> tuple[list, float, float]:
    """
    :param ind: sub indicator value
    :param prev_ind: prev_indicator value
    :param prev_window: prev_indicator window
    :param prev_window_avg: prev_indicator window average
    :param window_size: indicator window size
    :return: tuple[new_ind_window, indicator change, prev_ind_avg_per]
    """

    ind_change = ind / prev_ind if prev_ind else 0
    prev_window.append(ind)

    if len(prev_window) > window_size:
        del prev_window[0]

    prev_ind_window_avg_per = ind / prev_window_avg if prev_window_avg else 0

    return prev_window, ind_change, prev_ind_window_avg_per


def process_ind_wcap_reg(ind: float,
                         prev_ind: float,
                         prev_window: list,
                         window_size: int) -> tuple[list, float, float]:
    """
    :param ind: sub indicator value
    :param prev_ind: prev_indicator value
    :param prev_window: prev_indicator window
    :param window_size: indicator window size
    :return: tuple[new_ind_window, indicator change, prev_ind_avg_per], if len(new_ind_window) < window_size: prev_ind_avg_per return 0
    """

    ind_change = ind / prev_ind if prev_ind else 0
    prev_window.append(ind)

    prev_window_avg = 0
    if len(prev_window) > window_size:
        del prev_window[0]
        prev_window_avg = sum(prev_window) / len(prev_window)

    prev_ind_window_avg_per = ind / prev_window_avg if prev_window_avg else 0

    return prev_window, ind_change, prev_ind_window_avg_per


def get_last_1m_candle(cl: binance.Client, symbols: iter):
    candles = []
    full_range_candle = []
    key_label = (
        "openTime",
        "openPrice",
        "highPrice",
        "lowPrice",
        "lastPrice",
        "volume",
        "closeTime",
        "baseAssetVolume",
        "numberOfTrades",
        "takerBuyVolume",
        "takerBuyBaseAssetVolume",
        "ignore"
    )

    for symbol in symbols:
        klines = cl.futures_klines(
            symbol=symbol,
            interval=binance.enums.KLINE_INTERVAL_1MINUTE,
            limit=3
        )
        dict_klines = [
            {
                **{key_label[label_i]: klines[kline_i][label_i] for label_i in range(len(key_label))}, 'symbol': symbol
            } for kline_i in range(len(klines))
        ]
        candles.append(dict_klines)

        time.sleep(0.11)

    for candle in candles:
        for kline in reversed(candle):
            if kline["openTime"] + 60 * 1000 <= round(time.time() * 1000):
                full_range_candle.append(kline)
                break

    return full_range_candle


def get_kline(cl: binance.Client, symbols: iter, limit: int):
    candles = []
    key_label = (
        "openTime",
        "openPrice",
        "highPrice",
        "lowPrice",
        "lastPrice",
        "volume",
        "closeTime",
        "baseAssetVolume",
        "numberOfTrades",
        "takerBuyVolume",
        "takerBuyBaseAssetVolume",
        "ignore"
    )

    for symbol in symbols:
        klines = cl.futures_klines(
            symbol=symbol,
            interval=binance.enums.KLINE_INTERVAL_1HOUR,
            limit=limit
        )[:-1]
        dict_klines = [
            {
                **{key_label[label_i]: klines[kline_i][label_i] for label_i in range(len(key_label))}, 'symbol': symbol
            } for kline_i in range(len(klines))
        ]
        candles.append(dict_klines)

    return candles


def get_quantity_precision(cl: binance.Client, sym: str):
    info = cl.futures_exchange_info()
    time.sleep(0.1)
    for x in info['symbols']:
        if x["symbol"] == sym:
            return x['quantityPrecision']
    time.sleep(0.1)


def get_price_precision(cl: binance.Client, sym: str):
    info = cl.futures_exchange_info()
    time.sleep(0.1)
    for x in info['symbols']:
        if x["symbol"] == sym:
            return x['pricePrecision']


def get_volume_by_symbol(d: list, sym: str):
    for i in d:
        if i["symbol"] == sym:
            return i["quoteVolume"]


def get_last_price_by_symbol(d: list, sym: str):
    for i in d:
        if i["symbol"] == sym:
            return i["lastPrice"]


def get_ma_list_by_symbol(d: list, sym: str):
    for i in d:
        if i["symbol"] == sym:
            return i["maList"]


def get_value_by_key_in_symbol(d: list, key: str, sym: str):
    for i in d:
        if i["symbol"] == sym:
            return i[key]


def get_user_futures_usdt_balance(cl: binance.Client):
    account_balance = cl.futures_account_balance()
    time.sleep(0.1)
    for balance in account_balance:
        if balance['asset'] == 'USDT':
            return float(balance['balance'])


def create_order_buy_market(cl: binance.Client, sym: str, amount: float, leverage: int, margin_type: str):
    try:
        cl.futures_change_margin_type(
            symbol=sym,
            marginType=margin_type
        )
    except binance.exceptions.BinanceAPIException:
        print("Skip margin type set")

    time.sleep(0.1)

    cl.futures_change_leverage(
        symbol=sym,
        leverage=leverage
    )
    time.sleep(0.1)

    cl.futures_create_order(
        symbol=sym,
        side='BUY',
        type='MARKET',
        quantity=amount
    )
    time.sleep(0.1)


def create_order_sell_market(cl: binance.Client, sym: str, amount: float, leverage: int, margin_type: str):
    try:
        cl.futures_change_margin_type(
            symbol=sym,
            marginType=margin_type
        )
    except binance.exceptions.BinanceAPIException:
        print("Skip margin type set")

    cl.futures_change_leverage(
        symbol=sym,
        leverage=leverage
    )

    cl.futures_create_order(
        symbol=sym,
        side='SELL',
        type='MARKET',
        quantity=amount
    )


def create_order_market_sell_close(cl: binance.Client, sym: str, qnt: float):
    cl.futures_create_order(
        symbol=sym,
        type="MARKET",
        side="SELL",
        reduceOnly="true",
        quantity=qnt
    )
    time.sleep(0.1)


def get_ticker_quantity(cl: binance.Client, sym: str):
    amt = cl.futures_position_information(symbol=sym)[0]["positionAmt"]
    time.sleep(0.1)

    return amt


def create_order_range_close(cl: binance.Client, sym: str, sl_price: float, tf_price: float):
    cl.futures_create_order(
        symbol=sym,
        type="STOP_MARKET",
        side="SELL",
        stopPrice=sl_price,
        closePosition="true"
    )

    time.sleep(0.1)

    cl.futures_create_order(
        symbol=sym,
        type="TAKE_PROFIT_MARKET",
        side="SELL",
        stopPrice=tf_price,
        closePosition="true"
    )
    time.sleep(0.1)


def create_order_range_close_short(cl: binance.Client, sym: str, sl_price: float, tf_price: float):
    cl.futures_create_order(
        symbol=sym,
        type="TAKE_PROFIT_MARKET",
        side="BUY",
        stopPrice=tf_price,
        closePosition="true"
    )

    time.sleep(0.1)

    cl.futures_create_order(
        symbol=sym,
        type="STOP_MARKET",
        side="BUY",
        stopPrice=sl_price,
        closePosition="true"
    )


def query_open_order(cl: binance.Client, sym: str):
    return cl.futures_get_open_orders(symbol=sym)


def query_position(cl: binance.Client, sym: str):
    return cl.futures_position_information(symbol=sym)


def cancel_all_open_orders(cl: binance.Client, sym: str):
    cl.futures_cancel_all_open_orders(symbol=sym)
