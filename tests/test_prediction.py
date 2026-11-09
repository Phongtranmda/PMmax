"""Regression checks for feature-name alignment and saved stacking models."""

from pathlib import Path
import ast
from contextlib import redirect_stdout
import io
import unittest
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import StackingRegressor
from sklearn.linear_model import LinearRegression, Ridge

from mmax_prediction import align_features, predict_with_feature_names


class FeatureAlignmentTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(42)
        self.frame = pd.DataFrame(rng.normal(size=(40, 3)),
                                  columns=["BGA", "LS8-Band 1", "LS8-Band 2"])
        self.target = self.frame.to_numpy() @ np.array([2.0, 3.0, -1.0])
        self.model = Ridge().fit(self.frame, self.target)

    def test_aliases_and_reordered_columns(self):
        incoming = self.frame.rename(columns={"LS8-Band 1": "LS8_Band_1",
                                              "LS8-Band 2": "LS8-Band_2"})
        incoming = incoming.iloc[:, ::-1]
        before = incoming.copy()
        np.testing.assert_allclose(predict_with_feature_names(self.model, incoming),
                                   self.model.predict(self.frame))
        pd.testing.assert_frame_equal(incoming, before)

    def test_missing_extra_and_ambiguous_columns_fail(self):
        invalid = [self.frame.drop(columns="BGA"),
                   self.frame.assign(unexpected=0),
                   self.frame.rename(columns={"BGA": "LS8_Band_1"})]
        for frame in invalid:
            with self.subTest(columns=list(frame.columns)), self.assertRaises(ValueError):
                align_features(self.model, frame)

    def test_nameless_estimator_preserves_position(self):
        model = Ridge().fit(self.frame.to_numpy(), self.target)
        np.testing.assert_allclose(predict_with_feature_names(model, self.frame),
                                   model.predict(self.frame.to_numpy()))

    def test_native_stacking_equivalence_including_passthrough_and_drop(self):
        for passthrough in [False, True]:
            with self.subTest(passthrough=passthrough):
                stack = StackingRegressor(
                    estimators=[("ridge", Ridge()), ("unused", "drop"),
                                ("linear", LinearRegression())],
                    final_estimator=Ridge(), passthrough=passthrough, cv=2,
                ).fit(self.frame, self.target)
                originals = list(stack.estimators_)
                np.testing.assert_allclose(predict_with_feature_names(stack, self.frame),
                                           stack.predict(self.frame))
                self.assertTrue(all(a is b for a, b in zip(originals, stack.estimators_)))

    def test_local_saved_stack_against_independent_base_predictions(self):
        root = Path(__file__).resolve().parents[1]
        path = root / "Mmax_models" / "Stacking.pkl"
        if not path.exists():
            self.skipTest("Local fitted model is not distributed in Git")
        stack = joblib.load(path)
        raw = pd.read_excel(root / "Example data" / "EQ_sample_Mmax.xlsx").iloc[:64, :-1]
        raw = raw.astype(np.float32)
        # Independently restore the known workbook order to each fitted estimator.
        reference = stack.final_estimator_.predict(np.column_stack([
            estimator.predict(pd.DataFrame(raw.to_numpy(), columns=estimator.feature_names_in_))
            for estimator in stack.estimators_
        ]))
        incoming = raw.rename(columns={f"LS8-Band {i}": f"LS8_Band_{i}" for i in range(1, 8)})
        incoming = incoming.iloc[:, ::-1]
        originals = list(stack.estimators_)
        original_names = [list(e.feature_names_in_) for e in originals]
        with warnings.catch_warnings():
            warnings.filterwarnings("error", message=".*feature names.*", category=UserWarning)
            actual = predict_with_feature_names(stack, incoming)
            batched = np.concatenate([predict_with_feature_names(stack, incoming.iloc[i:i+17])
                                      for i in range(0, len(incoming), 17)])
        np.testing.assert_allclose(actual, reference, rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(batched, reference, rtol=1e-12, atol=1e-12)
        self.assertTrue(np.isfinite(actual).all())
        self.assertTrue(all(a is b for a, b in zip(originals, stack.estimators_)))
        self.assertEqual(original_names, [list(e.feature_names_in_) for e in stack.estimators_])

    def test_tool2_batches_with_real_mapping_rows_and_missing_values(self):
        root = Path(__file__).resolve().parents[1]
        model_path = root / "Mmax_models" / "Stacking.pkl"
        input_path = root / "Example data" / "Sample_area.txt"
        if not model_path.exists() or not input_path.exists():
            self.skipTest("Full local input and saved model are not distributed in Git")
        # Extract just the batch function: importing Tool 2 would run the full map.
        tree = ast.parse((root / "2. Mmax_export_maps.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef) and node.name == "predict_large")
        namespace = dict(np=np, pd=pd, BATCH_SIZE=37,
                         predict_with_feature_names=predict_with_feature_names)
        exec(compile(ast.Module(body=[function], type_ignores=[]), "<Tool 2 batches>", "exec"), namespace)
        frame = pd.read_csv(input_path, nrows=128, skipinitialspace=True)
        frame = frame.drop(columns=["OBJECTID", "X", "Y"])
        model = joblib.load(model_path)
        values = np.nan_to_num(frame.to_numpy(dtype=np.float32), nan=0.0)
        reference = model.final_estimator_.predict(np.column_stack([
            e.predict(pd.DataFrame(values, columns=e.feature_names_in_))
            for e in model.estimators_
        ]))
        with warnings.catch_warnings(), redirect_stdout(io.StringIO()):
            warnings.filterwarnings("error", message=".*feature names.*", category=UserWarning)
            actual = namespace["predict_large"](model, frame)
        np.testing.assert_allclose(actual, reference, rtol=1e-12, atol=1e-12)
        self.assertTrue(np.isfinite(actual).all())


if __name__ == "__main__":
    unittest.main()
