# Change log — BS Sjednica (Bileća) tender package

Revision 1 · 2026-08-07 · Rusmir Skopljak, dipl. ing. el.
Revision 2 · 2026-08-11 · airflow relayout and closure of the open items in
`07-calculations.md` §G — see the Revision 2 section at the end of this file.

Baseline of the pre-change state: `bht-sjednica-final-review/TD-OUTPUT-BASELINE-20260807/`
(byte-for-byte copy of TD-OUTPUT as of 2026-08-07, before any edit).
**Note:** since Rev 2 this folder is kept in sync with TD-OUTPUT as the delivery
copy; the pre-change state is the git history of Rev 1, not this folder.

Format: **file** · location · before → after · reason · source.

---

## 1. `4. Izjava o stanju zaliha BS Sjednica.docx` — package repair

### 1.1 Missing `[Content_Types].xml` — RED, fixed

| | |
|---|---|
| **Location** | OPC package root |
| **Before** | Part absent. The archive held 26 entries and no `[Content_Types].xml`. |
| **After** | Rebuilt with 4 `Default` entries (`rels`, `xml`, `jpeg`, `png`) and 18 `Override` entries, enumerated from the parts that actually exist in the package. |
| **Reason** | ECMA-376 Part 2 §10.1.2 makes the Content Types stream mandatory. Without it Word reports "unreadable content" and offers recovery; LibreOffice refuses outright (`Error: source file could not be loaded`). The document was undeliverable. |
| **Source** | `zipfile.ZipFile(...).namelist()`; `soffice --headless --convert-to txt` failing only on this one of the four docx files. |

### 1.2 Three dangling `customXml` relationships — RED, fixed

| | |
|---|---|
| **Location** | `word/_rels/document.xml.rels` (rId1, rId2, rId3) and `customXml/_rels/item{1,2,3}.xml.rels` |
| **Before** | `document.xml.rels` pointed at `../customXml/item1.xml`, `item2.xml`, `item3.xml`; all three targets were absent, as were `itemProps{1,2,3}.xml`. The three `customXml/_rels/*.rels` orphans pointed at the equally absent itemProps. |
| **After** | The three relationships and the three orphan `.rels` parts removed. Package is now internally consistent: every relationship resolves to a part that exists. |
| **Reason** | An OPC relationship whose target does not exist invalidates the package. Two repairs were possible — import the missing parts from a sibling document, or drop the references. Dropping was chosen because the `customXml` items are a Boldon James Classifier datastore plus an empty Word bibliography; importing `item2`/`item3` from another document would have stamped **that** document's classification label and label history onto this one. Verified first that `word/document.xml` references none of rId1–rId3 (it uses only rId10–rId16), so nothing in the body is orphaned by the removal. |
| **Note** | The document's own classification is untouched — it lives in `docProps/custom.xml` (`bjDocumentLabelXML`, `bjSaver`, `docIndexRef`), which is the store the Classifier add-in reads. Opening and re-saving in Word with the add-in installed will regenerate the `customXml` datastore automatically. |
| **Source** | `word/_rels/document.xml.rels` vs `namelist()`; `docProps/custom.xml`. |

All 23 remaining parts were copied byte-for-byte, so template formatting, styles, numbering, headers, footers and both images are unchanged.

**Verification** — all four checks pass on the repaired file:

| Check | Result |
|---|---|
| `soffice --headless --convert-to txt` on all four docx | 4/4 OK (was 3/4) |
| `zipfile.testzip()` | `None` (no CRC errors) |
| `docx.Document()` opens | OK — 14 paragraphs, 1 section |
| LibreOffice PDF render | 1 page, 2 images, 2288 chars of text |

### 1.3 Content corrections

The plan reference still cited *"18.4 — Agregatska postrojenja za RR čvorišta — nove
lokacije"*, inherited from the 46-generator template. **Left as is deliberately**: it
names a real line in the Investor's approved three-year investment plan, and changing
which budget line a procurement is booked against is a finance decision, not a document
correction. Flagged for the Investor to confirm the correct plan item for a hybrid
power-supply investment.

---

## 2. `3. TD JN Hibridni sistem napajanja BS Sjednica.docx`

Nine targeted OOXML run edits (`tools/fix_td.py` + `tools/ooxml_edit.py`). The document
is never regenerated, so template styles, numbering, headers, footers and layout are
byte-identical; only the affected runs change. Every edit must match its expected
occurrence count or the whole run is refused, so template drift fails loudly.

| # | Location | Before → After | Finding |
|---|---|---|---|
| 2.1 | Tabela 1, Izvedba_snaga | `kontejner_skid_13,5kVA` → `kontejner_skid_22kVA` | **F** |
| 2.2 | §3.1.3 | `kontejner dimenzija 3,00 x 2,10 x 2,40 m … ~850 kg` → `vanjskih dimenzija 3,005 × 2,30 m (zidni paneli 60 mm, unutrašnja površina 6,29 m², obim 10,13 m) … kontejner je trenutno PRAZAN` | **E** + Investor's site correction |
| 2.3 | §3.1.3 | `…150 m², zbog čega je predviđeno proširenje postojeće ograde` → `…150 m² (16,00 × 9,40 m)` | **H** — no BOQ item existed for a fence extension |
| 2.4 | §4.5.8 | `dokumentaciju za vučnu prikolicu,` deleted | **H** — skid inside a container, no trailer |
| 2.5 | §5.2.1 | `isporučene agregate, vučnu prikolicu i prateću opremu` → `isporučeni agregat, nosače fotonaponskih panela i prateću opremu` | **H** |
| 2.6 | §5.2.2 | same, postguarantee | **H** |
| 2.7 | §8.1.2 | `Izuzetno, plaćanje … nakon uspješne implementacije FN sistema na najmanje dvije lokacije.` deleted | **H** — single-location contract |
| 2.8 | §3.1.4 | `prema rješenju primijenjenom na lokaciji Brloški Potok iz referentne tenderske dokumentacije` → `prema zahtjevima iz Priloga II i Priloga III ove tenderske dokumentacije` | EL RED-11 — the referenced document is not in the package |
| 2.9 | §1.6 | `kao FG Wilson P22-6 (Skid),` → `… (Skid) ili ekvivalent,` | ZJN art. 54 — a brand was named without "or equivalent"; §2.1 had it, §1.6 did not |

## 3. `3.1 PRILOG II TD - predmjer Sjednica Bileca.xlsx`

openpyxl edits preserving styles, merges and formulas (`tools/fix_boq.py`).

| # | Location | Change | Finding |
|---|---|---|---|
| 3.1 | LOT 1 B13 | names the actual product: **Standard A-shaped Support 3.0 — LOW, Huawei BOM 21540481**, anchors **21540482** | HW F-01 — no part number was given, and the 21540421 family does not accept 585 W |
| 3.2 | LOT 1 B23 | geometry rebuilt from the **module field**, not the beam: field 3476 × 4576 mm, **projection 3236 mm** (was 2590), **top edge +3,74 m** (was +3,09) | **B** |
| 3.3 | LOT 1 B24 | overshoot restated: top edge **1,84 m above the fence** (was "cca 0,20 m" / "0,17 m") | **B** |
| 3.4 | LOT 1 B25 | states the real site load **qp ≥ 1,20 kN/m² (≈45 m/s)** and that the catalogue support rates only 0,52 kN/m² at 45° | CON R-01 |
| 3.5 | LOT 1 B20 | tilt tied to the wind proof; 25°–35° admissible if the calculation requires it | CON R-01 + Investor's snow correction |
| 3.6 | LOT 1 B32 (1.3) | static calculation becomes a **pre-award** submission, not a post-award deliverable | CON A-03 |
| 3.7 | LOT 1 B33 (1.4) | earthing conductor `H07V-K 25 mm²` → **Cu 50 mm² UV/burial-rated with bimetallic Cu/Fe-Zn joints**, R ≤ 10 Ω | EL RED-13 — H07V-K is indoor conduit wire and below EN 62305-3 Table 7 |
| 3.8 | LOT 1 B34 (1.5) | notes the iSSU input terminal requires **exactly 4 mm²** | HW F-06 |
| 3.9 | LOT 1 B35 (1.6) | PVDB corrected to **IP55** (Huawei PVDB500-15-2B is IP55, not IP65) and the SPD split out, because that box contains none | HW F-05 |
| 3.10 | LOT 1 new 1.6a | **new item**: DC type 2 SPD per string, 2 kpl | HW F-05 / EL RED-12 |
| 3.11 | LOT 1 items 2.6 / 2.7 / 2.8 | **deleted** — 2.7 priced a new 5,40 × 5,40 m slab that already exists; 2.6 and 2.8 were empty rows carrying formulas | **I** / CON R-07 (removes ~1 500–2 500 KM of phantom cost from a 15 000 KM LOT) |
| 3.12 | LOT 1 totals | `SUM` ranges rebuilt after the deletions | **J** |
| 3.13 | LOT 1 rows 52–57 | **new recap**: subtotal → popust → PDV 17 % → total | **J** — a LOT-1-only bidder previously never reached a total |
| 3.14 | LOT 1 rows 58+ | ~138 phantom rows trimmed | **J** |
| 3.15 | **LOT 2 F132** | `='LOT 1'!F52` → `='LOT 1'!F50` | **self-inflicted regression, caught by the recalculation test** |

### 3.15 in detail — a bug this process introduced and caught

Deleting rows 2.6–2.8 moved LOT 1's subtotal from row 52 to row 50. openpyxl does not
update **cross-sheet** references, so LOT 2's grand total silently kept pointing at the
old address and reported `SVE UKUPNO = 65.100` when LOT 1 + LOT 2 was `78.973` — LOT 1
was being dropped from the tender total entirely.

The first repair was also wrong: matching on `"UKUPNO LOT 1"` caught the **with-VAT**
line, which would have made the grand total charge VAT twice on LOT 1. The reference
must be the **ex-VAT** subtotal because LOT 2's recap applies VAT itself.

Verified by recalculating the workbook through LibreOffice with 100,00 KM injected into
every unit-price cell:

| | |
|---|---|
| LOT 1 ex-VAT | 13.873,00 |
| LOT 2 ex-VAT | 65.100,00 |
| SVE UKUPNO ex-VAT | **78.973,00** ✓ |
| PDV 17 % | **13.425,41** ✓ |
| SVE UKUPNO with VAT | **92.398,41** ✓ |
| LOT 1 standalone, 0 % discount | 13.873,00 → PDV 2.358,41 → **16.231,41** ✓ |

Both bidder paths — LOT 1 only, and LOT 1 + LOT 2 — now resolve correctly.

