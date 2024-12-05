binance-prediction
===

### 목적
  
암호화폐의 현재 가격 및 보조지표 활용 XGBoost와 LSTM 시계열 예측 모델을 통한 가격 변동폭 예측


### 실행 환경

- OS: Windows 10
- Python: 3.9.13
- NVIDIA CUDA: 11.2.0
- NVIDIA cuDNN: 8.1.1

### 프로젝트 특징(개발 필요성)
1. 일반적인 암호화폐 데이터 수집-예측 프로젝트는 단일 심볼의 처리에만 초점이 맞춰져 있지만, 이 프로젝트는 사용자화 가능한 파라미터로 **여러 심볼의 데이터를 한번에 수집** 할 수도 있으며, ML/DL 학습 시에도 **여러 심볼에 대한 동시 학습을 지원**합니다 (단일 심볼 데이터 처리 또한 지원합니다).

<br/>


2. 일반적인 암호화폐 데이터 수집-예측 프로젝트는 암호화폐 데이터 호출 API의 제한으로 인하여 분 단위의 데이터를 수집하여 학습에 사용할수 없지만, 이 프로젝트는 데이터 수집 과정을 실시간으로 처리하여 데이터 수집 시에 API 호출 제한을 받지 않으며, **분 단위 데이터를 수집할 수 있습니다**.

<br/>

3. 일반적인 암호화폐 가격 예측 프로젝트는 예측 목표, 또는 특징의 **[정상성](https://en.wikipedia.org/wiki/Stationary_process)을 고려하지 않는 경우가 많으며**, 이는 ML/DL 모델이 시계열 데이터로부터 정상적인 학습이 불가능하게 합니다. 이 프로젝트에서는 가능한 기본적인 시계열 분석 이론의 틀에서 벗어나지 않고 목표를 예측하려고 합니다.

<br>

### 의존성 설치

**1. TA-lib - 기술적 분석 라이브러리:**   
- C 기반 코어 라이브러리 설치 [TA-lib PyPI](https://pypi.org/project/ta-lib/#description)  
<br/>


**2. CUDA, cuDNN:** 
- [Nvidia Developer cuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive)  
- [Nvidia Developer CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)  
<br/>


**3. pip 의존성 설치:**
- ```$ pip install -r requirements.txt```  
<br/>

### 설명서

1. 데이터 수집: [datacollection](docs/datacollection.md)
2. datacollection을 통해 수집된 데이터 기반 ML/DL 예측: [predicttool](docs/predicttool.md)
