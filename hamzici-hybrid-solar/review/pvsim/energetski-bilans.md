# Energetski bilans — BS Hamzići (Čitluk)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit e42bbaa. Ulazi i pretpostavke: `pvsim/sites/hamzici.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site hamzici`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje azimut 225° (jugozapad), nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × 150 Ah LFP = 48,6 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,50 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 60 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
- **Potrošnja:** 1180 W TK + 45 W pomoćna (SMU, BMS, ventilatori) + hlađenje ormara do 150 W (linearno 20→35 °C).
- Parametri bez podatka proizvođača (efikasnost i punjenje baterije, stop SoC, zaprljanje, snijeg, hlađenje) su pretpostavke, označene u ulaznom fajlu; njihov uticaj je u tabeli osjetljivosti.

## Validacija prema PVGIS-u

| Nagib | PVcalc, kWh/god | pvsim s PVGIS gubicima 14 %, kWh/god | najveće mjesečno odstupanje | satna korelacija s PVGIS P |
|---|---|---|---|---|
| 45° | 9 047 | 8 996 | 2,3 % | 1,0000 |
| 60° | 8 484 | 8 430 | 2,2 % | 1,0000 |

## Gubici FN lanca (prosjek godine)

| Stavka | 45°, kWh | 60°, kWh | 45°, gubitak | 60°, gubitak |
|---|---|---|---|---|
| Ozračenje u ravni × kWp (STC) | 11 782 | 11 036 |  |  |
| Refleksija (IAM) | 11 424 | 10 695 | −3,03 % | −3,10 % |
| Temperatura i slabo svjetlo (Huld) | 10 461 | 9 803 | −8,43 % | −8,34 % |
| Zaprljanje | 10 248 | 9 606 | −2,04 % | −2,00 % |
| Snijeg | 10 234 | 9 599 | −0,14 % | −0,07 % |
| Neusklađenost + LID | 10 152 | 9 522 | −0,80 % | −0,80 % |
| DC kablovi | 10 105 | 9 479 | −0,46 % | −0,45 % |
| Optimizatori | 10 004 | 9 385 | −1,00 % | −1,00 % |
| iSSU S4875G2 (krivulja) | 9 585 | 8 972 | −4,19 % | −4,39 % |
| iSSU ograničenje 4 kW | 9 585 | 8 972 | −0,00 % | −0,00 % |

## Mjesečni bilans, nagib 45° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 520 | 911 | 427 | 46,8 | 155 |
| feb | 556 | 829 | 332 | 36,4 | 120 |
| mar | 798 | 910 | 232 | 25,5 | 84 |
| apr | 889 | 883 | 138 | 15,1 | 50 |
| maj | 971 | 918 | 100 | 11,0 | 36 |
| jun | 1 022 | 905 | 46 | 5,1 | 17 |
| jul | 1 125 | 952 | 15 | 1,6 | 5 |
| aug | 1 075 | 951 | 27 | 2,9 | 10 |
| sep | 895 | 896 | 90 | 9,9 | 33 |
| okt | 761 | 915 | 203 | 22,3 | 74 |
| nov | 498 | 882 | 414 | 45,4 | 150 |
| dec | 475 | 911 | 470 | 51,5 | 170 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 535 | 911 | 410 | 45,0 | 149 |
| feb | 551 | 829 | 341 | 37,3 | 123 |
| mar | 760 | 910 | 250 | 27,4 | 91 |
| apr | 817 | 883 | 172 | 18,8 | 62 |
| maj | 862 | 918 | 133 | 14,5 | 48 |
| jun | 895 | 905 | 75 | 8,2 | 27 |
| jul | 995 | 952 | 36 | 3,9 | 13 |
| aug | 978 | 951 | 51 | 5,6 | 19 |
| sep | 841 | 896 | 117 | 12,8 | 42 |
| okt | 744 | 915 | 223 | 24,5 | 81 |
| nov | 502 | 882 | 412 | 45,2 | 149 |
| dec | 492 | 911 | 454 | 49,8 | 164 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | RFI / Odluka do Rev 9 |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 9 585 | 8 972 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 365 | 1 278 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 8 725 / 859 | 8 552 / 421 |  |
| Potrošnja, kWh/god | 10 864 | 10 864 |  |
| Solarni udio u potrošnji | 77,0 % | 75,4 % |  |
| Decembar: FN / potrošnja, kWh | 475 / 911 | 492 / 911 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 273 / 319 / 346 | 293 / 347 / 364 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 97 / 121 | 104 / 128 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 903 / 1 054 / 1 144 | 969 / 1 145 / 1 203 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,55 / 0,44 | 0,52 / 0,42 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 2,3 / 3 | 2,4 / 3 |  |
| Najduže razdoblje bez rada DEA, dana | 104 | 74 |  |
| Ekvivalentnih ciklusa baterije, /god | 141 | 144 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 0,0 | 0,0 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 273 | 319 | 346 | 903 | 1 144 | 0,55 | 97 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 302 | 348 | 372 | 996 | 1 228 | 0,50 | 66 |
| Stop SoC 90 % | 302 | 348 | 372 | 996 | 1 228 | 0,50 | 66 |
| Stop SoC 100 % (punjenje do vrha) | 314 | 359 | 391 | 1 034 | 1 287 | 0,48 | 61 |
| Stop SoC 40 % | 263 | 314 | 331 | 870 | 1 093 | 0,57 | 162 |
| Punjenje 0,25 C | 273 | 319 | 346 | 903 | 1 144 | 0,55 | 97 |
| Punjenje 0,15 C | 304 | 356 | 383 | 932 | 1 181 | 0,54 | 96 |
| Start pri DOD 70 % | 280 | 330 | 346 | 926 | 1 143 | 0,54 | 146 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 318 | 373 | 378 | 1 051 | 1 249 | 0,48 | 185 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 246 | 294 | 318 | 811 | 1 051 | 0,62 | 88 |
| Potrošnja 1330 W stalno | 338 | 389 | 406 | 1 115 | 1 343 | 0,45 | 118 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 293 | 347 | 364 | 969 | 1 203 | 0,52 | 104 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 327 | 385 | 405 | 1 081 | 1 337 | 0,46 | 71 |
| Stop SoC 90 % | 327 | 385 | 405 | 1 081 | 1 337 | 0,46 | 71 |
| Stop SoC 100 % (punjenje do vrha) | 342 | 388 | 417 | 1 128 | 1 371 | 0,44 | 66 |
| Stop SoC 40 % | 282 | 338 | 353 | 932 | 1 165 | 0,54 | 174 |
| Punjenje 0,25 C | 293 | 347 | 364 | 969 | 1 203 | 0,52 | 104 |
| Punjenje 0,15 C | 326 | 387 | 404 | 1 000 | 1 232 | 0,50 | 103 |
| Start pri DOD 70 % | 299 | 356 | 372 | 988 | 1 227 | 0,51 | 156 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 340 | 400 | 405 | 1 122 | 1 339 | 0,45 | 197 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 261 | 316 | 332 | 861 | 1 098 | 0,58 | 93 |
| Potrošnja 1330 W stalno | 362 | 425 | 439 | 1 196 | 1 448 | 0,42 | 126 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 273 h/god u prosjeku (P90 319), gorivo 903 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 294 h/god; za gorivo (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) 811 l/god, tj. spremnik 500 l traje 0,62 god.
- **60°:** DEA 293 h/god u prosjeku (P90 347), gorivo 969 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 316 h/god; za gorivo (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) 861 l/god, tj. spremnik 500 l traje 0,58 god.

