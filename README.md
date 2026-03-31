# AutoScout AI

Lokální školní aplikace pro odhad obvyklé ceny ojetého auta a pro vyhodnocení, zda je konkrétní inzerát spíše výhodný nebo podezřelý.

## Struktura
- `crawler/` = oddělený sběr dat
- `app/` = samotná aplikace, preprocessing, trénování modelu a webové rozhraní

## Doporučený postup
1. Spusť crawler a sesbírej vlastní data.
2. Zkopíruj `crawler/data/autos_raw.csv` do `app/data/autos_raw.csv`.
3. Ve složce `app` spusť `train_model.cmd`.
4. Potom spusť `run_app.cmd`.

## Poznámka
Projekt je navržen tak, aby šel spustit bez IDE, čistě přes příkazový řádek na školním PC.
