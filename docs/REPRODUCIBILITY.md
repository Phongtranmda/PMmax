# Reproducing and validating results

## Current status

The initial documentation preparation did not repeat the expensive full training or full-area mapping run. The author subsequently reported a Stacking feature-name mismatch in Tool 2. The mapping adapter now aligns names separately for each fitted base estimator without changing saved weights or retraining. Existing output files are evidence of an earlier run, not validation of the updated full-area workflow. Some conditional or late-stage outputs are absent from the local results directory.

Run `python -m unittest discover -s tests -v` for feature-alignment regression checks. Tests cover alias matching, reordered inputs, invalid schemas, unnamed estimators and equivalence to native sklearn stacking with and without passthrough. When the local `Mmax_models/Stacking.pkl` is present, an additional check compares 64 workbook rows against independently prepared base-model predictions and verifies batched equivalence and absence of feature-name warnings. This saved-model check is skipped when artifacts are unavailable. Full-area execution remains unverified.

## Release validation procedure

1. Record the manuscript identifier, source commit, exact environment, input sources/licenses and SHA-256 hashes. Record every changed script setting.
2. Use a clean environment and fresh output directories. Ensure old `.pkl` files cannot enter the mapping ensemble.
3. Train with the documented workbook. Save console logs, metrics, actual selected model and all produced diagnostics. Explicitly explain any missing conditional outputs.
4. Generate the synthetic mapping input, point the map script at it, and verify raster count, 20 × 20 dimensions, CRS, resolution and NoData with GIS software. This checks the interface, not scientific prediction accuracy.
5. Restore the exact full-area input and original map settings. Run full mapping and verify registration against a reference raster, numerical ranges and spatial coverage.
6. Compare metrics and rasters against the manuscript with stated numerical tolerances. Record differences; do not silently replace published evidence.
7. Archive the exact inputs, model artifacts, results and environment for the release. Add persistent download links and checksums to `docs/DATA.md`. Tag the corresponding source commit.

## Existing behavior requiring scientific review

- The “best” individual model is chosen using holdout R2. That holdout therefore also influences model selection; it is not an untouched external validation set.
- The split and learning-curve folds are random, not spatially blocked. Spatial dependence and extrapolation require a study-specific validation discussion.
- Stacking uses scikit-learn's default internal cross-validation, not the shuffled `kf` used by the learning curve.
- NumPy/PyTorch are not comprehensively seeded; DeepNN predictions retain active dropout and training-mode BatchNorm. Repeated predictions, batch size and batch composition can change values. A final one-row batch may fail BatchNorm. Exact repeated DeepNN results are not guaranteed.
- Mapping aligns names and known Landsat aliases for named estimators; models without saved feature names still use positional order. Units and scientific meaning are not automatically validated.
- Training does not impute missing data; mapping replaces NaNs with zero. Describe and justify the data preparation used in the paper.
- Raster registration does not apply a half-cell shift; non-grid-aligned coordinates are truncated into cells and duplicates overwrite. Check the input grid convention.
- Ensemble spread is model disagreement, not total predictive uncertainty or a confidence interval.

These points are documented rather than silently corrected because changing them can change published numerical results. Any scientific correction should be released separately with validation and an explanation of its effect.
