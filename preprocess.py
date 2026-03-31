#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

CURRENT_YEAR = datetime.now().year

FUEL_MAP = {
    "diesel": "nafta",
    "nafta": "nafta",
    "benzín": "benzín",
    "benzin": "benzín",
    "hybrid": "hybrid",
    "plug-in hybrid": "plug-in hybrid",
    "elektro": "elektro",
    "elektromobil": "elektro",
    "lpg": "lpg",
    "cng": "cng",
}

TRANSMISSION_MAP = {
    "automat": "automatická",
    "automatická": "automatická",
    "manuální": "manuální",
    "manualni": "manuální",
    "poloautomatická": "poloautomatická",
}

BODY_MAP = {
    "kombi": "kombi",
    "sedan": "sedan",
    "hatchback": "hatchback",
    "suv": "suv",
    "mpv": "mpv",
    "liftback": "liftback",
    "kupé": "kupé",
    "cabrio": "cabrio",
    "dodávka": "dodávka",
    "pick-up": "pick-up",
    "terénní": "terénní",
    "roadster": "roadster",
    "limuzína": "limuzína",
}


def normalize_text(value: object) -> str | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text if text else None


def normalize_simple(value: object) -> str | None:
    text = normalize_text(value)
    if not text:
        return None
    return text.lower().replace("  ", " ").strip()


def parse_int(value: object) -> int | None:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).strip()
    if re.fullmatch(r"\d+(?:\.0+)?", text):
        try:
            return int(float(text))
        except ValueError:
            return None
    digits = re.sub(r"[^\d]", "", text)
    if not digits:
        return None
    try:
        return int(digits)
    except ValueError:
        return None


def infer_brand_model(row: pd.Series) -> tuple[str | None, str | None]:
    brand = normalize_text(row.get("brand"))
    model = normalize_text(row.get("model"))
    title = normalize_text(row.get("title"))
    if title:
        parts = title.split()
        if not brand and parts:
            brand = parts[0].title()
        if not model and len(parts) > 1:
            model = parts[1].upper() if len(parts[1]) <= 3 else parts[1].title()
    return brand, model


def main() -> int:
    parser = argparse.ArgumentParser(description="Vyčištění datasetu ojetých aut")
    parser.add_argument("--input", default="data/autos_raw.csv", help="Vstupní raw CSV")
    parser.add_argument("--output", default="data/autos_clean.csv", help="Výstupní čisté CSV")
    parser.add_argument("--report", default="data/preprocess_report.json", help="JSON report")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERR] Vstupní soubor neexistuje: {input_path}")
        return 1

    df = pd.read_csv(input_path)
    original_count = len(df)

    if df.empty:
        print("[ERR] Vstupní dataset je prázdný.")
        return 1

    # základní normalizace textů
    text_columns = [
        "title", "brand", "model", "fuel", "transmission", "body_type",
        "drive", "color", "detail_url", "source_page", "seed_url"
    ]
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].apply(normalize_text)

    numeric_columns = ["price_czk", "year", "km", "power_kw", "engine_ccm", "doors", "seats", "euro_norm", "owners_count"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].apply(parse_int)

    # dopočty brand/model
    inferred = df.apply(infer_brand_model, axis=1, result_type="expand")
    df["brand"] = inferred[0]
    df["model"] = inferred[1]

    # sjednocení kategorií
    df["fuel"] = df.get("fuel", pd.Series(dtype="object")).apply(lambda x: FUEL_MAP.get(normalize_simple(x), normalize_simple(x)))
    df["transmission"] = df.get("transmission", pd.Series(dtype="object")).apply(lambda x: TRANSMISSION_MAP.get(normalize_simple(x), normalize_simple(x)))
    df["body_type"] = df.get("body_type", pd.Series(dtype="object")).apply(lambda x: BODY_MAP.get(normalize_simple(x), normalize_simple(x)))

    # povinné sloupce
    required = ["price_czk", "year", "km", "brand", "model"]
    for col in required:
        if col not in df.columns:
            print(f"[ERR] Chybí povinný sloupec: {col}")
            return 1

    # odstranění záznamů bez klíčových hodnot
    df = df.dropna(subset=["price_czk", "year", "km", "brand", "model"])

    # filtry rozumných hodnot
    df = df[df["price_czk"].between(10000, 5000000)]
    df = df[df["year"].between(1990, CURRENT_YEAR + 1)]
    df = df[df["km"].between(0, 600000)]
    if "power_kw" in df.columns:
        df = df[(df["power_kw"].isna()) | (df["power_kw"].between(20, 700))]
    if "engine_ccm" in df.columns:
        df = df[(df["engine_ccm"].isna()) | (df["engine_ccm"].between(600, 7000))]

    # deduplikace
    if "detail_url" in df.columns:
        url_mask = df["detail_url"].notna() & (df["detail_url"] != "")
        df_with_url = df[url_mask].drop_duplicates(subset=["detail_url"], keep="first")
        df_without_url = df[~url_mask].drop_duplicates(subset=["brand", "model", "year", "km", "price_czk"], keep="first")
        df = pd.concat([df_with_url, df_without_url], ignore_index=True)
    else:
        df = df.drop_duplicates(subset=["brand", "model", "year", "km", "price_czk"], keep="first")

    # feature engineering
    df["age"] = CURRENT_YEAR - df["year"]
    df["age"] = df["age"].clip(lower=0, upper=50)
    df["power_kw"] = df["power_kw"].fillna(df["power_kw"].median() if df["power_kw"].notna().any() else 0)
    df["engine_ccm"] = df["engine_ccm"].fillna(df["engine_ccm"].median() if df["engine_ccm"].notna().any() else 0)
    df["doors"] = df["doors"].fillna(df["doors"].median() if df["doors"].notna().any() else 5)
    df["seats"] = df["seats"].fillna(df["seats"].median() if df["seats"].notna().any() else 5)
    df["owners_count"] = df["owners_count"].fillna(df["owners_count"].median() if df["owners_count"].notna().any() else 1)
    df["km_per_year"] = (df["km"] / df["age"].replace(0, 1)).round(2)
    df["brand"] = df["brand"].astype(str).str.title()
    df["model"] = df["model"].astype(str).str.strip()
    for col in ["fuel", "transmission", "body_type", "drive", "color"]:
        if col in df.columns:
            df[col] = df[col].fillna("neuvedeno")

    df = df.sort_values(["brand", "model", "year", "price_czk"]).reset_index(drop=True)

    if df.empty:
        print("[ERR] Po vyčištění nezůstal žádný záznam. Zkontroluj vstupní CSV a filtry v preprocess.py.")
        return 1

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")

    report = {
        "raw_rows": int(original_count),
        "clean_rows": int(len(df)),
        "removed_rows": int(original_count - len(df)),
        "brands": int(df["brand"].nunique()),
        "models": int(df["model"].nunique()),
        "price_min": int(df["price_czk"].min()),
        "price_max": int(df["price_czk"].max()),
        "year_min": int(df["year"].min()),
        "year_max": int(df["year"].max()),
    }
    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[OK] Raw záznamů: {original_count}")
    print(f"[OK] Vyčištěných záznamů: {len(df)}")
    print(f"[OK] Uloženo: {output_path}")
    print(f"[OK] Report: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
