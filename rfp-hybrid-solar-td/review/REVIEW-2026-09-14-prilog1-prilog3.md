# Technical and document review — Prilog I and Prilog III

Scope as requested: a deep review of **Prilog I** (Specifikacija zahtjeva) and
**Prilog III** (Situacije), with **Prilog II inspected for quantities only** — item
texts were not to be touched without a go-ahead. That restriction was lifted on
14.09.2026 for the reviewer's comments; those are answered separately in
`ODGOVOR-RECENZENTU-2026-08-27.md` and are not repeated here.

Baseline: `origin/hamzici-joint-td` at `1d8302f`, i.e. after the true-orientation
relay (both fields at azimut 225°, 4 × 1×3 landscape stands, pvsim re-run at 45°/225°).
Findings that the relay had already resolved are marked as such and not re-argued.

---

## 0. What was verified and found correct

| Checked | Result |
|---|---|
| Precedence chain TD JN → Prilog I → Prilog II → Prilog III | consistent; no clause contradicts a higher-ranked one |
| Both sites named in every joint deliverable | `rules_joint.py` COVERAGE passes |
| Energy figures traced to `pvsim/kpis.json` | Prilog I §8, INFO-02 pages and both proračuni quote the same run |
| `design.json` ↔ `kpis.json` array (tilt, azimut, kWp) | 45° / 225° / 7,02 kWp at both sites |
| Drawing extents, title blocks, text overlaps | `build_drawings` / `build_hamzici` checks pass, 0 overlaps |
| Prilog II arithmetic at unit price 100 | 23 priced rows LOT 1, 83 LOT 2; no orphan line rows |
| Hamzići site facts (Čitluk, k.č. 109/1, 32 m mast, 493 m, 1,80 m fence) | all present, no Sjednica-only fact left in a Hamzići sheet |

## 1. Fixed in this pass

### F-2 — Nobody was responsible for hauling the Buyer's equipment to site (**high**)

TD JN excludes the PV modules, batteries and control system as a separate procurement
(`posebna nabavka`) and Prilog II 5.14 repeats it — but no document said who collects
them from the warehouse and brings them to site. A bidder could price the whole LOT 2
and legitimately refuse the haul.

Added as LOT 2 scope at **both** sites:

| Where | What |
|---|---|
| Prilog I **§4.9** | pickup at skladište **Azići, Bojnička bb, Sarajevo**; scope, vehicle, handling, 3-working-day notice, documents, custody |
| Prilog I §5, dokaz **14** | otpremnica + zapisnik o preuzimanju, per site |
| Prilog II **5.19** | new row on **both** LOT 2 site sheets, kpl × 1 |
| Prilog III, p. 20 | `Oprema Kupca` row |
| TD JN | one clause after „Originalni PV instalacioni materijal će obezbijediti Kupac." |

Existing Prilog II item texts and quantities were not touched; 5.19 is a new row,
carried by a new `BOTH_SITES_NEW_ITEMS` mechanism that `check_boq_recalc` knows about.

### F-3 — Title block named the designer as their own checker (**low, doc**)

`bht_frame.draw_frame` filled `ovjerio:` with the same name as `Projektant:`. The field
is now left ruled and empty for a wet signature; the label stays so the field is still
marked.

### F-4 — Two holes in the build's own guard rails (**medium, tooling**)

1. `build_prilog1.FORBIDDEN` (inherited from the single-site build) bans the string
   `"Tačku 4.8"` on the grounds that *„Prilog I nema tačku 4.8"*. The **joint** Prilog I
   does have a §4.8 (demontaža Stulza), so that rule was one correct cross-reference away
   from failing the build for no reason. Filtered out of the joint list.
2. Nothing compared `cad/design.json` against `review/pvsim/kpis.json`. That is exactly
   how a package whose field faces 225° kept quoting a 180° yield. New
   `check_pvsim_matches_design()` runs first in `build_joint.main()` and refuses to build
   on any mismatch in tilt, azimut or kWp.

