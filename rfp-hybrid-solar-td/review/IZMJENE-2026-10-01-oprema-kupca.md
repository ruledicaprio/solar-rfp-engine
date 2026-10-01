# Izmjene 01.10.2026 — oprema Kupca (Huawei specifikacija isporuke)

Huawei specifikacija isporuke (36 stavki, 2 lokacije) unakrsno provjerena sa
Prilogom I (`review/prilog1.md`) i Prilogom II LOT 1 / LOT 2 (oba lista).
Tekst pod "Novo" je spreman za lijepljenje. Oznake: **P1** = Prilog I,
**P2-L2** = Prilog II LOT 2 (ista izmjena na listu Sjednica i na listu Hamzići).

---

## 1. Nova stavka: DC/DC pretvarač 48 V → 12 V / 24 V (oprema Kupca)

Huawei stavka 02131937: "AC-DC Power, −30…65 °C, 40 V–60 V, 13,5 V DC / 7,94 A,
25,2 V AC / 7,94 A, 26,8 V DC / 7,94 A, supplying continuity". Ulaz 40–60 V je
−48 V DC sabirnica, pa je to DC/DC pretvarač sa dva izlaza, 13,5 V i 26,8 V. Uz
njega dolazi i kabl za punjenje startnog akumulatora agregata (1,5 mm², 10 m).

**Specifikacija (novo, za P1 Tačka 4.5 i Tačku 9):**

> DC/DC pretvarač Kupca, Huawei 02131937: ulaz 40–60 V DC (−48 V sabirnica ormara
> ICC360), izlazi 13,5 V DC i 26,8 V DC, 7,94 A, radna temperatura −30…+65 °C,
> 1 kom po lokaciji. Izlaz 13,5 V puni startni akumulator agregata (12 V sistem)
> kablom Kupca 1,5 mm², 10 m. Izlaz 26,8 V napaja 24 V potrošače: videokameru,
> unutrašnju rasvjetu kontejnera i, po potrebi, rasvjetu stuba. Ponuđač ugrađuje
> pretvarač, povezuje ga i štiti izvode DC prekidačima u DC razvodu.

**Gdje mijenjati:**

| Mjesto | Sada | Novo |
|---|---|---|
| P1 4.5, red "Punjač akumulatora za start agregata" | DC/DC 48 V → 12/24 V prema agregatu, sa strujnim ograničenjem i signalizacijom | DC/DC pretvarač Kupca (Tačka 9), izlaz 13,5 V, sa kablom Kupca 10 m; Ponuđač ga ugrađuje i povezuje, sa DC prekidačem i signalizacijom ispada prema SMU |
| P1 4.5, novi red | — | **24 V potrošači** — sa izlaza 26,8 V DC/DC pretvarača Kupca: videokamera, rasvjeta kontejnera i, po potrebi, rasvjeta stuba; svaki izvod sa vlastitim DC prekidačem |
| P2-L2 5.18 | DC/DC pretvarači … 48 V → nazivni napon vatrodojavne centrale … i punjač akumulatora za start agregata (48 V → 12/24 V prema agregatu) … | DC/DC pretvarač 48 V → nazivni napon vatrodojavne centrale (centrala zadržava vlastite akumulatore prema EN 54-4), sa strujnim ograničenjem, zaštitom i signalizacijom. Ugradnja i povezivanje DC/DC pretvarača Kupca (13,5 V / 26,8 V): izlaz 13,5 V na startni akumulator agregata, izlaz 26,8 V na izvode 24 V iz Tačke 5.16. |
| P2-L2 5.16, spisak izvoda | … punjač akumulatora za start agregata (preko DC/DC pretvarača iz Tačke 5.18) … | … DC/DC pretvarač Kupca (punjenje startnog akumulatora agregata 13,5 V; izvodi 24 V: videokamera, rasvjeta) … |

**Prije nego što uđe u tender, provjeriti:**
- Da li oba izlaza rade istovremeno i da li je 7,94 A po izlazu ili ukupno.
  ≈107 W na 13,5 V i ≈213 W na 26,8 V nisu zbirna snaga.
