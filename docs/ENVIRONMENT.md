# Environment and computational requirements

The original successful training environment has not been supplied. Do not describe the following inventory as that environment or as a tested compatibility matrix.

Observed locally during documentation preparation on 2026-11-08: Windows, Python 3.14.3. Installed distribution metadata:

```text
numpy==2.3.5
pandas==2.3.3
matplotlib==3.10.8
joblib==1.5.3
shap==0.50.0
torch==2.10.0+cu128
scikit-learn==1.7.2
xgboost==3.2.0
lightgbm==4.6.0
catboost==1.2.10
rasterio==1.5.0
openpyxl==3.1.5
```

Package metadata alone does not prove import compatibility or successful execution. CUDA is not required by the scripts: tensors remain on the CPU and there is no GPU selection logic. A CPU PyTorch installation is sufficient for the intended code path.

The default training configuration uses up to 8 workers in some estimators. RAM and runtime depend on input dimensions, estimators, SHAP and raster extent; no measured minimum RAM or runtime is currently available. Record CPU, RAM, OS, Python, packages, wall-clock duration and peak memory for the actual release run. Allow space for the approximately 2 GB input plus hundreds of MB of models and raster outputs. Mapping reads the entire input even when prediction is batched.

After validating the complete workflow in a clean environment, capture it:

```powershell
python --version
python -m pip check
python -m pip freeze > requirements-lock.txt
```

Review the lock for local/private paths before publishing. Keep `requirements.txt` as the direct dependency list and describe the platform and Python version associated with the lock. A lock generated from an unrelated environment is not reproduction evidence.
