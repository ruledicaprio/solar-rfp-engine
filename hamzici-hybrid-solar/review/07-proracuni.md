# Objedinjeni proračuni — BS Hamzići (Čitluk)

**Verzija:** Rev 2, 11.09.2026. (FN niz na jugozapadu, 4 nosača 1 × 3, zidovi po stranama svijeta)
**Status:** radni proračun Naručioca uz zajedničku tendersku dokumentaciju za lokacije
Sjednica i Hamzići. **Nije zamjena za ovjereni statički i mašinski proračun** koji
dostavlja ponuđač — ovdje su izvedene vrijednosti koje tenderska dokumentacija propisuje
kao ulazne i granične.

**Lokacija:** φ = 43,2880° N, λ = 17,6248° E, **493 m n.v.** (PVGIS DEM; projekat 500 m),
k.č. 109/1 K.O. Hamzići, zakup 12,00 × 12,50 m = 150 m². Postojeći kontejner K2
3005 × 2300 mm na AB ploči 5,40 × 5,40 m, u sredini između nogu rešetkastog stuba
h = 32 m (platforma na +3,0 m iznad krova kontejnera). Ovjereni projekat:
GP-BS-10472-291 (2017), verzija A; geometrija u `cad/site_geometry.json`.

**Sistem je isti kao na Sjednici** (odluka Naručioca 11.09.2026.): 12 × iPV585-M2A na
4 nosača × 3 modula (položeno) pri 45°, azimut 225° (JZ), FG Wilson P18-6 u kontejneru,
baterije 6 × 150 Ah (48,6 kWh), ICC360-HA1-C1, ograničenje ispravljača 9,5 kW. Ovdje su
proračunate samo vrijednosti koje zavise od lokacije; ostale su u proračunu za Sjednicu i
vrijede i ovdje.

**Orijentacija.** Prema Google Maps (Naručilac 11.09.2026.) kompleks je zakrenut 45°:
vrata kontejnera i kapija ograde gledaju na **sjeverozapad (SZ)**, klima-uređaj Stulz je u
sredini **jugoistočnog (JI) zida**. Zidovi i strane se zato navode po stranama svijeta:
SZ (vrata), SI, JI (Stulz), JZ (FN niz). Crteži H-01 … H-05 su pravougaoni na kompleks,
sa strelicom sjevera zakrenutom 45°. Ovjereni crtež iz 2017. prikazuje vrata na suprotnoj
strani — zakrenut je ≈180° prema terenu.

---

## A. Ambijentalni uslovi

### A.1 Gustoća zraka

`p = 101325·(1 − 2,25577·10⁻⁵·h)^5,25588`, `ρ = p / (287,05·T)`:

| Stanje | p | ρ |
|---|---|---|
| 0 m, +25 °C (referenca tehničkog lista) | 101,3 kPa | **1,184 kg/m³** |
| 493 m, +25 °C | 95,5 kPa | **1,116 kg/m³** |
| 493 m, −5 °C | 95,5 kPa | 1,241 kg/m³ |
| 493 m, +40 °C | 95,5 kPa | 1,063 kg/m³ |

### A.2 Derating agregata na 493 m

ISO 3046-1 / ISO 8528-1: −1 % na svakih 100 m iznad 100 m (−3,9 %) i ≈−3 % za ambijent
+40 °C. Ukupni faktor **0,931**:

| | tehnički list (25 °C, 100 m) | **na lokaciji (493 m, 40 °C)** |
|---|---|---|
| Standby | 18 kVA / 14,4 kW | **16,8 kVA / 13,4 kW** |
| Prime | 16,5 kVA / 13,2 kW | **15,4 kVA / 12,3 kW** |

Protok zraka hladnjaka: `1980 × 1,184/1,063 ≈ 2206 m³/h` (C.1). Ljetni prosjek jula i
avgusta je 24,7 °C, pa je +40 °C mjerodavan projektni ambijent.

### A.3 Snijeg i led

Ovjereni projekat kontejnera računa sa **S = 2,10 kN/m²** na tlu. Pri nagibu 45° je
μ₁ = 0,4 (EN 1991-1-3 §5.3.2), pa na ravni panela:

```
s = μ₁ · Ce · Ct · sk = 0,4 · 1,0 · 1,0 · 2,10  ≈  0,84 kN/m²
```

**Mjerodavan je vjetar** (1,20 kN/m², B.1). Snijeg djeluje naniže i umanjuje
mjerodavni uzgon. Na 493 m u hercegovačkom pojasu snijeg je rijedak i kratkotrajan.

Led: ovjereni projekat stuba računa sa naslagom **20 mm, gustine 500 kg/m³** — zahtjev
za akreciju na profile i spojeve nosača. Provjera prema BAS EN 1991-1-3 sa NA ostaje
obavezna u ovjerenom proračunu ponuđača.

