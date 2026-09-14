# Objedinjeni proračuni — BS Sjednica (Bileća)

**Verzija:** Rev 9, 11.09.2026. (dopuna istog dana: prava orijentacija lokacije, polje
okrenuto na jugozapad, 4 odvojena nosača 1 × 3).
**Status:** radni proračun Naručioca uz tendersku dokumentaciju. **Nije zamjena za
ovjereni statički i mašinski proračun** koji dostavlja ponuđač — ovdje su izvedene
vrijednosti koje tenderska dokumentacija propisuje kao ulazne i granične.

**Lokacija:** φ = 42,9448° N, λ = 18,3236° E, **1076 m n.v.**, zakupljena parcela
≈150 m², postojeći kontejner K2 3005 × 2300 mm, antenski stub h = 38 m.

**Orijentacija:** kompleks je zakrenut 45° prema pravom sjeveru (Google Maps, Naručilac
11.09.2026.). Vrata kontejnera su na **JI**, hladnjak agregata (izlaz zraka i izduv) na
**SZ**, FN polje na **JZ**, vanjski ormari ICC i MTS na **SI**, u sjeni. Zidovi i strane u
ovom proračunu nose prave smjerove (SI, JI, JZ, SZ).

---

## A. Ambijentalni uslovi

### A.1 Gustoća zraka u funkciji visine i temperature

Barometarski: `p = 101325·(1 − 2,25577·10⁻⁵·h)^5,25588`, zatim `ρ = p / (287,05·T)`.

| Stanje | p | ρ |
|---|---|---|
| 0 m, +25 °C (referenca tehničkog lista) | 101,3 kPa | **1,184 kg/m³** |
| 1076 m, +25 °C | 89,0 kPa | **1,040 kg/m³** |
| 1076 m, −10 °C | 89,0 kPa | 1,179 kg/m³ |
| 1076 m, +40 °C | 89,0 kPa | 0,991 kg/m³ |
| 1076 m, za proračun vjetra (ovjereni projekat) | — | 1,0904 kg/m³ |

**Mjerodavno za:** derating hlađenja agregata (A.2), pritisak vjetra (B.1), gustoću
izduvnih gasova (C.4).

### A.2 Derating agregata na 1076 m

Prema ISO 3046-1 / ISO 8528-1, orijentaciono −1 % snage na svakih 100 m iznad 100 m,
uz dodatnih ≈−3 % za ambijent +40 °C u odnosu na referentnih +25 °C. Ukupni faktor
**0,875**:

| | tehnički list (25 °C, 100 m) | **na lokaciji (1076 m, 40 °C)** |
|---|---|---|
| Standby | 18 kVA / 14,4 kW | **15,8 kVA / 12,6 kW** |
| Prime | 16,5 kVA / 13,2 kW | **14,4 kVA / 11,6 kW** |

Protok zraka hladnjaka raste obrnuto sa gustoćom: `1980 × 1,184/1,090 ≈ 2151 m³/h`.
Ta vrijednost se koristi kao mjerodavni protok u C.1.

**Ponuđač je dužan dostaviti derating proizvođača za tačne uslove lokacije** — ovo je
tenderski zahtjev, ne pretpostavka.

### A.3 Snijeg i led

Koeficijent oblika pri nagibu 45°: **μ₁ = 0,4** prema EN 1991-1-3 §5.3.6 (linearno od
0,8 pri 30° do 0 pri 60°).

Najveća visina snijega opažena na lokaciji je **≈0,5 m**. Pri gustoći slegnutog
snijega 300 kg/m³ to je ≈1,5 kN/m² na tlu, odnosno na ravan panela:

```
s = μ₁ · Ce · Ct · sk = 0,4 · 1,0 · 1,0 · 1,5  ≈  0,6 kN/m²
```

**Mjerodavan je vjetar** — 1,20 kN/m² je dvostruko više. Pri 45° i donjoj ivici na
+0,50 m snijeg se na ravni panela ne zadržava, a izložen vrh u pojasu bure sa udarima
45 m/s ga raznosi. Snijeg pritom djeluje naniže i **umanjuje** mjerodavni uzgon iz
B.5, pa nije ni u jednoj kombinaciji nepovoljan.

**Led je druga stvar.** Naledica se na ovoj koti stvara i zadržava tamo gdje se snijeg
ne zadržava. Zahtjev ostaje **radijalni led 20 mm gustine 300 kg/m³** (Prilog I §1.1,
predmjer 1.3) — mjerodavan je kao akrecija na profile, spojeve i kablove, a ne kao
opterećenje ravni panela.

Provjera snijega prema **BAS EN 1991-1-3 sa BiH nacionalnim aneksom** svejedno mora
postojati u ovjerenom proračunu ponuđača.

### A.4 Ciklusi smrzavanja

Na 1076 m temeljne trake su izložene ciklusima smrzavanja i odmrzavanja uz prisustvo
vode, pa uz klasu čvrstoće mora biti propisana i klasa izloženosti. Usvojeno:
**C30/37, XC4 + XF3, aerant 4–6 %**, na podlozi C12/15, armatura **B500B**, zaštitni
sloj **50 mm**, dubina temeljenja **900 mm**.

### A.5 Geometrija Sunca i decembarski prihvat

Visina Sunca u podne `= 90 − φ + δ`, φ = 42,9448°.

| Datum | δ | Visina u podne | Nagib za normalnu upadnost |
|---|---|---|---|
| 21.12. | −23,44° | **23,6°** | 66,4° |
| 21.03. / 21.09. | 0° | 47,1° | 42,9° |
| 21.06. | +23,44° | 70,5° | 19,5° |

Udio direktnog zračenja prihvaćen u podne 21. decembra, `cos(|h − (90 − nagib)|)`, za
polje okrenuto na jug (polje je okrenuto na JZ, gdje je upadni ugao u podne veći; taj
gubitak je u A.6):

