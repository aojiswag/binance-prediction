datacollection: 바이낸스 1분 캔들스틱 및 보조지표 데이터 수집 가이드
===

### 1. 바이낸스 API 발급

- python-binance 라이브러리의 `futures_klines()` 등 데이터를 가져오는 기능을 사용하기 위해서 Binance API와 연결이 필요하고, 이 때 **API key**및 **Secret key**를 요구합니다.  
  
- 아래의 가이드를 통해 API 키를 발급받을 수 있습니다  
  - [How to Create API Keys on Binance? -Binance FAQ](https://www.binance.com/en/support/faq/how-to-create-api-keys-on-binance-360002502072)

### 2. 바이낸스 API *env/settings.py* 등록

- 과정 1에서 발급받은 API 정보를 `binance-prediction/datacollection/env/settings.py`에 등록하여야 합니다.  
이 파일은 기본적으로 프로젝트에 포함되어있지 않으며, 동일 경로의
[settings_example.py](../datacollection/env/settings_example.py)
파일을 수정하여 등록할 수 있습니다.

```
from dataclasses import dataclass

@dataclass(frozen=True)
class ApiInfo:
    key: str = ""
    secret: str = ""

    def __getitem__(self, item):
        return self.key, self.secret
```

[settings_example.py](../datacollection/env/settings_example.py)는 위와 같은 구조이며  

ApiInfo 클래스의 **"key" 필드에는 Binance API의 "API key"** 를, **"secret" 필드에는 Binance API 의 "Secret Key"** 를 문자열 형태로 입력하고, `settings.py` 파일명으로 저장하여 `datacollection/env/`에 위치시켜야 합니다.  

### 3. *main.py* 실행

*main.py* 를 실행할 때 사용자화 가능한 파라미터의 목록입니다:

|파라미터|설명|기본값|
|-------|---|-----|
|candle_update_delay_offset_sec|*python-binance* 라이브러리에서 *futures_klines()* 함수를 이용해서 캔들스틱 데이터를 가져올 때, 차트의 캔들스틱 데이터가 API에 반영될 때 까지 약 5초의 시간이 걸립니다(그리고 이는 환경에 따라 차이가 있습니다).<br>예를 들어 *12:00:00* 에 *11:59:00~12:00:00* 의 캔들스틱 데이터를 요청하면 *11:59:00~11:59:55* 시점의 데이터가 반환됩니다. *candle_update_delay_offset_sec* 은 요청 시작 시간을 지연시켜 온전한 1분 캔들스틱 데이터를 반환할 수 있게 합니다.|8|
|top_volume_ticker_length|24시간 기준 거래량 상위 *top_volume_ticker_length* 개 심볼의 데이터를 수집합니다.|100|
|day_init_window_size|전일 대비 지표 변화량을 계산하기 위해 이전 데이터를 저장하는 Window의 크기입니다.|1440|
|price_window_size|RSI, MACD, MFI 등 보조지표를 계산하기 위해 데이터를 저장하는 Window의 크기입니다.|1440|
|delist_filter_ms|심볼의 상장폐지 여부를 확인하기 위하여 심볼 정보의 마지막으로 업데이트된 시간과 현재 시간을 비교하여 마지막 업데이트로부터 *delist_filter_ms* 이상 지났을 시 해당 심볼을 필터에 추가하고 더 이상 데이터가 수집되지 않게 합니다.|360000|
|ma_vol_window_size|어떤 심볼은 1분간 캔들스틱 거래량이 0인 경우가 발생합니다(즉, 1 분간 체결된 거래 없음). 이는 특정 연산 및 학습에 오류를 발생시킵니다. 따라서 오류가 발생할 수 있는 거래량 연산에서 거래량은 *ma_vol* 즉, 이동 평균 거래량으로 대신합니다.<br>이 파라미터는 *ma_vol* 을 계산할 때의 Window 크기입니다. 즉, 파라미터를 *x*로 설정하면 *x*분 만큼의 거래량을 이동평균합니다.|7|
|ma_score_target|현재 가격이 각 *ma_score_target*캔들 수 이동평균을 초과했는지 확인하고, 초과했을 경우 *ma_score*를 증가시킵니다.<br>예를 들어 *ma_score_target*이 (5, 10, 15) 이고, 현재 가격이 5캔들, 10캔들, 15캔들 이동평균 가격을 모두 초과했을 경우 *ma_score*는 3입니다.  |(5, 10, 15, 20, 30, 45, 60)|
|period_rsi|[TA-Lib Documentation: RSI](https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html?highlight=rsi#ta.momentum.rsi)의 window size|12
|period_macd_fast,<br>period_macd_slow,<br>period_macd_sig|[TA-Lib Documentation: MACD](https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html?highlight=macd#ta.trend.macd)의 window size|12,<br>26,<br>9
|period_mfi|[TA-Lib Documentation: MFI](https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html?highlight=mfi#ta.volume.MFIIndicator)의 window size|21
|period_stoch_rsi_fast,<br>period_stoch_rsi_slow|[TA-Lib Documentation: RSI](https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html?highlight=rsi#ta.momentum.rsi) + [TA-Lib Documentation: STOCH](https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html?highlight=stoch#ta.momentum.stoch).<br><br>StochRSI를 TA-Lib의 [stochrsi](https://technical-analysis-library-in-python.readthedocs.io/en/latest/ta.html?highlight=stochrsi#ta.momentum.stochrsi)를 사용하여 구현하지 않은 이유:<br> 바이낸스 거래 화면의 StochRSI와, TA-Lib 구현 StochRSI는 계산 방법에 차이가 있기에, 바이낸스 거래 화면의 StochRSI와 프로그램에서 계산된 StochRSI를 동기화하기 위함입니다. 이에 대한 [*Issue*](https://github.com/TA-Lib/ta-lib-python/issues/203#issuecomment-804149529)|14,<br>3
  

### 4. 수집되는 데이터
프로그램이 시작되면, *day_init_window_size*로 설정된 시간 이후에 `datacollection/tradelog` 폴더에 데이터가 저장됩니다.

저장되는 데이터의 구조는 다음과 같습니다.

|레이블|설명|
|-----|---|
|now_time|이 데이터가 저장된 시간.|
|symbol|Binance Futures 의 Symbol|
|last_price|현재 종가|
|base_asset_volume|1 캔들 거래량 (1분 거래량)|	
|prev_day_ma_vol_per_vol|1 캔들 거래량 / 전일 1 캔들 거래량 전체의 평균|
|volume_change|현재 1캔들 거래량 / 이전 1캔들 거래량|
|buy_volume_ratio|해당 가산자산 구매 거래량 / 해당 가산자상 판매 거래량|
|buy_volume_ratio_change|현재 *buy_volume_ratio* / 이전 *buy_volume_ratio*|
|ma_score|*ma_score_target* 캔들 이동평균 초과 개수|
|rsi_change|현재 RSI / 이전 RSI|
|prev_day_rsi_avg_per|현재 RSI / 전일 전체 RSI의 평균|	
|macd_change|현재 MACD / 이전 MACD|
|prev_day_macd_avg_per|현재 MACD / 전일 전체 MACD의 평균|
|macd_hist_change|현재 MACD 히스토그램 값 / 이전 MACD 히스토그램 값|
|prev_day_macd_hist_avg_per|현재 MACD 히스토그램 / 전일 전체 MACD 히스토그램의 평균|
|mfi_change|현재 Money Flow Index / 이전 Money Flow Index|
|prev_day_mfi_avg_per|현재 Money Flow Index / 전일 전체 Money Flow Index의 평균|
|ssd_change|현재 Stochastic RSI slow d 값 / 이전 Stochastic RSI slow d 값|
|prev_day_ssd_avg_per|현재 Stochastic RSI slow d / 전일 전체 Stochastic RSI slow d 평균|


이 데이터가 수집됐다면, [predicttool](docs/predicttool.md)을 통해 가격 변동 예측을 시도할 수 있습니다.