### A.4 Beton i smrzavanje

Zadržano je **C30/37, XC4 + XF3, aerant 4–6 %**, na podlozi C12/15, armatura B500B,
zaštitni sloj 50 mm, dubina 900 mm — ista specifikacija kao na Sjednici, radi jednog
opisa za obje lokacije u LOT-u 1. Na 493 m bi XF1 bio dovoljan.

Tlo: prema ovjerenom projektu σdop = **150 kN/m²**, bez podzemne vode; krš, stijena blizu
površine (fotografije).

### A.5 Geometrija Sunca

Visina Sunca u podne `= 90 − φ + δ`, φ = 43,288°:

| Datum | δ | Visina u podne | Nagib za normalnu upadnost |
|---|---|---|---|
| 21.12. | −23,44° | **23,3°** | 66,7° |
| 21.03. / 21.09. | 0° | 46,7° | 43,3° |
| 21.06. | +23,44° | 70,2° | 19,8° |

Polje gleda na **jugozapad (azimut 225°)**. Pri 45° upadni ugao direktnog zračenja u podne
21. decembra je 42,4° (cos 0,739); zimsko Sunce je okomito na ravan polja oko 14:30 po
sunčevom vremenu. Strmiji nagib pomaže decembru, ali agregat godišnje radi više: pri
60° 492 kWh u decembru prema 475 kWh pri 45°, ali **293 h/god rada agregata prema
273 h** (A.6). **Usvojeni nagib: 45°** (odluka 11.09.2026.); 60° ostaje samo kao
poređenje.

**Horizont:** PVGIS DEM ≤2,7°, samo na sjeveru. **Stablo** JJI–JI od stuba (≈7–9 m,
15–20 m, procjena iz fotografija, izvan zakupa) se sa sredine FN niza u JZ pojasu vidi na
azimutu ≈123–141°, do 13–26° visine — za ravan okrenutu na jugozapad bočno i iza nje.
Stablo ostaje (odluka 11.09.2026.); uticaj je u A.6.

### A.6 Energetski bilans — simulacija (pvlib + PVGIS-SARAH3, 2005–2023)

Isti alat i ista metoda kao na Sjednici (tamo A.6): satni bilans na −48 V DC sabirnici za
19 godina bez prekida. Ulazi i pretpostavke: `pvsim/sites/hamzici.json`; rezultati:
`review/pvsim/` (`kpis.json`, `energetski-bilans.md`, slike; pvsim commit e42bbaa).
Razlike u ulazima prema Sjednici: zaprljanje 1–3 % mjesečno (suši i prašnjaviji ljetni
period), snijeg zanemariv (≤1 % u januaru i februaru), više hlađenja ormara ljeti.
Potrošnja **1180 W / 1330 W je privremena**, preuzeta sa Sjednice do dostavljanja
izmjerene potrošnje ove bazne stanice. Baterija je ista kao na Sjednici:
**6 × 150 Ah = 48,6 kWh** (Odluka, Aneks 2). Pomoćna potrošnja je 45 W, sa trajnim
potrošačima na −48 V (D.9).

**Provjera prema PVGIS-u.** Isti model modula sa PVGIS-ovim gubitkom 14 % daje
8 996 kWh/god prema 9 047 kWh/god iz PVGIS PVcalc (−0,6 %) za ravan 45° / 225°; nijedan
mjesec ne odstupa više od 2,3 %; satna korelacija sa PVGIS-ovom proizvodnjom r = 1,0000.

**Gubici FN lanca (prosjek godine, 45°, azimut 225°).**

| Stavka | kWh/god | Gubitak |
|---|---|---|
| Ozračenje u ravni × kWp (STC) | 11 782 | |
| Refleksija (IAM) | 11 424 | −3,03 % |
| Temperatura i slabo svjetlo | 10 461 | −8,43 % |
| Zaprljanje | 10 248 | −2,04 % |
| Snijeg | 10 234 | −0,14 % |
| Neusklađenost + LID | 10 152 | −0,80 % |
| DC kablovi | 10 105 | −0,46 % |
| Optimizatori | 10 004 | −1,00 % |
| **iSSU S4875G2 → DC sabirnica** | **9 585** | −4,19 % |

Na sabirnicu stiže **9 585 kWh/god** (1 365 kWh/kWp, 81,4 % od STC). Temperaturni
gubitak (8,4 %) je veći nego na Sjednici — lokacija je niža i toplija, a polje na
jugozapadu hvata popodnevno Sunce.

**Mjesečni bilans (prosjek 2005–2023).**

| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | Agregat (DC), kWh | Agregat, h | Gorivo, l |
|---|---|---|---|---|---|
| jan | 520 | 911 | 427 | 46,8 | 155 |
| feb | 556 | 829 | 332 | 36,4 | 120 |
| mar | 798 | 910 | 232 | 25,5 | 84 |
| apr | 889 | 883 | 138 | 15,1 | 50 |
| maj | 971 | 918 | 100 | 11,0 | 36 |
| jun | 1 022 | 905 | 46 | 5,1 | 17 |
| jul | 1 125 | 952 | 15 | 1,6 | 5 |
| aug | 1 075 | 951 | 27 | 2,9 | 10 |
| sep | 895 | 896 | 90 | 9,9 | 33 |
| okt | 761 | 915 | 203 | 22,3 | 74 |
| nov | 498 | 882 | 414 | 45,4 | 150 |
| dec | 475 | 911 | 470 | 51,5 | 170 |
| **godina** | **9 585** | **10 864** | **2 494** | **273** | **903** |

**Ključni pokazatelji (nagib 45°, azimut 225°, bez stabla).**

| Pokazatelj | Vrijednost |
|---|---|
| Solarni udio u potrošnji | 77,0 % |
| **Rad agregata** | **273 h/god** prosjek · P90 319 h · najgora godina 346 h (2010) |
| Startova agregata | 97/god prosjek, najviše 121 |
| **Gorivo** | **903 l/god** prosjek · P90 1 054 l · najviše 1 144 l |
| Dopuna spremnika 500 l (pri 20 %) | 2,3 puta godišnje, najkraći razmak 57 dana |
| Najduže razdoblje bez rada agregata | 104 dana |
| Ekvivalentnih ciklusa baterije | 141/god |
| Rad ispod 30 % opterećenja | 0 h |
| Nepokrivena potrošnja | 0 kWh u 19 godina |

**Orijentacija: jug ili jugozapad.** Naručilac je 11.09.2026. odlučio da FN niz gleda na
**jugozapad**: niz je paralelan sa JZ granicom zakupa, JI strana otpada (stablo, put na
sjeveroistoku), a ormari ICC360 i MTS stoje u sjeni niza (C.6). Cijena te odluke je
izračunata istim modelom:

| Slučaj | FN, kWh/god | Decembar, kWh | DEA h/god — prosjek / P90 / najgora | Gorivo, l/god |
|---|---|---|---|---|
| 45°, jug (180°) | 10 448 | 601 | 226 / 271 / 307 | 746 |
| **45°, jugozapad (225°) — usvojeno** | **9 585** | **475** | **273 / 319 / 346** | **903** |
| 60°, jugozapad (225°) — poređenje | 8 972 | 492 | 293 / 347 / 364 | 969 |

Jugozapad daje 8,3 % manje energije godišnje i 21 % manje u decembru, a agregat radi
**≈+47 h i troši ≈+157 l godišnje** više nego pri jugu. Jugozapad ni u jednom mjesecu nije
bolji od juga (jun i jul su izjednačeni); razlika je u novembru–februaru, kada agregat
radi. **Albedo:** PVGIS računa sa refleksijom tla ρ = 0,20; sa ρ = 0,35 jugozapad daje
+1,7 % energije i −6 h/god (267 h), ali refleksija tla ne zavisi od azimuta, pa jug
dobija isto i razlika ostaje.

**Stablo.** Zasjenjenje prema tri procjene položaja i visine (povoljna / srednja /
nepovoljna), uz propuštanje pola direktnog zračenja kroz golu krošnju zimi:
decembar −0,1 / −0,3 / −2,4 %, rad agregata 275 / 277 / 283 h/god (+1…+10 h), gorivo
907 / 914 / 936 l/god (`review/pvsim/photo/zasjenjenje.json`).

**Osjetljivost na postavke SMU i pretpostavke (45°, azimut 225°).**

| Slučaj | DEA h/god prosjek | P90 | Najgora | Gorivo l/god | Startova/god |
|---|---|---|---|---|---|
| **Osnovni (Prilog I §4.6): stop SoC 60 %, punjenje 0,5 C** | **273** | **319** | **346** | **903** | **97** |
| SMU bez parametriranja: stop SoC 90 %, 0,25 C | 302 | 348 | 372 | 996 | 66 |
| Stop SoC 100 % | 314 | 359 | 391 | 1 034 | 61 |
| Stop SoC 40 % | 263 | 314 | 331 | 870 | 162 |
| Punjenje 0,15 C | 304 | 356 | 383 | 932 | 96 |
| Start pri DOD 70 % | 280 | 330 | 346 | 926 | 146 |
| Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei) | 318 | 373 | 378 | 1 051 | 185 |
| Potrošnja 1180 W stalno | 246 | 294 | 318 | 811 | 88 |
| Potrošnja 1330 W stalno | 338 | 389 | 406 | 1 115 | 118 |

Trajni potrošači na −48 V (D.9, 25 W) dodaju ≈15 h rada agregata i ≈50 l goriva godišnje (pvsim, azimut 225°).