| Nagib | Upadni ugao | cos | Prihvat u decembru |
|---|---|---|---|
| 15° | 51,4° | 0,624 | 62 % |
| 25° | 41,4° | 0,750 | 75 % |
| 35° | 31,4° | 0,854 | 85 % |
| **45° (usvojeno)** | **21,4°** | **0,931** | **93 %** |
| 55° | 11,4° | 0,980 | 98 % |

**Zaključak.** Zimski optimum ovdje je ≈ φ + 10…15 = **53–58°**, dakle 45° je već
*ispod* decembarskog optimuma, a spuštanje na 35° košta oko 8 % decembarskog prinosa.
Ali za otočni sistem sa baterijom od ≈1 dana nije mjerodavan samo decembar: agregat
radi i u nizovima oblačnih dana u proljeće i jesen, gdje strmiji nagib gubi.
Simulacija (A.6, azimut 225°) daje pri 60° 473 kWh u decembru prema 444 kWh pri 45°, ali
**321 h rada agregata godišnje prema 299 h** — strmiji nagib povećava rad agregata.
**Usvojeni nagib: 45°** (odluka 11.09.2026., `review/09-odluka-nosaci-nagib.md`).

### A.6 Energetski bilans — simulacija (pvlib + PVGIS-SARAH3, 2005–2023)

Satni bilans na −48 V DC sabirnici za 19 godina, bez prekida: stanje baterija i nivo
goriva prenose se iz godine u godinu, pa decembarski deficit koji se nastavi u januaru
ostaje jedan deficit. Alat je `pvsim` u repozitoriju; ulazi i pretpostavke su u
`pvsim/sites/sjednica.json` (svaka pretpostavka sa izvorom), rezultati u
`review/pvsim/` (`kpis.json`, `energetski-bilans.md`, slike). Zamjenjuje raniju
procjenu sa paušalnim performance ratio 0,80.

| Ulaz | Vrijednost |
|---|---|
| Ozračenje | PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), satno; polje 45°, azimut 225° (JZ); horizont iz DEM-a (≤5,7°, samo sjever) |
| FN lanac | refleksija Martin-Ruiz (a_r 0,16); temperatura modula Faiman (26,9 / 6,2); model modula Huld c-Si (PVGIS); zaprljanje 1–2,5 % mjesečno; snijeg do 8 % u januaru; neusklađenost 0,3 %, LID 0,5 %; DC kablovi 0,78 % pri Imp (D.2); optimizatori 99,0 %; **iSSU S4875G2 po krivulji proizvođača** (Vin 330 V), 4 kW po modulu |
| Potrošnja | 1180 W TK + 45 W pomoćna (20 W SMU, BMS i ispravljači u mirovanju + 25 W trajni potrošači na −48 V, D.8) + hlađenje ormara do 150 W (linearno 20 → 35 °C) |
| Baterija | 6 × 150 Ah LFP = **48,6 kWh** (Odluka, Aneks 2; odluka Naručioca 11.09.2026.); η punjenja i pražnjenja 97,5 %; punjenje do 0,5 C; donja granica 5 % |
| Agregat | ispravljači ograničeni na 9,5 kW AC (η 96 %); start pri DOD 85 %, stop pri SoC 60 %, najkraći rad 1 h (Prilog I §4.6); gorivo P18-6 prime: 2,6 / 3,4 / 4,4 l/h pri 50 / 75 / 100 % |

**Provjera prema PVGIS-u.** Isti model modula, sa PVGIS-ovim paušalnim gubitkom 14 %,
daje 8 785 kWh/god prema 8 849 kWh/god iz PVGIS PVcalc (−0,7 %); nijedan mjesec ne
odstupa više od 2,2 %, a satna korelacija sa PVGIS-ovom proizvodnjom je r = 1,0000.
Specifični prinos je ispod fizičke granice od ≈1800 kWh/kWp.

**Gubici FN lanca (prosjek godine).**

| Stavka | kWh/god | Gubitak |
|---|---|---|
| Ozračenje u ravni × kWp (STC) | 11 281 | |
| Refleksija (IAM) | 10 921 | −3,18 % |
| Temperatura i slabo svjetlo | 10 216 | −6,46 % |
| Zaprljanje | 10 035 | −1,77 % |
| Snijeg | 9 878 | −1,57 % |
| Neusklađenost + LID | 9 799 | −0,80 % |
| DC kablovi | 9 755 | −0,45 % |
| Optimizatori | 9 657 | −1,00 % |
| **iSSU S4875G2 → DC sabirnica** | **9 242** | −4,29 % |

Na sabirnicu stiže **9 242 kWh/god** (1 317 kWh/kWp, 81,9 % od STC). Najveći
pojedinačni gubitak nosi iSSU: fiksni gubitak mu je ≈44 W po modulu, a moduli dugo
rade pri malom opterećenju.

**Mjesečni bilans (prosjek 2005–2023).**

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | Agregat (DC), kWh | Agregat, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 478 | 911 | 467 | 51,2 | 169 |
| feb | 534 | 829 | 346 | 38,0 | 125 |
| mar | 766 | 910 | 259 | 28,4 | 94 |
| apr | 834 | 882 | 162 | 17,8 | 59 |
| maj | 927 | 913 | 116 | 12,8 | 42 |
| jun | 993 | 892 | 64 | 7,0 | 23 |
| jul | 1 104 | 932 | 19 | 2,0 | 7 |
| aug | 1 039 | 931 | 43 | 4,7 | 15 |
| sep | 857 | 887 | 128 | 14,0 | 46 |
| okt | 762 | 913 | 217 | 23,7 | 78 |
| nov | 504 | 882 | 405 | 44,4 | 147 |
| dec | 444 | 911 | 502 | 55,0 | 182 |
| **godina** | **9 242** | **10 794** | **2 728** | **299** | **988** |

