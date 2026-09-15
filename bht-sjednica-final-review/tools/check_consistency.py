# -*- coding: utf-8 -*-
"""
Cross-document consistency check for the BS Sjednica tender package.

Reads every deliverable in its native form - OOXML straight out of the .docx zip,
openpyxl for the .xlsx, PyMuPDF for the .pdf, ezdxf for the .dxf - so nothing is
lost to a text-export round trip (LibreOffice's txt export mangles Bosnian
diacritics on a cp1252 console, which silently breaks naive greps).

Two kinds of check:

  CONFLICT  a fact that must have exactly one value across the package
            (generator rating, container size, panel geometry, LOT values)
  BANNED    text that must not appear at all - leftovers from the 46-generator
            template that this single-location job inherited

Exit code is the number of failures, so it can gate a release.
"""
from __future__ import annotations

import glob
import os
import re
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paths import TD                                                # noqa: E402


# --------------------------------------------------------------------------
# readers
# --------------------------------------------------------------------------
def read_docx(path):
    """Concatenate the visible text of every w:t run, in document order."""
    z = zipfile.ZipFile(path)
    out = []
    for part in ("word/document.xml", "word/header1.xml", "word/header2.xml",
                 "word/header3.xml", "word/footer1.xml", "word/footer2.xml",
                 "word/footer3.xml", "word/footnotes.xml", "word/endnotes.xml"):
        if part not in z.namelist():
            continue
        xml = z.read(part).decode("utf-8", "replace")
        # Paragraph breaks have to survive as text: the run collector below keeps
        # only <w:t> contents, so a bare "\n" substitution here was discarded and
        # adjacent table cells came out glued together ("gorivomranije:"), which
        # silently defeated every \b-anchored pattern.
        xml = re.sub(r"</w:p>", "<w:t>\n</w:t>", xml)
        out.append("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)))
        out.append("\n")
    return "".join(out)


def read_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=False)
    out = []
    for ws in wb:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str):
                    out.append(c.value)
                elif c.value is not None:
                    out.append(str(c.value))
    return "\n".join(out)


def read_pdf(path):
    import fitz
    d = fitz.open(path)
    return "\n".join(d[i].get_text() for i in range(d.page_count))


def read_dxf(path):
    import ezdxf
    d = ezdxf.readfile(path)
    out = []
    for e in d.modelspace():
        if e.dxftype() == "TEXT":
            out.append(e.dxf.text)
        elif e.dxftype() == "MTEXT":
            out.append(e.text)
    return "\n".join(out)


READERS = {".docx": read_docx, ".xlsx": read_xlsx, ".pdf": read_pdf, ".dxf": read_dxf}


# NOTE - a blind spot worth knowing about: Prilog III is an image-only PDF
# (scanned drawing sheets with no text layer), so READERS returns nothing for it
# and none of the rules below ever see its content. Anything that lives only on
# those sheets, and any disagreement between them and the prose, is invisible
# here and has to be read off the drawings by eye.
def load():
    docs = {}
    for p in sorted(glob.glob(os.path.join(TD, "*")) +
                    glob.glob(os.path.join(TD, "grafika", "*.dxf"))):
        ext = os.path.splitext(p)[1].lower()
        if ext not in READERS or os.path.basename(p).startswith("~"):
            continue
        try:
            docs[os.path.relpath(p, TD)] = READERS[ext](p)
        except Exception as exc:                       # noqa: BLE001
            print(f"  ! could not read {os.path.basename(p)}: "
                  f"{type(exc).__name__}: {exc}")
    return docs