**Zaključak.** Uz baterije od 48,6 kWh, trajne potrošače na −48 V i polje na jugozapadu,
prosječan rad agregata je **≈270 h/god** — **iznad 250 h/god iz RFI** i u prosječnoj
godini, ne samo u lošijim (u 9 od 10 godina do ≈320 h, najviše ≈350 h). To je cijena
odluke Naručioca o orijentaciji na jugozapad (11.09.2026.), navedena otvoreno. Spremnik od
500 l ne traje godinu dana (≈900 l/god). TD navodi simulirane vrijednosti — **≈270 h/god
i ≈900 l/god** (raspon 270~320 h/god), dopuna dva do tri puta godišnje — uz obavezno
parametriranje SMU iz Priloga I §4.6.

---

## B. Konstrukcija — nosači FN panela

### B.1 Proračunski pritisak vjetra

Ovjereni projekat (2017) računa prema JUS U.C7.110–113 sa osnovnom brzinom vjetra
**vm,50,10 = 25 m/s**: srednji pritisak qm,T,10 = 0,29 kN/m², a pritisak na udar
qg,T,z = 0,41 kN/m² na 1,5 m i 0,56 kN/m² na 4,5 m (Gz = 1,86).

Uz vb,0 = 25 m/s, BAS EN 1991-1-4 na visini gornje ivice polja (z = 2,93 m):

| Kategorija terena | ce(z) | qp |
|---|---|---|
| II (nisko rastinje) | 1,63 | 0,64 kN/m² |
| I (otvoren teren) | 2,08 | 0,81 kN/m² |
| 0 (izložen vrh) | 2,33 | 0,91 kN/m² |

(qb = ½ · 1,25 · 25² = 0,39 kN/m²; `design.json` nosi 0,69–0,96 kN/m², izvedeno za
ranije polje sa gornjom ivicom na 3,74 m — ta vrijednost je gornja granica.)

**Usvojeno: qp ≥ 1,20 kN/m²**, isto kao na Sjednici. Izvedena vrijednost je niža, ali
jedna konstrukcija nosača i jedan temelj za obje lokacije pojednostavljuju LOT 1, a
rezerva pokriva nepoznatu orografiju i buru u širem području Mostara. **Ponuđač
dokazuje nosivost ovjerenim proračunom za lokaciju.**

### B.2 Kataloški nosači

Kataloški nosač tipa A je pri 45° deklarisan na 0,52 kN/m² — ispod i najniže izvedene
vrijednosti (0,64 kN/m²). Nosač je i ovdje **CUSTOM IZRADA**.

### B.3 Geometrija polja

Kao Sjednica (odluka Naručioca 11.09.2026.): **4 odvojena nosača × 3 modula** (1 kolona ×
3 reda, položeno — duža stranica modula vodoravno), polje 2278 × 3442 mm = 7,84 m² po
nosaču, horizontalna projekcija pri 45° **2434 mm**, ukupno 12 modula = 7,02 kWp; 2 stringa
× 6 modula, svaki string na dva nosača. Odvojene male ploče umjesto jednog velikog
„jedra" su izbor Naručioca zbog vjetra na obje lokacije; ranije polje 2 × 2 portret
(dubina 3,24 m) ne staje u JZ pojas od 3,30 m (B.4).

### B.4 Položaj polja

| | |
|---|---|
| Donja / gornja ivica | **+0,50 m / +2,93 m** od terena |
| Kota ograde | **+1,80 m** od ploče (ovjereni `04_Ograda.dwg`); teren oko ploče je na **−0,20 m**, pa je ograda 2,00 m iznad terena |
| **Nadvišenje ograde** | **0,93 m** (2,93 − 2,00) |
| Raspoloživi pojas JZ od ploče | **3300 mm** × 12 500 mm (zakup 12,00 × 12,50 m, ploča 5,40 m u sredini) |
| Dubina polja / dužina trake | 2434 / 2600 mm → trake **350 mm** od granice zakupa i od ploče |
| Dužina niza (4 nosača, razmak 0,40 m) | 4 × 2278 + 3 × 400 = **10 312 mm** od raspoloživih 12,50 m, centrirano na ploču |

Niz je u JZ pojasu, izvan ograde; visoka ivica polja je 0,38 m od JZ ograde i 1,98 m od JZ
zida kontejnera. Kapija i vrata su na SZ, pa prolaz kroz polje nije potreban. JI strana
otpada zbog stabla, a put je na sjeveroistoku (Naručilac 11.09.2026.). Tačan položaj
utvrđuje Ponuđač geodetskim snimanjem.

### B.5 Dejstva vjetra po nosaču

Ista geometrija i isti usvojeni qp kao na Sjednici, pa i ista dejstva (metoda
07-proracuni Sjednice, B.5; `pvsim/stands.py`, raspored 4x3L):

