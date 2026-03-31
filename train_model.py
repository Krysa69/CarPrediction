#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CURRENT_YEAR = datetime.now().year

FEATURE_COLUMNS = [
    "brand", "model", "fuel", "transmission", "body_type",
    "year", "age", "km", "km_per_year", "power_kw", "engine_ccm", "doors", "seats", "owners_count"
]

TARGET_COLUMN = "price_czk"
NUMERIC_FEATURES = ["year", "age", "km", "km_per_year", "power_kw", "engine_ccm", "doors", "seats", "owners_count"]
CATEGORICAL_FEATURES = ["brand", "model", "fuel", "transmission", "body_type"]


def build_pipeline() -> Pipeline:
    numeric_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, NUMERIC_FEATURES),
        ("cat", categorical_transformer, CATEGORICAL_FEATURES),
    ])

    model = RandomForestRegressor(
        n_estimators=250,
        max_depth=18,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )

    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])


def main() -> int:
    parser = argparse.ArgumentParser(description="Trénování modelu pro odhad ceny auta")
    parser.add_argument("--input", default="data/autos_clean.csv", help="Vstupní vyčištěný dataset")
    parser.add_argument("--model-out", default="model/model_bundle.joblib", help="Kam uložit model bundle")
    parser.add_argument("--metrics-out", default="model/metrics.json", help="Kam uložit metriky")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERR] Vstupní dataset neexistuje: {input_path}")
        return 1

    df = pd.read_csv(input_path)
    if len(df) < 200:
        print("[ERR] Dataset je příliš malý na smysluplné trénování.")
        return 1

    missing_columns = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing_columns:
        print(f"[ERR] Chybí sloupce: {', '.join(missing_columns)}")
        return 1

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    mae = float(mean_absolute_error(y_test, preds))
    rmse = float(mean_squared_error(y_test, preds) ** 0.5)
    r2 = float(r2_score(y_test, preds))

    market_summary = (
        df.groupby(["brand", "model"], dropna=False)
        .agg(
            median_price=("price_czk", "median"),
            median_km=("km", "median"),
            median_year=("year", "median"),
            median_power_kw=("power_kw", "median"),
            count=("price_czk", "count"),
        )
        .reset_index()
    )

    global_summary = {
        "median_price": float(df["price_czk"].median()),
        "median_km": float(df["km"].median()),
        "median_year": float(df["year"].median()),
        "median_power_kw": float(df["power_kw"].median()),
    }

    bundle = {
        "pipeline": pipeline,
        "features": FEATURE_COLUMNS,
        "trained_at": datetime.now().isoformat(),
        "dataset_rows": int(len(df)),
        "metrics": {"mae": mae, "rmse": rmse, "r2": r2},
        "market_summary": market_summary.to_dict(orient="records"),
        "global_summary": global_summary,
        "allowed_values": {
            "brands": sorted([str(x) for x in df["brand"].dropna().unique().tolist()]),
            "models": sorted([str(x) for x in df["model"].dropna().unique().tolist()]),
            "fuels": sorted([str(x) for x in df["fuel"].dropna().unique().tolist()]),
            "transmissions": sorted([str(x) for x in df["transmission"].dropna().unique().tolist()]),
            "body_types": sorted([str(x) for x in df["body_type"].dropna().unique().tolist()]),
        },
    }

    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)

    metrics_path = Path(args.metrics_out)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(bundle["metrics"], ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Dataset řádků: {len(df)}")
    print(f"[OK] MAE: {mae:.2f} Kč")
    print(f"[OK] RMSE: {rmse:.2f} Kč")
    print(f"[OK] R²: {r2:.4f}")
    print(f"[OK] Model uložen: {model_path}")
    print(f"[OK] Metriky uloženy: {metrics_path}")

    if len(df) < 1500:
        print("[WARN] Dataset má méně než 1500 záznamů. Zkontroluj, jestli splňuje zadání.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