# --------------------------------------------------------------------------
# rules
# --------------------------------------------------------------------------
# name -> {variant label: regex}.  Exactly ONE variant may appear package-wide.
CONFLICTS = {
    # Rev 7 (2026-08-12): FG Wilson P18-6. 22 kVA was the original set; 13,5 kVA
    # was adopted on 2026-08-11 and withdrawn a day later, because its
    # site-derated prime rating (9,7 kW at 1076 m / 40 C) is below the 12,5 kW
    # the rectifiers can draw. Both earlier ratings are now superseded, so either
    # one appearing anywhere is a live conflict.
    "generator rating": {
        "18 kVA (correct)": r"18\s*kVA",
        "22 kVA (superseded)": r"22\s*kVA",
        "13,5 kVA (superseded)": r"13[,.]5\s*kVA",
        # excluded: bibliographic/explanatory mentions of the MATISA 2x13 kVA
        # reference installation, which are correct usages rather than conflicts
        "2x13 kVA as a spec": r"(?<!MATISA )(?<!agregata \()2\s*[x×]\s*13\s*kVA(?![^.]{0,40}referent)",
    },
    # A superseded value quoted in Prilog I's "Ranije navedeno" column is a
    # documented correction, not a live specification: it is always followed within
    # the same table row by the corrected value, so a lookahead excludes it.
    "container external size": {
        "3005 x 2300 (certified project)":
            r"3005\s*[x×]\s*2300|3[,.]00\s*[x×]\s*2[,.]30|3[,.]005\s*[x×]\s*2[,.]30",
        "3,08 x 2,20 (WRONG)": r"3[,.]08\s*[x×]\s*2[,.]20(?![^§]{0,90}3[,.]005)",
        "3,00 x 2,10 (WRONG)": r"3[,.]00\s*[x×]\s*2[,.]10(?![^§]{0,90}3[,.]005)",
    },
    "PV module power": {
        "585 Wp": r"585\s*Wp",
        "540 Wp": r"540\s*Wp",
    },
    "panel horizontal projection": {
        # 2590 mm survives only inside S-03's note explaining the correction, so a
        # following "nije"/"ISPRAVLJENO" marks a legitimate historical mention
        # also excluded when followed by the corrected 3236 (Prilog I corrections table)
        "2590 (WRONG - beam length)":
            r"2590\s*mm(?![^.]{0,80}(nije|ISPRAVLJENO|raniji))(?![^§]{0,90}3236)"
            r"|2[,.]59\s*m\b",
        "3236 (correct - module field)": r"3236\s*mm|3[,.]24\s*m\b",
    },
    # +3,74 was correct for the 2x6 design; the 2026-08-08 3x4 redesign raised the
    # bottom edge to spend the freed-up wind budget on height (review/07-calculations.md
    # F.6), so +3,74 is now only a legitimate historical/superseded mention (Prilog I
    # §0's corrigendum table, or S-03's design-history note) when the corrected +4,74
    # appears nearby, same lookahead pattern as the 2590/3236 correction above.
    # Rev 7c (2026-08-12): the bottom edge returns to +0,50 m, so the top edge is
    # +3,74 again - the same figure the 2x6 design had, reached a different way.
    # The +4,74 of the raised 3x4 layout is now the superseded variant. Watch the
    # direction of these lookaheads: they invert every time this value moves.
    "top panel edge level": {
        "+3,09 (WRONG - never correct)": r"\+?3[,.]09(?![^§]{0,90}3[,.]74)",
        "+4,74 (superseded - the raised 3x4 layout)":
            r"\+?4[,.]74(?![^§]{0,90}3[,.]74)",
        "+3,74 (correct - bottom edge back at +0,50)": r"\+?3[,.]74",
    },
    # Rev 2 (2026-08-11): the airflow relayout and the section-G closures below.
    # Each corrected value is quoted once more in Prilog I's "Ranije navedeno"
    # column, so the superseded variants carry the same lookahead as above.
    # The certified project of this K2 object ("04 AG dio.docx" 4.4.2.3) dimensions
    # the floor for a total (g+p) UDL of 10,00 kN/m². The 2,00 kN/m² in the same
    # project is the pedestrian live load on the walkable strip, so it may only
    # appear where it is named as such - hence the lookahead rather than a ban.
    "container floor capacity": {
        "10,00 kN/m² (correct - K2 project 4.4.2.3)": r"10[,.]00\s*kN/m²",
        "2,00 kN/m² (WRONG - that is the walkable-strip live load)":
            r"2[,.]00\s*kN/m²(?![^§]{0,160}(pokretn|prohodn|walkable))",
    },
    "foundation concrete class": {
        "C25 (WRONG - no exposure class)": r"\bC25\b(?![^§]{0,90}C30/37)",
        "C30/37 XF3 (correct)": r"C30/37",
    },
    "fuel tank footprint": {
        "1200 x 700 (WRONG - estimate)":
            r"1200\s*[x×]\s*700(?![^§]{0,90}1050\s*[x×]\s*600)",
        "1050 x 600 x 1310 (correct - vendor data)":
            r"1050\s*[x×]\s*600",
    },
    # The TANK is 500 l; the FIRST FILL is 250 l (TD _K, BOQ 4.16 quantity). Only
    # the fill is checked here - a bare "500 l" is the tank, and is covered by
    # SINGLE_VALUE["fuel tank"] - so every pattern is anchored on the filling.
    "first fuel fill": {
        "200 l (WRONG)": r"najmanje\s*200\s*l|≥\s*200\s*l",
        "500 l / pun spremnik (superseded)":
            r"500\s*l\s*\(pun spremnik\)|tankanje\s*500\s*l",
        "250 l (correct - matches BOQ 4.16)":
            r"[Pp]rvo punjenje je 250\s*l|tankanje\s*250\s*l",
    },
    # Rev 7: the Huawei quotation on file (EQUIPEMENT/CABINETS/iSitePower ...
    # BOQ_v2.xlsx, sheet L3-iSitePower-A) quotes ICC360-HA1-C1 (01075399), and
    # review/01-huawei-solar.md §185/§190 had already said so. Rev 2 unified on
    # ICC330-H1 + MTS9302 by counting mentions - a majority count is not evidence.
    "power system named": {
        "ICC360-HA1-C1 (correct - per the vendor quotation)": r"ICC360-HA1-C1",
        "ICC330-H1 + MTS9302 (superseded)": r"ICC330-H1",
    },
    "fence overhang": {
        "0,17 m (WRONG)": r"0[,.]17\s*m",
        "0,20 m (WRONG)": r"nadvi[šs]uje ogradu[^.]{0,20}0[,.]20\s*m",
        # Two corrections stack here. Rev 6: the fence is 2,10 m off the certified
        # 04 Ograda.dwg, not the 1,90 m assumed earlier. Rev 7c: the bottom edge
        # drops back to +0,50 m, taking a further 1,00 m off the overhang.
        # 1,84 -> 2,84 -> 2,64 -> 1,64, and only the last one is live.
        "1,84 m / 1836 mm (superseded - 2x6 against a 1,90 m fence)":
            r"(1[,.]84\s*m|1836\s*mm)(?![^§]{0,90}(1[,.]64|1636))",
        "2,84 m / 2836 mm (superseded - raised 3x4, 1,90 m fence)":
            r"(2[,.]84\s*m|2836\s*mm)(?![^§]{0,90}(1[,.]64|1636))",
        "2,64 m / 2636 mm (superseded - raised 3x4, 2,10 m fence)":
            r"(2[,.]64\s*m|2636\s*mm)(?![^§]{0,90}(1[,.]64|1636))",
        "1,64 m / 1636 mm (correct)": r"1[,.]64\s*m|1636\s*mm",
    },
    "fence height": {
        "1,90 m (superseded - was an assumption)":
            r"ograd[ae][^.]{0,20}h\s*=\s*1[,.]90\s*m",
        "2,10 m (correct - certified 04 Ograda.dwg)":
            r"ograd[ae][^.]{0,20}h\s*=\s*2[,.]10\s*m",
    },
    # ---- Rev 8 (2026-08-12) --------------------------------------------------
    # These six all survived six revisions inside Prilog I because nothing here
    # was watching them. Five are values that moved when the bottom edge dropped
    # to +0,50 m or when the set became the P18-6; the sixth is the sheet-metal
    # duct area inherited from the Mostar "POTOCI" specification.
    "overturning moment per support": {
        "42,6 kNm (correct - bottom edge +0,50 m)": r"42[,.]6\s*kNm",
        "62,8 kNm (superseded - bottom edge +1,50 m)": r"62[,.]8\s*kNm",
        "64,3 kNm (superseded - the 2x6 design)": r"64[,.]3\s*kNm",
    },
    "uplift couple per foundation strip": {
        "26,6 kN (correct)": r"26[,.]6\s*kN\b",
        "39,2/39,3 kN (superseded - bottom edge +1,50 m)": r"39[,.][23]\s*kN\b",
    },
    "heat radiated into the room": {
        "5,8 kW (correct - P18-6)": r"5[,.]8\s*kW",
        "7,1 kW (superseded - P22-6)": r"7[,.]1\s*kW",
    },
    # 3 x In depends on the rating: 78 A at 18 kVA, 95 A at 22 kVA. Prilog I
    # carried BOTH - §4.1 said 78 A and §4.5 said 95 A, in the same document.
    "generator sustained fault current (3 x In)": {
        "78 A (correct - 18 kVA)": r"78\s*A\b",
        "95 A (superseded - 22 kVA)": r"95\s*A\b",
    },
    "discharge duct developed area": {
        "1,0 m² (correct - radiator is 60 mm off the wall)":
            r"1[,.]0\s*m²(?=[^§]{0,120}(kanal|prirubnic|hladnjak))"
            r"|(kanal|prelazni komad)[^§]{0,160}?1[,.]0\s*m²",
        "6 m² (superseded - inherited from Mostar)":
            r"[≈~]\s*6\s*m²|P\s*[≈~]?\s*6\s*m2",
    },
    "foundation concrete volume": {
        "8,91 m³ (correct - full-depth strip)": r"8[,.]91\s*m³",
        "2,44 m³ (superseded - 450x275 footing)": r"2[,.]44\s*m³",
    },
}