```
F  = cf · qp · A = 1,5 · 1,20 · 7,84          = 14,1 kN
Fh = F · sin 45° = 10,0 kN        Fv = 10,0 kN
G  = (3 · 32 + 95 kg) · 9,81                   =  1,9 kN
ULS uzgon = 1,5 · 10,0 − 0,9 · 1,9             = 13,3 kN
M  = 1,5 · Fh · (0,50 + 1,721 · sin 45°)       = 25,7 kNm
spreg po traci = 25,7 / 1,60                   = 16,1 kN
```

Moment prevrtanja **25,7 kNm** po nosaču (raniji nosač 3 × 4 portret: 42,6 kNm, −40 %);
pri izvedenom qp 0,96 kN/m² bio bi 20,6 kNm. Masa rama ≈95 kg je procjena — potvrđuje je
proizvođač.

### B.6 Temelji

Kao Sjednica: **8 traka** (2 po nosaču) 400/500 × 2600 mm, **puna dubina 900 mm**,
**1,053 m³ po traci → 8,42 m³** C30/37. Potrebno je 0,74 m³ po traci: vlastita težina
trake 25,3 kN > potrebnih 17,9 kN (spreg 16,1 kN / 0,9), odnosno 0,9 × 25,3 = 22,7 kN > 16,1 kN. Količine:
podložni beton 0,52 m³, iskop 9,88 m³, zatrpavanje 0,94 m³, odvoz 8,94 m³ (LOT 1,
sekcija 2). Oba postojeća prstena uzemljivača presijecaju svih 8 traka (D.6).

### B.7 Pod kontejnera i unos opreme

| | |
|---|---|
| Nosivost poda (g+p) | **10,00 kN/m²** — ovjereni projekat, AG dio §4.4.2 (sekundarni HOP U 100 × 50 × 3 na 0,51 m, primarni nosači 15,00 kN/m′) |
| Agregat mokro | 372 kg / 0,96 m² = **3,80 kN/m²** |
| Pun spremnik 500 l | 590 kg / 0,63 m² = **9,2 kN/m²** |

Koncentrisana opterećenja na malom broju sekundarnih nosača: **čelični roštilj za
raznošenje opterećenja je OBAVEZAN**, kao na Sjednici.

**Unos:** skid širine 620 mm kroz vrata **1,00 × 2,15 m** na SZ zidu (kapija ograde
1,30 m) — nije potrebno skidati krovni panel ni otvarati zid. Najprije se unosi agregat,
zatim spremnik.

---

## C. Mašinski dio — agregat

Referentni agregat, spremnik i sekundarna zaštita su isti kao na Sjednici (tamo C.2,
C.6). Razlike su u rasporedu otvora i izduvu.

### C.1 Zrak za hlađenje

| | |
|---|---|
| Protok hladnjaka (tehnički list) | 1980 m³/h |
| Korigovano na gustoću lokacije (493 m, 40 °C) | **2206 m³/h** |
| Zrak za sagorijevanje | 90 m³/h |
| **Ukupno kroz usis** | **2296 m³/h** |
| Maks. vanjski otpor | **125 Pa** |

Izlaz toplog zraka ide kroz **postojeće otvore klima-uređaja Stulz** u sredini JI zida
(odluka Naručioca 11.09.2026.). Projekat klimatizacije iz 2017. predviđa dva otvora
30/70 cm; ugrađeni WDE80 je veći uređaj, pa se stvarni otvori mjere pri obilasku.
Uz 50 % slobodne površine žaluzina:

| | Bruto | Slobodno | Brzina | Δp |
|---|---|---|---|---|
| Oba otvora Stulz 300 × 700 zajedno | 0,42 m² | 0,210 m² | **3,0 m/s** | ≈12 Pa |
| Izlaz 600 × 600 (spojeni/prošireni otvori) | 0,36 m² | 0,180 m² | 3,5 m/s | ≈17 Pa |
| Usisna žaluzina 500 × 700, SI zid | 0,35 m² | 0,175 m² | **3,6 m/s** | ≈18 Pa |
| Hauba vani, rešetka na vrhu 700 × 600 | 0,42 m² | 0,210 m² | 3,0 m/s | ≈12 Pa |

Izlazna površina mora biti **≥0,36 m² bruto**: jedan otvor 300 × 700 sam (0,21 m²) dao
bi ≈6 m/s kroz žaluzinu. Plenum od hladnjaka do otvora ≈1,5 m² razvijene površine.
Vani je **hauba 700 × 600** zatvorenih bočnih strana i dna, sa rešetkom na vrhu
(+1,30 m): topli zrak ide naviše kroz otvorenu rešetku platforme P I, a ne u JI pojas uz
kontejner; FN niz i ormari su na JZ strani. Od nogu stuba hauba je 1,25 m.
Ukupni otpor sa haubom ≲60 Pa — **unutar budžeta od 125 Pa**.

