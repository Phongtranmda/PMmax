"""Train and evaluate regression models for maximum earthquake magnitude (Mmax).

Run from the repository root; edit SETTINGS below to configure paths.
See README.md and docs/USER_GUIDE.md for inputs, outputs and limitations.
This module executes the workflow when run or imported.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import shap
import torch
import torch.nn as nn

from sklearn.model_selection import train_test_split, GridSearchCV, KFold, learning_curve
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, ExtraTreesRegressor, StackingRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.base import BaseEstimator, RegressorMixin

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.inspection import permutation_importance


# ==========================================================
# SETTINGS
# ==========================================================

RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
N_JOBS = 1

OUTPUT_DIR = "Mmax_results"
MODEL_DIR = "Mmax_models"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


# ==========================================================
# LOAD DATA
# ==========================================================

df = pd.read_excel(os.path.join(os.getcwd(), "Example data", "EQ_sample_Mmax.xlsx"))

X = df.iloc[:, :-1]
y = df.iloc[:, -1]

feature_names = X.columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
)


# ==========================================================
# METRICS
# ==========================================================

def evaluate(y_true, y_pred):
    epsilon = 1e-8
    r2 = r2_score(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + epsilon))) * 100
    return r2, rmse, mae, mape


# ==========================================================
# DEEP LEARNING MODEL (PYTORCH)
# ==========================================================

class TorchRegressor(BaseEstimator, RegressorMixin):

    def __init__(self, input_dim, epochs=400, lr=0.001):
        self.input_dim = input_dim
        self.epochs = epochs
        self.lr = lr

    def _build_model(self):
        return nn.Sequential(
            nn.Linear(self.input_dim, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.3),

            nn.Linear(128, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),

            nn.Linear(64, 1)
        )

    def fit(self, X, y):

        # Convert pandas inputs to NumPy before creating tensors.
        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        X = torch.tensor(X, dtype=torch.float32)
        y = torch.tensor(y.reshape(-1, 1), dtype=torch.float32)

        self.model = self._build_model()
        #optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=1e-5)
        loss_fn = nn.MSELoss()

        for _ in range(self.epochs):
            optimizer.zero_grad()
            pred = self.model(X)
            loss = loss_fn(pred, y)
            loss.backward()
            optimizer.step()

        return self

    def predict(self, X):

        if isinstance(X, pd.DataFrame):
            X = X.values

        X = torch.tensor(X, dtype=torch.float32)

        with torch.no_grad():
            pred = self.model(X).numpy().flatten()

        return pred
# ==========================================================
# SHAP FOR STACKING MODEL
# ==========================================================

def shap_stacking_model(model, X_train, X_test, feature_names):

    print("\n🔍 SHAP analysis for Stacking model...")

    # Subsample the background and explanation data to reduce runtime.
    X_background = shap.sample(X_train, 300)
    X_explain = shap.sample(X_test, 300)

    # Use KernelExplainer for the stacking ensemble.
    explainer = shap.KernelExplainer(model.predict, X_background)

    shap_values = explainer.shap_values(X_explain)

    # summary plot
    plt.figure()
    shap.summary_plot(
        shap_values,
        X_explain,
        feature_names=feature_names,
        show=False
    )

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/SHAP_stacking_summary.png", dpi=300)
    plt.close()

    # bar importance
    plt.figure()
    shap.summary_plot(
        shap_values,
        X_explain,
        feature_names=feature_names,
        plot_type="bar",
        show=False
    )

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/SHAP_stacking_bar.png", dpi=300)
    plt.close()

    print("✅ SHAP Stacking saved")
# ==========================================================
# MODELS
# ==========================================================

models = {

    "Linear": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LinearRegression())
    ]),

    "Ridge": Pipeline([
        ("scaler", StandardScaler()),
        ("model", Ridge())
    ]),

    "Lasso": Pipeline([
        ("scaler", StandardScaler()),
        ("model", Lasso(max_iter=5000))
    ]),

    "ElasticNet": Pipeline([
        ("scaler", StandardScaler()),
        ("model", ElasticNet(max_iter=5000))
    ]),

    "SVR": Pipeline([
        ("scaler", StandardScaler()),
        ("model", SVR())
    ]),

    "RandomForest": RandomForestRegressor(
        n_estimators=300,
        random_state=RANDOM_STATE,
        n_jobs=8
    ),

    "ExtraTrees": ExtraTreesRegressor(
        n_estimators=300,
        random_state=RANDOM_STATE,
        n_jobs=8
    ),

    "XGBoost": XGBRegressor(
        n_estimators=400,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        n_jobs=8,
        objective="reg:squarederror"
    ),

    "LightGBM": LGBMRegressor(
        n_estimators=400,
        learning_rate=0.05,
        random_state=RANDOM_STATE,
        n_jobs=8
    ),

    "CatBoost": CatBoostRegressor(
        iterations=400,
        learning_rate=0.05,
        depth=6,
        verbose=0,
        random_state=RANDOM_STATE
    ),

    "MLP": Pipeline([
        ("scaler", StandardScaler()),
        ("model", MLPRegressor(
            hidden_layer_sizes=(128, 64, 32),
            max_iter=2000,
            random_state=RANDOM_STATE
        ))
    ]),

    "DeepNN": Pipeline([
        ("scaler", StandardScaler()),
        ("model", TorchRegressor(input_dim=X.shape[1]))
    ])
}


# ==========================================================
# TRAINING
# ==========================================================

results = []

kf = KFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

best_model = None
best_score = -np.inf
best_name = None

for name, model in models.items():

    print(f"\nTraining: {name}")

    model.fit(X_train, y_train)

    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)

    train_metrics = evaluate(y_train, y_train_pred)
    test_metrics = evaluate(y_test, y_test_pred)

    if test_metrics[0] > best_score:
        best_score = test_metrics[0]
        best_model = model
        best_name = name

    joblib.dump(model, f"{MODEL_DIR}/{name}.pkl")

    results.append({
        "Model": name,
        "Train R2": train_metrics[0],
        "Test R2": test_metrics[0],
        "RMSE": test_metrics[1],
        "MAE": test_metrics[2],
        "MAPE (%)": test_metrics[3]
    })


# ==========================================================
# STACKING ENSEMBLE
# ==========================================================

print("\nTraining: Stacking Ensemble")

stack = StackingRegressor(

    estimators=[

        ("et", ExtraTreesRegressor(
            n_estimators=400,
            random_state=RANDOM_STATE,
            n_jobs=4
        )),

        ("rf", RandomForestRegressor(
            n_estimators=300,
            random_state=RANDOM_STATE,
            n_jobs=4
        )),

        ("xgb", XGBRegressor(
            n_estimators=400,
            learning_rate=0.05,
            max_depth=4,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=RANDOM_STATE,
            n_jobs=4,
            objective="reg:squarederror"
        )),

        ("lgbm", LGBMRegressor(
            n_estimators=400,
            learning_rate=0.05,
            random_state=RANDOM_STATE,
            n_jobs=4
        ))
    ],

    final_estimator=Ridge(alpha=1.0),
    n_jobs=1
)

stack.fit(X_train, y_train)

stack_train_pred = stack.predict(X_train)
stack_train_metrics = evaluate(y_train, stack_train_pred)

y_pred = stack.predict(X_test)

stack_metrics = evaluate(y_test, y_pred)

results.append({
    "Model": "Stacking",
    "Train R2": stack_train_metrics[0],
    "Test R2": stack_metrics[0],
    "RMSE": stack_metrics[1],
    "MAE": stack_metrics[2],
    "MAPE (%)": stack_metrics[3]
})

joblib.dump(stack, f"{MODEL_DIR}/Stacking.pkl")


# ==========================================================
# SAVE RESULTS
# ==========================================================

results_df = pd.DataFrame(results).sort_values(by="Test R2", ascending=False)

results_df.to_excel(f"{OUTPUT_DIR}/evaluation.xlsx", index=False)

print("\nBest model:", best_name)


# ==========================================================
# RESIDUAL PLOT
# ==========================================================

pred = best_model.predict(X_test)
residuals = y_test - pred

plt.figure(figsize=(6,5))
plt.scatter(pred, residuals)
plt.axhline(0)
plt.xlabel("Predicted")
plt.ylabel("Residual")
plt.title("Residual Plot")
plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/residual.png")
plt.close()


# ==========================================================
# LEARNING CURVE
# ==========================================================

train_sizes, train_scores, val_scores = learning_curve(
    best_model,
    X_train,
    y_train,
    cv=kf,
    scoring="r2",
    n_jobs=1
)

plt.figure()
plt.plot(train_sizes, np.mean(train_scores, axis=1), label="Train")
plt.plot(train_sizes, np.mean(val_scores, axis=1), label="Validation")
plt.legend()
plt.xlabel("Training Size")
plt.ylabel("R2")
plt.title("Learning Curve")
plt.savefig(f"{OUTPUT_DIR}/learning_curve.png")
plt.close()


# ==========================================================
# SHAP ANALYSIS
# ==========================================================

print("\nRunning SHAP...")

try:

    # ===== SAMPLE DATA FOR FAST SHAP =====
    SHAP_SAMPLE = 300

    X_train_sample = shap.sample(X_train, SHAP_SAMPLE, random_state=RANDOM_STATE)
    X_test_sample  = shap.sample(X_test, SHAP_SAMPLE, random_state=RANDOM_STATE)

    explainer = shap.Explainer(best_model, X_train_sample)

    shap_values = explainer(X_test_sample)

    shap.summary_plot(shap_values, X_test_sample, show=False)

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/shap_summary.png", dpi=300)
    plt.close()

except Exception as e:
    print("SHAP skipped:", e)

shap_stacking_model(stack, X_train, X_test, feature_names)
# ==========================================================
# FEATURE IMPORTANCE
# ==========================================================

if hasattr(best_model, "feature_importances_"):

    importances = best_model.feature_importances_
    indices = np.argsort(importances)[::-1]

    sorted_features = [feature_names[i] for i in indices]
    sorted_importance = importances[indices]

    # ===== SAVE TO EXCEL =====
    importance_df = pd.DataFrame({
        "Feature": sorted_features,
        "Importance": sorted_importance
    })

    importance_df.to_excel(f"{OUTPUT_DIR}/feature_importance.xlsx", index=False)

    print("✓ Feature importance saved to Excel")

    # ===== PLOT =====
    plt.figure(figsize=(8,6))

    bars = plt.bar(range(len(sorted_importance)), sorted_importance)

    plt.xticks(range(len(sorted_importance)),
               sorted_features,
               rotation=45,
               ha="right")

    plt.ylabel("Importance")
    plt.title("Feature Importance")

    # ===== ADD VALUE ON BAR =====
    for bar, value in zip(bars, sorted_importance):
        plt.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height(),
            f"{value:.3f}",
            ha='center',
            va='bottom',
            fontsize=9
        )

    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/importance.png", dpi=300)
    plt.close()

else:
    print("Best model does not support feature_importances_")

# ==========================================================
# STACKING FEATURE IMPORTANCE (PERMUTATION)
# ==========================================================

print("\nCalculating Stacking Feature Importance...")

perm = permutation_importance(
    stack,
    X_test,
    y_test,
    n_repeats=10,
    random_state=RANDOM_STATE,
    n_jobs=4
)

importance = perm.importances_mean
indices = np.argsort(importance)[::-1]

sorted_features = [feature_names[i] for i in indices]
sorted_importance = importance[indices]

importance_df = pd.DataFrame({
    "Feature": sorted_features,
    "Importance": sorted_importance
})

importance_df.to_excel(f"{OUTPUT_DIR}/stacking_feature_importance.xlsx", index=False)

plt.figure(figsize=(8,6))
bars = plt.bar(range(len(sorted_importance)), sorted_importance)

plt.xticks(
    range(len(sorted_importance)),
    sorted_features,
    rotation=45,
    ha="right"
)

plt.ylabel("Importance")
plt.title("Stacking Feature Importance")

for bar, value in zip(bars, sorted_importance):
    plt.text(
        bar.get_x()+bar.get_width()/2,
        bar.get_height(),
        f"{value:.3f}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/stacking_importance.png", dpi=300)
plt.close()

print("✓ Stacking feature importance saved")

print("\n✓ Pipeline Completed Successfully")
