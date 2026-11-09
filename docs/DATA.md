# Input specification and data availability

## Training workbook

Default: `Example data/EQ_sample_Mmax.xlsx`, first worksheet, first row containing headers. The supplied workbook has 14,029 data rows and 15 columns. All columns except the last are used as predictors; the last is the target. Do not add identifiers, coordinates or an index column to this workbook unless deliberately changing the model.

Predictors must be numeric, finite, consistently encoded and supplied in this order:

| Position | Training column | Mapping column |
| --- | --- | --- |
| 1 | BGA | BGA |
| 2 | PGA | PGA |
| 3 | Geology | Geology |
| 4 | Elevation | Elevation |
| 5 | Slope | Slope |
| 6 | Curvature | Curvature |
| 7 | Aspect | Aspect |
| 8 | LS8-Band 1 | LS8_Band_1 |
| 9 | LS8-Band 2 | LS8_Band_2 |
| 10 | LS8-Band 3 | LS8_Band_3 |
| 11 | LS8-Band 4 | LS8_Band_4 |
| 12 | LS8-Band 5 | LS8_Band_5 |
| 13 | LS8-Band 6 | LS8_Band_6 |
| 14 | LS8-Band 7 | LS8_Band_7 |

The final training column is `Mmax`. The authors must document the magnitude scale, target construction, source references, predictor units, raster preprocessing, geology codebook, spatial coverage and data permissions before release. These details cannot be inferred reliably from column names.

## Mapping table

Default: `Example data/Sample_area.txt`. Despite the `.txt` extension, it is a comma-separated file with a header. `X` and `Y` are mandatory; `OBJECTID` is optional. All columns other than `OBJECTID`, `X`, and `Y` become model inputs in their existing order. Do not include the target or extra metadata columns.

For models with saved feature names, `mmax_prediction.py` reorders inputs to the fitted order and restores the estimator's exact spelling. It recognizes `LS8-Band 1`, `LS8-Band_1` and `LS8_Band_1` as aliases (bands 1–7). Each Stacking base estimator receives its own fitted names, accommodating LightGBM's underscore spelling alongside XGBoost's space spelling. Missing, unexpected and ambiguous names are rejected. Models without saved feature names still use positional input: retain the documented order when preparing files for the complete ensemble. Units and category meanings are not automatically checked.

Default CRS: `EPSG:32648` (WGS 84 / UTM zone 48N), with 30-unit cells. The script assigns this CRS; it does not transform coordinates. Input units and coordinate reference system must match the settings. Use regular grid coordinates, finite XY values and a unique row per intended cell. Duplicate cells overwrite earlier assignments. Missing cells retain NaN NoData. Confirm center-versus-corner registration against a reference raster.

Mapping NaNs become zero before prediction. The supplied file contains missing values. Zero replacement is implementation behavior, not a scientifically validated missing-data policy. Reject or deliberately preprocess other invalid values before running.

## Availability and rights

| Material | Local size | Publication handling |
| --- | ---: | --- |
| Training workbook | 1,384,093 bytes | Included locally and not ignored; confirm redistribution rights before committing |
| Full mapping table | 2,027,395,256 bytes | Excluded from Git; publish in a persistent data archive with download instructions |
| Fitted model directory | Several hundred MB | Excluded from Git; regenerate or archive the exact manuscript models |
| Synthetic mapping example | 20 × 20 cells | Generated without copying observations; interface test only |

**Author action required:** add the archive DOI/URL, data license, attribution, acquisition/preprocessing methods, and exact restoration paths here. No download link is currently available. A repository clone alone does not reproduce the full study-area maps. If data cannot be released, explain the restriction and access procedure; synthetic data do not reproduce the paper's findings.