### C.2 Toplota u prostoriju

Kao Sjednica: **5,8 kW** zračene toplote, odnosi je struja zraka hladnjaka.

### C.3 Dopunska ventilacija

Aksijalni **izvlačni** ventilator **1200 m³/h, Ø315 mm, 48 V DC (EC)**, napajan sa DC
razvoda (D.9, izvod D4), na **JI** zidu gore, sjeveroistočno od haube. Radi po termostatu dok
agregat ne radi (i za hlađenje nakon zaustavljanja); kontroler DEA ga isključuje dok
agregat radi, jer tada prostor ventilira struja zraka hladnjaka. Kao izlazni otvor ne
ulazi u uslov razmaka ≥3 m od izduva (C.4).

### C.4 Izduvni sistem

| | |
|---|---|
| Protok / temperatura | 192 m³/h pri 413 °C |
| Prečnik | **NO 50**, brzina 27,2 m/s (< 30 m/s) |
| Trasa | elastični umetak → uspon na ≈+2,30 m → preko JZ prolaza do **JI zida**, prigušivač u JZ prolazu; izlaz kroz JI zid jugozapadno od haube; završetak ≥0,40 m od zida (H-04: 3,25 m do sredine usisne žaluzine) |
| Protutlak | ≈1,6 kPa uz dozvoljenih 10,2 kPa |
| Izolacija i opšav | 4 m × 0,52 m²/m + prigušivač ≈ **2,5 m²** |

**Završetak ne može biti iznad krova**: platforma stuba na +3,0 m je iznad krova
kontejnera (+2,89 m). Izduv izlazi horizontalno kroz JI zid, usmjeren na JI — dalje od
FN niza i ormara (JZ), usisa (SI) i ulaznih vrata (SZ) — sa hvatačem iskri i kapom protiv
padavina, ≥3 m od usisa zraka i odušne cijevi spremnika. Najbliža noga stuba je ≈0,7 m
od cijevi: izduv se ne smije usmjeriti na noge stuba ni na kablove.

### C.5 Gorivo

Prime potrošnja P18-6 (2,6 / 3,4 / 4,4 l/h pri 50 / 75 / 100 %); pri ograničenju 9,5 kW
≈3,3 l/h.

| | |
|---|---|
| Očekivani godišnji rad (A.6) | **≈270 h/god**; u 9 od 10 godina do ≈320 h, najviše ≈350 h |
| Očekivana godišnja potrošnja (A.6) | **≈900 l/god**; najviše ≈1 140 l |
| Spremnik 500 l, dopuna pri 20 % | ≈400 l, ≈120 h rada — **dva do tri puta godišnje** (2,3) |
| **Prvo punjenje** | **250 l** |

### C.6 Raspored otvora i opreme

Ukrsno strujanje **SI → JI**, hauba naviše:

| Element | Zid / položaj | Napomena |
|---|---|---|
| Usis 500 × 700 | **SI** | donja ivica +0,30 m, uz alternator (SZ kraj agregata), jugoistočno od korita spremnika |
| Plenum + izlaz ≥0,36 m² | **JI**, u sredini | kroz postojeće otvore Stulz; višak otvora zatvoriti panelom 60 mm; vani hauba 700 × 600, rešetka na vrhu +1,30 m |
| Izduv NO 50 | **JI**, iz JZ prolaza | horizontalno na ≈+2,30 m, jugozapadno od haube, ispod platforme stuba; prigušivač u JZ prolazu; završetak ≥0,40 m od zida |
| Ventilator Ø315, izvlačni | **JI**, gore | sjeveroistočno od haube; izlazni otvor (C.3) |
| Agregat | u sredini, os **SZ–JI** | hladnjak na JI; prolazi JZ i SI po 0,78 m, na SZ kraju 0,97 m do GRO |
| Spremnik 500 l | **ugao SZ × SI** (prema sjeveru) | korito uz SI i SZ zid, iza okvira agregata; od vrata do korita 0,945 m slobodno |
| Oduška spremnika | kroz **SZ** zid sjeveroistočno od vrata; stojeća cijev uz SZ ogradu, sjeveroistočno od kapije i izvan krila vrata; završetak +2,80 m | H-04: 4,7 m od završetka izduva, 3,2 m od usisa, 3,7 m od ICC360; principijelno — konačno prema elaboratu zaštite od požara |
| GRO | **SZ**, jugozapadno od vrata | raspoloživi zid 0,595 m → širina GRO ≤0,50 m |
| DC razvod −48 V | **SZ**, sjeveroistočno od vrata, iznad spremnika | ≈300 × 200 × 150 mm (D.9) |
| Ulazna vrata | **SZ** | 1,00 × 2,15 m |
| Huawei ICC360-HA1-C1 i MTS | vani na ploči, **JZ** strana | između dvije JZ noge stuba, iza FN niza i u njegovoj sjeni (Naručilac 11.09.2026.); vrata prema kontejneru, ispred njih 0,85 m slobodno; napajanje (F1) i −48 V kroz JZ zid; MTS principijelno — tip i mjere dostavlja Naručilac |

