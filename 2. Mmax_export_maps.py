"""Export model predictions and ensemble statistics as georeferenced GeoTIFFs.

Run from the repository root; edit SETTINGS below to configure paths.
See README.md and docs/USER_GUIDE.md for inputs, outputs and limitations.
This module executes the workflow when run or imported.
"""

import os
import numpy as np
import pandas as pd
import joblib
import rasterio
from rasterio.transform import from_origin
from glob import glob
import torch
import torch.nn as nn
from sklearn.base import BaseEstimator, RegressorMixin
from mmax_prediction import predict_with_feature_names

# ==========================================================
# SETTINGS
# ==========================================================

MODEL_DIR = "Mmax_models"
INPUT_FILE = os.path.join(os.getcwd(), "Example data", "Sample_area.txt")

OUTPUT_DIR = "Mmax_maps_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PIXEL_SIZE = 30
CELL_SIZE = PIXEL_SIZE
CRS = "EPSG:32648"

BATCH_SIZE = 500000


# ==========================================================
# TORCH REGRESSOR (FOR LOADED MODELS)
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
# READ DATA
# ==========================================================

print("Reading prediction file...")

df = pd.read_csv(INPUT_FILE, skipinitialspace=True)

print("Columns:", df.columns.tolist())
print(df.head())

# ==========================================================
# XY COORDINATES
# ==========================================================

x = df["X"].to_numpy()
y = df["Y"].to_numpy()

# ===== DEBUG RASTER SIZE =====
print("\n===== COORDINATE INFO =====")
print("X range:", x.min(), x.max())
print("Y range:", y.min(), y.max())

print("Extent X:", x.max() - x.min())
print("Extent Y:", y.max() - y.min())

print("Expected width:", (x.max() - x.min()) / CELL_SIZE)
print("Expected height:", (y.max() - y.min()) / CELL_SIZE)
print("============================\n")

# ==========================================================
# FEATURES
# ==========================================================

#feature_cols = [c for c in df.columns if c not in ["OBJECTID", "X", "Y","dis_faults_resize_Band_1"]]
feature_cols = [c for c in df.columns if c not in ["OBJECTID", "X", "Y"]]
X_area = df[feature_cols].copy()

print("Total points:", len(X_area))
print("Feature count:", X_area.shape[1])

# ==========================================================
# PREDICT FUNCTION (LARGE DATA SAFE)
# ==========================================================

def predict_large(model, X):

    preds = []
    n = len(X)

    for i in range(0, n, BATCH_SIZE):

        batch = X.iloc[i:i+BATCH_SIZE]

        # Convert numeric values while retaining the source column identities.
        batch_np = batch.to_numpy(dtype=np.float32, copy=False)

        # ===== HANDLE NaN (SVR safe) =====
        if np.isnan(batch_np).any():
            batch_np = np.nan_to_num(batch_np, nan=0.0)

        batch_input = pd.DataFrame(batch_np, columns=batch.columns, index=batch.index)
        # Each stacking base estimator receives its own fitted column spelling.
        p = predict_with_feature_names(model, batch_input)

        preds.append(p)

        print(f"Batch {i} → {i+len(batch)} done")

    return np.concatenate(preds)


# ==========================================================
# EXPORT RASTER FUNCTION (NEW METHOD)
# ==========================================================

def export_raster(df, col):

    x_min, x_max = df["X"].min(), df["X"].max()
    y_min, y_max = df["Y"].min(), df["Y"].max()

    width = int((x_max - x_min) / CELL_SIZE) + 1
    height = int((y_max - y_min) / CELL_SIZE) + 1

    transform = from_origin(x_min, y_max, CELL_SIZE, CELL_SIZE)

    raster = np.full((height, width), np.nan, dtype=np.float32)

    cols = ((df["X"] - x_min) / CELL_SIZE).astype(int)
    rows = ((y_max - df["Y"]) / CELL_SIZE).astype(int)

    vals = df[col].to_numpy(dtype=np.float32, copy=False)
    raster[rows, cols] = vals

    out = os.path.join(OUTPUT_DIR, f"{col}.tif")

    with rasterio.open(
        out,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=1,
        dtype=np.float32,
        crs=CRS,
        transform=transform,
        nodata=np.nan
    ) as dst:

        dst.write(raster, 1)

    print("Exported:", col)


# ==========================================================
# LOAD MODELS
# ==========================================================

model_files = glob(os.path.join(MODEL_DIR, "*.pkl"))

print("Models found:", len(model_files))

if len(model_files) == 0:
    raise ValueError("❌ No models found in folder")

# ==========================================================
# CREATE RESULT DATAFRAME
# ==========================================================

df_result = pd.DataFrame({
    "X": x,
    "Y": y
})

all_preds = []

# ==========================================================
# LOOP MODELS
# ==========================================================

for path in model_files:

    name = os.path.basename(path).replace(".pkl", "")
    print(f"\nProcessing: {name}")

    model = joblib.load(path)

    pred = predict_large(model, X_area)

    df_result[name] = pred

    all_preds.append(pred)

# ==========================================================
# ENSEMBLE + UNCERTAINTY
# ==========================================================

print("\nCreating ensemble maps...")

all_preds = np.array(all_preds)

df_result["Ensemble_Mean"] = np.mean(all_preds, axis=0)
df_result["Uncertainty_STD"] = np.std(all_preds, axis=0)

# Coefficient of variation across loaded model predictions.
df_result["CV"] = df_result["Uncertainty_STD"] / (
    df_result["Ensemble_Mean"] + 1e-6
)

# ==========================================================
# EXPORT ALL RASTERS
# ==========================================================

print("\nExporting rasters...")

for c in df_result.columns[2:]:
    export_raster(df_result, c)

print("\n✓ ALL DONE SUCCESSFULLY")
