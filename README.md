# PMmax: earthquake maximum-magnitude modelling and mapping

PMmax is a Python research workflow for fitting regression models to maximum earthquake magnitude (`Mmax`) and exporting spatial predictions as GeoTIFF rasters. It contains two standalone scripts: training and evaluation, followed by prediction and raster export.

**Repository status:** source code, example inputs, trained models, output maps, evaluation tables, figures and training logs are included at https://github.com/Phongtranmda/PMmax. These are supplied example results, not a newly validated reproduction run. Remaining manuscript metadata, data licensing details and the verified reproduction environment still need documentation.

## Workflow

```text
EQ_sample_Mmax.xlsx → 1. Training_Mmax.py → Mmax_models/*.pkl
                                        → Mmax_results/*
Sample_area.txt + Mmax_models/*.pkl
                   → 2. Mmax_export_maps.py → Mmax_maps_results/*.tif
```

Training fits Linear, Ridge, Lasso, ElasticNet, SVR, RandomForest, ExtraTrees, XGBoost, LightGBM, CatBoost, MLP and a PyTorch DeepNN, followed by a stacking ensemble. It exports evaluation metrics, fitted models, diagnostic plots, and feature-importance/SHAP results where supported. Mapping predicts with **every `.pkl` file** in the configured model directory and exports each prediction, their mean, standard deviation, and coefficient of variation.

## Download the complete example and results