Oko 820 kWh/god FN proizvodnje se ljeti ne može iskoristiti jer su baterije pune;
zimi i u oblačnim nizovima proljeća i jeseni razliku pokriva agregat.

**Ključni pokazatelji (nagib 45°, azimut 225°).**

| Pokazatelj | Vrijednost |
|---|---|
| Solarni udio u potrošnji | 74,7 % |
| **Rad agregata** | **299 h/god** prosjek · P90 364 h · najgora godina 376 h |
| Startova agregata | 106/god prosjek, najviše 131 |
| **Gorivo** | **988 l/god** prosjek · P90 1 202 l · najviše 1 241 l |
| Dopuna spremnika 500 l (pri 20 %) | 2,5 puta godišnje, najviše 3 |
| Najduže razdoblje bez rada agregata | 109 dana |
| Ekvivalentnih ciklusa baterije | 141/god |
| Rad ispod 30 % opterećenja | 0 h |
| Nepokrivena potrošnja | 0 kWh u 19 godina |

**Osjetljivost na postavke SMU i pretpostavke.**

| Slučaj | DEA h/god prosjek | P90 | Najgora | Gorivo l/god | Startova/god |
|---|---|---|---|---|---|
| **Osnovni (Prilog I §4.6): stop SoC 60 %, punjenje 0,5 C** | **299** | **364** | **376** | **988** | **106** |
| SMU bez parametriranja: stop SoC 90 %, 0,25 C | 331 | 388 | 418 | 1 092 | 72 |
| Stop SoC 100 % | 346 | 403 | 432 | 1 138 | 67 |
| Stop SoC 40 % | 290 | 353 | 371 | 959 | 179 |
| Punjenje 0,15 C | 334 | 405 | 413 | 1 021 | 106 |
| Start pri DOD 70 % | 308 | 369 | 386 | 1 018 | 160 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 345 | 410 | 419 | 1 140 | 200 |
| Potrošnja 1180 W stalno | 271 | 333 | 347 | 897 | 97 |
| Potrošnja 1330 W stalno | 371 | 440 | 447 | 1 226 | 130 |

Pri 48,6 kWh punjenje od 0,25 C (≈12 kW) više ne ograničava agregat i daje isto što i
0,5 C; stop pri SoC 90 % daje isto što i „SMU bez parametriranja". Trajni potrošači na
−48 V (D.8, 25 W) dodaju ≈16 h rada agregata i ≈50 l goriva godišnje (pvsim, azimut 225°).

**Orijentacija polja: jug ili jugozapad.** FN plato je na JZ strani kompleksa, a nosači
stoje u nizu paralelno sa ogradom, pa gledaju na **jugozapad (225°)** — odluka Naručioca
11.09.2026., uz poznatu cijenu:

| 45°, prosjek 2005–2023 | FN, kWh/god | Decembar, kWh | DEA h/god prosjek / P90 / najgora | Gorivo, l/god | Neiskorišteno ljeti, kWh/god |
|---|---|---|---|---|---|
| Jug (180°) | 10 137 | 560 | 247 / 307 / 327 | 815 | 1 244 |
| **Jugozapad (225°, usvojeno)** | **9 242** (−8,8 %) | **444** (−21 %) | **299 / 364 / 376** | **988** | 821 |
| Jug-jugozapad (202,5°), za poređenje | 9 845 | 528 | 262 / 322 / — | 865 | 1 087 |

- JZ nijedan mjesec ne daje više od juga; u junu i julu su jednaki. Gubitak je od
  novembra do februara — upravo kad agregat radi: **+52 h/god i +173 l/god**.
- Veći albedo tla (ρ 0,35 umjesto 0,20 u PVGIS-u) smanjuje rad agregata za JZ polje za
  ≈7 h/god; odbijeno zračenje ne zavisi od azimuta, pa jednako pomaže i jugu — razlika
  ostaje.
- Popodnevna toplota ide na štetu JZ polja (Faiman) i već je u rezultatu.

**Zaključak.**

- Uz polje okrenuto na JZ, baterije od 48,6 kWh i trajne potrošače na −48 V prosječan
  rad agregata je **≈300 h/god — iznad granice od 250 h/god iz RFI** i u prosječnoj
  godini (u 9 od 10 godina do ≈360 h, najviše ≈380 h); to je cijena odluke Naručioca o
  orijentaciji JZ (11.09.2026.). Spremnik od 500 l **ne traje godinu dana**
  (≈990 l/god). Odluka (Aneks 2) i Prilog I navode simulirane vrijednosti
  (`review/09-odluka-nosaci-nagib.md`).
- Najveći uticaj ima **kapacitet baterije**: sa 28,8 kWh (6 × 100 Ah iz stare ponude)
  agregat bi radio ≈345 h i trošio ≈1 140 l godišnje. Drugi je **stop SoC**: punjenje
  agregatom do vrha povećava rad agregata za 11–16 %.
- **Agregat je konstrukcijski neophodan**: pokriva ≈25 % potrošnje, najviše od
  novembra do februara.

---

## B. Konstrukcija — nosači FN panela

### B.1 Proračunski pritisak vjetra

Osnovni udar 3 s ≈ **45 m/s**, ρ = 1,0904 kg/m³:

```
qp = 0,5 · 1,0904 · 45²  ≈  1,10 kN/m²   →  usvojeno qp ≥ 1,20 kN/m²
```

### B.2 Kataloški nosači i opterećenje lokacije

Kataloški nosači tipa A deklarisani su na sljedeće udare, odnosno pritiske:

| Nagib | Deklarisani udar | Deklarisani qp | vs. lokacija 1,20 kN/m² |
|---|---|---|---|
| 15° | 40 m/s | 0,87 kN/m² | **ne zadovoljava** |
| 25° | 40 m/s | 0,87 kN/m² | **ne zadovoljava** |
| 35° | 35 m/s | 0,67 kN/m² | **ne zadovoljava** |
| 45° | 31 m/s | 0,52 kN/m² | **ne zadovoljava** |

