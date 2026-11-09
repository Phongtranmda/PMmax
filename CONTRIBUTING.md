# Contributing

Use repository issues for reproducible bug reports and feature proposals after the public repository is created. Include OS, Python/package versions, relevant settings, exact error, and a minimal shareable example. Do not attach confidential data or large model files.

Keep comments and public documentation in English. Changes to feature order, preprocessing, train/test splitting, model architecture or raster registration must explain their scientific impact. Preserve original input data and use separate output directories for comparisons.

Before proposing changes, run `python scripts/check_repository.py` and `python -m unittest discover -s tests -v` in your scientific environment. The saved-model regression check is skipped if local model artifacts are absent. Report which tests were actually run; syntax checks alone do not validate scientific results. Submit a pull request describing the problem, behavior change and validation evidence. Confirm permission to contribute code and data under the adopted project license.