# these must appear with a single consistent value; reported if they disagree
SINGLE_VALUE = {
    "LOT 1 estimate": r"15\.000,00",
    "LOT 2 estimate": r"34\.000,00",
    "total estimate": r"49\.000,00",
    "fuel tank": r"500\s*l\b",
    "site altitude": r"1076\s*m",
    # closed in Rev 2 - each was specified nowhere or in only one document
    # renamed "rasvjeta prepreke" -> "rasvjeta stuba" (Naručilac, 15.09.2026);
    # the old term is still accepted so the Rev 9 package keeps passing
    "tower obstruction lighting (G-9)": r"rasvjet[ae]\s+(stuba|prepreke)",
    "type 1+2 AC SPD (G-6)": r"[Tt]ip\s*1\s*\+\s*2|TIP\s*1\s*\+\s*2",
    "signal-line SPD (G-6)": r"61643-21",
    "fire elaborate priced (G-5)": r"elaborat[a]?\s+za[šs]tite\s+od\s+po[žz]ara",
    "intake on the north wall": r"SJEVERNI\s*zid|SJEVERNOM\s*zidu",
    "discharge on the west wall": r"ZAPADNI\s*zid|ZAPADNOM\s*zidu",
    # Rev 8: the rectifier input cap is the governing electrical requirement
    # (07-proracuni D.5) and it had gone missing from the BOQ entirely - the
    # prose said "limit the input power" without ever saying to what.
    "rectifier input cap as a number": r"9[,.]5\s*kW",
    # Rev 8: the drip tray under the tank was referenced by two BOQ items but
    # supplied by none, and its size appeared nowhere.
    "drip tray under the fuel tank": r"1150\s*[x×]\s*640",
    "exhaust insulation area": r"3[,.]0\s*m²",
    # Rev 9 (2026-09-11): the SMU settings the TD now requires, and the genset
    # operation the pvsim simulation gives with them - both must be stated.
    "SMU start at DOD 85 %": r"DOD\s*85\s*%",
    "SMU stop at SoC 60 %": r"SoC\s*60\s*%",
    "expected genset operation ≈250 h/god": r"≈\s*250\s*h",
    "expected fuel ≈820 l/god": r"≈\s*820\s*l",
}

