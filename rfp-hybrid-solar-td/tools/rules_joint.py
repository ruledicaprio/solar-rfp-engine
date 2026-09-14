# -*- coding: utf-8 -*-
"""
Consistency check for the joint two-site package (rfp-hybrid-solar-td/TD-OUTPUT).

Reuses the Sjednica checker's readers and rules: both sites carry the same
system, so every "exactly one value" rule (generator rating, container size,
module power, stand forces, foundation volume, ...) still has one correct value
across the joint package. Site-specific values that differ (fence 2,10 / 1,80 m,
overhang 1,64 / 1,74 m, altitude 1076 / 493 m) are not variants of those rules,
so they do not collide; they are added below as values that must be present.

Two additions for the joint package:
  COVERAGE   every deliverable names both sites
  BANNED+    single-site leftovers, wrong facts about Hamzići, and the estimate
             placeholders / 50 000 KM figures that the Investor's estimate of
             12.09.2026 (100 000 KM bez PDV-a: LOT 1 30 000, LOT 2 70 000) replaced

Exit code = number of failures, so the package cannot be released by accident.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths                                                        # noqa: E402

sys.path.insert(0, os.path.join(paths.SITES["sjednica"]["folder"], "tools"))
import check_consistency as cc                                      # noqa: E402

# ---- 11.09.2026: true orientation, SW fields, 4x3L stand at both sites --------
# The Sjednica checker keeps guarding the standalone Rev 9 package, so the values
# this round supersedes are overridden here rather than there.
SUPERSEDED_SINGLE = {"expected genset operation ≈250 h/god", "expected fuel ≈820 l/god",
                     "intake on the north wall", "discharge on the west wall"}
SINGLE_VALUE = {k: v for k, v in cc.SINGLE_VALUE.items()
                if "estimate" not in k and k not in SUPERSEDED_SINGLE}
SINGLE_VALUE.update({
    "Hamzići altitude 493 m": r"493\s*m",
    "Hamzići parcel k.č. 109/1": r"109/1",
    "Hamzići fence 1,80 m": r"1[,.]80\s*m",
    "Stulz WDE80 removal": r"Stulz\s*WDE80",
    "Stulz delivered to Alipašino Polje": r"Alipašino\s*Polje",
    "Sjednica expected genset ≈300 h/god": r"≈\s*300\s*h",
    "Sjednica expected fuel ≈990 l/god": r"≈\s*990\s*l",
    "Hamzići expected genset ≈270 h/god": r"≈\s*270\s*h",
    "Hamzići expected fuel ≈900 l/god": r"≈\s*900\s*l",
    "PV azimuth 225° (true SW)": r"225\s*°",
    "walls named by true direction (SI/SZ/JI/JZ)": r"\b(SI|SZ|JI|JZ)\s+zid",
    # estimate, Investor 12.09.2026 (replaces the Sjednica 15 000 / 34 000 / 49 000 rules)
    "total estimate 100.000,00 KM": r"100\.000,00\s*KM",
    "LOT 1 estimate 30.000,00 KM": r"30\.000,00\s*KM",
    "LOT 2 estimate 70.000,00 KM": r"70\.000,00\s*KM",
    "estimate in words (sto hiljada)": r"sto\s+hiljada\s+konvertibilnih\s+maraka",
    "one price form per LOT": r"zaseban\s+za\s+(svaki\s+LOT|LOT\s*1\s+i\s+za\s+LOT\s*2)",
    # recenzija A. Čolpa, 27.08.2026
    "bidder's technical solution required with the bid":
        r"tehni[čc]k\w*\s+rje[šs]enj\w*\s+konstrukcije",
    "static calculation is a precondition for STARTING the works":
        r"uslov\s+(je\s+)?za\s+po[čc]inja\w*\s+radova|PO[ČC]ETAK\s+RADOVA",
    "foundation strip of one constant width": r"jedinstven\w*\s+[šs]irin\w*",
})

CONFLICTS = dict(cc.CONFLICTS)
CONFLICTS.update({
    "panel horizontal projection": {
        "2434 mm (correct - 4x3L)": r"2434\s*mm|2[,.]43\s*m\b",
        "3236 mm (superseded - 3x4)": r"3236\s*mm",
        "2590 (WRONG - beam length)": cc.CONFLICTS["panel horizontal projection"][
            "2590 (WRONG - beam length)"],
    },
    "top panel edge level": {
        "+2,93 (correct - 4x3L)": r"\+\s*2[,.]93",
        "+3,74 (superseded - 3x4)": r"\+\s*3[,.]74",
        "+4,74 (superseded - the raised 3x4 layout)": r"\+\s*4[,.]74",
    },
    "fence overhang (Sjednica)": {
        "0,83 m (correct - 4x3L, 2,10 m fence)": r"0[,.]83\s*m",
        "1,64 m / 1636 mm (superseded - 3x4)": r"1[,.]64\s*m|1636\s*mm",
    },
    "fence overhang (Hamzići)": {
        "0,93 m (correct - 4x3L)": r"0[,.]93\s*m",
        "1,74 m (superseded - 3x4)": r"1[,.]74\s*m",
    },
    "overturning moment per support": {
        "25,7 kNm (correct - 4x3L)": r"25[,.]7\s*kNm",
        "42,6 kNm (superseded - 3x4)": r"42[,.]6\s*kNm",
        "62,8 kNm (superseded - bottom edge +1,50 m)": r"62[,.]8\s*kNm",
        "64,3 kNm (superseded - the 2x6 design)": r"64[,.]3\s*kNm",
    },
    "uplift couple per foundation strip": {
        "16,1 kN (correct - 4x3L)": r"16[,.]1\s*kN\b",
        "26,6 kN (superseded - 3x4)": r"26[,.]6\s*kN\b",
        "39,2/39,3 kN (superseded - bottom edge +1,50 m)": r"39[,.][23]\s*kN\b",
    },
    "foundation concrete volume": {
        "9,36 m³ (correct - 8 constant-section strips)": r"9[,.]36\s*m³",
        "8,42 m³ (superseded - 400/500 taper)": r"8[,.]42\s*m³",
        "8,91 m³ (superseded - 6 strips)": r"8[,.]91\s*m³",
        "2,44 m³ (superseded - 450x275 footing)": r"2[,.]44\s*m³",
    },
    "foundation strip section": {
        "500 mm constant (correct - reviewer 27.08.2026)": r"500\s*×\s*2600\s*mm",
        "400/500 taper (withdrawn - cannot be cut in rock)": r"400\s*(mm\s*)?\(gore\)",
        "450/550 taper (superseded - 3x4)": r"450\s*(mm\s*)?\(gore\)",
    },
    "PV azimuth": {
        "225° (correct - true SW)": r"azimut\w*\s*(od\s*)?225",
        "180° (superseded - south)": r"azimut\w*\s*(od\s*)?180",
    },
})

# a superseded value named as such is a record, not a live specification
cc.CORRECTION_MARKERS = re.compile(cc.CORRECTION_MARKERS.pattern
                                   + r"|zamijenjen\w*|prethodn\w*|ne\s+stane|ne\s+bi\s+stao",
                                   re.I)

BANNED = dict(cc.BANNED)
BANNED.update({
    # Reviewer A. Čolpa, 27.08.2026: the per-stand design forces are not tendered as
    # figures, the estimated stand mass is withdrawn, and the static calculation is a
    # condition for STARTING the works, not for handover.
    "static calculation as a handover condition (withdrawn, reviewer 27.08.2026)":
        r"prora[čc]un\s+se\s+dostavlja[^.]{0,60}primopredaj",
    "estimated stand mass tendered as a figure (withdrawn, reviewer 27.08.2026)":
        r"[Mm]asa\s+(nosa[čc]a|rama)[^.|]{0,40}≈\s*\d+\s*kg",
    "per-stand design forces tendered as required values (withdrawn, reviewer 27.08.2026)":
        r"Projektne\s+sile\s+po\s+nosa[čc]u[^.]{0,40}podizanje\s*≥",
    "Hamzići placed in Čapljina (it is Čitluk)": r"Čapljin",
    "Hamzići tower as 36 m (it is 32 m)": r"AS\s*36\s*m|visine\s+(h\s*=\s*)?36\s*m",
    "question-mark placeholder": r"Hamzi[ćc]i\?",
    "single-site title": r"NAPAJANJA\s+SJEDNICA,\s+BILEĆA\s+\(LOT",
    "single-site phrase in the Odluka": r"na\s+baznoj\s+stanici\s+Sjednica",
    "withdrawn 2017 grid connection presented as existing": r"priključen\w*\s+na\s+EES\s+preko",
    "2x2 portrait stand (superseded by 4x3L)": r"2\s*reda\s*×\s*2\s*(kolone|modula)",
    "south-facing field (superseded by SW)": r"orijentacij\w*\s+JUG\s*\(azimut",
    "Hamzići PV in the south strip (it is the JZ band)": r"pojasu\s+južno\s+od\s+ploče",
    "estimate placeholder left": r"___\.___",
    "estimate in words 'pedeset hiljada' (it is 100 000)": r"pedeset\s*hiljada",
    "superseded 50 000 KM estimate (15 000 / 35 000)": r"\b(50|15|35)\.000,00\s*KM",
    "typo 'LOT 1a iznos'": r"LOT\s*1a\s+iznos",
    "combined price form (one form per LOT)": r"Obrazac\s+za\s+cijenu\s+ponude\s+\(LOT\s*1\s+i\s+LOT\s*2\)",
})

def load():
    cc.TD = paths.TD
    docs = cc.load()
    for p in sorted(glob.glob(os.path.join(paths.GRAFIKA, "*", "*.dxf"))):
        try:
            docs[os.path.relpath(p, paths.TD)] = cc.read_dxf(p)
        except Exception as exc:                                    # noqa: BLE001
            print(f"  ! could not read {p}: {exc}")
    return docs


def main():
    docs = load()
    print(f"documents read: {len(docs)}")
    for n in docs:
        print(f"   {n}  ({len(docs[n]):,} chars)")
    fails = 0

    print("\n=== COVERAGE (every deliverable names both sites) ===")
    for name, text in docs.items():
        # drawings and the per-site calculations belong to one site by design
        if name.startswith("grafika") or name.startswith("proracuni_BS_"):
            continue
        has = {s: bool(re.search(p, text, re.I)) for s, p in
               (("Sjednica", r"Sjednic"), ("Hamzići", r"Hamzi[ćc]"))}
        ok = all(has.values())
        fails += not ok
        print(f"  {'OK  ' if ok else 'FAIL'} {name}: " +
              ", ".join(f"{s} {'da' if v else 'NE'}" for s, v in has.items()))

    print("\n=== CONFLICTS (exactly one variant allowed) ===")
    for topic, variants in CONFLICTS.items():
        found = {label: cc.scan(docs, pat, live_only="WRONG" in label or "superseded" in label)
                 for label, pat in variants.items()}
        found = {k: v for k, v in found.items() if v}
        if len(found) > 1:
            fails += 1
            print(f"  FAIL  {topic}: {len(found)} variants coexist")
            for label, hits in found.items():
                print(f"          '{label}' in " + ", ".join(f"{k} x{v}" for k, v in hits.items()))
        elif found:
            label = next(iter(found))
            print(f"  OK    {topic}: '{label}' ({sum(found[label].values())} mentions)")
        else:
            print(f"  --    {topic}: not mentioned anywhere")

    print("\n=== REQUIRED VALUES ===")
    for topic, pat in SINGLE_VALUE.items():
        hits = cc.scan(docs, pat)
        if not hits:
            fails += 1
            print(f"  FAIL  {topic}: absent from the whole package")
        else:
            print(f"  OK    {topic}: {sum(hits.values())} mentions in {len(hits)} document(s)")

    print("\n=== BANNED TEXT ===")
    for topic, pat in BANNED.items():
        hits = cc.scan(docs, pat, live_only=True)
        if hits:
            fails += 1
            print(f"  FAIL  {topic}: " + ", ".join(f"{k} x{v}" for k, v in hits.items()))
        else:
            print(f"  OK    {topic}: gone")

    print(f"\nRESULT: {fails} failure(s)")
    return fails


if __name__ == "__main__":
    sys.exit(main())
