datacollection: 바이낸스 1m 캔들스틱 및 보조지표 데이터 수집 가이드
===

### 1. 바이낸스 API 발급

- python-binance 라이브러리의 `futures_klines()` 등 Raw data를 데이터를 가져오는 기능을 사용하기 위해서 Binance API와 연결이 필요하고, 이 때 **API key**및 **Secret key**를 요구합니다.  
  
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
|---|---|---|
|candle_update_delay_offset_sec|python-binance 라이브러리에서 futures_klines() 함수를 이용해서 캔들스틱 데이터를 가져올 때, 차트의 캔들스틱 데이터가 API에 반영될 때 까지의 약 5초의 시간이 걸립니다. 예를 들어 12:00:00 에 11:59:00 ~ 12:00:00 의 캔들스틱 데이터를 요청하면 실제로는 11:59:00 ~ 11:59:55 시점의 데이터가 반환됩니다. *candle_update_delay_offset_sec* 은 이 문제를 해결하기 위해서 요청 시작 시간을 지연시킵니다.|8|
|top_volume_ticker_length|bruh|
|price_window_size|b|
|day_init_window_size|b|
|delist_filter_ms|b|