# text that must not survive from the 46-generator template
BANNED = {
    "towing trailer (this job is skid-mounted)": r"vu[čc]n[uae]?\s+prikolic",
    "multi-location rollout clause": r"najmanje\s+dvije\s+lokacije",
    "fence extension with no BOQ item": r"pro[šs]irenje\s+postoje[ćc]e\s+ograde",
    "unresolved reference site": r"Brlo[šsž]ki\s+Potok",
    "empty numbered clause": r"\n\s*1\.5\s*\n\s*1\.6",
    "placeholder": r"\bTBD\b|\bXXX\b|<<[^>]+>>",
    # Rev 2: the blanket placement that put intake, discharge and the 505 °C
    # exhaust on the same wall, next to the outdoor power cabinets (EL RED-03)
    "all openings on the north wall": r"sve\s+na\s+SJEVERNOJ\s+strani",
    # Rev 9 (2026-09-11): energy figures come from the pvsim simulation only.
    # The Odluka's 250 h and "a year per 500 l" were never reachable with this
    # design (review/09-odluka-nosaci-nagib.md); the old PR 0,80 estimate and the
    # "bifacial" label survived on the Prilog III pages the checker could not read.
    "old yield estimate (PR 0,80)":
        r"10[,.]1\s*[–-]\s*10[,.]9\s*MWh|560\s*[–-]\s*600\s*kWh",
    "bifacial modules (they are monofacial iPV)": r"bifacijal",
    "250 h limit as the design basis": r"250\s*h(\s*/\s*god)?\s*\(stand",
    "500 l as a year of fuel": r"najmanje\s+godinu\s+između\s+dopuna",
    "withdrawn genset P22-6": r"P22-6",
    "two PV stands (there are three)": r"2\s*\(dva\)\s*nosača",
}


