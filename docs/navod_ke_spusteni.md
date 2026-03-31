# Návod ke spuštění

## 1. Instalace knihoven
Ve složce `app` spusť:

```bat
py -m pip install -r requirements.txt
```

## 2. Přenos datasetu z crawleru
Zkopíruj soubor:

```text
crawler/data/autos_raw.csv
```

do složky:

```text
app/data/autos_raw.csv
```

## 3. Předzpracování a trénování modelu
Ve složce `app` spusť:

```bat
py preprocess.py --input datautos_raw.csv --output datautos_clean.csv --report data\preprocess_report.json
py train_model.py --input datautos_clean.csv --model-out model\model_bundle.joblib --metrics-out model\metrics.json
```

Případně jednoduše:

```bat
train_model.cmd
```

## 4. Spuštění aplikace
Ve složce `app` spusť:

```bat
py app.py
```

nebo:

```bat
run_app.cmd
```

Aplikace poběží na adrese:

```text
http://127.0.0.1:5000
```