## 2. Reported — needs your decision

### F-5 — Sjednica radiator airflow is derived at the wrong air density (**medium, technical**)

`07-proracuni` A.1 tabulates four densities for Sjednica, including **0,991 kg/m³** at
the +40 °C design ambient and **1,0904 kg/m³** which is the density *the certified
project uses for the wind calculation*. A.2 then derives the radiator flow from the
wind density:

```
sada:      1980 × 1,184/1,090  ≈  2151 m³/h
ispravno:  1980 × 1,184/0,991  ≈  2366 m³/h      (+10 %)
```

Hamzići does it correctly — `1980 × 1,184/1,063 ≈ 2206 m³/h`, the +40 °C density at
493 m. The tell is that the **higher, more heavily derated site reports the lower flow**
(2151 < 2206), which cannot be right.

Consequence: the intake total in C.1 goes **2241 → ≈2456 m³/h**, so the 500 × 700
intake louvre and its free area should be re-checked before this is corrected in the
document. That is why it is reported rather than fixed — it ripples into louvre sizing
at one site only.

### F-10 — Hamzići shading: the tree crown looks wider than the model assumes (**low**)

The deciduous tree JJI–JI of the mast is modelled at ≈7–9 m height, 15–20 m away, and
the array now faces JZ, so it mostly avoids it (≤2 % of December production). In the
site photographs the crown reads wider than the modelled cylinder. Not worth a re-run;
worth one measurement on the mandatory site visit.

### F-11 — Two asymmetries between the Sjednica and Hamzići blocks of Prilog III (**low**)

Sjednica's `cad/site_geometry.json` still records `pv_arrays: … facing SOUTH (azimuth
180 deg)` and carries no `plan_north_bearing_deg`, while its own `design.json` says 225°
and „plan north = true NE". Hamzići's block is complete (`plan_north_bearing_deg: 315`,
every side named). Nothing downstream reads the stale keys — the drawings and the TD
take orientation from `design.json` — but the file is the site's record and should say
the same thing.

Second: `bht-sjednica-final-review/review/prilog1.md` (the per-site source) still names
walls in the **plan** frame (SJEVERNI zid, istočni kraj), while the joint Prilog I names
them in the **true** frame (SI/SZ/JI/JZ). Both are internally consistent; only the joint
document ships.

## 3. Note on the photographs

The site photographs credited to **Rusmir Skopljak** (08.09.2026) were used as the
primary check on three things, and all three held: the container door and gate are on
the same face at Hamzići; the Stulz sits on the wall opposite the door, centred; and the
terrain outside the slab drops about 0,20 m, which is what puts the fence at 2,00 m
above ground while the certified drawing calls it 1,80 m above the slab. The Stulz body
and its wall cut-outs were sized *from the photographs* — `site_geometry.json` flags
them as estimates and Prilog I requires the bidder to measure them at the site visit.

## 4. What was rebuilt, and what still needs a local run

| Deliverable | State |
|---|---|
| Prilog I `.docx` | rebuilt; guards pass |
| TD JN, NZ, Odluka, Izjava `.docx` | rebuilt |
| Prilog II LOT 1 / LOT 2 `.xlsx` | rebuilt |
| `grafika/**.dxf` | rebuilt, both sites |
| `proračuni_BS_*.pdf` | **stale** — the step needs LibreOffice |
| `3.2 Prilog III TD - Situacije.pdf` | **not rebuilt** — fails identically on the untouched base branch |
| `grafika/**.dwg` | **stale** — needs the ODA File Converter |

The three gaps are environment limits, not content: LibreOffice cannot open any file in
this container, ODA is absent, and the Prilog III memorandum line fails its fit check on
the base branch too (verified in a scratch worktree). One local `build_joint.py` run
closes all three.

`rules_joint.py` reports the stale proračuni PDFs as its only remaining disagreement —
they still carry the superseded strip section and concrete volume.