# A superseded value quoted inside a documented correction is a record, not a live
# specification. Prilog I's corrigendum table and the drawings' design-history notes
# both do this deliberately, so a hit whose neighbourhood carries one of these
# markers does not count. Keep the list short - it is an exemption, not a loophole.
# Stems, not whole words: Bosnian inflects these ("mjerodavan / mjerodavna /
# mjerodavni", "ranije / ranija / raniji"), and an over-specific ending silently
# turns the exemption off - which is exactly how the first version of this list
# let a documented correction be reported as a live conflict.
CORRECTION_MARKERS = re.compile(
    r"\branij[aeiou]\w*|ISPRAVLJENO|IZMJENA|NIJE\s+mjerodav|nisu\s+mjerodav|"
    r"umjesto|razli[čc]ito\s+u\s+dokumentima|REDOSLIJED\s+MJERODAVNOSTI", re.I)
CONTEXT = 240


def scan(docs, pattern, live_only=False, skip=()):
    """Count matches per document. With live_only, ignore matches that sit inside
    a documented correction."""
    hits = {}
    for name, text in docs.items():
        if name in skip:
            continue
        n = 0
        for m in re.finditer(pattern, text, re.I):
            if live_only:
                near = text[max(0, m.start() - CONTEXT):m.end() + CONTEXT]
                if CORRECTION_MARKERS.search(near):
                    continue
            n += 1
        if n:
            hits[name] = n
    return hits


def main():
    docs = load()
    print(f"documents read: {len(docs)}")
    for n in docs:
        print(f"   {n}  ({len(docs[n]):,} chars)")
    fails = 0

    print("\n=== CONFLICTS (exactly one variant allowed) ===")
    for topic, variants in CONFLICTS.items():
        found = {label: scan(docs, pat, live_only="WRONG" in label or
                             "superseded" in label)
                 for label, pat in variants.items()}
        found = {k: v for k, v in found.items() if v}
        if len(found) > 1:
            fails += 1
            print(f"  FAIL  {topic}: {len(found)} variants coexist")
            for label, hits in found.items():
                print(f"          '{label}' in " +
                      ", ".join(f"{k} x{v}" for k, v in hits.items()))
        elif len(found) == 1:
            label = next(iter(found))
            print(f"  OK    {topic}: '{label}' "
                  f"({sum(found[label].values())} mentions)")
        else:
            print(f"  --    {topic}: not mentioned anywhere")

    print("\n=== REQUIRED VALUES ===")
    for topic, pat in SINGLE_VALUE.items():
        hits = scan(docs, pat)
        if not hits:
            fails += 1
            print(f"  FAIL  {topic}: absent from the whole package")
        else:
            print(f"  OK    {topic}: {sum(hits.values())} mentions "
                  f"in {len(hits)} document(s)")

    print("\n=== BANNED TEXT (template leftovers) ===")
    for topic, pat in BANNED.items():
        hits = scan(docs, pat, live_only=True)
        if hits:
            fails += 1
            print(f"  FAIL  {topic}: " +
                  ", ".join(f"{k} x{v}" for k, v in hits.items()))
        else:
            print(f"  OK    {topic}: gone")

    print(f"\nRESULT: {fails} failure(s)")
    return fails


if __name__ == "__main__":
    sys.exit(main())
