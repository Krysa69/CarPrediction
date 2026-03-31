#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

CURRENT_YEAR = datetime.now().year
MODEL_PATH = Path("model/model_bundle.joblib")


@dataclass
class PredictionResult:
    predicted_price: int
    listed_price: int | None
    delta: int | None
    delta_pct: float | None
    verdict: str
    confidence: str
    reasons: list[str]


def load_bundle(model_path: Path = MODEL_PATH) -> dict[str, Any]:
    if not model_path.exists():
        raise FileNotFoundError(f"Model bundle neexistuje: {model_path}")
    return joblib.load(model_path)


def prepare_input(payload: dict[str, Any]) -> pd.DataFrame:
    year = int(payload.get("year") or CURRENT_YEAR)
    km = int(payload.get("km") or 0)
    age = max(CURRENT_YEAR - year, 0)
    km_per_year = round(km / (age if age > 0 else 1), 2)

    row = {
        "brand": str(payload.get("brand") or "Neuvedeno").title(),
        "model": str(payload.get("model") or "Neuvedeno").strip(),
        "fuel": str(payload.get("fuel") or "neuvedeno"),
        "transmission": str(payload.get("transmission") or "neuvedeno"),
        "body_type": str(payload.get("body_type") or "neuvedeno"),
        "year": year,
        "age": age,
        "km": km,
        "km_per_year": km_per_year,
        "power_kw": int(payload.get("power_kw") or 0),
        "engine_ccm": int(payload.get("engine_ccm") or 0),
        "doors": int(payload.get("doors") or 5),
        "seats": int(payload.get("seats") or 5),
        "owners_count": int(payload.get("owners_count") or 1),
    }
    return pd.DataFrame([row])


def find_market_row(bundle: dict[str, Any], brand: str, model: str) -> dict[str, Any] | None:
    for row in bundle.get("market_summary", []):
        if str(row.get("brand")) == brand and str(row.get("model")) == model:
            return row
    return None


def build_reasons(payload: dict[str, Any], predicted_price: int, listed_price: int | None, bundle: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    brand = str(payload.get("brand") or "Neuvedeno").title()
    model = str(payload.get("model") or "Neuvedeno").strip()
    market_row = find_market_row(bundle, brand, model)
    global_summary = bundle.get("global_summary", {})

    year = int(payload.get("year") or CURRENT_YEAR)
    km = int(payload.get("km") or 0)
    power_kw = int(payload.get("power_kw") or 0)

    if market_row and market_row.get("count", 0) >= 5:
        med_km = float(market_row.get("median_km") or 0)
        med_year = float(market_row.get("median_year") or CURRENT_YEAR)
        med_kw = float(market_row.get("median_power_kw") or 0)
        if km > med_km * 1.15:
            reasons.append("Nájezd je vyšší než medián podobných vozů stejné značky a modelu.")
        elif med_km and km < med_km * 0.85:
            reasons.append("Nájezd je nižší než medián podobných vozů, což může cenu zvyšovat.")
        if year > med_year:
            reasons.append("Vůz je novější než běžný medián této modelové řady.")
        elif year < med_year:
            reasons.append("Vůz je starší než běžný medián této modelové řady.")
        if power_kw and med_kw and power_kw > med_kw * 1.10:
            reasons.append("Výkon motoru je vyšší než medián podobných vozů.")
    else:
        if km > float(global_summary.get("median_km", 0)):
            reasons.append("Nájezd je vyšší než medián celého datasetu.")
        if year < float(global_summary.get("median_year", CURRENT_YEAR)):
            reasons.append("Rok výroby je starší než medián celého datasetu.")

    if listed_price is not None:
        if listed_price < predicted_price * 0.85:
            reasons.append("Inzerovaná cena je výrazně nižší než modelový odhad, proto může jít o výhodnou nebo rizikovou nabídku.")
        elif listed_price > predicted_price * 1.15:
            reasons.append("Inzerovaná cena je výrazně vyšší než modelový odhad trhu.")
        else:
            reasons.append("Inzerovaná cena je blízko odhadované tržní hodnotě.")

    if not reasons:
        reasons.append("Vstupní parametry se pohybují v běžném rozmezí známém z trénovacích dat.")

    return reasons[:4]


def evaluate_confidence(payload: dict[str, Any], bundle: dict[str, Any]) -> str:
    score = 0
    for key in ["brand", "model", "year", "km", "power_kw", "fuel", "transmission", "body_type"]:
        if payload.get(key) not in (None, "", 0, "0"):
            score += 1

    allowed = bundle.get("allowed_values", {})
    if str(payload.get("brand") or "").title() in allowed.get("brands", []):
        score += 1
    if str(payload.get("model") or "").strip() in allowed.get("models", []):
        score += 1

    if score >= 9:
        return "vysoká"
    if score >= 7:
        return "střední"
    return "nižší"


def classify_offer(predicted_price: int, listed_price: int | None) -> tuple[str, int | None, float | None]:
    if listed_price is None:
        return "Byla vypočtena pouze odhadovaná tržní cena bez vyhodnocení konkrétní nabídky.", None, None

    delta = listed_price - predicted_price
    delta_pct = round((delta / predicted_price) * 100, 2) if predicted_price else None

    if listed_price < predicted_price * 0.80:
        verdict = "Podezřele levná nabídka"
    elif listed_price < predicted_price * 0.95:
        verdict = "Spíše výhodná nabídka"
    elif listed_price <= predicted_price * 1.10:
        verdict = "Běžná tržní nabídka"
    elif listed_price <= predicted_price * 1.25:
        verdict = "Spíše dražší nabídka"
    else:
        verdict = "Podezřele drahá nabídka"

    return verdict, delta, delta_pct


def predict_offer(payload: dict[str, Any], model_path: Path = MODEL_PATH) -> PredictionResult:
    bundle = load_bundle(model_path)
    pipeline = bundle["pipeline"]
    frame = prepare_input(payload)
    predicted_price = int(round(float(pipeline.predict(frame)[0]), 0))

    listed_price_raw = payload.get("listed_price")
    listed_price = int(listed_price_raw) if listed_price_raw not in (None, "") else None
    verdict, delta, delta_pct = classify_offer(predicted_price, listed_price)
    confidence = evaluate_confidence(payload, bundle)
    reasons = build_reasons(payload, predicted_price, listed_price, bundle)

    return PredictionResult(
        predicted_price=predicted_price,
        listed_price=listed_price,
        delta=delta,
        delta_pct=delta_pct,
        verdict=verdict,
        confidence=confidence,
        reasons=reasons,
    )
