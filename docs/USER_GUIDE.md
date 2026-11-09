# User guide

## Training settings

Edit `1. Training_Mmax.py` directly. Paths are relative to the working directory, so launch from the repository root.

| Setting | Default | Meaning |
| --- | --- | --- |
| `RANDOM_STATE` | 42 | Split, several estimators, learning curve folds and importance sampling |
| `TEST_SIZE` | 0.2 | Holdout fraction |
| `CV_FOLDS` | 5 | Learning curve folds |
| `OUTPUT_DIR` | `Mmax_results` | Metrics and figures |
| `MODEL_DIR` | `Mmax_models` | Serialized fitted models |

`N_JOBS = 1` is not a global worker limit: several estimators explicitly use 8 workers and stacking estimators/permutation importance use 4. Edit those settings individually when limiting CPU use. Hyperparameters and the workbook path are defined in the source. `GridSearchCV` is imported but not run.

Training writes these outputs:

- `evaluation.xlsx`: Model, Train R2, Test R2, RMSE, MAE and MAPE (%), sorted by Test R2. MAPE uses an epsilon of `1e-8` in the denominator.
- `residual.png` and `learning_curve.png`: diagnostics for the best individual model by holdout R2, excluding Stacking.
- `shap_summary.png`: conditional on successful SHAP explanation of the selected individual model; errors are printed and this plot may be absent.
- `SHAP_stacking_summary.png` and `SHAP_stacking_bar.png`: stacking Kernel SHAP outputs. This call is not protected by the preceding exception handler; a failure stops later steps.
- `feature_importance.xlsx` and `importance.png`: only when the selected model exposes `feature_importances_`.
- `stacking_feature_importance.xlsx` and `stacking_importance.png`: permutation importance, 10 repeats. Earlier SHAP failure prevents their creation.
- 13 model files in `Mmax_models/`: Linear, Ridge, Lasso, ElasticNet, SVR, RandomForest, ExtraTrees, XGBoost, LightGBM, CatBoost, MLP, DeepNN and Stacking, each with `.pkl` extension.

## Mapping settings

Keep `mmax_prediction.py` in the same directory as `2. Mmax_export_maps.py`. It aligns named inputs separately for each fitted model and each Stacking base estimator. Supported Landsat spellings include `LS8-Band 1`, `LS8-Band_1` and `LS8_Band_1` for bands 1–7. This fixes the saved Stacking model's mixed LightGBM/XGBoost naming without retraining or disabling feature validation. Models without saved names still require the documented predictor order.

| Setting | Default | Meaning |
| --- | --- | --- |
| `MODEL_DIR` | `Mmax_models` | Loads every `.pkl` file in this directory |
| `INPUT_FILE` | `Example data/Sample_area.txt` | Comma-separated spatial inputs |
| `OUTPUT_DIR` | `Mmax_maps_results` | GeoTIFF destination |
| `PIXEL_SIZE` / `CELL_SIZE` | 30 | Cell dimensions in CRS units |
| `CRS` | `EPSG:32648` | Assigned output CRS |
| `BATCH_SIZE` | 500000 | Prediction rows per batch |

For a small example, run `python scripts/make_synthetic_mapping_example.py`, point `INPUT_FILE` at `Example data/Sample_area_synthetic.csv`, and keep the default CRS and 30-unit cell size. Train first or restore trusted compatible models. Full training is still required if no models exist. For a deliberately reduced mapping run, copy selected trusted models into a separate directory and set `MODEL_DIR` accordingly; ensemble statistics then describe only that subset.

Outputs are single-band float32 GeoTIFFs with NaN NoData. A complete 13-model run produces 16 rasters. `Ensemble_Mean` is the unweighted mean across all loaded models (including Stacking); `Uncertainty_STD` is NumPy's population standard deviation (`ddof=0`); `CV = Uncertainty_STD / (Ensemble_Mean + 1e-6)`. CV is not multiplied by 100 and can be unstable near zero. The script does not save a prediction CSV.

Raster width and height are `int(coordinate_range / CELL_SIZE) + 1`. Rows increase southward from maximum Y. The full input, all prediction arrays and full rasters are held in memory; batching only limits individual prediction calls.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| File not found | Run from the repository root and check the configured input path |
| No models found | Run training first or restore models to `MODEL_DIR` |
| Feature mismatch or implausible predictions | Check count, order, units and category coding against the training table |
| Missing Excel engine | Install `openpyxl` in the environment running the script |
| Cannot load a model | Restore the original training environment; do not assume pickle compatibility across library versions |
| DeepNN class cannot be found | Run the provided mapping script directly; it defines the class needed by the saved object |
| Memory exhausted | Start with the synthetic input; reduce prediction batch size and spatial extent; full table/raster memory remains allocated |
| Misaligned output map | Verify CRS, grid spacing and whether XY values are centers or corners |
| SHAP skipped or slow | Read the console output; generic SHAP is conditional and stacking Kernel SHAP may be expensive |
| Different repeated DeepNN predictions | See the documented PyTorch training-mode and random-seed limitations |

Only load model files from trusted sources: joblib/pickle deserialization can execute code. Keep training and mapping package versions consistent.
