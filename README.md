# FluoSA (Fluorescence Signal Analyzer)

<p>&nbsp;</p>

FluoSA inputs *.LIF and *.tif files, detects user-defined neural structures, and quantifies the fluorescence signal changes (frame-wise fluorescence intensity and the dF/F0) in these structures.

<p>&nbsp;</p>

The outputs of FluoSA include:

1. An annotated video showing the detected neural structures:

    ![alt text](https://github.com/yujiahu415/FluoSA/blob/main/Examples/Annotated_video.gif?raw=true) 

2. Spreadsheets storing frame-wise fluorescence intensity in each detected neural structure:

    ![alt text](https://github.com/yujiahu415/FluoSA/blob/main/Examples/Output_F.png?raw=true)

3. Spreadsheets storing summary of fluorescence signal changes (dF/F0) in each detected neural structure:

    ![alt text](https://github.com/yujiahu415/FluoSA/blob/main/Examples/Output_summary.png?raw=true)

<p>&nbsp;</p>

## Installation
### 1 Install FluoSA
```
python3 -m pip install FluoSA
```

### 2 Install CUDA toolkit v11.8
https://developer.nvidia.com/cuda-11-8-0-download-archive?target_os=Windows&target_arch=x86_64

### 3 Install Detectron2
```
python3 -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
```

### 4 Install PyTorch 2.0.1
#### 4.1 For Windows and Linux
##### 4.1.1 If using GPU
```
python3 -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu118
```
##### 4.1.2 CPU only
```
python3 -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cpu
```
#### 4.2 For Mac
```
python3 -m pip install torch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2
```

<p>&nbsp;</p>

## Usage
In your terminal / command prompt, type:
```
FluoSA
```

Then the user interface will be initiated:

![alt text](https://github.com/yujiahu415/FluoSA/blob/main/Examples/GUI.png?raw=true) 