## 4. `1. NZ …docx` and `2. Prijedlog Odluke …docx`

Checked against the corrected TD and **left unchanged**. The LOT values (15.000 /
35.000 / 50.000 KM), the procedure type, the commission members and the contact block
are already consistent across both documents and the TD; the consistency checker
confirms a single value for each across the package. No template leftovers were found
in either file.

## 5. Drawings and PDFs

### 5.1 `Prilog_III_situacija_sjednica_bileca.pdf` — 79.6 MB → 8.5 MB, losslessly

The plan assumed the bulk was the CAD-derived vector pages and that they would have
to be rasterised. Measurement showed otherwise, so no rasterisation was needed:

| Cause | Detail |
|---|---|
| Un-subsetted duplicate fonts | Full **Arial Regular (1.05 MB) and Arial Bold (0.99 MB) embedded 17 times** between them — **16.64 MB** of the file. |
| Never compressed | The content streams were stored without deflate. |

Fix: `subset_fonts()` + `save(garbage=4, deflate=True, deflate_images=True, deflate_fonts=True, clean=True)`.
Embedded font bytes fall from 16.64 MB to 0.40 MB.

Proof it is lossless, across all 34 pages: extracted text identical, drawing-object
count identical, image count identical, page geometry identical, and pages 6, 12, 17,
29 and 31 render **pixel-for-pixel identical** at 100 dpi. All pages stay vector and
searchable. Applied after the corrected sheets are spliced in (§5.3).

### 5.2 CAD infrastructure

- `cad/style_profile.json` — layers, text styles, dimension styles, blocks and text
  heights harvested from the certified site project's own DWGs, so the new sheets match
  it: layers `Okvir`, `Tekst`, `Kote`, `Objekat`, `Konstrukcija`, `Panel`, `Kabal`,
  `Osovina`, `Orijentacija`; dimension styles `M 20 / M 50 / M 100 / M 200`
  (`dimscale` = plot denominator, `dimtxt` 2.5, `dimasz` 1.0); title block `Sastavnica`.
- `cad/site_geometry.json` — **existing-state ground truth measured from the certified
  project**, resolving finding **E**. Container is **3005 × 2300 mm external** with
  60 mm sandwich walls, centred on the 5400 × 5400 slab (offsets 1197 / 1550).
  Self-consistent: internal 2180 × 2885 = 6.29 m² and perimeter 10.13 m, both of which
  the source drawing states in its own annotations. Neither the TD's 3,00 × 2,10 nor
  Prilog III's 3,08 × 2,20 matches.
- `cad/bht_frame.py` — A3 frame and BH Telecom title block. The logo is traced from
  `bht-logo.svg` by parsing the path data and flattening the Béziers (cairosvg is
  unusable on this machine — its cairo DLL is absent). Designer field:
  **Rusmir Skopljak, dipl. ing. el.**
- `cad/build_drawings.py`, `cad/export.py`, `cad/render.py` — sheet construction and the
  DXF → DWG → verify → PDF pipeline.

Pipeline proven end to end on S-01: ezdxf → DXF → ODA → **DWG header AC1024** →
ODA → DXF → ezdxf, with 25 layers, all five `M *` dimension styles, hatches and 23
diacritic-bearing text strings surviving intact.

### 5.3 Sheets

| Sheet | State |
|---|---|
| S-01 Postojeće stanje 1:50 | built, converted to DWG and verified, A3 PDF plotted |
| S-02 / S-03 / M-01 / E-01 | blocked on the expert numbers |

---

## 6. Verification tooling

`tools/check_consistency.py` reads every deliverable in its native form — OOXML from
the docx zip, openpyxl, PyMuPDF, ezdxf — rather than via a text export, because
LibreOffice's txt export mangles Bosnian diacritics on a cp1252 console and silently
defeats naive greps. It asserts that facts which must have one value have exactly one,
and that template leftovers are gone. Exit code = failure count, so it can gate release.

**Baseline before correction: 7 failures.**

| | Check | Baseline |
|---|---|---|
| CONFLICT | generator rating | FAIL — `22 kVA`, `13,5 kVA` and `2×13 kVA` coexist (finding **F**) |
| CONFLICT | container external size | FAIL — three different sizes (finding **E**) |
| CONFLICT | PV module power | FAIL — 585 Wp and 540 Wp coexist (finding **L**) |
| CONFLICT | panel horizontal projection | one value (2,59 m) — but it is the **wrong** one (finding **B**) |
| CONFLICT | top panel edge level | one value (+3,09) — likewise wrong (finding **B**) |
| CONFLICT | fence overhang | FAIL — 0,17 m and 0,20 m coexist |
| BANNED | "vučna prikolica" | FAIL — 3 occurrences in the TD (finding **H**) |
| BANNED | "najmanje dvije lokacije" | FAIL — 1 occurrence in the TD (finding **H**) |
| BANNED | "proširenje postojeće ograde" | FAIL — 1 occurrence in the TD (finding **H**) |

LOT values are already consistent (15.000 / 35.000 / 50.000 KM across six documents),
as are the 500 l tank and the 1076 m altitude.

---

## 7. New finding — genset technical data is missing from the package

`EQUIPEMENT/GENSET/P22-6.pdf` is a **three-page web-page printout with no text layer**;
`P22-6.md` is its OCR. Between them they give ratings, engine model and the
standard/optional equipment lists, but **no physical dimensions, no dry or wet weight,
no cooling-air or combustion-air flow, no exhaust connection size and no back-pressure
limit**.

Those are precisely the figures needed to size the container ventilation and exhaust
(finding **D**), to check the container floor against the skid plus a full 500 l tank,
and to prove the set fits through a 1,00 m gate and a 900 × 2000 mm door. Per
`prompt.md` §3 this is a **YELLOW**: the tender names a generator model whose
installation cannot be verified from the documents supplied with it. The full FG Wilson
technical data sheet must be obtained, or the tender must place the sizing obligation
explicitly on the bidder with stated minimum performance requirements.


---

## 8. Revision 2 — 2026-08-07, Investor's decisions

### 8.1 New deliverable: `3. Prilog I TD - Specifikacija zahtjeva.docx`

A new tender annex (7 pages, A4, BH Telecom house style), generated by
`tools/make_prilog1.py`. It carries the requirements and the **proofs the bidder must
submit with the offer**, which is the change that matters most: under a lowest-price
award, anything verified after award is verified too late.

Structure follows the draft the Investor supplied. Section 0 of the document is a
**corrections table** listing every value that differs from that draft, with its source,
so the changes are visible rather than silent. The nine corrections are:

| Item | Draft said | Correct | Source |
|---|---|---|---|
| PV geometry | projection 2590 mm, top +3,09 m | **3236 mm, +3,74 m** | derived from the module field, not the beam |
| Fence height | 1,80 m | **1,90 m** | certified site project |
| Container | 3,08 × 2,20 × 2,80 / 3,00 × 2,10 | **3,005 × 2,30, empty** | certified project (6,29 m², 10,13 m) |
| Radiator air | ≈4250 m³/h | **1980 m³/h** | FG Wilson TDS |
| Intake louvre | ≥0,43 m² (1200 × 800) | **500 × 700 adequate** | 125 Pa restriction budget |
| Room fan | ≥2400 m³/h | **1200 m³/h supplementary** | radiator has its own fan |
| Exhaust | DN 65 minimum | **DN 50 passes; DN 65 recommended** | 2,6 kPa vs 10,2 kPa limit |
| Panel bottom edge | ≥1,20 m for snow | **+0,50 m** | snow not governing (wind-scoured site) |
| Snow | s_k = 3,00 kN/m² governing | **check required, not governing** | Investor's site knowledge |

The draft's ventilation figures were the electrical review's superseded estimates; the
bottom-edge change would also have pushed the top edge to +4,44 m, increased the wind
lever arm and broken the fit in the 1950 mm south strip.

### 8.2 BOQ round 2 — consolidated into `tools/fix_boq_all.py`

| Change | Reason |
|---|---|
| Item 1.1 rewritten: BOM 21540481, corrected geometry, **real site wind load with design actions** (≥27 kN uplift, ≥30 kN horizontal, ≥64 kNm overturning), full material/section/galvanising/EXC2 spec | calc F.1, F.2 — makes the item BOQ-quantifiable instead of naming an unbuildable catalogue kit |
| Item 1.2 → **chemical (epoxy) anchors**, M16/M20 with ETA, ≥30 kN each, 4 per support, pull-out test on ≥10 % | calc B.6 — gravity foundation was 40 % short; rock anchors address the actual failure mode |
| Item 2.3 → **C30/37, XC4 + XF3**, air-entrained 4–6 %, B500B, cover ≥50 mm, frost depth stated by bidder | calc A.4 — freeze-thaw at 1076 m; the BOQ had no exposure class at all |
| **New item 1.8** — optional 3 supports × 4 modules, priced separately, excluded from all sums | calc F.6 — halves sail per structure (15,91 → 7,95 m²) at the same 7,02 kWp |
| LOT 2 GRO → **RCD 4p 63 A/300 mA S-type + 2 × RCBO 16 A/30 mA type A** | calc D.4 — SHUNT excitation with 0 % short-circuit capacity means overcurrent can never meet IEC 60364-4-41 |

### 8.3 Three bugs found and fixed in the BOQ tooling

Documented because they are all silent-corruption modes in openpyxl, and any future
edit will meet them again:

1. **Formulas are not translated on row insert.** After two rounds of insertions, item
   1.3 sat on row 35 while still computing `D32*E32`. Fix: regenerate every product
   formula from scratch after all structural edits, so each references its own row.
2. **Substring matching on item numbers.** `"4.1"` matched `"4.10"`, producing SUM
   ranges over the wrong rows and a `#VALUE!` grand total. Fix: exact match only.
3. **Stale merge ranges migrate onto other rows.** Deleting a total row left its
   `A:E` merge behind; openpyxl does not move merge anchors, so `A37:E37` settled over
   item 1.7 and `A47:E47` over item 2.4 — hiding their unit, quantity and price columns
   and making the description read as `None`. This is why those two items appeared
   blank. Fix: a final pass that strips any merge covering a priced item row and
   restores content from the baseline by item number.

The first attempt at round 2 also destroyed items 1.3–1.7 by inserting 3 rows and then
writing 5 lines into them. It was caught by the recalculation test, the file was
restored from the baseline, and the two scripts were consolidated into one that runs
from a pristine copy every time.

**Verification after all of it** — LOT 1 13.873,00 + LOT 2 64.900,00 = 78.773,00;
PDV 13.391,41; total 92.164,41; LOT-1-only 16.231,41. Item 1.8 correctly outside the
totals. Diff against baseline: **0 unintended content losses**.

