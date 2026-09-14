# -*- coding: utf-8 -*-
"""
Builds the BS Hamzići (Čitluk) tender drawings H-01 … H-05 into
hamzici-hybrid-solar/TD-OUTPUT/grafika/:

    sheets_hamzici.py -> DXF -> extents checks -> DWG AC1024 (ODA) -> verify
                      -> A3 PDF

The export chain is the Sjednica one (bht-sjednica-final-review/cad/export.py)
with its module-level DWGDIR pointed at this site's grafika folder, and the hard
extents gate is its build_drawings.check_extents.  layout_check() below is
stricter: nothing but the frame may leave the inner drawing frame or enter the
title block, and no two texts may overlap.

    python build_hamzici.py               all five sheets
    python build_hamzici.py H-02 H-04     some of them
    python build_hamzici.py --dxf-only    skip DWG / PDF
    python build_hamzici.py --strict      layout warnings fail the build
"""
from __future__ import annotations

import itertools
import os
import sys

# never write __pycache__ into the read-only Sjednica cad folder
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sheets_hamzici as H     # noqa: E402  (also puts the Sjednica cad folder on sys.path)
import build_drawings as B     # noqa: E402
import export as X             # noqa: E402
from bht_frame import A3_H, A3_W, MARGIN, MARGIN_L, TB_H, TB_W   # noqa: E402
from ezdxf import bbox         # noqa: E402

GRAFIKA = os.path.join(os.path.dirname(HERE), "TD-OUTPUT", "grafika")


def build(names, strict=False):
    os.makedirs(GRAFIKA, exist_ok=True)
    made, bad = [], 0
    print("DXF + extents checks:")
    for name in names:
        fn, sc = H.SHEETS[name]
        doc = fn()
        B.check_extents(doc, name, sc)          # hard gate: SystemExit if off the A3 sheet
        outside, in_tb, overlaps = B.layout_check(doc, sc)
        n = len(outside) + len(in_tb) + len(overlaps)
        bad += n
        print(f"  {'OK ' if not n else 'WARN'} {name}  1:{sc}  check_extents OK  "
              f"outside-frame={len(outside)}  in-title-block={len(in_tb)}  "
              f"text-overlaps={len(overlaps)}")
        for tag, rows in (("outside", outside), ("title block", in_tb),
                          ("overlap", overlaps)):
            for r in rows[:12]:
                print(f"       {tag}: {r}")
        p = os.path.join(GRAFIKA, f"{name}.dxf")
        doc.saveas(p)
        made.append(p)
    # tank vent / ICC360 / exhaust rules (raises if one is broken)
    r = H.site_checks()
    print(f"  site checks OK: vent→exhaust {r['vent_exhaust'] / 1000:.2f} m, "
          f"vent→intake {r['vent_intake'] / 1000:.2f} m, vent→ICC360 {r['vent_icc360'] / 1000:.2f} m "
          f"(horizontal), exhaust→intake {r['exhaust_intake'] / 1000:.2f} m, "
          f"PV→JZ fence {r['array_fence'] / 1000:.2f} m, PV→JZ wall {r['wall_array'] / 1000:.2f} m, "
          f"in front of ICC360 {r['icc360_front'] / 1000:.2f} m / MTS {r['mts_front'] / 1000:.2f} m")
    if strict and bad:
        raise SystemExit(f"{bad} layout warnings (--strict)")
    return made


def main(argv):
    flags = {a for a in argv if a.startswith("--")}
    names = [a for a in argv if not a.startswith("--")] or list(H.SHEETS)
    unknown = [n for n in names if n not in H.SHEETS]
    if unknown:
        raise SystemExit(f"unknown sheet(s): {unknown}; known: {list(H.SHEETS)}")
    build(names, strict="--strict" in flags)
    if "--dxf-only" in flags:
        return 0
    X.DWGDIR = GRAFIKA          # export.py reads and writes its module-level DWGDIR
    print()
    return X.main(names)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
