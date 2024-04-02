# FluoSA
Fluorescence Signal Analyzer (FluoSA) for calcium imaging on user-defined neural structures.

FluoSA inputs *.LIF files, detects user-defined neural structures, and quantifies the fluorescence signal changes (frame-wise fluorescence intensity and the dF/F0) in these structures.

<p>&nbsp;</p>

## Installation
### 1 Install FluoSA
```
python3 -m pip install FluoSA
```

<p>&nbsp;</p>

### 2 Install CUDA toolkit v11.8
https://developer.nvidia.com/cuda-11-8-0-download-archive?target_os=Windows&target_arch=x86_64

<p>&nbsp;</p>

### 3 Install PyTorch 2.0.1
#### 3.1 For Windows and Linux
##### 3.1.1 If using GPU
```
python3 -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
```
##### 3.1.2 CPU only
```
python3 -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu
```
#### 3.2 For Mac
```
python3 -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2
```

<p>&nbsp;</p>

### 4 Install Detectron2
```
python3 -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
```

<p>&nbsp;</p>

## Usage
In your terminal / command prompt, type:
```
FluoSA
```

Then the user interface will be initiated:

![alt text](https://github.com/umyelab/FluoSA/blob/main/Examples/GUI.png?raw=true) 

