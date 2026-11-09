"""Match mapping inputs to fitted feature names without changing saved models."""

from copy import copy
import re

import pandas as pd
from sklearn.ensemble import StackingRegressor


def _feature_key(name):
    """Recognize only the Landsat aliases used by the supplied project files."""
    match = re.fullmatch(r"LS8[-_]Band[ _]([1-7])", str(name))
    return f"LS8-Band {match.group(1)}" if match else name


def align_features(model, frame):
    """Reorder named predictors and restore each estimator's fitted spelling.

    Estimators without feature names retain the input's positional order.
    Ambiguous aliases, missing predictors and unexpected predictors are rejected.
    """
    names = getattr(model, "feature_names_in_", None)
    if names is None:
        names = getattr(model, "feature_names_", None)
    if names is None or len(names) == 0:
        expected = getattr(model, "n_features_in_", frame.shape[1])
        if expected != frame.shape[1]:
            raise ValueError(f"Feature count mismatch: model={expected}, data={frame.shape[1]}")
        return frame.to_numpy(copy=False)

    names = list(names)
    actual_keys = [_feature_key(name) for name in frame.columns]
    expected_keys = [_feature_key(name) for name in names]
    if len(set(actual_keys)) != len(actual_keys):
        raise ValueError("Duplicate or ambiguous input feature names after Landsat alias matching")
    if len(set(expected_keys)) != len(expected_keys):
        raise ValueError("Duplicate or ambiguous fitted feature names after Landsat alias matching")
    missing = [name for name in expected_keys if name not in actual_keys]
    extra = [name for name in actual_keys if name not in expected_keys]
    if missing or extra:
        raise ValueError(f"Feature mismatch: missing={missing}, unexpected={extra}")
    positions = [actual_keys.index(name) for name in expected_keys]
    aligned = frame.iloc[:, positions].copy(deep=False)
    aligned.columns = names
    return aligned


class _PredictionAdapter:
    """Supply a base estimator with its own feature names during stack.predict."""

    def __init__(self, estimator):
        self.estimator = estimator

    def predict(self, frame):
        return predict_with_feature_names(self.estimator, frame)


def predict_with_feature_names(model, frame):
    """Predict with per-estimator feature alignment, including fitted stacks.

    A shallow stack copy retains sklearn's native transform/final prediction
    logic and fitted weights. Only its base-estimator prediction interfaces are
    adapted; the original fitted model and serialized file are not modified.
    """
    aligned = align_features(model, frame)
    if not isinstance(model, StackingRegressor):
        return model.predict(aligned)

    if any(method != "predict" for method in model.stack_method_):
        raise ValueError("Only regression stacking with predict methods is supported")
    if not isinstance(aligned, pd.DataFrame):
        aligned = pd.DataFrame(aligned, columns=frame.columns, index=frame.index)
    adapted = copy(model)
    adapted.estimators_ = [
        estimator if isinstance(estimator, str) and estimator == "drop"
        else _PredictionAdapter(estimator)
        for estimator in model.estimators_
    ]
    return adapted.predict(aligned)