Na crtežu H-04 razmak od završetka izduva do sredine usisne žaluzine je **3,25 m**
(≥3 m); izvlačni ventilator je izlazni otvor i ne ulazi u taj uslov. Hladnjak agregata je
uz JI zid, na mjestu otvora Stulz. Spremnik u sjevernom uglu ostavlja obje bočne strane
agregata od 0,78 m slobodnim. Kratka DC trasa ide od FN niza do PVDB uz ICC360 (H-02).
Mjere otvora Stulz se uzimaju pri obilasku, pa je raspored u kontejneru na crtežu H-04
principijelan — Ponuđač ga potvrđuje na licu mjesta.

### C.7 Demontaža klima-uređaja Stulz

Postojeći kompaktni zidni klima-uređaj **Stulz WDE80** (8 kW, rashladni medij R407C,
radni opseg −20 do +50 °C; natpisna pločica nije čitljiva na fotografijama) na JI zidu se
odspaja (230 V AC, 48 V DC, signalizacija) i demontira **bez otvaranja rashladnog kruga**,
pakuje i prevozi u skladište **BH Telecom d.d., Alipašino Polje, Sarajevo**, uz zapisnik o
primopredaji (tip, serijski broj, stanje). Otvori ostaju za izlaz zraka agregata.

---

## D. Elektro dio

### D.1 String FN panela

Isto kao Sjednica: 2 stringa × 6 × iPV585-M2A (nosači PV-1 + PV-2 i PV-3 + PV-4),
Voc 309,3 V, Imp 13,67 A, PVDB500-15-2B, 2 × iSSU S4875G2.

### D.2 DC kabl

Niz je u JZ pojasu, a PVDB uz ormar ICC360 na JZ strani ploče; trasa je kratka, ≈12 m u
jednom smjeru prema H-02 (tačnu dužinu potvrđuje Izvođač). Provjera za 20 m ostaje na
strani sigurnosti:

```
ΔU = 2 · 20 · 13,67 · 0,0175 / 6 = 1,59 V = 0,62 % od 257 V     ZADOVOLJAVA (<1 %)
```

### D.3 Potrošnja

1180 W nazivno / 1330 W maksimalno — **privremeno**, do izmjerene potrošnje; uz to 45 W
pomoćne potrošnje na −48 V, sa trajnim potrošačima (D.9).

### D.4 Struja kvara agregata

Isto kao Sjednica: In = 26,0 A, traženo 3 × In ≈ 78 A trajno ≥10 s — **PMG ili AREP/AUX
pobuda obavezna**; zaštita od indirektnog dodira preko RCD.

### D.5 Ograničenje ulazne snage ispravljača

Derativana prime snaga je 12,3 kW, neograničeni ispravljački sistem vuče ≈12,5 kW.
**Ograničenje 9,5 kW** ostaje; ovdje je to 77 % derativane prime snage (na Sjednici
82 %), dakle sa većom rezervom, a agregat ostaje iznad 30 % opterećenja.

### D.6 Uzemljenje i zaštita od munje

| | |
|---|---|
| Postojeći uzemljivač | Fe/Zn 25 × 4 mm: prsten u temeljima stopa stuba i prsten na dubini 0,8 m (ovjereni `3.6.9 Plan uzemljivača`) |
| Vodič do nosača | Cu 50 mm², bimetalni spojevi Cu/Fe-Zn |
| Ciljani otpor | ≤10 Ω |
| Ukrštanja sa temeljnim trakama | oba postojeća prstena (kvadrati 7,50 m i 10,00 m oko ploče, 1,05 m i 2,30 m od ivice ploče, dubina 0,8 m) presijecaju svih 8 temeljnih traka u JZ pojasu (dubina 0,9 m): lociranje, otkopavanje i premještanje ispod ili oko trake ili premoštavanje, bez trajnog prekida prstena; otpor se mjeri prije i poslije radova — posebna stavka LOT 1 |
| FN polje i stub | rešetkasti stub h = 32 m; metoda kotrljajuće sfere, LPL I (r = 20 m): na visini gornje ivice (2,93 m) zaštićeni radijus je ≈9,6 m, a polje je ≈1–5 m od najbliže noge stuba → **unutar zone zaštite, dodatne hvataljke nisu potrebne** |

### D.7 Prenaponska zaštita

Kao Sjednica: AC porijeklo **TIP 1 + 2** (Iimp ≥12,5 kA), DC tip 2 po stringu, signalni
vodovi prema **EN 61643-21** (stub sa LPS).

