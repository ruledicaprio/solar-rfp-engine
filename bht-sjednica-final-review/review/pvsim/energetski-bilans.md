# Energetski bilans — BS Sjednica (Bileća)

*Simulacija pvlib + PVGIS-SARAH3, satno 2005–2023. Generisano 2026-09-11, pvsim 0.1.0, commit e42bbaa. Ulazi i pretpostavke: `pvsim/sites/sjednica.json`; brojevi: `kpis.json` u ovom folderu. Ne uređivati ručno — `python -m pvsim report --site sjednica`.*

## Metoda

- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno za 19 godina; horizont iz PVGIS DEM-a; polje azimut 225° (jugozapad), nagib 45° i 60°.
- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman (26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.
- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija 6 × 150 Ah LFP = 48,6 kWh, η punjenja/pražnjenja 97,5 %, punjenje do 0,50 C. DEA preko ispravljača ograničenih na 9,5 kW AC (η 96 %): start pri DOD 85 %, stop pri SoC 60 %, najkraći rad 1,0 h. Gorivo po tehničkom listu P18-6 (prime).
- **Potrošnja:** 1180 W TK + 45 W pomoćna (SMU, BMS, ventilatori) + hlađenje ormara do 150 W (linearno 20→35 °C).
- Parametri bez podatka proizvođača (efikasnost i punjenje baterije, stop SoC, zaprljanje, snijeg, hlađenje) su pretpostavke, označene u ulaznom fajlu; njihov uticaj je u tabeli osjetljivosti.

## Validacija prema PVGIS-u

| Nagib | PVcalc, kWh/god | pvsim s PVGIS gubicima 14 %, kWh/god | najveće mjesečno odstupanje | satna korelacija s PVGIS P |
|---|---|---|---|---|
| 45° | 8 849 | 8 785 | 2,2 % | 1,0000 |
| 60° | 8 277 | 8 212 | 2,1 % | 1,0000 |

## Gubici FN lanca (prosjek godine)

| Stavka | 45°, kWh | 60°, kWh | 45°, gubitak | 60°, gubitak |
|---|---|---|---|---|
| Ozračenje u ravni × kWp (STC) | 11 281 | 10 543 |  |  |
| Refleksija (IAM) | 10 921 | 10 204 | −3,18 % | −3,21 % |
| Temperatura i slabo svjetlo (Huld) | 10 216 | 9 549 | −6,46 % | −6,42 % |
| Zaprljanje | 10 035 | 9 382 | −1,77 % | −1,74 % |
| Snijeg | 9 878 | 9 304 | −1,57 % | −0,84 % |
| Neusklađenost + LID | 9 799 | 9 230 | −0,80 % | −0,80 % |
| DC kablovi | 9 755 | 9 189 | −0,45 % | −0,45 % |
| Optimizatori | 9 657 | 9 097 | −1,00 % | −1,00 % |
| iSSU S4875G2 (krivulja) | 9 242 | 8 689 | −4,29 % | −4,49 % |
| iSSU ograničenje 4 kW | 9 242 | 8 689 | −0,00 % | −0,00 % |

## Mjesečni bilans, nagib 45° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 478 | 911 | 467 | 51,2 | 169 |
| feb | 534 | 829 | 346 | 38,0 | 125 |
| mar | 766 | 910 | 259 | 28,4 | 94 |
| apr | 834 | 882 | 162 | 17,8 | 59 |
| maj | 927 | 913 | 116 | 12,8 | 42 |
| jun | 993 | 892 | 64 | 7,0 | 23 |
| jul | 1 104 | 932 | 19 | 2,0 | 7 |
| aug | 1 039 | 931 | 43 | 4,7 | 15 |
| sep | 857 | 887 | 128 | 14,0 | 46 |
| okt | 762 | 913 | 217 | 23,7 | 78 |
| nov | 504 | 882 | 405 | 44,4 | 147 |
| dec | 444 | 911 | 502 | 55,0 | 182 |

## Mjesečni bilans, nagib 60° (prosjek godina)

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | DEA, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 511 | 911 | 440 | 48,3 | 160 |
| feb | 543 | 829 | 340 | 37,3 | 123 |
| mar | 739 | 910 | 273 | 30,0 | 99 |
| apr | 766 | 882 | 206 | 22,6 | 75 |
| maj | 821 | 913 | 164 | 18,0 | 59 |
| jun | 867 | 892 | 105 | 11,5 | 38 |
| jul | 973 | 932 | 52 | 5,7 | 19 |
| aug | 941 | 931 | 78 | 8,5 | 28 |
| sep | 800 | 887 | 154 | 16,9 | 56 |
| okt | 743 | 913 | 240 | 26,3 | 87 |
| nov | 512 | 882 | 398 | 43,7 | 144 |
| dec | 473 | 911 | 477 | 52,3 | 173 |

## Ključni pokazatelji

| Pokazatelj | 45° | 60° | RFI / Odluka do Rev 9 |
|---|---|---|---|
| FN na DC sabirnici, kWh/god | 9 242 | 8 689 |  |
| Specifični prinos na sabirnici, kWh/kWp | 1 317 | 1 238 |  |
| FN iskorišteno / odbačeno (baterija puna), kWh/god | 8 421 / 821 | 8 227 / 461 |  |
| Potrošnja, kWh/god | 10 794 | 10 794 |  |
| Solarni udio u potrošnji | 74,7 % | 72,9 % |  |
| Decembar: FN / potrošnja, kWh | 444 / 911 | 473 / 911 |  |
| DEA rad, h/god — prosjek / P90 / najgora god. | 299 / 364 / 376 | 321 / 392 / 397 | ≤250 h/god |
| DEA startova, /god — prosjek / najviše | 106 / 131 | 114 / 141 |  |
| Gorivo, l/god — prosjek / P90 / najgora god. | 988 / 1 202 / 1 241 | 1 060 / 1 296 / 1 313 |  |
| Spremnik 500 l traje, god — prosjek / najgora | 0,51 / 0,40 | 0,47 / 0,38 | ≥1 god |
| Dopuna goriva, /god — prosjek / najviše | 2,5 / 3 | 2,6 / 4 |  |
| Najduže razdoblje bez rada DEA, dana | 109 | 81 |  |
| Ekvivalentnih ciklusa baterije, /god | 141 | 144 |  |
| Rad DEA ispod 30 % opterećenja, h/god | 0,0 | 0,0 |  |
| Nepokrivena potrošnja, kWh | 0,0 | 0,0 | 0 |
| ≤250 h/god (P90 / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |
| ≥1 god na spremnik (prosjek / najgora god.) | **NIJE ispunjeno** / **NIJE ispunjeno** | **NIJE ispunjeno** / **NIJE ispunjeno** | |

## Osjetljivost, nagib 45°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 299 | 364 | 376 | 988 | 1 241 | 0,51 | 106 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 331 | 388 | 418 | 1 092 | 1 382 | 0,46 | 72 |
| Stop SoC 90 % | 331 | 388 | 418 | 1 092 | 1 382 | 0,46 | 72 |
| Stop SoC 100 % (punjenje do vrha) | 346 | 403 | 432 | 1 138 | 1 423 | 0,44 | 67 |
| Stop SoC 40 % | 290 | 353 | 371 | 959 | 1 225 | 0,52 | 179 |
| Punjenje 0,25 C | 299 | 364 | 376 | 988 | 1 241 | 0,51 | 106 |
| Punjenje 0,15 C | 334 | 405 | 413 | 1 021 | 1 275 | 0,49 | 106 |
| Start pri DOD 70 % | 308 | 369 | 386 | 1 018 | 1 276 | 0,49 | 160 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 345 | 410 | 419 | 1 140 | 1 385 | 0,44 | 200 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 271 | 333 | 347 | 897 | 1 146 | 0,56 | 97 |
| Potrošnja 1330 W stalno | 371 | 440 | 447 | 1 226 | 1 475 | 0,41 | 130 |

## Osjetljivost, nagib 60°

| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | najgora | Spremnik traje, god | Startova/god |
|---|---|---|---|---|---|---|---|
| Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C | 321 | 392 | 397 | 1 060 | 1 313 | 0,47 | 114 |
| SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C | 355 | 426 | 431 | 1 171 | 1 423 | 0,43 | 77 |
| Stop SoC 90 % | 355 | 426 | 431 | 1 171 | 1 423 | 0,43 | 77 |
| Stop SoC 100 % (punjenje do vrha) | 373 | 442 | 454 | 1 228 | 1 496 | 0,41 | 72 |
| Stop SoC 40 % | 310 | 383 | 388 | 1 024 | 1 283 | 0,49 | 191 |
| Punjenje 0,25 C | 321 | 392 | 398 | 1 060 | 1 313 | 0,47 | 114 |
| Punjenje 0,15 C | 357 | 439 | 445 | 1 095 | 1 370 | 0,46 | 113 |
| Start pri DOD 70 % | 327 | 400 | 406 | 1 081 | 1 341 | 0,46 | 170 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 369 | 436 | 449 | 1 219 | 1 484 | 0,41 | 214 |
| Potrošnja 1180 W stalno (bez hlađenja i pomoćne) | 287 | 357 | 369 | 950 | 1 219 | 0,53 | 102 |
| Potrošnja 1330 W stalno | 396 | 475 | 481 | 1 309 | 1 590 | 0,38 | 138 |

## Zaključak (izveden iz brojeva iznad)

- **45°:** DEA 299 h/god u prosjeku (P90 364), gorivo 988 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 333 h/god; za gorivo (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) 897 l/god, tj. spremnik 500 l traje 0,56 god.
- **60°:** DEA 321 h/god u prosjeku (P90 392), gorivo 1 060 l/god. Najpovoljniji slučaj osjetljivosti za sate (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) daje P90 357 h/god; za gorivo (Potrošnja 1180 W stalno (bez hlađenja i pomoćne)) 950 l/god, tj. spremnik 500 l traje 0,53 god.