- "25,2 V AC" u Huawei listi izgleda kao greška u kucanju; potvrditi sa Huawei.
- Kamera troši trajno. P1 4.5 dozvoljava **≤25 W prosječno** za sve trajne
  potrošače, a energetski bilans (Tačka 8) računa sa 45 W pomoćne potrošnje.
  Ako kamera ne stane u 25 W, podiže se budžet i ponovo pokreće
  `python -m pvsim run` za obje lokacije (rad agregata i gorivo u Tački 8 se mijenjaju).
- Rasvjeta stuba na 24 V je alternativa sadašnjem zahtjevu (LED 48 V DC ili
  postojeća svjetiljka preko DC/AC ≤100 W) u P1 4.5 i P2-L2 5.17; ako se
  uvodi, dodati "ili LED 24 V sa izlaza 26,8 V DC/DC pretvarača Kupca".

---

## 2. Spisak opreme Kupca (P1 4.9 i P2-L2 5.19)

Sada (oba mjesta): "fotonaponski moduli iPV585-M2A (12 kom), PVDB 500-15-2B,
ispravljači iSSU S4875G2, baterijski moduli LFP i ormar hibridnog sistema
ICC360-HA1-C1 sa pripadajućim modulima"

**Novo:**

> fotonaponski moduli iPV585-M2A (12 kom po lokaciji), FN razdjelna kutija PVDB,
> ormar hibridnog sistema Huawei ICC360-HA1-C1 sa ispravljačkim modulima R4875
> (3 kom), solarnim modulima S4875G3 (2 kom), AC ulaznim modulom AIU03,
> prenaponskom zaštitom SPM01A, DC/DC pretvaračem 13,5 V / 26,8 V, senzorom nivoa
> goriva, priborom i kablovima, te baterijski moduli LFP; spisak sa količinama je
> u Prilogu I, Tačka 9

U P1 4.9 zadržati "(12 kom po lokaciji)": build ga traži (`REQUIRED` u
`tools/build_joint.py`).

---

## 3. iSSU S4875G2 → S4875G3

Huawei lista ima **ispravljačke module R4875** (AC → −48 V, 3 kom) i **solarne
module S4875G3 sa AFCI** (FN → −48 V, 2 kom). iSSU S4875G2 se ne isporučuje.

| Mjesto | Sada | Novo |
|---|---|---|
| P1 4.5, red "DC kablovi" | priključak na iSSU presjekom 4 mm² | priključak na solarni modul S4875G3 presjekom 4 mm² |
| P1 8, prvi pasus | krivulju efikasnosti iSSU S4875G2 | krivulju efikasnosti solarnog modula S4875G2 (proračun; isporučuje se S4875G3) |
| P2-L2 5.12, napomena | ulaznu stezaljku iSSU modula | ulaznu stezaljku solarnog modula S4875G3 |
| P2-L2 5.14 | string 1 → PVDB → iSSU 1; string 2 → PVDB → iSSU 2; GRO, sekcija SOLAR → Huawei iSSU | string 1 → PVDB → solarni modul S4875G3 br. 1; string 2 → PVDB → solarni modul S4875G3 br. 2 |

U P1 8 je ostavljen G2 jer pvsim računa sa krivuljom G2. Ako se ne želi
spominjati G2, potrebna je krivulja G3 u `pvsim/` i ponovno pokretanje simulacije.

---

## 4. Greška nađena usput (stara, nije od Huawei liste)

| Mjesto | Sada | Novo |
|---|---|---|
| P2-L2 5.14, prva alineja | 12 modula 585 Wp na **3 nosača (po 4 modula)** | 12 modula 585 Wp na **4 nosača (po 3 modula)** |

P1 3.1 i P2 LOT 1 1.1 kažu 4 nosača × 3 modula; 5.14 je zaostao iz ranije
varijante.

---

## 5. Moja greška u Tački 9 (P1) i u Prilogu III