### 8.4 Consistency checker

Taught to recognise a **documented correction**: a superseded value quoted in Prilog I's
"Ranije navedeno" column is always followed within the same table row by the corrected
value, so a lookahead distinguishes it from a live specification. Without this the
corrections table would have failed the very check it exists to satisfy.

**Final gate: 0 failures across 10 documents.**

---

# Revision 2 · 2026-08-11

Two things drove this revision: the Investor asked for the genset air intake to be
taken through the **container walls** with the equipment positioned properly, and the
items left open in `07-calculations.md` §G had to be closed in the documents that are
actually issued.

## 9. Airflow relayout — closes EL RED-03

### 9.1 What was wrong

Rev 1 put the intake louvre (500 × 700), the radiator discharge louvre (600 × 600) **and**
the 505 °C exhaust on the **north** wall, 1,4 m apart, on the same face as the existing
outdoor cabinets ICC330-H1 and MTS9302. On drawing M-01 the fuel tank stood directly in
front of the intake (tank x 450–1650 against an intake at x 250–750), and the plan and the
section disagreed about which wall the openings were on. The room fan and the 110 % bund
were not drawn at all.

### 9.2 What it is now

Cross-flow, south-east in → west out (`cad/design.json` → `ventilation.layout`, drawing M-01):

| Element | Wall | Position |
|---|---|---|
| Intake louvre 500 × 700 | **JUG** | east end, bottom edge +0,30 m |
| Radiator duct + discharge louvre 600 × 600 | **ZAPAD** | on the radiator axis, shortest route |
| Exhaust DN 65 | **ZAPAD** | riser, terminating above the roof, spark arrestor |
| Tank vent | **SJEVER** | east end, ≥3 m from exhaust and intake |
| Room fan Ø315 | **ISTOK** | high, north of the entrance door |

Nothing discharges toward the cabinet wall, and intake and exhaust are on opposite ends
of the airflow path. M-01 gained cardinal wall labels, the door leaf and swing, airflow
arrows, the 110 % bund and the room fan; its plan and section now agree. The louvre and
duct sizes themselves are **unchanged** — the 125 Pa budget was already satisfied and is
not affected by moving the openings.

### 9.3 Fuel tank — real data

The Investor supplied the tank data on 2026-08-11: **1050 × 600 × 1310 mm, 170 kg empty**.
This supersedes the unverified 1200 × 700 × 800 estimate that Rev 1 carried. Full mass is
now ≈590 kg on 0,63 m² = **9,2 kN/m²**, which changes the floor conclusion below.

## 10. Section G items — closed