### D.8 Novi GRO

Kontejner je prazan — nema GRO ni postojećih krugova. Novi GRO (TN-S, jedini spoj N i PE
u GRO): dovod agregata 18 kVA preko sklopke 1-0-2, glavni RCD 63 A/300 mA tip S, SPD
tip 1 + 2, odvodi — pod naponom samo dok agregat radi: AC ulaz Huawei ICC360-HA1-C1
(ispravljači, ograničenje 9,5 kW; izvod F1 kroz JZ zid), rasvjeta i utičnice u kontejneru
(RCBO 16 A/30 mA), pomoćni potrošači agregata, blokada ventilacije pri gašenju.
**Nema kruga za klima-uređaj** (demontira se). GRO je na SZ zidu, jugozapadno od
vrata; raspoloživi zid je 0,595 m, pa je **širina GRO ≤0,50 m** (npr. 500 × 250 × 800 mm).

### D.9 Trajni potrošači na −48 V DC

Agregat je jedini izvor izmjeničnog napona i ≈97 % godine ne radi. Potrošači koji moraju
raditi stalno napajaju se zato sa −48 V DC iz ormara ICC360, preko novog DC razvoda na SZ
zidu, sjeveroistočno od vrata (odluka Naručioca 11.09.2026, obje lokacije):

| Potrošač | Napajanje | Prosječno |
|---|---|---|
| Svjetiljka za obilježavanje stuba, LED | 48 V DC, foto-senzor (≈12 h noću) | ≈8 W |
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
| Nagib 45° | godišnji rad agregata (A.5, A.6) | 273 h pri 45° prema 293 h pri 60° |
| Azimut 225° (jugozapad) | odluka Naručioca 11.09.2026. (A.6) | 273 h prema 226 h na jug — cijena ≈+47 h i ≈+157 l/god |
| Custom nosač | qp lokacije vs. kataloške deklaracije (B.1, B.2) | 0,64–0,91 > 0,52 kN/m² |
| Usvojeni qp 1,20 kN/m² | jedna konstrukcija za obje lokacije (B.1) | moment 25,7 kNm po nosaču |
| 4 nosača 1 × 3, položeno | pojas JZ 3,30 m; odvojene ploče umjesto jednog „jedra" (B.3, B.4) | 2434 mm od raspoloživih 3300 |
| Izlaz zraka kroz otvore Stulz | odluka Naručioca, protok 2206 m³/h (C.1) | ≥0,36 m² bruto + hauba naviše, ≲60 Pa |
| Horizontalni izduv | platforma stuba +3,0 m iznad krova (C.4) | NO 50, JI zid |
| Ormari ICC360 i MTS | u sjeni FN niza, na JZ strani (C.6) | 0,85 m slobodno ispred |
| Ograničenje ispravljača 9,5 kW | derating u prime režimu (D.5) | 77 % od 12,3 kW |
| Baterije 6 × 150 Ah (48,6 kWh) | Odluka, Aneks 2 (A.6) | ≈270 h/god prema ≈320 h sa 28,8 kWh |
| Parametriranje SMU | osjetljivost simulacije (A.6) | ≈270 h i ≈900 l/god |
| Trajni potrošači na −48 V DC | agregat je jedini AC izvor; odluka Naručioca (D.9) | ≤25 W, ≈+15 h/god rada DEA |

---

## F. Otvorene stavke

1. **Izmjerena DC potrošnja** bazne stanice — do tada vrijedi 1180 W / 1330 W sa Sjednice.
2. **Natpisna pločica i otvori klima-uređaja Stulz** — mjere otvora određuju plenum i
   izlaznu žaluzinu (C.1).
3. **Fotografije unutrašnjosti kontejnera** i potvrda orijentacije (Google Maps) i
   položaja FN niza pri obilasku.
4. **Ovjereni statički proračun nosača i temelja** za qp ≥ 1,20 kN/m² — uslov prije
   dodjele ugovora; masa rama nosača.
5. **Derating proizvođača** za 493 m i +40 °C (A.2, D.5).
6. **Baterije i struja punjenja** — 6 × 150 Ah (48,6 kWh) prema Odluci; najveću struju
   punjenja potvrđuje proizvođač baterija (A.6).
7. **Tip i mjere MTS-a** — ormar je na crtežima principijelno (C.6).
8. **Tri izgubljene fotografije** (20260908_121619, _121701, _123320) — ponovni izvoz.
9. **Procijenjene vrijednosti** po lokaciji i LOT-u dostavlja Naručilac.

---

*Geometrija lokacije: `cad/site_geometry.json`; vrijednosti sistema: `cad/design.json`;
energetski bilans: `review/pvsim/`. Crteži H-01 … H-05 formatiraju kote iz tih fajlova.*