Install [Git LFS](https://git-lfs.com/), then run:

```bash
git lfs install
git clone https://github.com/Phongtranmda/PMmax.git
cd PMmax
git lfs pull
```

Use this method to obtain the actual large files; an archive or clone without LFS content may contain pointer files. The figures and evaluation workbooks in `Mmax_results/` can also be browsed or downloaded directly. Re-running the workflow can overwrite the supplied example outputs.

## Installation

Use a dedicated Python environment and run commands from this repository's root. Python 3.11 is a suggested fresh-install baseline, **not a verified reproduction environment**. The inspection environment uses Python 3.14.3; its observed package versions are recorded separately. Neither constitutes a confirmed environment for the original training run.

Windows PowerShell (with Python 3.11 installed):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

Linux/macOS (installation and full execution still require validation):

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip check
```

Use the environment's Python executable wherever `python` appears below. `requirements.txt` lists direct dependencies without claiming a tested version lock. See [environment notes](docs/ENVIRONMENT.md) for reproducibility and resource requirements.

## Run the workflow

1. Read the [data specification](docs/DATA.md). Place the training workbook at `Example data/EQ_sample_Mmax.xlsx`.
2. Train from the repository root:

   ```powershell
   python "1. Training_Mmax.py"
   ```

3. Use the included full mapping input (download it with Git LFS as described below), or create the small synthetic mapping example:

   ```powershell
   python scripts/make_synthetic_mapping_example.py
   ```

   For the example, change `INPUT_FILE` in `2. Mmax_export_maps.py` to `os.path.join(os.getcwd(), "Example data", "Sample_area_synthetic.csv")`. The synthetic file tests the interface and spatial export; it is not scientific evidence or a reproduction of the study area.
4. Verify `MODEL_DIR`, feature order, `PIXEL_SIZE`, and `CRS` in the mapping script, then run:

   ```powershell
   python "2. Mmax_export_maps.py"
   ```

5. Inspect `Mmax_results/evaluation.xlsx` and the rasters in `Mmax_maps_results/` using GIS software. Re-running scripts overwrites matching output files. Preserve earlier runs in separate directories.

These scripts use settings near the top of each file; they do not provide command-line arguments or an interactive interface. Importing a script executes its workflow, so run them as scripts. A full training run includes potentially expensive stacking SHAP calculations; no quick-training mode is provided.

## Inputs and outputs

| Item | Purpose |
| --- | --- |
| `1. Training_Mmax.py` | Fit and evaluate models; save diagnostics and serialized models |
| `2. Mmax_export_maps.py` | Load models and generate GeoTIFF rasters |
| `Example data/EQ_sample_Mmax.xlsx` | Numeric predictors followed by target in the last column |
| `Example data/Sample_area.txt` | Comma-separated coordinates and predictors; large external input |
| `Mmax_models/` | 13 fitted `.pkl` files for a complete training run |
| `Mmax_results/` | Evaluation workbook, diagnostic plots and conditional importance outputs |
| `Mmax_maps_results/` | One raster per model plus `Ensemble_Mean.tif`, `Uncertainty_STD.tif`, `CV.tif` |

The repository includes `Mmax_models/`, `Mmax_results/`, `Mmax_maps_results/`, `catboost_info/` and all example inputs as supporting example results. Large models (`*.pkl`), maps (`*.tif`) and `Example data/Sample_area.txt` use Git LFS. The complete files total approximately 3.5 GiB. Original local files are retained. See the [user guide](docs/USER_GUIDE.md) for settings, exact outputs and troubleshooting.

## Interpretation and reproducibility

- The training/test split uses 80%/20% with seed 42. Reported test metrics are from this holdout, not cross-validation averages. Five-fold shuffled cross-validation is used for the selected model's learning curve. No grid search is executed.
- The printed “Best model”, residual plot and learning curve select among the 12 individual models; Stacking is added later to the evaluation table and is not included in that selection.
- Mapping matches named predictors to each fitted estimator, including each Stacking base estimator. The Landsat aliases `LS8-Band 1`, `LS8-Band_1` and `LS8_Band_1` (bands 1–7) are supported. Missing, extra or ambiguous named features raise an error. Models without saved feature names still require the positional order documented in [DATA.md](docs/DATA.md). Keep `mmax_prediction.py` alongside Tool 2.
- Mapping replaces NaN predictor values with zero. Training has no corresponding imputation stage. This can affect scientific interpretation.
- `Uncertainty_STD` measures disagreement between loaded models, not a calibrated prediction interval. `CV` is a ratio, not a percentage. These products do not forecast earthquake occurrence time or probability.
- PyTorch seeds are not fixed and its wrapper does not switch the network into evaluation mode during prediction. Dropout/BatchNorm therefore affect repeatability and batch dependence. The existing numerical implementation has been preserved; see [reproducibility notes](docs/REPRODUCIBILITY.md) before using results in a manuscript.
- The raster transform uses the minimum X and maximum Y as the upper-left **corner**, without a half-cell offset. Confirm whether source XY values are cell centers before interpreting spatial alignment.

## Documentation and contribution

- [User guide and troubleshooting](docs/USER_GUIDE.md)
- [Input schema and data availability](docs/DATA.md)
- [Reproduction procedure and limitations](docs/REPRODUCIBILITY.md)
- [Environment and computational resources](docs/ENVIRONMENT.md)
- [GitHub publication checklist](docs/PUBLISHING.md)
- [Contributing](CONTRIBUTING.md) and [change history](CHANGELOG.md)

## Citation, authors and license

**Software author and copyright holder:** Tran Van Phong.

**Affiliation:** Institute of Earth Sciences, Vietnam Academy of Science and Technology.

**Contact:** [tvphong@ies.vast.vn](mailto:tvphong@ies.vast.vn).

**Associated manuscript:** in preparation for submission to *Computers & Geosciences*; not yet published. The manuscript title has not yet been supplied. No publication DOI is listed.

Software citation metadata are provided in [CITATION.cff](CITATION.cff). Before a versioned release, confirm the software title. Add release metadata and software DOI when available; add a paper citation only when its bibliographic details are verified. An unpublished manuscript does not need a fabricated DOI or publication year.

**License:** the software and its documentation are distributed under the [MIT License](LICENSE). Copyright (c) 2026 Tran Van Phong. Data and third-party dependencies require their own applicable terms; a software license does not establish permission to redistribute the example data.

The repository documentation was prepared with reference to the [journal's code and reproducibility requirements](https://shop.elsevier.com/journals/computers-and-geosciences/0098-3004) and [CAGEO author instructions](https://github.com/cageo/author_instructions). Documentation alone does not establish scientific reproducibility or journal acceptance.
