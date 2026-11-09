# Change history

## Unreleased — Stacking mapping fix

- Fixed mixed Landsat feature spellings in fitted Stacking base estimators by aligning inputs separately for each estimator.
- Added named feature reordering and explicit rejection of missing, extra or ambiguous features; unnamed estimators retain positional inputs.
- Preserved fitted weights and sklearn's stacking prediction logic using an in-memory adapter; saved model files are not modified.
- Added regression checks, including comparison with the local saved Stacking model when available.

## Unreleased — repository preparation

- Adopted the MIT License with copyright holder Tran Van Phong (2026).

- Added English installation, usage, input/output and reproducibility documentation.
- Added an English GitHub publication procedure and metadata/license templates.
- Added a direct dependency list, Git exclusions and repository checks for CI.
- Added a deterministic synthetic spatial-input generator.
- Standardized script introductions and standardized all comments in English without changing executable logic.

No release number, publication DOI or validation claim has been assigned.
