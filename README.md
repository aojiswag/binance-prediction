binance-prediction
===

### 목적
  
암호화폐 현재 가격 및 보조지표 활용 XGBoost와 LSTM 시계열 예측 모델을 통한 가격 변동폭 예측


### 실행 환경

- OS: Windows 10
- Python: 3.9.13
- NVIDIA CUDA: 11.2.0
- NVIDIA cuDNN: 8.1.1

### 의존성 설치

**1. TA-lib - 기술적 분석 라이브러리:**   
- C 기반 코어 라이브러리 설치 [TA-lib PyPI](https://pypi.org/project/ta-lib/#description)  
<br>


**2. CUDA, cuDNN:** 
- [Nvidia Developer cuDNN Archive](https://developer.nvidia.com/rdp/cudnn-archive)  
- [Nvidia Developer CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)  
<br>


**3. pip 의존성 설치:**
- ```$ pip install -r requirements.txt```  
<br>

### 설명서

1. 데이터 수집: [datacollection](docs/datacollection.md)
2. datacollection을 통해 수집된 데이터 기반 ML/DL 예측: [predicttool](docs/predicttool.md)
