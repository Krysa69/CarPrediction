#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, render_template, request

from predict import load_bundle, predict_offer

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "model_bundle.joblib"
METRICS_PATH = BASE_DIR / "model" / "metrics.json"

app = Flask(__name__)


def load_metadata() -> dict:
    metadata = {
        "brands": [],
        "models": [],
        "fuels": ["benzín", "nafta", "hybrid", "plug-in hybrid", "elektro", "lpg", "cng", "neuvedeno"],
        "transmissions": ["manuální", "automatická", "poloautomatická", "neuvedeno"],
        "body_types": ["kombi", "sedan", "hatchback", "suv", "mpv", "liftback", "kupé", "cabrio", "dodávka", "pick-up", "terénní", "roadster", "limuzína", "neuvedeno"],
        "metrics": None,
        "dataset_rows": None,
        "trained_at": None,
    }
    if MODEL_PATH.exists():
        bundle = load_bundle(MODEL_PATH)
        allowed = bundle.get("allowed_values", {})
        metadata["brands"] = allowed.get("brands", [])[:300]
        metadata["models"] = allowed.get("models", [])[:500]
        metadata["fuels"] = allowed.get("fuels", metadata["fuels"])
        metadata["transmissions"] = allowed.get("transmissions", metadata["transmissions"])
        metadata["body_types"] = allowed.get("body_types", metadata["body_types"])
        metadata["dataset_rows"] = bundle.get("dataset_rows")
        metadata["trained_at"] = bundle.get("trained_at")
        metadata["metrics"] = bundle.get("metrics")
    elif METRICS_PATH.exists():
        metadata["metrics"] = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return metadata


@app.route("/")
def index():
    metadata = load_metadata()
    return render_template("index.html", metadata=metadata, model_ready=MODEL_PATH.exists())


@app.route("/analyza", methods=["GET", "POST"])
def analyze():
    metadata = load_metadata()
    if request.method == "GET":
        return render_template("form.html", metadata=metadata, values={}, model_ready=MODEL_PATH.exists())

    values = {
        "brand": request.form.get("brand", "").strip(),
        "model": request.form.get("model", "").strip(),
        "year": request.form.get("year", "").strip(),
        "km": request.form.get("km", "").strip(),
        "power_kw": request.form.get("power_kw", "").strip(),
        "engine_ccm": request.form.get("engine_ccm", "").strip(),
        "fuel": request.form.get("fuel", "").strip(),
        "transmission": request.form.get("transmission", "").strip(),
        "body_type": request.form.get("body_type", "").strip(),
        "doors": request.form.get("doors", "").strip(),
        "seats": request.form.get("seats", "").strip(),
        "owners_count": request.form.get("owners_count", "").strip(),
        "listed_price": request.form.get("listed_price", "").strip(),
    }

    required = ["brand", "model", "year", "km", "power_kw"]
    missing = [key for key in required if not values.get(key)]
    if missing:
        return render_template(
            "form.html",
            metadata=metadata,
            values=values,
            error="Vyplň alespoň značku, model, rok výroby, nájezd a výkon.",
            model_ready=MODEL_PATH.exists(),
        )

    if not MODEL_PATH.exists():
        return render_template(
            "error.html",
            title="Model ještě není natrénovaný",
            message="Nejdřív vlož vlastní dataset do app/data/autos_raw.csv a spusť train_model.cmd.",
        )

    try:
        result = predict_offer(values, MODEL_PATH)
    except Exception as exc:
        return render_template(
            "error.html",
            title="Nepodařilo se provést analýzu",
            message=f"Chyba: {exc}",
        )

    return render_template("result.html", result=result, values=values, metadata=metadata)


@app.route("/o-projektu")
def about():
    metadata = load_metadata()
    return render_template("about.html", metadata=metadata, model_ready=MODEL_PATH.exists())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