**Zaključak:** nijedan kataloški nagib nije usklađen sa lokacijom. Nosač je zato
**CUSTOM IZRADA**, a tender traži **ovjereni statički proračun za lokaciju prije
dodjele ugovora**. Kataloške konvencije (marže, prepusti) zadržane su samo kao
geometrijska referenca.

### B.3 Geometrija polja

| | |
|---|---|
| Modul | Huawei iPV585-M2A, **2278 × 1134 × 30 mm, 32,0 kg** |
| Raspored | **3 reda × 1 kolona, položeno** — 3 modula po nosaču |
| Širina polja | **2278 mm** |
| Dužina polja po nagibu | **3442 mm** (3 × 1134 + 2 × 20) |
| Horizontalna projekcija pri 45° | **2434 mm** |
| Broj nosača | **4** (PV-1 … PV-4) → ukupno **12 modula = 7,02 kWp** |
| Niz | 4 × 2278 + 3 × 400 = **10 312 mm**, na JZ platou (zakup 16 × 9,4 m), **400 mm od ograde**, azimut 225° |
| Masa nosača | **ne zadaje se** — utvrđuje je izrađivač ovjerenim proračunom; u dokazu na podizanje se zanemaruje (v. B.5) |

**Zašto 4 × 1×3 (odluka Naručioca 11.09.2026.):** odvojene male ploče umjesto jednog
velikog „jedra", niže polje i manji moment po nosaču (B.5), i **isti nosač na obje
lokacije** — na Hamzićima je JZ pojas dubok 3,30 m, a polje 2×2 portret pri 45° (3,24 m)
tu ne staje.

### B.4 Visinski položaj polja

| | |
|---|---|
| **Donja ivica** | **+0,50 m** od nivoa terena |
| **Gornja ivica** | **+2,93 m** (0,50 + 2,434) |
| Kota ograde | +2,10 m (ovjereni projekat, `04 Ograda`) |
| **Nadvišenje ograde** | **0,83 m** |

> Pri 45° ravan panela presijeca kotu ograde na **1600 mm** od donje ivice (horizontalno),
> dakle 834 mm prije gornje ivice. Nosači stoje **400 mm od ograde** (S-02), pa ravan
> panela ne dolazi do ograde; odmak se potvrđuje pri poziciranju nosača, uz uslov da
> konstrukcija u cijelosti ostane unutar zakupljene parcele 16,00 × 9,40 m.

### B.5 Dejstva vjetra po nosaču pri 45°

| | |
|---|---|
| Površina izložena vjetru | **7,84 m²** (2278 × 3442 mm) |
| Krak težišta iznad terena | **1,717 m** |
| **ULS uzgon** | **14,1 kN** — ne zavisi od visine |
| **Horizontalna sila** | **10,0 kN** |
| **Moment prevrtanja** | **25,7 kNm** |
| **Spreg po traci**, razmak 1600 mm | **16,1 kN** |

Krak težišta: `c = b + (3,442/2)·sin45° = b + 1,217 m`.
Sila: `F = c_f · qp · A = 1,5 · 1,20 · 7,84 = 14,1 kN`, `F_h = F · sin45° = 10,0 kN`,
`F_v = F · cos45° = 10,0 kN`.
Moment: `M = 1,5 · F_h · c = 1,5 · 10,0 · 1,717 = 25,7 kNm` (`pvsim/stands.py`, raspored
4x3L). Zamijenjeni nosač 2×2 portret (3 × 4 modula) imao je 42,6 kNm po nosaču — novi
je za 40 % niži, a gornja ivica 0,8 m niža.

Uzgon: `1,5 · F_v − 0,9 · G = 1,5 · 9,98 − 0,9 · 0,94 = 14,1 kN`. **Vlastita težina
konstrukcije se zanemaruje** — kao povoljno dejstvo ona smanjuje uzgon, pa je njeno
izostavljanje na strani sigurnosti; u `G` ulaze samo moduli (3 × 32 kg = 0,94 kN).
Stvarnu masu nosača utvrđuje izrađivač ovjerenim proračunom i ona ovaj dokaz može samo
poboljšati.

**Mjerodavni su uzgon i prevrtanje, a ne nosivost tla.**

### B.6 Temelji

| | |
|---|---|
| Broj nosača | 4 |
| Traka po nosaču | 2 → **ukupno 8 traka** |
| Dimenzija trake | **500 × 2600 mm, jedinstvena širina po cijeloj dubini** (bez proširenja u dnu), **puna dubina 900 mm** |
| **Zapremina trake** | **1,170 m³** → ukupno **9,36 m³** C30/37 |
| Razmak traka (poprečno) | **1600 mm** |
| Razmak grupa ankera | 1200 mm |
| Beton | **C30/37 (XC4 + XF3, aerant 4–6 %)** na podlozi C12/15 |
| Armatura | **B500B**, zaštitni sloj 50 mm |
| Ankeri | **M16–M20 hemijski (rezinski)**, za kraški vapnenac — nije kataloški dio |

**Zašto traka ide punom dubinom.** Spreg iz B.5 daje **16,1 kN** uzgona na navjetrenu
traku. Uz `γG,stb = 0,9` stabilizujuća težina mora biti ≥17,9 kN, tj. traka ≥0,74 m³:

```
puna traka   1,170 m³ × 24 kN/m³  =  28,1 kN  ≥ 17,9 kN   ZADOVOLJAVA
             (faktorisano: 0,9 × 28,1 = 25,3 kN ≥ 16,1 kN)
```

**Zašto traka nije proširena u dnu.** Rov se u stijeni siječe jednom širinom po cijeloj
dubini; temelj širi u dnu nego u vrhu tražio bi potkopavanje, što na kršu nije izvodivo.
Traka je zato jedinstvenog presjeka 500 mm, a rov se ne zatrpava — beton i podložni
beton ga ispunjavaju do vrha.