Red "Sprega sa agregatom i nadzor" kaže "napojna jedinica AC/DC 13,5 V". To je
pogrešno: radi se o DC/DC pretvaraču sa dva izlaza iz Tačke 1.

**Novo (dva reda umjesto jednog):**

| Oprema | Po lokaciji | Ukupno (2 lokacije) |
|---|---|---|
| Sprega sa agregatom i nadzor: interfejsni modul agregata, bežični senzor nivoa goriva, bežični relej, omnidirekciona antena | po 1 kom | po 2 kom |
| DC/DC pretvarač 40–60 V DC → 13,5 V i 26,8 V DC, 7,94 A (punjenje startnog akumulatora agregata, 24 V potrošači) | 1 kom | 2 kom |

Prilog III čita tabelu iz `review/prilog1.md`. Ako se Tačka 9 ispravi samo u
.docx, Prilog III ostaje sa starim tekstom; ispraviti i `prilog1.md`.

---

## 6. Moguća preklapanja: odlučiti prije objave

Huawei isporučuje stvari koje Prilog II već traži od Ponuđača. Kod svake stavke
odlučiti da li Ponuđač i dalje isporučuje ili samo ugrađuje.

| Huawei stavka (po lokaciji) | Prilog II / Prilog I | Pitanje |
|---|---|---|
| Bežični magnetostriktivni senzor nivoa goriva, **0,6 m** | P2-L2 4.2: DVA nezavisna mjerača nivoa, nivo u nadzorni centar; spremnik visine **1310 mm** | Sonda od 0,6 m pokriva samo donji dio spremnika visokog 1,31 m. Potvrditi dužinu sa Huawei ili tražiti dužu. Može li ona biti jedan od dva mjerača, pa Ponuđač daje samo drugi i priključak na spremniku? |
| Interfejsni modul agregata 02313CTJ + bežični relej + antena | P2-L2 5.7 i P1 4.6: modul **GIM01C1** | Da li je 02313CTJ GIM01C1 ili drugi modul? Uskladiti naziv. Ako start/stop ide bežičnim relejem, da li signalni kabl iz 5.5 ostaje? |
| Prenaponska zaštita SPM01A | P2-L2 5.13: DC SPD tip 2 po stringu; 5.6: AC SPD tip 1+2 u GRO | Da li je SPM01A AC ili DC zaštita? Ako DC: pokriva li 5.13? Ako AC: tip 2 nije dovoljan uz LPS (5.6 to već kaže), pa GRO SPD ostaje. |
| AC ulazni kabl ZA-RVV 4 × 25 mm², 10 m + PE 16 mm², 17 m | P2-L2 5.5: NYY-J 5 × 6 mm², do 15 m (Sjednica) / ≈3–5 m (Hamzići) | Koji kabl ide GRO → AIU03? Na Sjednici je trasa do 15 m, a Huawei kabl ima 10 m. |
| H07Z-K 4 mm² crni + bijeli, 24 + 24 m | P2-L2 5.16: DC razvod napojen kablom 2 × 6 mm² | Da li Huawei kabl služi za DC izvode ICC360? Ako da, 5.16 može ostati na 2 × 6 mm² (duža trasa) ili preći na Huawei kabl. |
| FN produžni kablovi 4 mm², 3 m (8) i 7 m (2) | P2-L2 5.12: H1Z2Z2-K 6 mm², 100 m + završni priključak 4 mm² | Huawei kablovi pokrivaju završni priključak 4 mm²; 100 m od 6 mm² ostaje Ponuđaču. Može se dodati napomena. |
| Kabl za punjenje startnog akumulatora 1,5 mm², 10 m | P2-L2 5.18 | Pokriveno Tačkom 1. |

---

## 7. Baterije

LFP baterijski moduli nisu na Huawei listi; Kupac ih daje iz druge nabavke.
P1 4.9 i P2-L2 5.19 ih već navode. Huawei daje samo baterijske kablove 4AWG
(2 para) i CAN kabl sa završnim otpornikom. Ništa se ne mijenja.
