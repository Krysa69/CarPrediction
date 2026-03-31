# Body k obhajobě

## Proč toto téma
Vybral jsem problém, který má reálné použití. Běžný člověk často nepozná, zda je nabídka ojetého auta cenově přiměřená.

## Proč nestačí jen odhad ceny
Samotná predikce ceny je užitečná, ale aplikace jde dál. Porovnává modelový odhad s konkrétní inzerovanou cenou a vrací praktický verdikt pro rozhodování uživatele.

## Jak vznikla data
Data byla získána mým vlastním crawlerem. Nepoužil jsem žádný hotový dataset.

## Jak proběhlo čištění
Odstranil jsem duplicity, nesmyslné ceny, neplatné roky, přehnané nájezdy a sjednotil kategorické hodnoty.

## Jaký model jsem zvolil
Použil jsem regresní model RandomForestRegressor. Zvolil jsem ho proto, že dobře pracuje s nelineárními vztahy a nepotřebuje složité ruční nastavování.

## Co dělá aplikace navíc
Kromě odhadu ceny vrací i odchylku od inzerované ceny, slovní vyhodnocení a stručné důvody.