| § G | Item | Closure |
|---|---|---|
| 2 | Concrete class stated twice, inconsistently | BOQ 2.3 lead text rewritten to C30/37 XC4+XF3 on C12/15, B500B; 2.2b C10 → C12/15; `design.json` and S-03 note synced |
| 3 | Floor capacity claimed from a K3 type sheet | Governing value is **2,00 kN/m²** (project brief); K2 is what is installed. Both the genset (3,93 kN/m²) and the full tank (9,2 kN/m²) exceed it, so the load-spreading frame under **both** the skid and the bund is now **required**, not conditional (BOQ 4.4 rewritten — it previously argued that strengthening was "not expected") |
| 4 residual | Reference alternator is shunt-excited by default | BOQ now reads "kao Stamford BCI164C **u izvedbi sa PMG ili AREP/AUX pobudom**" |
| 5 | Fire elaborate, fuel shut-off valve, ventilation interlock specified but unpriced | New priced items **4.19, 4.20, 4.21** |
| 6 | AC SPD priced as type 2; no signal-line SPD anywhere | BOQ AC SPD → **type 1+2, Iimp ≥12,5 kA (10/350)**; new priced item **5.11** for EN 61643-21 signal-line protection |
| 7 | Three different power systems named | Unified on **ICC330-H1 + MTS9302** (Investor's decision) across the TD, the Odluka, the BOQ and Prilog I |
| 9 | Tower obstruction lighting absent from the whole package | New priced item **5.10**: survey and transfer of all 7 existing circuits, with **K7 obstruction lighting on its own monitored circuit** and the bidder measuring its real load for the energy balance |

Also aligned while in there: first fuel fill 200 l → **500 l** (the BOQ priced 500 l all
along), exhaust **DN 65 adopted** rather than "recommended", and the garbled LOT-2 scope
sentence (Y-16, a LOT-1 fragment merged into it) rewritten.

## 11. Prilog I — figures and precedence

Prilog I now carries the equipment figures (Slika 1–4) and a **Slika 5 lifted directly out
of drawing M-01**, so the specification and the drawing cannot drift apart — the figure is
rendered from the DXF by `tools/render_equipment.py`, not drawn separately. §4.3 gained a
binding "Raspored otvora" table and a callout forbidding any arrangement that puts intake,
discharge and exhaust on one wall or vents toward the cabinets.

A **REDOSLIJED MJERODAVNOSTI** clause was added to §0: TD → Prilog I → Prilog II →
Prilog III, and it states explicitly that the inherited K3 pages in Prilog III (including
their 10,00 kN/m² floor figure) do not govern.

## 12. Tooling

- `tools/render_equipment.py` (new) — vendor figures and the M-01 layout extract.
- `tools/fix_td2.py`, `tools/fix_boq_gaps.py` (new) — the text and BOQ edits above.
  `fix_td2.py` is idempotent; `fix_boq_gaps.py` carries the same integrity pass as
  `fix_boq_all.py` plus a **shrink guard** that refuses to save if a priced item's
  description loses more than half its text (it caught a whole-cell write that had
  replaced item 5.6's entire GRO specification with a single bullet).
- `cad/render.py` — `render_window()` for document figures; `cad/bht_frame.py` gained an
  `Izvod` layer so leader callouts can be separated from labels.
- `tools/check_consistency.py` — six new conflict rules and six new required values.
  Two bugs of its own were fixed: the docx reader discarded paragraph breaks, gluing
  adjacent table cells into fake words ("gorivomranije:") and silently defeating every
  `\b`-anchored pattern; and the correction-marker list used the ending `mjerodavn`,
  which does not match the masculine `mjerodavan`.

**Final gate: 0 failures across 13 documents.** BOQ recalculated through LibreOffice with
100 KM on every item: LOT 1 20.008 + LOT 2 65.300 = 85.308, with VAT 99.810,36.

## 13. Still open

- §G 1 — certified static calculation for 45° at qp ≥ 1,20 kN/m² (bidder, pre-award).
- §G 8 — revision of the certified electrical project (its PMO source no longer exists).
- The real power of the obstruction light is measured by the bidder under item 5.10;
  until then the December energy balance carries an allowance, not a measured figure.
- Prilog III still contains the **K3** container drawings (pages 8–15) although the site
  folder identifies the container as **K2**. They are inherited pages and are now
  explicitly non-governing, but replacing them with K2 drawings would be the cleaner fix.
- Container height 2400 mm is taken from the type sheet; `02-construction.md` Y-05 lists
  four conflicting heights. To be confirmed on the mandatory site visit.

---

# Revision 3 · 2026-08-11

Investor review of Rev 2. One item reverses a Rev-2 change, and the Investor is
right on the evidence.

## 14. Floor capacity is 10,00 kN/m² — Rev-2 change RETRACTED

`SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m\2 - ARHITEKTONSKO GRADJEVINSKI DIO\04 AG dio.docx`
is the certified project of **this K2 object**, and its §4.4.2.3 PODNA KONSTRUKCIJA
dimensions the floor for *"ukupno opterećenje (g+p) **10.00 kN/m2**"* — secondary beams
HOP 100×50×3 at 0,51 m carrying 5,10 kN/m′, primary beams 15,00 kN/m′. The 2,00 kN/m²
that appears in §POD of the same document is the **pedestrian live load on the walkable
strip**, not the structural capacity.

So Rev 2 §G-3 was wrong twice over: it took the walkable-strip figure for the design
load, and it argued the 10,00 kN/m² came from a K3 type sheet. It did not — it is in the
K2 project. **`02-construction.md` R-08's claim that no such document is in the pack is
hereby retracted**; the document was in the site project folder all along.

The load-spreading frame **stays required**, but for the correct reason: 10,00 kN/m² is a
uniformly distributed load, while the genset (3,93 kN/m²) and the full tank (9,2 kN/m²)
bear concentrated on a few secondary beams. The frame distributes onto the primary beams.
Item 4.4 and the section-4 note now say that; neither claims capacity is exceeded.

## 15. Sheets S-03 and M-01 were not true A3

Measured content extents against the frame: **M-01** ran to x=14705 against a 10500-unit
frame (the section 1–1 sat beside the sheet), **S-03** to y=12836 against 8910 (the note
block sat above it). `export.py` plots with `fit_page=True`, so the overflow was absorbed
by shrinking the whole sheet — it printed smaller than A3 and the scales in the title
blocks (1:25, 1:30) were false. These are Situacija pages 3–4 = Prilog III pages 5–6.

Fixed by moving the section and the note blocks inside the frame and compacting every
note block (M-01 22 lines → 10, S-03 13 → 7, E-01 12 → 6, S-02 8 → 5, S-01 5 → 3). All
five sheets now plot with the frame **at the page edge**.

`build_drawings.py` gained `check_extents()`, which refuses to write a sheet whose content
leaves the A3 area. It immediately caught two more: S-02's parcel boundary overran the
top edge by 150 units, and E-01's notes ran 495 units off the bottom. It also caught a
loop variable in `sheet_m01` (`for label, tx, ty ...`) that was shadowing the tank origin
`tx`, which put the section's dashed tank 3 m off its true position.

## 16. Two strings of six

12 modules on 3 supports are wired as **2 strings × 6**, not 3 × 4. The binding constraint
is the priced **PVDB500-15-2B, which has two outputs**; 6 × 51,55 V = 309 V Voc sits inside
the iSSU's 85–435 V window and Imp 13,67 A is under the 15 A per output. A string therefore
spans two supports, so E-01's "svaki string kompletan po nosaču" rule is gone.

BOQ: item 1.1 routing text rewritten, **1.5 DC cable 150 → 100 m**, **1.6a DC SPD 3 → 2 kpl**.
The last also settles a Rev-2 inconsistency — 3 SPD sets were priced against 2 drawn on
E-01. LOT 1 falls by 5.100 KM at the 100 KM/unit test rate.

## 17. Other Investor corrections

- **Fuel tank moved east** along the north wall, onto more secondary beams and clear of
  the radiator duct penetration; its own spreading frame is now drawn under the bund.
- **PV panels hatched** on S-02 with a cross-hatch mesh (ANSI37). `NET` was tried first
  and came out as a solid fill through the plot backend.
- **Prilog I section 0 deleted** — a 17-row corrigendum against internal working versions
  that no bidder ever saw. The REDOSLIJED MJERODAVNOSTI precedence clause is kept, moved
  to the top and stripped of its now-wrong floor-load sentence.
- **PV foundation unchanged** — confirmed by the Investor, together with the earthworks
  and strip-footing items in BOQ section 2.
- TD, NZ and Odluka still said **LOT 1 = 2 kom/kpl** supports, stale since the 3×4
  redesign; corrected to 3 in all three.

## 18. Checker

`check_consistency.py`: the floor-capacity rule flipped polarity — 10,00 kN/m² is now the
correct variant, and 2,00 kN/m² is only tolerated where it is named as the walkable-strip
load. The `INHERITED_ANNEX` / `ANNEX_EXEMPT` machinery is deleted: with 10,00 kN/m²
correct, the inherited Prilog III pages agree with the package instead of contradicting it.

**Gate: 0 failures across 13 documents.** BOQ recalculated through LibreOffice:
LOT 1 14.908 + LOT 2 65.300 = 80.208, with VAT 93.843,36.

## 19. Still open

Unchanged from Rev 2 (§G 1 static calculation, §G 8 certified electrical project revision,
measured obstruction-light load), plus:

- Prilog III pages 8–15 are still the **K3** container drawings while the site is K2. They
  are now explicitly non-governing under the precedence clause, but replacing them with the
  K2 set — which exists, in `2 - ARHITEKTONSKO GRADJEVINSKI DIO` — would be the clean fix.
- Container height 2400 mm is from the type sheet; `02-construction.md` Y-05 lists four
  conflicting heights. To be confirmed on the site visit.

## 20. Prilog III rebuilt from parts (Rev 3, second pass)

The annex was previously maintained by splicing corrected sheets into an inherited
30-page PDF. It is now **assembled from sources** by `tools/build_prilog3.py`, which
made the Investor's restructure possible:

| Was | Now |
|---|---|
| 8 K3 container drawings (G-01..G-08) | **6 K2 drawings** from the certified project of this object: osnova, presjek 1-1, presjek 2-2, fasade, detalji, osnova temelja |
| 9 K3 electrical drawings (E-01..E-09) | **1 K2 drawing**: 3.5.2 Jednopolna šema GRO. The PMO sheets go with the rest — the PMO no longer has a supply, and sheet E-01 of this package shows the new GRO |
| INFO-03 (RFI block diagram), INFO-04 (named PowerCube), closing REFERENTNA DOKUMENTACIJA page | removed |
| INFO-01 at page 25 | moved directly behind the cover |
| inherited cover | rebuilt in the style of the TD title page |

**30 pages → 16**, 10,0 MB → 7,3 MB, and the K3 container — which was never the
container on this site — no longer appears anywhere in the package.

Three things the vendor DWGs needed:

- **Fonts.** The cover is generated with PyMuPDF, whose base-14 fonts have no
  š/ć/č/ž/đ; Bosnian text came out as question marks. The system Arial is embedded.
- **Text normalisation.** The inherited pages set words with non-breaking spaces and
  soft hyphens, so `"OPŠTI PODACI O LOKACIJI"` and `"INFO-01"` could not be found by
  substring search — the same class of bug as the docx reader in §12.
- **Cropping.** The GRO single-line parks a duplicate load table outside its sheet
  frame; plotted fit-to-page that padding shrank the drawing into a corner. Cropping
  is **opt-in per sheet**, after a heuristic applied to all of them threw away real
  content on the plans. The bounding boxes come from `ezdxf.bbox` — a hand-rolled
  version ignored block INSERTs, and the stray table is a block, so it survived
  every crop until that was fixed.

Also in this pass: **the container is drawn on S-03**, on the existing slab north of
the fence, so the section shows what the panel actually oversails.

## 21. Note on the K2 architectural drawings

They are the 2018 as-built set and show the container with RBS cabinets and
"UREĐAJI ZA NAPAJANJE" in place. The package states the container is now **PRAZAN**
(Investor's site visit, `05-site-corrections.md` C-1). That is not a contradiction to
fix in the drawings — they are a historical annex — and the precedence clause in
Prilog I §0 settles which document governs.

## 22. Rev 6 — Investor's mark-up on the Situacija set (2026-08-11)

Scope was deliberately confined to `cad/`: the drawing sources, `design.json` and
`site_geometry.json`. No BOQ, no TD, no Prilog I.

**Three real geometry errors, not preferences.**

- **The footings were drawn too short.** `design.json`, the S-02 leader and the
  S-02 legend all said 450 × 3300; `sheets_new.py` drew **450 × 1500**. On S-03 the
  pair was drawn as two 450-wide pads under the panel ends, which is the wrong
  projection — the strips run NORTH–SOUTH at 1600 mm centres EAST–WEST, so section
  A–A sees **one** 3300 mm strip spanning the whole 3236 mm panel projection and the
  other directly behind the section plane. Both now come from `support.strip_l` /
  `strip_w` rather than from literals, which is what let them drift apart.
- **The fence was a single hairline.** It is now drawn to the certified elevation in
  `461 Graficki dio TEMELJ i OGRADA/04 Ograda.dwg`, which had never been opened:
  posts 50×50×3 at 1335 mm, ram 30×30×2, infill Ø4 50×50 woven mesh, gate posts
  70×70×3, Č.0361 hot-dip galvanised, post footing to −1,50 m. That drawing also
  settles the height: **+2,10**, not the 1,90 carried through the package with no
  source. `site_geometry.json` records the measurement and its provenance. Infill
  starts +0,20 per the Investor.
- **M-01 overflowed the frame.** The west-duct leader tail sat at y = 7400 against a
  frame top of 7175 — outside the frame but inside the paper, which is why
  `check_extents` (paper-only) passed it while the plot clipped it. Plan and section
  moved down 700 units. The bund's spreading frame also started 20 mm *inside* the
  60 mm south wall.

**Two defects found while measuring.**

- **S-03 printed the wrong bottom-panel level.** `b` held `bottom_edge` (1500); the
  tower bracing loop `for a, b in zip(lvl, lvl[1:])` then rebound it to 4600, so the
  sheet read *"donja ivica panela +4,60"* and drew that line 3,1 m too high. `lvl`
  was clobbered the same way. Third instance of this class in this package (after
  `tx` on M-01) — loop variables in these sheet functions now get local names.
- **Array-to-fence distance disagreed three ways**: Prilog I and the S-02 note both
  say 400 mm, S-02 drew 150, S-03 drew 800. Prilog I cannot be regenerated, so 400
  governs and both sheets now use it.

**Investor's layout decisions.** The bund now runs the **full internal length of the
south wall**: 2885 × 800 with a 330 mm upstand = **762 l**, comfortably over the
550 l (110 %) required and 260 mm shallower than 1600 × 1060. That is what makes the
container usable — the 2180 mm internal depth is otherwise fully committed
(bund + skid with its spreading frame + GRO), and the aisle was 50 mm. It is now
**370 mm**, and M-01 note 8 says so, so no bidder rearranges it casually. The tank
is drawn in the east half of the bund; its footprint is not binding, since the tank
is to be fabricated.

Also: the bund was dropped from S-02 (it is an M-01 detail, not a 1:50 site plan),
the S-02 note block moved under the legend bottom-left, three leaders that ran off
the sheet edge were shortened or re-aimed, and *"postojeći"* was dropped from the
S-01 outdoor-cabinet callout.

### Open — the prose was deliberately left behind

Carrying 2,10 m into the drawings makes the derived overhang **2,64 m**, not 2,84.
By the Investor's instruction the correction stopped at `cad/`, so four lines still
carry the old figures and need hand editing (Prilog I is hand-maintained):

| document | line |
|---|---|
| Prilog I (and `_K`) §1 | *"AB ploča 5,40 × 5,40 m, ograda h = 1,90 m, kapija 1,00 m"* → h = 2,10 m |
| Prilog I (and `_K`) | *"Nadvišenje ograde — 2,84 m iznad kote ograde h = 1,90 m"* → 2,64 m / h = 2,10 m |
| Prilog I (and `_K`) §4.2 | *"referentno 1600 × 1060 mm"* → 2885 × 800 mm, 762 l |
| TD §lokacija | *"metalna ograda visine 1,90 m"* → 2,10 m |

`check_consistency.py` still reports 0 failures **only because Prilog III is
image-only** — it cannot read the drawings' text. Do not read that as agreement.

---

## §23 — Rev 7: FG Wilson **P18-6** (18 kVA) becomes the reference set (2026-08-12)

### Why the rating moved twice in two days

The package was drafted around the **P22-6 (22 kVA)**. On 2026-08-11 the Investor
set **13,5 kVA**, and `design.json` plus all five sheets were swapped to the
**P13.5-6**. Working through the BOQ and Prilog I edits turned up the reason that
rating does not survive the site:

| | at 25 °C / 100 m | derated at 1076 m, 40 °C |
|---|---|---|
| P13.5-6 standby | 10,8 kW | **9,7 kW** |
| P13.5-6 prime | 9,9 kW | 8,9 kW |
| rectifier draw (3 × R4875G5) | — | **12,5 kW on the AC side** |

The set would have been overloaded before it charged anything. On 2026-08-12 the
Investor returned to the original first choice, the **P18-6**, read off
`EQUIPEMENT/GENSET/P18-6.pdf` (TDS 2019-08-14).

**The derate still bites, and the BOQ now says so numerically.** 18 kVA / 14,4 kW
standby derates to **12,6 kW** — 0,1 kW above the draw — and the site's real duty
is *prime*, not standby (there is no utility; the set cycles on battery SoC, see
03-electrical Y-02), where **11,6 kW is below it**. BOQ 3.1 already required the
rectifier input to be limited "so as not to overload the DEA" but gave no number.
It now caps the AC input at **9,5 kW** (≈82 % of derated prime), which leaves
≈8,2 kW for charging above the 1,33 kW TK load and keeps the engine clear of the
30 % minimum-load line that Y-03 warned about.

### What the data sheet changed — and what it did not

**The skid is 1550 × 620 × 1020 on all three sets**, so no drawing geometry moved
again. Nor did the ventilation: the P18-6 carries the same Perkins **404D-22G1**
(2,2 l) and the same cooling pack as the P22-6, so radiator air stays **1980 m³/h**
(2151 site-derated), combustion air **90 m³/h**, intake restriction 3 kPa. Louvres
500 × 700 and 600 × 600 stand at 3,6 / 3,5 m/s and ≈33 Pa against the 125 Pa budget,
so BOQ 4.7/4.8 were not churned.

| | P22-6 | P13.5-6 | **P18-6** |
|---|---|---|---|
| standby | 22 kVA / 17,6 kW | 13,5 / 10,8 | **18 / 14,4** |
| alternator | FGL10060 | FGL10020 | **FGL10040**, still SHUNT |
| mass wet | 385 kg | 308 | **372** → floor **3,80** kN/m² |
| exhaust | 234 m³/h @ 505 °C | 174 @ 490 | **192 @ 413** |
| DN 50 velocity | 33 m/s ✗ | 24,6 ✓ | **27,2 ✓** |
| fuel 75 % standby | — | — | **3,7 l/h** → 925 l/yr at 250 h |
| In at 400 V | 31,75 A | 19,5 | **26,0** (3 × In = 78 A) |

**Exhaust stays NO 50** — 27,2 m/s is inside the customary 30 m/s and back pressure
is ≈1,9 kPa against 10,2. The DN 65 requirement written for the P22-6 is withdrawn,
which restores agreement with BOQ 4.11, whose text always said `NO 50 mm`.

**The PMG/AREP requirement is now backed by the sheet itself**: P18-6 p.4 states
*Short Circuit Capacity 0 %* in the standard SHUNT build, the rated fault current
arriving only with the optional PMG/AUX winding. BOQ 3.1 quotes this.

### Also carried in the same pass

- **ICC330-H1 + MTS9302 → ICC360-HA1-C1 (PowerCube 1000)** everywhere the *power
  system* is named — the Huawei quotation and `01-huawei-solar.md` §185/§190 both
  said so, and Rev 2 had unified the other way on a majority count. Where the text
  describes what physically stands on the north face, **both** cabinets stay
  (`ICC360-HA1-C1 / MTS9302A`) — the TK cabinet is still there.
- **Fence 1,90 → 2,10 m and overhang 2,84 → 2,64 m** in the prose: the four lines
  left open at the end of §22 are now closed in Prilog I `_K` and the BOQ.
- **Bund → korito** in Prilog I §4.2, matching the double-skin decision.
- **Estimates 15.000 / 34.000 / 49.000 KM**, including the LOT 2 qualification
  threshold in TD `_K` and the figure in the Odluka.

### A silent-corruption bug found in `fix_boq_lots.py`

Its first run left the BOQ **arithmetically wrong without erroring**: `insert_rows`
translates no formulas, so after three rows went in above `UKUPNO 5`, section 6's
items still multiplied `D128..D131`, `UKUPNO 6` summed a blank band and the
recapitulation pointed at the wrong pair of cells. Patching the two sums known to
move was not enough. The script now runs `translate_formulas()` — every formula
re-derived from an untouched copy with its row references remapped — plus
`extend_section_sums()`, because rows inserted immediately *above* a total fall
outside its range and the new 5.12–5.14 would have been priced and not counted.
Verified by pricing every item at 100 KM and recalculating through LibreOffice.

A first attempt rebuilt the ranges from structure instead and was **rejected**: the
sheet's numbering is irregular (LOT 2's `UKUPNO 3` spans items numbered `1.1` *and*
`3.2`), so inferring ranges collapsed that total to a single cell.

### Open

1. **The old non-`_K` duplicates are the only remaining conflicts.**
   `check_consistency.py` reports 5 failures and every one of them is
   `3. TD JN ....docx` / `3. Prilog I ....docx`, which still carry 22 kVA,
   ICC330-H1, 1,90 m and the 500 l first fill. The `_K` files are the master. They
   should be deleted from `TD-OUTPUT/` or the check taught to skip them — Investor's
   call, but shipping both is the real hazard.
2. **Prilog III page 3 (site data) is stale and inherited.** It still reads
   *22 kVA / 17,6 kW*, *FG Wilson P22-6 (motor Perkins 404D-22G1)* and *ograda
   visine 1,90 m*. Spot-redaction was tried and reverted — the values share text
   objects with the labels beside them, so the rect takes the neighbour with it and
   the reprint collides with the next column. The page needs re-typesetting from
   data the way `cover_page()` is built.
3. **`strip_entity()` truncates the municipality**: the page renders *"Bile"*, not
   *"Bileća"* — the redaction rect is 14 pt too wide to the left. Pre-existing,
   visible on any render of page 3.
4. **BOQ `UKUPNO LOT 2` excludes `UKUPNO 3`** (`=F94+F127+F135`). Inherited, not
   introduced here: §3 is the DEA *specification*, priced under 4.1 — but **3.2,
   the 500-hour spare-parts set, is a genuine priced item that falls out of the
   total**. A bidder would price it and it would not be counted.
5. **BOQ item 4.19 has a number and no description** in the inherited file. The
   script's integrity check is comparative so it does not fail on it, but a
   numbered empty item invites a query at tender.
6. Prilog I §4.3 still carries the **pre-Rev-4 airflow layout** (intake SOUTH, tank
   vent NORTH), contradicting BOQ 4.8, M-01 and `design.json`, which all say intake
   NORTH / vent SOUTH. Out of scope for the genset swap; needs one more edit pass.
7. Type-2 DC SPD integration in the PVDB500-15-2B is still unproven, so BOQ 5.13
   stays priced.

### §23b — maintenance space around the genset (Investor, 2026-08-12)

The skid was drawn in the **south-west corner with its load-spreading frame flush
against both walls** — 60 mm to the south face and 0 to the west. Two sides of the
machine could not be reached. The container is empty, so nothing ever required it;
the position was inherited from when the 110 % bund still ran the length of the
south wall and left only a 370 mm aisle.

The skid is now **centred in the free floor**. Interior depth 2180 less the 740 mm
frame leaves 1440 mm, split evenly:

| side | clear | |
|---|---|---|
| SOUTH | **720 mm** | full-length service corridor, clear of the kada |
| NORTH | **720 mm** | 520 mm where the GRO stands proud of the wall |
| EAST | **1155 mm** | alternator and control-panel end |
| WEST | 60 mm | the radiator face — discharges into the duct, not serviced here |

`gx` is held at `ox+180` so the frame stops at `ox+1790`, just short of the kada at
`ox+1795`: the two never overlap in plan. The **exhaust riser moved from `oy+1100`
to `oy+1800`** — the radiator duct band travelled with the skid to
`oy+850..oy+1450`, and the old riser position is now inside it.

Carried into `design.json` as `access.service_clearance_mm`, onto M-01 as two
in-plan labels plus **normative note 9** (the old note 9 becomes 10), and into
**BOQ 4.1**, which until now said only *"uz obavezan servisni pristup"* with no
figures. A dimension chain for the three clearances was drawn on the east side and
**removed** — that is where the door swings and it crossed the arc.

### §23c — MTS9302A restored, LOT 2 scope shaded on E-01, notes cut back (Investor, 2026-08-12)

**1. MTS9302A was missing from S-01 (Prilog III p. 4/16).** Collapsing the
`ICC330-H1 + MTS9302` pair to the single quoted `ICC360-HA1-C1` in §23 dropped the
second box from the plan as well. Two cabinets stand on the north face and both
belong there: the hybrid power cabinet **ICC360-HA1-C1** and the existing TK
equipment cabinet **MTS9302A**, which is a separate procurement and never went
away. `cab` in `site_plan()` carries both again (650 × 650 and 600 × 600), with the
S-01 leader and legend row saying so.

**2. E-01 (p. 8/16) now shades the LOT 2 supply boundary** — **DEA**, **KOA/ATS**
and the **GRO with its type 1+2 AC SPD** are hatched, with a key reading *"isporuka
i montaža — LOT 2"*. The PV side and the Huawei equipment stay unshaded: they are
the Buyer's separate procurement. The key was first placed at x=13600 and landed on
top of the Investor's address in the title block; it sits at x=7500 now, clear of
the note lines to its left and well short of the title block at ≈11500.

**3. Every note block cut back**, on the Investor's instruction: no commentary, and
nothing that Prilog I or Prilog II already carries.

| sheet | was | now | dropped |
|---|---|---|---|
| M-01 | 10 notes, 20 lines | 6 notes, 8 lines | ventilation arithmetic, floor-load derivation, the ICC360 and GRO rationales |
| E-01 | 6 notes | 4 notes | protection-coordination and lightning-zone clauses (Prilog I) |
| S-02 | 5 lines | 3 lines | sail area, ULS uplift and overturning figures |
| S-03 | 5 notes, 10 lines | 4 notes, 5 lines | slope dimensions, the repeated wind figures, the full fence build-up |
| S-01 | 3 lines | 2 lines | container area and perimeter |

The S-03 fence leader read *"(v. napomenu 5)"* and there is no note 5 any more —
the cross-reference is gone with it. **Renumbering notes breaks leaders that cite
them; there is one such reference on these sheets and it was the only one.**

### §23d — genset centred on S-02, panel bottom edge back to +0,50 m (Investor, 2026-08-12)

**1. S-02 (p. 5/16) still drew the genset in the SW corner.** M-01 was recentred in
§23b but S-02 keeps its own `gx, gy` and was left behind, so the two sheets
disagreed about where the machine stands. S-02 now uses `cx+180, cy+840`, the same
offsets as M-01. **These two must be changed together — nothing links them.**

**2. Panel bottom edge +1,50 m → +0,50 m** (p. 6/16). Worth being clear that this
gives capacity back rather than spending it: the +1,50 m of `07-calculations` F.6
was never a requirement. It was the wind margin freed by the 3×4 relayout,
deliberately **spent as height**, sized to bring overturning back up to — not past —
the old 2×6 design's 64,3 kNm. Banking it instead:

| per support | at +1,50 m | **at +0,50 m** |
|---|---|---|
| centroid arm | 3,118 m | **2,118 m** |
| overturning | 62,8 kNm | **42,6 kNm** (−32 %) |
| couple over the 1600 mm strip spacing | 39,2 kN | **26,6 kN** |
| ULS uplift | 18,1 kN | **18,1 kN** — height-independent |
| top edge | +4,74 m | **+3,74 m** |
| above the 2,10 m fence | 2,64 m | **1,64 m** |

**Snow is the standing counter-argument** and it has already been ruled on:
`02-construction` argued against a +0,50 m bottom edge on snow grounds, and
`07-calculations` A.3 set that aside on the Investor's site knowledge — a
wind-scoured bura-belt peak with 45 m/s gusts does not accumulate snow. That earlier
ruling is what makes this reversal consistent rather than a new risk. The bidder's
certified calculation still has to carry a code snow check either way.

**One thing this does not improve:** at 45° the panel plane now crosses fence height
**1600 mm** from the bottom edge instead of 600 mm. The array's set-back from the
fence must be re-confirmed when the supports are sited — the 400 mm figure in the
BOQ was derived at the old height, and the sentence quoting it has been dropped
rather than silently re-used.

Carried into `design.json` (`array`, `wind.overturning_kNm_per_support` and its
note), S-02/S-03 — where the level labels are formatted from `design.json`, so they
followed automatically — plus Prilog I `_K` §1, BOQ LOT 1 1.1 and
`make_prilog1.py`.

`check_consistency.py`: **+3,74 is the live value again**, the same figure the 2×6
design had, reached a different way; +4,74 becomes superseded. The overhang chain is
now four deep — 1,84 → 2,84 → 2,64 → **1,64** — and only the last is live. These
lookaheads invert every time the value moves; check their direction when editing.

All six remaining `check_consistency` failures are confined to the superseded
non-`_K` duplicates and Prilog III's inherited site-data page (open items 1 and 2).

### §23e — `review/07-proracuni.md` (bosanski) dodan

Bosanska verzija objedinjenih proračuna, tražena 12.08.2026. **Pisana je na
AKTUELNE vrijednosti (Rev 7c), a nije prevod `07-calculations.md`** — engleski
dokument je datirani zapis pregleda, pisan za P22-6 (22 kVA) i donju ivicu na
+1,50 m, i namjerno ostaje nepromijenjen. Prevod zastarjelih brojeva bio bi gori od
nikakvog.

Struktura prati original (A ambijent, B konstrukcija, C mašinski, D elektro,
E sažetak, F otvorene stavke), sa svim brojevima povučenim iz `cad/design.json`:
P18-6 18 kVA, derating 12,6 / 11,6 kW, ograničenje ispravljača **9,5 kW**, izduv
**NO 50** pri 27,2 m/s, donja ivica **+0,50 m**, moment **42,6 kNm**, korito
1150 × 640, servisni prostor 720/720/1155, ICC360-HA1-C1 + MTS9302A.

Gdje se dokument razlikuje od engleskog, mjerodavan je bosanski i `design.json` —
to je i navedeno u zaglavlju fajla. `check_consistency.py` skenira samo `TD-OUTPUT/`,
pa `review/` ne ulazi u provjeru: brojevi u ovom fajlu se održavaju ručno.

---

## §24 — Prilog II sažet i ispravljen (Naručilac, 2026-08-12)

Predmjer je kroz šest revizija narastao na **157 redova u LOT-u 2**, od kojih je ~40
bilo „siročad" — nastavci opisa tačke 3.1 razliveni po redovima bez broja stavke.
Sažimanje je vođeno pravilom **„brisati objašnjenje, zadržati obavezu"**, uz
`COVERAGE` listu od 74 obavezna tokena koja mora preživjeti, inače `compact_boq.py`
staje.

| list | prije | poslije |
|---|---|---|
| LOT 1 | 190 redova, 1.1 u jednoj ćeliji od 3222 znaka | **38 redova** |
| LOT 2 | 157 redova, sekcija 3 preko 42 reda | **84 reda** |

### Greške koje je provjera otkrila

| # | Greška | Ispravka |
|---|---|---|
| E1 | Prva stavka sekcije 3 numerisana **`1.1`** umjesto `3.1`; stavka 4.1 i Prilog I referencirali „Tačku 3.1" — obje reference visile | prenumerisano u `3.1` |
| **E2** | **Stavka 6.4 ostala bez opisa (167 → 0 znakova)** — regresija iz mog pokretanja `fix_boq_lots.py`; integrity pass je vratio 4.19 a 6.4 propustio | opis vraćen; provjera pooštrena (v. niže) |
| E3 | Stavka 4.19 imala broj i nijedan opis (naslijeđeno) | postaje set rezervnih dijelova |
| **E4** | **Dvostruko obračunavanje**: `3.1` i `4.1` obje cjenovne, pa je `UKUPNO LOT 2` namjerno izostavljao `UKUPNO 3` — a time je **ispadala i 3.2 (rezervni dijelovi), koju ponuđač ukalkuliše a ne broji se** | sekcija 3 je sada nenaplativa specifikacija; rezervni dijelovi su 4.19, unutar `UKUPNO 4` |
| E5, E9 | 5.13 i 5.6 referencirale obrisanu „Tačku 1.6" (PVDB je u Huawei paketu); „Tačka 1.1" nejednoznačna otkad i LOT 2 ima 1.1 | → „PVDB koji obezbjeđuje Kupac"; → „LOT 1, Tačka 1.1" |
| E6 | Jedinica `pšl` | → `paušal` |
| E7 | Tri prazna reda u LOT 1 (ostatak Rev 7 repacka) | obrisani |
| E8 | 4.4 nosila **3,93 kN/m²** (vrijednost za P22-6) i riječ „tankvane" | → 3,80 kN/m², „korita"; `OBRAZLOŽENJE` obrisano |
| **E10** | 5.6 tvrdila *„agregat je SHUNT pobude"* — a tender PMG/AREP **zahtijeva**. Premisa je bila neistinita, iako je zaključak (RCD obavezan) tačan | prepisano na tačan razlog: i sa PMG/AREP je 3 × In ≈ 78 A, što ne isključuje prekidač C 32 A u 0,4 s |
| **E11** | LOT 1 1.1 nosila moment **62,8 kNm**, a 1.2 **39,3 kN/traci** — vrijednosti za donju ivicu +1,50 m | → **42,6 kNm** i **26,6 kN** |
| E12 | LOT 1 1.1 referencirala obrisanu „Tačku 1.6a" i odmak **400 mm** od ograde | referenca uklonjena; odmak → ponuđač ga utvrđuje pri poziciranju |

> **Ispravka zapisa uz §23d.** Tamo stoji da je rečenica sa 400 mm „dropped rather
> than silently re-used". To je bilo tačno samo za napomenu na crtežu S-02 — u
> predmjeru je ostala i uklonjena je tek sada, kroz E12.

### Dvije zamke koje su se ponovo javile

1. **Referenca na drugi list se ne remapira.** `REF` u `remap_formulas` ima
   lookbehind na `!`, pa `='LOT 1'!F50` ostaje netaknuta — a `UKUPNO LOT 1` je pri
   sažimanju otišlo sa reda 50 na 31. Rekapitulacija je pokazivala na prazan red i
   **ukupna cijena ponude bi tiho pala na vrijednost samo LOT-a 2**. Sada se
   prevodi ručno, kroz `rowmap` drugog lista.
2. **`remap_formulas` vraća formule iz netaknute kopije**, pa je stavci 3.1 vratila
   cjenovnu formulu koju smo joj namjerno skinuli. Brisanje se ponavlja *poslije*
   remapa.

### Provjera koja je propustila E2 je pooštrena

`fix_boq_lots.py::assert_no_loss()` zamjenjuje raniji integrity pass. Raniji je
*popravljao* prazne opise i pri tome propustio da 6.4 izgubi svih 167 znakova —
nađeno je tek diffom protiv gita. Novi **pada umjesto da krpi**, i provjerava tri
stvari: da stavka nije nestala, da opis nije pao ispod 50 % originalne dužine (osim
namjerno sažetih), i da svaka cjenovna formula adresira svoj red.

### Provjereno

Sve stavke po 100 KM, prerachunato kroz LibreOffice: `UKUPNO 4` = 27 000,
`UKUPNO 5` = 23 300, `UKUPNO 6` = 400, `UKUPNO LOT 2` = **50 700**, LOT 1 = **4 608**,
`SVE UKUPNO` = **55 308** — poklapa se sa ručnim zbirom u cent. Nijedna „Tačka X.Y"
ne pokazuje na nepostojeću stavku. `check_consistency.py` ostaje na 6 grešaka, sve
iz starih non-`_K` duplikata.

### §24b — izlazna žaluzina na S-02

`sheet_s02` je crtao izlaznu žaluzinu na **`cy + 130`** — osa hladnjaka dok je
agregat stajao u jugozapadnom uglu. Nakon centriranja (§23b) osa je na `cy + 1150`,
pa je žaluzina bila **720 mm ispod hladnjaka koji opslužuje**. Sada se `dy_c` izvodi
iz `gy`, kao na M-01.

**Treći put da se S-02 i M-01 raziđu** jer S-02 drži vlastite kopije koordinata
(prvo agregat, pa žaluzina). Sve što je vezano za položaj agregata mora se računati
iz `gx`/`gy`, nikad ispisivati.

### §25 — preostale greške zatvorene, provjera na 0 (Naručilac, 2026-08-12)

**1. Stari non-`_K` duplikati obrisani.** `3. TD JN … .docx` i
`3. Prilog I … .docx` (bez `_K`) nosili su 22 kVA, ICC330-H1, ogradu 1,90 m,
+4,74 m i prvo punjenje 500 l. `_K` je master od 2026-08-11, pa su dva fajla istog
sadržaja u paketu značila da se može poslati pogrešan. Uklonjeni iz `TD-OUTPUT/`;
ostaju u git historiji.

**2. Stranica opštih podataka Priloga III (str. 3) se više ne naslijeđuje.** Do sada
je preuzimana verbatim iz prethodnog aneksa i zato je i dalje govorila *22 kVA /
17,6 kW*, *FG Wilson P22-6* i *ograda visine 1,90 m*. Nova `site_data_page()` je
slaže iz `cad/design.json`, u stilu `cover_page()`.

To rješava i dvije stare mane te stranice: `strip_entity()` je rezao **„Bileća" na
„Bile"**, a red „Kontejner" je izlazio izvan okvira tabele. Obje su nestale zajedno
sa naslijeđenom stranicom; `strip_entity()` više se ne poziva.

> **Ista klasa greške po treći put.** `insert_textbox` **ne crta ništa** kad tekst ne
> stane — samo vrati negativan broj. Red „Kontejner" je tako izašao prazan iz prvog
> builda. Visina reda se sada mjeri unaprijed na pomoćnoj stranici sa istim fontom, a
> red koji i dalje ne stane **ruši build**. Isti obrazac kao `assert_no_loss` u
> predmjeru i `check_extents` na crtežima: tiho odbacivanje sadržaja mora postati
> greška.

**Rezultat: `check_consistency.py` → 0 grešaka.** Jedina živa vrijednost u paketu je
sada 18 kVA, ICC360-HA1-C1, 250 l, ograda 2,10 m, nadvišenje 1,64 m i gornja ivica
panela +3,74 m.

Napomena za buduće provjere: PyMuPDF upisuje **neprelomive razmake** (`\xa0`), pa
naivno `"18 kVA" in text` ne pogađa na stranicama koje sam generiše. Regexi u
`check_consistency.py` koriste `\s*`, što u Pythonu hvata i `\xa0`, pa provjera radi
— ali ručni grep ne.

---

## §26 — Rev 8 (12.08.2026.): Prilog I iz markdowna, količine, sažeti proračuni

Naručilac je vratio ranije `_K` dokumente i preimenovao paket (nema više `_K`
sufiksa; `TD-OUTPUT/DWG/` je sada `TD-OUTPUT/grafika/`). Poređenje je pokazalo da je
**vraćeni Prilog I zapravo posljednji `_K`** uz Naručiočeve vlastite izmjene — dakle
nijedna ranija ispravka nije izgubljena. Ono što je nađeno su **zaostale greške koje
nikad nisu ni bile uhvaćene**.

### Prilog I se sada gradi iz markdowna

Odluka Naručioca: Prilog I dobija izgled md dokumenata (kao render
`proracuni_sjednica.pdf`), ali ostaje `.docx`. Novi izvor je `review/prilog1.md`,
build je `tools/build_prilog1.py` (Pandoc + `tools/ref-prilog1.docx`).

Time pada zabrana regenerisanja Priloga I koja je važila od početka, pa je
**`tools/make_prilog1.py` obrisan** — držan je „u koraku, nikad pokrenut" upravo zbog
te zabrane, a dva generatora istog fajla su zamka.

> **Zašto je zabrana uopšte postojala i zašto sada pada.** Prilog I je bio ručno
> uređivan, pa bi ga regenerisanje pregazilo. Sada je izvor tekstualni i pod
> verzijom, a build **provjerava rezultat**: 15 zabranjenih vrijednosti ne smije se
> pojaviti, 26 obaveznih mora. Ručno uređivanje `.docx`-a bilo je jedina zaštita dok
> provjere nije bilo; sada je zamijenjeno nečim što ne zaboravlja.

### Trinaest zaostalih grešaka u Prilogu I

| # | Bilo | Sada |
|---|---|---|
| P1 | moment prevrtanja 62,8 kNm | **42,6 kNm** |
| P2 | spreg po traci 39,3 kN | **26,6 kN** |
| P3 | „400 mm južno od kote ograde" | odmak se utvrđuje pri poziciranju |
| P4 | toplota u prostor 7,1 kW | **5,8 kW** |
| P5 | usisna žaluzina na **JUŽNOM** zidu | **SJEVERNI**, istočni kraj |
| P6 | odušna cijev na **SJEVERNOM** zidu | **JUŽNI**, istočni kraj |
| P7 | „usis JUG → izlaz ZAPAD" (2×) | **SJEVER → ZAPAD** |
| P8 | kanal ≈6 m² | **≈1,0 m²** |
| P9 | struja kvara PMG/AREP ≥95 A | **≥78 A** |
| P10 | 407 A / 16 A pri kvaru | **≈333 A / ≈13 A** |
| P11 | „NO 50 (stavka 4.11)" | stavka **4.10** |
| P12 | roštilj „vidi Tačku 4.8" | Tačka **4.2** (Prilog I nije imao 4.8) |
| P13 | „Tečnički nacrti" | „Tehnički" |

**P5–P7 su bile najozbiljnije**: Prilog I je slao ponuđača da probije pogrešan zid
kontejnera. P9 je stajala u istoj tabeli koja tri reda više navodi In = 26,0 A —
95 A je 3 × In za 22 kVA. Slika rasporeda bila je screenshot starog rasporeda i
zamijenjena je renderom aktuelnog M-01.

### Količine u Prilogu II

Naručilac je osporio 6 m² limenog kanala. Bio je u pravu, i trag vodi do
specifikacije za salu **„POTOCI" Mostar**, odakle je predmjer naslijeđen: tamo stavka
glasi 10 m², jer je agregat stajao u hali daleko od zida.

- **4.5 kanal: 6 m² → ≈1,0 m².** Hladnjak je 60 mm od zapadnog zida, kanal je
  prelazni komad ≈0,2 m.
- **4.12 izolacija izduva: 6 m² → ≈3,0 m².** 6 m² traži 12 m cijevi. Trasa se sada
  iskazuje u metrima (1 m + do 4 m), kako je i mostarski predložak radio — površina
  se time više ne može otkinuti od dužine.
- **4.10 je sama sebi protivrječila**: isti opis tražio je izduv „oboreno prema
  zemlji u obliku lule" i „završetak IZNAD KROVA usmjeren naviše". Ostaje iznad
  krova, kako traže Prilog I §4.4 i `design.json`.

**Temeljne trake — najveća izmjena.** S-02 crta traku **pune dubine 900 mm** i tako
kaže njegova napomena 2, a predmjer je nosio **0,41 m³ po traci** (traka 450 × 275 na
dnu rova). Iskop je pritom već bio dimenzionisan za rov od 900 mm, pa su se iskop i
beton razilazili.

> **Presudila je provjera na podizanje.** Spreg iz vjetra je 26,6 kN po traci; uz
> `γG,stb = 0,9` treba 29,6 kN stabilizujuće težine. Puna traka daje
> `1,485 × 24 × 0,9 = 32,1 kN` i zatvara provjeru vlastitom težinom. Traka od
> 0,41 m³ daje 8,9 kN i **fali joj 17,7 kN**, koje bi mogla posuditi samo od trenja o
> zasip — na kršu to nije dokaz. Ankeri prenose uzgon u traku, ne u tlo, pa tu
> razliku ne pokrivaju. Mjerodavan je crtež.

Sekcija 2 je zato preračunata koherentno: iskop **10,35 m³**, podložni beton
**0,54 m³**, beton C30/37 **8,91 m³**, zatrpavanje **0,89 m³**, odvoz **9,45 m³**.

**Ovo diže vrijednost LOT-a 1** — 8,91 m³ betona umjesto 2,44 m³ — pa procijenjenu
vrijednost od 15.000 KM treba preispitati. Upisano kao otvorena stavka F.7.

### Tri stvari koje niko nije isporučivao

Otkrivene su usput, i nijedna nije nastala u ovoj reviziji:

1. **Ograničenje ulazne snage ispravljača od 9,5 kW nije postojalo u predmjeru.** To
   je mjerodavno elektro ograničenje (D.5): derativana prime snaga je 11,6 kW, a
   neograničen ispravljački sistem vuče 12,5 kW. Prilog I je tražio „ograničenje
   ulazne snage" **bez brojke**, što ne obavezuje nikoga. Sada stoji u Tačkama 3.1 i
   5.7 predmjera i u Prilogu I §4.6, a dokaz je uvršten u red 12 tabele dokaza.
2. **Prihvatno korito ispod spremnika niko nije isporučivao.** Tačke 4.2 i 4.3 obje
   su upućivale na „korito iz Tačke 4.3", ali 4.3 isporučuje samo roštilj. Korito
   1150 × 640, rub 200 mm, sada je stavka pod 4.2.
3. **Stavka 6.4 imala je formulu, ali ni jedinicu ni količinu** — dokumentacija
   izvedenog stanja za cijeli LOT 2 tiho je ispadala iz `UKUPNO 6`. Sada `kpl 1`.

Prve dvije je uhvatila `COVERAGE` lista iz `compact_boq.py`, koja se do sada
pokretala samo unutar tog skripta; treću je uhvatio prerachun sa 100 KM po stavci.
**Obje provjere sada su dio `fix_boq_quantities.py`.**

### Antivibracija

Bila je pola rečenice u 4.1, bez tipa, broja i progiba. Po odluci Naručioca ostaje
unutar 4.1, dopunjena: gumeno-metalni oslonci, min. 4 kom, vlastita frekvencija
≤8 Hz, statički progib ≥5 mm, između skida i roštilja.

Uz to jedan stvarni propust: **gorivo je do motora išlo krutom Cu cijevi NO 8.** Motor
stoji na antivibracionim osloncima i pomiče se, pa se kruta cijev na priključku zamara
i puca. Izduv je već imao elastični umetak, hladnjak ceradni spoj; vod goriva je bio
jedini koji je ostao krut. Dodan fleksibilni umetak na oba voda.

### Proračuni

`review/07-proracuni.md` sažet je po nalogu Naručioca: izbačen je svaki trag
prethodnih iteracija odabira (P22-6, 13,5 kVA, donja ivica +1,50 m, povlačenje DN 65,
prelazak 2×6 → 3×4, „naslijeđeni predmjer", odnos prema `07-calculations.md`).
Zadržani su tehnički dokazi, ne njihova historija.

**Snijeg je dobio pozitivnu formulaciju umjesto „izračunat, pa odbačen".** Uz
koeficijent oblika `μ₁ = 0,4` pri 45° (EN 1991-1-3 §5.3.6) i najveću opaženu visinu
snijega na lokaciji od ≈0,5 m pri gustoći slegnutog snijega 300 kg/m³:

```
s = 0,4 · 1,0 · 1,0 · 1,5 kN/m²  ≈  0,6 kN/m²      prema vjetru 1,20 kN/m²
```

Vjetar je mjerodavan sa dvostrukom razlikom, a snijeg djeluje naniže i **umanjuje**
uzgon — dakle nije nepovoljan ni u jednoj kombinaciji. Kodna provjera prema BAS EN
1991-1-3 svejedno ostaje obavezna u ovjerenom proračunu ponuđača. **Led je odvojen od
snijega**: radijalna naledica 20 mm / 300 kg/m³ ostaje zahtjev, kao akrecija na
profile i spojeve, jer se led na ovoj koti zadržava tamo gdje se snijeg ne zadržava.

### Provjere

- `check_consistency.py` → **0 grešaka**, uz **6 novih pravila** (42,6 kNm · 26,6 kN ·
  5,8 kW · 78 A · 1,0 m² · 8,91 m³) i **3 nove obavezne vrijednosti** (9,5 kW ·
  1150 × 640 · 3,0 m²). Putanje su prilagođene preimenovanom paketu.
- Prerachun predmjera kroz LibreOffice sa 100 KM po stavci: `UKUPNO 4/5/6`,
  `UKUPNO LOT 1/2` i `SVE UKUPNO` slažu se sa ručnim zbirom, bez odstupanja.
- `COVERAGE`: svih 76 tehničkih zahtjeva prisutno.
- Sve unakrsne reference „Tačka X.Y" u Prilogu I i Prilogu II pogađaju postojeću
  stavku.
- Prilog I: 11 stranica, 5 slika, 15 zabranjenih vrijednosti odsutno.

Sigurnosne kopije prije Rev 8 su u `review/backup-rev7/`, **izvan** `TD-OUTPUT/` —
strani fajlovi u isporučnom folderu su tačno ona zamka koja je zatvorena u §25.

---

## §27 — Rev 9 (11.09.2026.): energetski bilans iz simulacije, granice rada agregata

### Energetske vrijednosti dolaze samo iz simulacije

Sve solarne brojke u paketu su do Rev 9 bile procjena (performance ratio 0,80 →
„10,1–10,9 MWh", „560–600 kWh u decembru", „110–190 h/god") ili stranica INFO-02 sa
oznakom „NISU MJERODAVNE". Od Rev 9 izvor je `pvsim` (pvlib + PVGIS-SARAH3, satno
2005–2023): FN lanac sa gubicima po komponentama i satni bilans baterija / agregat za
19 godina. Model je provjeren prema PVGIS-u: satna korelacija r = 1,0000, godišnje
−0,7 %, mjesečno ≤2,0 %. Rezultati su u `review/pvsim/` (`kpis.json`,
`energetski-bilans.md`, slike) i ne prepisuju se ručno.

### Nalaz: granice iz Odluke nisu ostvarive

Odluka (Aneks 2) je navodila najviše 250 h/god rada agregata i spremnik od 500 l koji
traje najmanje godinu. Uz baterije od 48,6 kWh i trajne potrošače na −48 V simulacija
daje **≈250 h i ≈820 l godišnje** uz postavke SMU iz Priloga I, a bez njih ≈280 h i
≈910 l: prosjek je na granici od 250 h, a lošije godine iznad nje (u 9 od 10 godina do
≈310 h, najviše ≈330 h), a 500 l traje oko pola godine. Naručilac je 11.09.2026. odlučio da se tvrdnje zamijene simuliranim
vrijednostima, uz obavezno parametriranje SMU (`review/09-odluka-nosaci-nagib.md`).

### Baterije: 6 × 150 Ah (48,6 kWh)

Odluka navodi „6x150 Ah (48,6 kWh)", a Huawei ponuda na dosjeu 6 × ESM-48100A6
(28,8 kWh, i to uz module od 540 W — zastarjela je). Simulacija je prvo računala sa
28,8 kWh (≈280 h i ≈940 l godišnje). Naručilac je 11.09.2026. potvrdio 6 × 150 Ah:
svi dokumenti sada računaju sa 48,6 kWh, a 28,8 kWh ostaje u tabeli osjetljivosti.

### Trajni potrošači na −48 V DC

Lokacija nema mrežu, pa je agregat jedini izvor izmjeničnog napona, a ≈97 % godine ne
radi. Izvodi GRO su zato pod naponom samo dok agregat radi — i signalna rasvjeta stuba
(K7), koju je Rev 8 prevezivao u novi GRO, bila bi većinom bez napajanja. Naručilac je
11.09.2026. odlučio da se trajni potrošači napajaju sa −48 V DC iz ormara ICC360, preko
novog DC razvoda: LED svjetiljka stuba za 48 V DC, vatrodojavna centrala i punjač
akumulatora za start agregata preko DC/DC pretvarača, ventilator prostora 48 V DC, jedna
svjetiljka u kontejneru i predgrijač rashladne tečnosti, koji kontroler agregata uključuje
samo prije starta. Grijači na 230 V iz Rev 8 (rashladna tečnost u stavci 3.1, prostor u
stavci 4.13) ne bi radili dok agregat stoji: predgrijač prelazi na DC, a grijač prostora
se ne predviđa. Prilog I §4.5 ih ograničava na 25 W prosječno; simulacija računa
sa 45 W pomoćne potrošnje umjesto 20 W, što dodaje ≈13 h rada agregata godišnje. Prilog II
dobija nove stavke 5.16–5.18 (`tools/fix_boq_dc_aux.py`).

### Izmjene

| Fajl | Izmjena |
|---|---|
| `2.1 Prijedlog Odluke …docx` | Aneks 2: odlomak o 250 h i „godinu između dopuna" zamijenjen odobrenim tekstom (≈250 h, ≈820 l, dvije dopune godišnje). LOT 2: „stand-by … P22-6" → prime režim, ograničenje 9,5 kW, P18-6. LOT 1: „2 (dva) nosača" → „3 (tri)". OOXML izmjena, `tools/fix_odluka_rev9.py` |
| `3. Prilog I …docx` | §4.6: obavezno parametriranje SMU (start DOD 85 %, stop SoC 60 %, struja punjenja do granice BMS-a, najkraći rad 1 h); dokaz 12 proširen; novi §8 „Očekivani energetski bilans (informativno)" sa dvije slike — ukupno 7 slika |
| `3.2 Prilog III …pdf` | naslovna strana dobila logo (od Rev 8 je izostajao); opšti podaci: „bifacijalni" → monofacijalni iPV sa optimizatorima, „Maks. rad DEA 250 h/god" → očekivani rad iz simulacije; INFO-02 nanovo sastavljena iz simulacije, sa tekstom koji provjera čita |
| `proracuni_BS_Sjednica_Bileca.pdf / .md` | PDF sada ima tekstualni sloj (ranije slike iz jsPDF-a, nevidljive za provjeru); `.md` je bio izvor Priloga I pod pogrešnim imenom — zamijenjen izvorom proračuna. `tools/build_proracuni.py` |
| `review/07-proracuni.md` | A.5: zaključak o nagibu prema godišnjem radu agregata; A.6 zamijenjen simulacijom (ulazi, provjera, gubici, mjesečni bilans, pokazatelji, osjetljivost); C.5 prema prime potrošnji i simulaciji; D.3, E i F dopunjeni |
| `cad/design.json` | novi blokovi `energy` (iz `kpis.json`, sa sha256) i `control` (postavke SMU) — `tools/sync_energy.py` |

### Nosači i nagib ostaju

Sjednica ostaje 3 × 4 pri 45°. Nagib 60° daje više u decembru (617 prema 560 kWh), ali
agregat radi više (263 prema 247 h/god), a moment prevrtanja raste za 44–72 %. Crteži,
predmjer i Prilog I §3 se ne mijenjaju.

### Provjere

- Prije izmjena: Prilog I i svih pet crteža Rev 8 reprodukovani su u radnom folderu i
  identični su isporučenim (razlikuju se samo vremenske oznake).
- `build_prilog1.py`: 7 slika, 20 zabranjenih vrijednosti odsutno, 32 obavezne
  prisutne.
- `build_prilog3.py --k2-from-existing`: 16 stranica; K2 listovi preuzeti iz
  postojećeg priloga, pa projekat lokacije (232 MB) nije potreban.
- `build_proracuni.py`: 11 stranica sa tekstom.
- `check_consistency.py`: čita 14 dokumenata, među njima prvi put i proračune; nova
  pravila za DOD 85 % · SoC 60 % · ≈250 h · ≈820 l i zabrane za staru procjenu
  prinosa, „bifacijal", 250 h kao osnovu, „godinu između dopuna", P22-6 i „2 (dva)
  nosača". Rezultat: **2 greške, obje su procijenjene vrijednosti (LOT 2 i ukupno)
  koje Naručilac tek dostavlja.**
- Stranice Priloga III (naslovna, opšti podaci, INFO-02), Priloga I (§4.6, §8),
  Odluke i proračuna (A.6, C.5) renderovane i pregledane.

---

## §28 — dopuna Rev 9 (11.09.2026.): prava orijentacija, polje JZ, nosač 4 × 1×3

### Orijentacija

Google Maps (Naručilac, 11.09.2026.) pokazuje da je kompleks zakrenut 45°: plan „gore"
je **SI**. Vrata su na JI, hladnjak agregata (izlaz zraka i izduv) na SZ, FN plato na JZ,
ormari ICC i MTS na SI. Crteži ostaju pravougaoni na kompleks, sa strelicom sjevera
zakrenutom za 45° (`bht_frame.north_arrow(..., plan_north=45)`); svi zidovi i strane
nose prave smjerove. Hamzići: plan „gore" je SZ (315°).

### Polje na jugozapad, nosač 4 × 1×3

Niz nosača paralelan sa ogradom gleda na **225°**. Cijena prema jugu: +52 h/god rada
agregata i +173 l/god goriva (decembar −21 %); prosjek je sada ≈300 h/god, iznad
250 h iz RFI — navedeno otvoreno u 07-proracuni A.6 i u `09-odluka-nosaci-nagib.md` §5.
Nosač je **4 × 1×3 položeno** (isti na obje lokacije): 7,84 m², moment 25,7 kNm umjesto
42,6, gornja ivica +2,93 m, 8 traka 400/500 × 900 × 2600 = 8,42 m³.

### Izmjene

| Fajl | Izmjena |
|---|---|
| `pvsim/` | raspored nosača 4x3L (`stands.py`), azimut 225° iz `design.json`; izvještaji ponovo pokrenuti (commit e42bbaa) |
| `cad/design.json` | `support`, `array` (4 nosača, 225°, +2,93 m), `wind`, `foundation` (8 traka), novi blok `orientation`; `energy` preko `sync_energy.py` |
| `cad/sheets_new.py`, `build_drawings.py` | S-02: 4 nosača 1 × 3 i trake iz `design.json`; S-01/S-02 zakrenuta strelica sjevera; S-03, M-01: pravi smjerovi; M-01 i E-01: novi **DC razvod −48 V** (D1–D6), sklopka izvora „1 DEA · 0 · 2 rezerva" |
| `3.2 Prilog III …pdf` | memorandum BH Telecom u zaglavlju A4 stranica i INFO-02; stranice-razdjelnici A i B uklonjene (naslov bloka na stranici sa fotografijom); opšti podaci bez reda „Kontejner" i napomene, kraći red DEA, novi red „Orijentacija", zadnji red „Očekivani rad agregata 300~360 h/god" |
| `review/07-proracuni.md` | orijentacija; A.5, A.6 pri 225° sa tabelom jug/JZ i albedom; B.3–B.6 za 4 × 1×3; C.1, C.3, C.5, C.7, D.1, D.6, E, F |
| `review/09-odluka-nosaci-nagib.md` | §5 — odluke 11.09.2026. |

Hamzići (zajednički paket): kompleks preuređen prema pravoj orijentaciji — ormari ICC360 i
MTS na JZ strani iza FN polja, spremnik u sjevernom uglu, usis na SI zidu, izduv kroz JI
zid (`hamzici-hybrid-solar/cad/sheets_hamzici.py`, H-01…H-05).
