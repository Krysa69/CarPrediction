# AutoScout AI

AutoScout AI je softwarový projekt zaměřený na analýzu inzerátů ojetých automobilů pomocí strojového učení.  
Aplikace pracuje s reálně sesbíranými daty z veřejně dostupných inzerátů, tato data vyčistí, připraví pro model a následně umožní odhadnout běžnou cenu vozidla a vyhodnotit, zda konkrétní nabídka působí výhodně, běžně nebo podezřele.

## Smysl projektu

Při nákupu ojetého auta běžný uživatel často nepozná, zda je cena inzerátu přiměřená.  
Cílem projektu je vytvořit nástroj, který:

- odhadne běžnou cenu auta podle jeho parametrů,
- porovná odhad s inzerovanou cenou,
- vyhodnotí, zda je nabídka levná, běžná nebo drahá,
- zobrazí stručné důvody výsledku.

Projekt tedy neslouží jen jako obyčejná kalkulačka ceny, ale jako podpůrný nástroj pro orientační posouzení inzerátu.

## Hlavní části projektu

Projekt je rozdělen na dvě části:

### 1. Crawler
Samostatná část projektu slouží ke sběru dat z webu s inzeráty ojetých aut.

Úkol crawleru:
- procházet zadané seznamy vozidel,
- získávat údaje o vozech,
- ukládat data do souboru CSV,
- vytvořit základ pro trénování modelu.

Crawler je oddělený od aplikace, aby bylo jasně vidět:
- odkud data pochází,
- že nebyl použit žádný hotový dataset,
- že data byla získána vlastním sběrem.

### 2. Aplikace
Aplikační část obsahuje:
- čištění dat,
- trénování modelu,
- predikční logiku,
- webové rozhraní ve Flasku.

## Použitá data

Projekt pracuje s reálně sesbíranými daty z veřejně dostupných inzerátů ojetých vozidel.

Použité atributy zahrnují například:
- značku,
- model,
- rok výroby,
- cenu,
- nájezd kilometrů,
- výkon,
- objem motoru,
- druh paliva,
- typ převodovky,
- typ karoserie.

Data nejsou převzata z hotového datasetu.  
Byla získána vlastním crawlerem a následně zpracována v rámci projektu.

## Zpracování dat

Před trénováním modelu probíhá preprocessing, tedy příprava dat.

Tato část zahrnuje:
- odstranění neplatných nebo neúplných záznamů,
- převod textových údajů na číselné hodnoty,
- čištění číselných sloupců,
- deduplikaci záznamů,
- výpočet odvozených atributů, například stáří auta nebo průměrného nájezdu za rok,
- transformaci kategoriálních dat pomocí One-Hot Encoding,
- škálování numerických hodnot.

Výsledkem je vyčištěný dataset vhodný pro strojové učení.

## Model strojového učení

Pro odhad ceny vozidla je použit regresní model typu **RandomForestRegressor**.

Model se učí vztah mezi parametry auta a jeho cenou.  
Na základě historických inzerátů se snaží odhadnout, jaká cena je pro zadané vozidlo obvyklá.

### Výstup modelu
Model vrací:
- odhad běžné ceny vozidla,
- rozdíl mezi odhadovanou a inzerovanou cenou,
- slovní vyhodnocení nabídky.

## Jak projekt funguje

Celý proces funguje v tomto pořadí:

1. crawler sesbírá data a uloží je do `autos_raw.csv`,
2. skript `preprocess.py` data vyčistí a vytvoří `autos_clean.csv`,
3. skript `train_model.py` natrénuje model a uloží jej do složky `model`,
4. skript `app.py` spustí webovou aplikaci,
5. uživatel zadá parametry auta a cenu z inzerátu,
6. aplikace spočítá odhad ceny a zobrazí výsledek.

## Struktura projektu

```text
app/
├── data/
├── docs/
├── model/
├── notebooks/
├── static/
├── templates/
├── vendor/
├── app.py
├── predict.py
├── preprocess.py
├── README.md
├── requirements.txt
├── run_app.cmd
├── train_model.cmd
└── train_model.py
```

## Popis hlavních souborů

### `preprocess.py`
Načítá surový dataset `autos_raw.csv`, čistí data a vytváří `autos_clean.csv`.

### `train_model.py`
Načítá vyčištěná data, natrénuje model, spočítá metriky a uloží model.

### `predict.py`
Obsahuje logiku pro vytvoření predikce a vyhodnocení nabídky.

### `app.py`
Spouští Flask webovou aplikaci a zajišťuje komunikaci mezi formulářem a predikcí.

### `requirements.txt`
Obsahuje seznam použitých Python knihoven.

## Spuštění projektu

Projekt je možné spustit bez IDE, pouze pomocí Pythonu a terminálu.

### Instalace knihoven
Ve složce `app` spusť:

```powershell
python -m pip install -r requirements.txt
```

### Vložení dat
Do složky:

```text
app/data/
```

vlož soubor:

```text
autos_raw.csv
```

### Preprocessing dat
```powershell
python preprocess.py
```

### Trénování modelu
```powershell
python train_model.py
```

### Spuštění aplikace
```powershell
python app.py
```

Poté otevři webový prohlížeč a přejdi na adresu:

```text
http://127.0.0.1:5000
```

## Co aplikace dělá po spuštění

Uživatel vyplní formulář s parametry auta:
- značka,
- model,
- rok výroby,
- nájezd km,
- výkon,
- palivo,
- převodovka,
- karoserie,
- inzerovaná cena.

Aplikace následně:
- odhadne běžnou cenu vozu,
- porovná ji s inzerovanou cenou,
- vypočítá rozdíl,
- zobrazí verdikt.

Příklad výsledku:
- odhadovaná cena: 280 000 Kč
- inzerovaná cena: 330 000 Kč
- výsledek: spíše dražší nabídka

## Použité technologie

- Python
- Flask
- pandas
- NumPy
- scikit-learn
- joblib

## Dokumentace a obhajoba

Součástí projektu je také:
- popis zdroje dat,
- postup zpracování dat,
- trénování a vyhodnocení modelu,
- návod ke spuštění,
- dokumentace k obhajobě.

Projekt je navržen tak, aby byl:
- prakticky použitelný,
- spustitelný na školním PC bez IDE,
- obhajitelný po technické stránce.

## Upozornění

Výsledek aplikace je orientační.  
Skutečná cena auta může být ovlivněna i dalšími faktory, které nejsou v inzerátu vždy uvedeny, například:
- technický stav,
- servisní historie,
- výbava,
- nehody,
- kosmetické poškození.

Model tedy neslouží jako absolutní pravda, ale jako podpůrný odhad.

## Autor projektu

Projekt byl vytvořen jako originální softwarová práce se zaměřením na:
- sběr reálných dat,
- jejich zpracování,
- použití strojového učení,
- vytvoření použitelné aplikace nad natrénovaným modelem.