Traka manje zapremine ne zatvara ovu provjeru vlastitom težinom i morala bi je
posuditi od trenja o zasip, što na kršu nije dokaz. Ankeri prenose uzgon u traku, ne
u tlo, pa tu razliku ne pokrivaju.

Izvedene količine (predmjer LOT 1, sekcija 2), po traci i ukupno za 8 traka:

| | po traci | ukupno |
|---|---|---|
| Iskop (širina 500, dubina 950 mm) | 1,235 m³ | **9,88 m³** |
| Podložni beton C12/15, d = 50 mm | 0,065 m³ | **0,52 m³** |
| Beton C30/37 | 1,170 m³ | **9,36 m³** |
| Zatrpavanje | — | **nema** |
| Odvoz viška | 1,235 m³ | **9,88 m³** |

Rov je jedinstvene širine, a traka ide punom dubinom, pa ga beton (1,170 m³) i podložni
beton (0,065 m³) ispunjavaju u cijelosti: **zatrpavanja nema**, a sav iskopani materijal
se odvozi. Obrada vidljivih gornjih površina traka: 0,50 × 2,60 × 8 = **10,4 m²**.

Dubina i armatura se **potvrđuju ovjerenim proračunom ponuđača** za qp ≥ 1,20 kN/m².
Temelji se izvode **IZVAN ograđenog platoa**.

### B.7 Pod kontejnera i unos opreme

| | |
|---|---|
| Nosivost poda (g+p, ravnomjerno) | **10,00 kN/m²** — ovjereni projekat, „04 AG dio" 4.4.2.3 |
| Agregat mokro | 372 kg / 0,96 m² = **3,80 kN/m²** |
| Pun spremnik 500 l | 590 kg / 0,63 m² = **9,2 kN/m²** |
| Ukupna masa u kontejneru | **962 kg** |

Obje vrijednosti su ispod 10,00 kN/m², ali su **koncentrisana opterećenja na malom
broju sekundarnih nosača**, dok se 10,00 kN/m² odnosi na ravnomjerno raspodijeljeno
opterećenje. Zbog toga je **čelični roštilj za raznošenje opterećenja OBAVEZAN** —
ispod skida **i** ispod korita — sa prenosom na primarne nosače.

Vrijednost **2,00 kN/m²** iz istog projekta je pokretno opterećenje prohodnog dijela
poda i **nije mjerodavna** za oslanjanje opreme.

**Unos:** skid širine **620 mm** kroz vrata **900 × 2000 mm** — ostaje 280 mm zazora;
visina skida 1020 mm. **Nije potrebno skidati krovni panel ni otvarati zid.**

---

## C. Mašinski dio — agregat

Referentni agregat: **FG Wilson P18-6 (Skid) ili ekvivalent**, tehnički list
2019-08-14. Motor **Perkins 404D-22G1**, 4-cilindarski, linijski, atmosferski, 2,2 l,
1500 o/min. Generator **FG Wilson FGL10040**, IP23, klasa izolacije H, AVR R120.
Skid **1550 × 620 × 1020 mm**, 365 kg suho / **372 kg mokro**.

### C.1 Zrak za hlađenje

| | |
|---|---|
| Protok hladnjaka (tehnički list) | **1980 m³/h** (33 m³/min) |
| Korigovano na gustoću lokacije | **2151 m³/h** |
| Zrak za sagorijevanje | **90 m³/h** (1,5 m³/min) |
| **Ukupno kroz usis** | **2241 m³/h** |
| Maks. vanjski otpor (tehnički list) | **125 Pa** |
| Maks. otpor usisa za sagorijevanje | 3 kPa |

Žaluzine, uz uobičajenih 50 % slobodne površine:

| | Bruto | Slobodno | Brzina | Δp |
|---|---|---|---|---|
| Usisna žaluzina | 500 × 700 = 0,35 m² | 0,175 m² | **3,56 m/s** | ≈17 Pa |
| Izlazna žaluzina | 600 × 600 = 0,36 m² | 0,180 m² | **3,46 m/s** | ≈16 Pa |

Ukupno ≈33 Pa — **duboko unutar budžeta od 125 Pa**, pa se žaluzine ne smanjuju.

**Limeni kanal.** Hladnjak stoji **60 mm** od SZ zida (zid 60 mm), pa kanal nije
razvod nego **prelazni komad** od prirubnice hladnjaka do žaluzine 600 × 600 mm:
razvijena dužina ≈0,2 m × 2,4 m opsega ≈ 0,5 m², sa prirubnicama i fazonskim komadima
**≈1,0 m²**. Doprinos padu pritiska je zanemariv.

### C.2 Toplotni bilans u prostoriji

| | |
|---|---|
| Toplota odvedena rashladnom tečnošću i uljem | 15,2 kW |
| **Toplota zračena u prostoriju** | **5,8 kW** |

Toplotu iz prostorije odnosi struja zraka hladnjaka; **ventilator hladnjaka je
rashladni put**, ne prostorni ventilator.

### C.3 Dopunska ventilacija prostorije

Aksijalni ventilator **1200 m³/h, Ø315 mm, 48 V DC (EC)**, napajan sa DC razvoda (D.8), u
JI zidu; radi po termostatu dok agregat ne radi, a kontroler DEA ga isključuje dok
agregat radi.
Minimalna propisana prostorna ventilacija **120 m³/h** (6 izmjena zraka na sat).
**Ovaj ventilator nije dio rashladnog puta** — on je dopuna.

### C.4 Izduvni sistem

| | |
|---|---|
| Protok izduvnih gasova (standby, 50 Hz) | **192 m³/h** (3,2 m³/min) |
| Temperatura izduva | **413 °C** |
| Usvojeni prečnik | **NO 50** |
| **Brzina** | **27,2 m/s** — ispod uobičajenih 30 m/s ✔ |
| **Protutlak** | **≈1,9 kPa** uz dozvoljenih **10,2 kPa** ✔ |

