@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -m pip install -r requirements.txt
if not exist data\autos_raw.csv (
  echo [ERR] Chybi soubor data\autos_raw.csv
  pause
  exit /b 1
)
py preprocess.py --input data\autos_raw.csv --output data\autos_clean.csv --report data\preprocess_report.json
if errorlevel 1 (
  pause
  exit /b 1
)
py train_model.py --input data\autos_clean.csv --model-out model\model_bundle.joblib --metrics-out model\metrics.json
pause
