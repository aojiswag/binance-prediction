
class CorrelDataSet:
    def __init__(self, **data):
        self.now_time = data.get("nowTime", 0)
        self.symbol = data.get("symbol", 0)
        self.last_price = data.get("lastPrice", 0)
        self.lower_price = data.get("lowerPrice", 0)
        self.lower_price_per_now_price = data.get("lowerPricePerNowPrice", 0)

        self.base_asset_volume = data.get("baseAssetVolume", 0)

        self.volume_change = data.get("volumeChange", 0)
        self.buy_volume_ratio = data.get("buyVolumeRatio", 0)
        self.buy_volume_ratio_change = data.get("buyVolumeRatioChange", 0)

        self.ma_score = data.get("maScore", 0)

        self.rsi = data.get("rsi", 0)
        self.rsi_change = data.get("rsiChange", 0)
        self.prev_day_rsi_avg_per = data.get("prevDayRsiAvgPer", 0)

        self.macd = data.get("macd", 0)
        self.macd_change = data.get("macdChange", 0)
        self.prev_day_macd_avg_per = data.get("prevDayMacdAvgPer", 0)
        self.macd_hist = data.get("macdHist", 0)
        self.macd_hist_change = data.get("macdHistChange", 0)
        self.prev_day_macd_hist_avg_per = data.get("prevDayMacdHistAvgPer", 0)

        self.mfi = data.get("mfi", 0)
        self.mfi_change = data.get("mfiChange", 0)
        self.prev_day_mfi_avg_per = data.get("prevDayMfiAvgPer", 0)

        self.ssd = data.get("ssd", 0)
        self.ssd_change = data.get("ssdChange", 0)
        self.prev_day_ssd_avg_per = data.get("prevDaySsdAvgPer", 0)

    def update_last_price(self, _last_price):
        self.last_price = _last_price

    def recalc_lower_price_per_now_price(self):
        self.lower_price_per_now_price = self.last_price / self.lower_price

    def __iter__(self):
        for _, val in self.__dict__.items():
            yield val

    def get_log_header(self):
        return [x for x, _ in self.__dict__.items()]


class RegDataSet:
    def __init__(self, **data):
        self.now_time = data.get("nowTime", 0)
        self.symbol = data.get("symbol", 0)
        self.last_price = data.get("lastPrice", 0)

        self.base_asset_volume = data.get("baseAssetVolume", 0)
        self.ma_vol = data.get("maVol", 0)
        self.prev_day_ma_vol_per_vol = data.get("prevDayMaVolPerVol", 0)
        self.prev_day_ma_vol_per_ma_vol = data.get("prevDayMaVolPerMaVol", 0)
        self.volume_change = data.get("volumeChange", 0)
        self.buy_volume_ratio = data.get("buyVolumeRatio", 0)
        self.buy_volume_ratio_change = data.get("buyVolumeRatioChange", 0)

        self.ma_score = data.get("maScore", 0)

        ma_over_list = data.get("maOverList", [0 for _ in range(7)])

        self.ma_over_1 = ma_over_list[0]
        self.ma_over_2 = ma_over_list[1]
        self.ma_over_3 = ma_over_list[2]
        self.ma_over_4 = ma_over_list[3]
        self.ma_over_5 = ma_over_list[4]
        self.ma_over_6 = ma_over_list[5]
        self.ma_over_7 = ma_over_list[6]

        self.rsi = data.get("rsi", 0)
        self.rsi_change = data.get("rsiChange", 0)
        self.prev_day_rsi_avg_per = data.get("prevDayRsiAvgPer", 0)

        self.macd = data.get("macd", 0)
        self.macd_change = data.get("macdChange", 0)
        self.prev_day_macd_avg_per = data.get("prevDayMacdAvgPer", 0)
        self.macd_hist = data.get("macdHist", 0)
        self.macd_hist_change = data.get("macdHistChange", 0)
        self.prev_day_macd_hist_avg_per = data.get("prevDayMacdHistAvgPer", 0)

        self.mfi = data.get("mfi", 0)
        self.mfi_change = data.get("mfiChange", 0)
        self.prev_day_mfi_avg_per = data.get("prevDayMfiAvgPer", 0)

        self.ssd = data.get("ssd", 0)
        self.ssd_change = data.get("ssdChange", 0)
        self.prev_day_ssd_avg_per = data.get("prevDaySsdAvgPer", 0)

        self.price_dif = 0
        self.over_buy_limit = 0
        self.over_sell_limit = 0
        self.over_bin_limit = 0

    def __iter__(self):
        for _, val in self.__dict__.items():
            yield val

    def get_log_header(self):
        return [x for x, _ in self.__dict__.items()]


class DiffDataSet:
    def __init__(self, **data):
        self.now_time = data.get("nowTime", 0)
        self.symbol = data.get("symbol", 0)
        self.last_price = data.get("lastPrice", 0)

        self.base_asset_volume = data.get("baseAssetVolume", 0)
        self.prev_day_ma_vol_per_vol = data.get("prevDayMaVolPerVol", 0)

        self.volume_change = data.get("volumeChange", 0)
        self.buy_volume_ratio = data.get("buyVolumeRatio", 0)
        self.buy_volume_ratio_change = data.get("buyVolumeRatioChange", 0)

        self.ma_score = data.get("maScore", 0)

        self.rsi_change = data.get("rsiChange", 0)
        self.prev_day_rsi_avg_per = data.get("prevDayRsiAvgPer", 0)

        self.macd_change = data.get("macdChange", 0)
        self.prev_day_macd_avg_per = data.get("prevDayMacdAvgPer", 0)

        self.macd_hist_change = data.get("macdHistChange", 0)
        self.prev_day_macd_hist_avg_per = data.get("prevDayMacdHistAvgPer", 0)

        self.mfi_change = data.get("mfiChange", 0)
        self.prev_day_mfi_avg_per = data.get("prevDayMfiAvgPer", 0)

        self.ssd_change = data.get("ssdChange", 0)
        self.prev_day_ssd_avg_per = data.get("prevDaySsdAvgPer", 0)

    def __iter__(self):
        for _, val in self.__dict__.items():
            yield val

    def get_log_header(self):
        return [x for x, _ in self.__dict__.items()]


class YMode:
    DIF = "DIF"
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"
    BIN_LIMIT = "BIN_LIMIT"