**Prečnik određuje brzina, ne protutlak** — protutlak ima petostruku rezervu, a brzina
je ta koja se približava granici.

Trasa i količine:

| | |
|---|---|
| Elastični umetak → prigušivač, sa jednim lukom 90° | **1 m** |
| Prigušivač → izlaz iznad krova | **do 4 m** |
| Vanjski prečnik izolacije (NO 50 + 2 × 50 mm vune + Al lim) | ≈165 mm |
| **Površina izolacije i opšava** | 5,0 m × 0,52 m + prigušivač ≈ **3,0 m²** |

Završetak je **iznad krova, usmjeren naviše**, sa hvatačem iskri i kapom protiv upada
padavina.

### C.5 Gorivo

Agregat radi u prime režimu (D.5), pa je mjerodavna potrošnja iz tehničkog lista
P18-6 za prime snagu 13,2 kW:

| Opterećenje (prime) | Potrošnja, 50 Hz |
|---|---|
| 100 % | 4,4 l/h |
| **75 %** | **3,4 l/h** |
| 50 % | 2,6 l/h |

Pri ograničenju ispravljača na 9,5 kW agregat daje ≈9,5 kW (≈72 % prime), dakle
≈3,3 l/h.

| | |
|---|---|
| Očekivani godišnji rad (A.6) | **≈300 h/god**; u 9 od 10 godina do ≈360 h, najviše ≈380 h |
| Očekivana godišnja potrošnja (A.6) | **≈990 l/god**; najviše ≈1 240 l |
| Spremnik **500 l**, dopuna pri 20 % (SMU „Refuel THR") | ≈400 l, tj. ≈120 h rada između dopuna — **2–3 puta godišnje** (prosjek 2,5) |
| **Prvo punjenje** | **250 l** (spremnik se pri primopredaji ne puni do vrha) |

Raniji tekst ovdje je navodio „do 250 h/god" i ≈925 l/god — dakle ni tada spremnik od
500 l nije bio godišnja zaliha.

### C.6 Spremnik i sekundarna zaštita

Spremnik **dvoplašni, 500 l**, 1050 × 600 × 1310 mm, 170 kg prazan / ≈590 kg pun, sa
nivo sondom i **sondom za detekciju curenja u međuplaštu**.

**Tankvana zapremine 110 % NIJE zahtijevana**, jer međuplašt dvoplašnog spremnika
jeste sekundarna zaštita. Ispod spremnika se izvodi samo **prihvatno korito (kada)
1150 × 640 mm, visina ruba 200 mm**, za prihvat kapanja i prosipanja pri punjenju i
pretakanju, sa vidljivim najnižim mjestom za kontrolu i pražnjenje.

> Tankvana ne dobija zapreminu visinom, jer spremnik koji u njoj stoji istiskuje
> zapreminu zadržavanja — računa se samo **slobodna površina × visina ruba**. Uz
> slobodnu površinu od 0,33 m², koliko je ostaje u raspoloživom pojasu, rub bi morao
> biti visok **1,67 m** da se dosegne 110 %. Zato dvoplašni spremnik, a ne tankvana.

### C.7 Raspored otvora i servisni prostor

Ukrsno strujanje **SI → SZ**:

| Element | Zid | Napomena |
|---|---|---|
| Usis 500 × 700 | **SI**, jugoistočni kraj | donja ivica +0,30 m; zasjenjena strana, najhladniji zrak |
| Kanal + izlazna žaluzina 600 × 600 | **SZ** | na osi hladnjaka, prelazni komad |
| Izduv NO 50 | **SZ** | uspon uz zid, iznad krova |
| Oduška spremnika | **JZ**, jugoistočni kraj | ≥3 m od izduva i usisa |
| Ventilator Ø315 | **JI**, gore | donja ivica ≈+1,75 m |
| GRO | **SI** | uz vanjski ormar koji napaja |
| DC razvod −48 V | **SI**, uz GRO | trajni potrošači D.8 |

Izlaz toplog zraka i izduv **nisu** na SI strani, pa se vanjski ormari
**ICC360-HA1-C1** (sa aktivnim hlađenjem) i **MTS9302A** ne izlažu toplom zraku.

**Servisni prostor oko agregata** — agregat je centriran u slobodnom prostoru:

| Strana | Slobodno |
|---|---|
| JZ | **720 mm** |
| SI | **720 mm** (520 mm na dijelu gdje je GRO) |
| JI | **1155 mm** |
| SZ | 60 mm — hladnjak, izduvava u kanal, ne servisira se s te strane |

Unutrašnja dubina 2180 mm umanjena za 740 mm (roštilj) ostavlja 1440 mm, podijeljeno
na pola. **Ovi prolazi se ne smiju zauzimati opremom niti skladištenjem.**

Skid stoji na **antivibracionim gumeno-metalnim osloncima** (vlastita frekvencija
≤8 Hz, statički progib ≥5 mm) između skida i roštilja. Zbog toga svi priključci na
motor moraju biti elastični: izduv preko elastičnog umetka, hladnjak preko ceradnog
spoja, a **vod goriva preko fleksibilnog umetka na polaznom i povratnom vodu** — kruta
Cu cijev NO 8 na priključku motora koji se pomiče zamara se i puca.

---

## D. Elektro dio

### D.1 String FN panela

| | |
|---|---|
| 6 × iPV585-M2A | Voc **309,3 V**, Vmp **256,7 V**, Imp 13,67 A, Isc 14,40 A |
| Prozor iSSU S4875G2 | 85–435 V DC, maks. 25 A, maks. 4000 W |
| Provjera | 257 V ✔ · 13,67 A ✔ · 3510 W ✔ |
| Optimizator SUN2000-600W-P | Vout 0–80 V, **Iout maks. 15 A** → 13,67 A ✔ |
| PVDB500-15-2B | 100–500 V, **maks. 15 A po ruti**, 2 rute → 1 string po ruti ✔ |
| Huawei pravilo za string | iPV540/585/630: **3–12 modula po stringu** → 6 ✔ |

**12 modula = 2 stringa × 6**, a ne 3 × 4: PVDB ima dva izlaza, a 6 × 51,55 V = 309 V
Voc je unutar prozora iSSU. String time obuhvata dva nosača (PV-1 + PV-2, PV-3 + PV-4).

> **Napomena koju tender ne smije ostaviti otvorenom:** iSSU se povezuje **isključivo**
> na iPV module sa optimizatorima. Obični 585 W moduli tražili bi SSU S4875G6 i drugo
> pravilo za string (3–7 modula ispod −10 °C).

### D.2 DC kabl

```
6 mm² Cu, 25 m u jednom smjeru, Imp 13,67 A
ΔU = 2 · 25 · 13,67 · 0,0175 / 6 = 1,99 V = 0,78 % od 257 V     ZADOVOLJAVA (<1 %)
```

Presjek je predimenzionisan; **ograničenje je stezaljka, a ne kabl** — ulazna
stezaljka iSSU traži **tačno 4 mm²**, pa je na ormaru potreban prelaz.

### D.3 DC potrošnja

| | pri 53,5 V | pri 48,0 V |
|---|---|---|
| 1180 W nazivno | 22,1 A | 24,6 A |
| 1330 W maksimalno | 24,9 A | 27,7 A |

Godišnje 10 337 kWh pri stalnih 1180 W; simulacija (A.6) dodaje hlađenje ormara i
pomoćnu potrošnju sa trajnim potrošačima (D.8), pa računa sa 10 794 kWh/god, u decembru
911 kWh.

### D.4 AC strana agregata — pobuda i struja kvara

| | |
|---|---|
| Nazivna struja pri 18 kVA / 400 V | **In = 26,0 A** |
| Traženo 3 × In, 10 s (ISO 8528-3) | **≈78 A** |
| Trajna struja kvara sa SHUNT pobudom | **≈13 A (0,5 × In)** — **ISPOD** nazivne struje |

**Standardna SHUNT pobuda nije prihvatljiva.** Kod nje se pri kvaru napon na
stezaljkama uruši, pobuda nestaje, i trajna struja kvara padne ispod nazivne — ne može
aktivirati nijednu prekostrujnu zaštitu. Tehnički list referentnog P18-6 na strani 4
navodi **Short Circuit Capacity 0 %** u standardnoj izvedbi, a traženu trajnu struju
kvara daje tek opciona **PMG / AUX** pobuda. **Zahtjev za nezavisnom pobudom (PMG ili
AREP/AUX) time je potvrđen samim tehničkim listom.**

Posljedica za zaštitu: na otočnom izvoru struja kvara ne može pouzdano isključiti
MCB, pa se zaštita od indirektnog dodira oslanja na **RCD** prema IEC 60364-4-41.

### D.5 Ograničenje ulazne snage ispravljača — **mjerodavno**

| | |
|---|---|
| Ispravljački sistem 3 × R4875G5 | 12 kW DC → **≈12,5 kW na AC strani** |
| Derativana snaga agregata, standby | **12,6 kW** — bez ikakve rezerve |
| Derativana snaga agregata, **prime** | **11,6 kW** — **premašeno** |

Lokacija **nije na mreži** i agregat radi ciklično po stanju napunjenosti baterija
(SoC), pa je mjerodavan **PRIME režim**, a ne standby. Neograničeno opterećenje od
12,5 kW premašuje raspoloživu snagu.

**Usvojeno: ulazna snaga ispravljačkog sistema ograničava se u kontroleru na
maks. 9,5 kW dok radi agregat** (≈82 % derativane prime snage). To ostavlja ≈8,2 kW
za punjenje baterija iznad TK potrošnje od 1,33 kW i istovremeno drži agregat iznad
minimalnog opterećenja od 30 %, čime se sprječava mokri rad motora (cilindarsko
glaziranje). **Ponuđač dokazuje usklađenost proračunom deratinga za lokaciju.**

Brojka **9,5 kW** mora stajati u predmjeru (Tačke 3.1 i 5.7) — opisni zahtjev
„ograničiti ulaznu snagu" bez broja ne obavezuje nikoga.

### D.6 Uzemljenje i zaštita od munje

| | |
|---|---|
| Traženi presjek vodiča | **Cu 50 mm²** prema EN 62305-3, tabela 7 |
| Postojeći prstenasti uzemljivač | Fe/Zn 25 × 4 mm — **obavezni bimetalni spojevi** Cu/Fe-Zn |
| Ciljani otpor rasprostiranja | **≤10 Ω** |
| Razmak kabla od odvoda munje | **≥0,5 m** |
| FN polja vs. zona zaštite stuba | **unutar** zone kotrljajuće sfere (7,6 m stvarno, najdalji ugao niza, prema 10,68 m zaštićenog poluprečnika pri LPL I) → **nisu potrebne dodatne hvataljke** |

Sistem uzemljenja **TN-S**; tačka spajanja **N i PE samo u novom GRO**.

### D.7 Prenaponska zaštita

Objekat ima vanjski sistem zaštite od munje (antenski stub h = 38 m) i separacija nije
održana, pa **tip 2 sam po sebi nije dovoljan**:

- **AC porijeklo: kombinovani TIP 1 + 2** prema EN 61643-11, Iimp ≥12,5 kA (10/350 µs)
  po polu, Up ≤1,5 kV, 4p, sa daljinskom signalizacijom
- **DC, po stringu: tip 2** — u PVDB ormaru
- **Signalni i komunikacioni vodovi: EN 61643-21**, na oba kraja dionice

### D.8 Trajni potrošači na −48 V DC

Agregat je jedini izvor izmjeničnog napona i ≈97 % godine ne radi. Potrošači koji moraju
raditi stalno napajaju se zato sa −48 V DC iz ormara ICC360, preko novog DC razvoda
(odluka Naručioca 11.09.2026):

| Potrošač | Napajanje | Prosječno |
|---|---|---|
| Signalna rasvjeta stuba (K7), LED | 48 V DC, foto-senzor (≈12 h noću) | ≈8 W |
| Vatrodojavna centrala | DC/DC | ≈4 W |
| Punjač akumulatora za start agregata | DC/DC | ≈3 W |
| Ventilator prostora 48 V DC (EC) | termostat, ljeti | ≈2 W |
| Predgrijač rashladne tečnosti DEA | DC, samo prije starta pri niskoj temperaturi (≈0,1 kWh po startu) | ≈1 W |
| Gubici DC/DC | | ≈3 W |
| **Ukupno** | | **≈21 W → usvojeno ≤25 W** |

Jedna svjetiljka u kontejneru je za 48 V DC, pa je svjetlo dostupno i kad agregat ne
radi; radi samo pri obilasku i ne ulazi u trajnu potrošnju. Energetski bilans (A.6)
računa sa 45 W pomoćne potrošnje na −48 V: 20 W za SMU, BMS i ispravljače u mirovanju i
25 W za trajne potrošače.

---

## E. Šta šta određuje — sažetak

| Veličina | Određuje je | Vrijednost |
|---|---|---|
| Nagib 45° | godišnji rad agregata (A.5, A.6) — 60° daje više u decembru, a ukupno više rada DEA | 299 h pri 45° prema 321 h pri 60° (azimut 225°) |
| Azimut 225° (JZ) | položaj FN platoa; odluka Naručioca 11.09.2026. (A.6) | +52 h/god i +173 l/god prema jugu |
| Nosač 4 × 1×3, položeno | odvojene male ploče, isti nosač na obje lokacije (B.3) | 7,84 m² po nosaču |
| Custom nosač | qp lokacije vs. kataloške deklaracije (B.2) | nijedan nagib ne prolazi |
| Donja ivica +0,50 m | vjetar je mjerodavan, snijeg nije (A.3) | moment 25,7 kNm |
| Puna dubina temeljne trake | spreg od uzgona po traci (B.6) | 0,9 × 25,3 = 22,7 > 16,1 kN |
| Prečnik izduva NO 50 | brzina, ne protutlak (C.4) | 27,2 m/s < 30 |
| Roštilj za raznošenje | koncentrisano vs. ravnomjerno opterećenje (B.7) | OBAVEZAN |
| Ograničenje ispravljača 9,5 kW | derating u prime režimu (D.5) | 11,6 kW raspoloživo |
| PMG/AREP pobuda | struja kvara ispod In kod SHUNT (D.4) | 0 % po tehničkom listu |
| Spremnik 500 l | simulirani rad ≈300 h i ≈990 l/god (A.6, C.5) | ≈120 h rada između dopuna, 2–3 dopune godišnje |
| Baterije 6 × 150 Ah (48,6 kWh) | Odluka, Aneks 2; odluka Naručioca (A.6) | ≈300 h/god prema ≈345 h sa 28,8 kWh |
| Stop SoC 60 %, punjenje do granice BMS-a | osjetljivost simulacije (A.6) | ≈10 % manje rada DEA nego bez parametriranja |
| Trajni potrošači na −48 V DC | agregat je jedini AC izvor; odluka Naručioca (D.8) | ≤25 W, ≈+16 h/god rada DEA |

---

## F. Otvorene stavke

1. **Odmak polja od ograde** (400 mm na S-02) potvrđuje se pri poziciranju nosača
   (B.4) — ravan panela siječe kotu ograde na 1600 mm od donje ivice.
2. **Ovjereni statički proračun nosača i temelja** za qp ≥ 1,20 kN/m² — uslov prije
   dodjele ugovora, ne isporuka nakon nje.
3. **Derating agregata za tačne uslove lokacije** iz podataka proizvođača (A.2, D.5).
4. **Integracija DC odvodnika tipa 2 u PVDB500-15-2B** nije dokazana nijednim
   dokumentom u paketu — stavka ostaje zasebno iskazana dok se ne potvrdi.
5. **Kapacitet baterija** — riješeno 11.09.2026.: **6 × 150 Ah (48,6 kWh)**, kako navodi
   Odluka; ponuda na dosjeu (6 × ESM-48100A6, 28,8 kWh, uz module od 540 W) je
   zastarjela i Huawei narudžbu treba uskladiti. Proračun A.6 računa sa 48,6 kWh.
6. **Masa nosača se ne zadaje** (komentar recenzenta, 27.08.2026.) — utvrđuje je izrađivač
   ovjerenim proračunom; dokaz na podizanje je vodi kao zanemarenu (B.5).
7. **Procijenjena vrijednost LOT 1** (15.000 KM) računata je na raniju zapreminu
   temeljnih traka; puna dubina iz B.6 nosi 9,36 m³ betona u 8 traka umjesto 2,44 m³.
8. **Struja punjenja baterija** (Prilog I §4.6): simulacija (A.6) pretpostavlja 0,5 C;
   najveću struju punjenja potvrđuje proizvođač baterija. Pri 48,6 kWh ni 0,25 C ne
   ograničava agregat; tek pri 0,15 C rad agregata raste na ≈335 h/god.
9. **Stvarna potrošnja** 1180 W / 1330 W je iz RFI; pri stalnih 1330 W rad agregata je
   ≈370 h/god (A.6, osjetljivost).

---

*Izvedene vrijednosti se održavaju u `cad/design.json`; crteži S-01…S-03, M-01 i E-01
formatiraju kote direktno iz tog fajla. Historija izmjena je u `00-change-log.md`.*
