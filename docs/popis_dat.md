# Popis původu dat

Data nejsou převzata z hotového datasetu. Byla získána vlastním crawlerem ze skutečných veřejně dostupných inzerátů ojetých vozidel.

## Zdroj
- inzeráty na webu TipCars

## Způsob získání
- vlastní Python crawler v samostatné složce `crawler`
- výstup do CSV a JSON
- následná deduplikace a čištění v `preprocess.py`

## Povinné předzpracování
- odstranění duplicit
- odstranění neplatných a extrémně chybných hodnot
- převod textových a číselných sloupců do jednotného formátu
- doplnění odvozených atributů `age` a `km_per_year`
- škálování numerických atributů a OneHot encoding kategorií během trénování modelu
