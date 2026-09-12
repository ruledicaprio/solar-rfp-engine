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


def _label(e):
    t = e.dxftype()
    if t in ("TEXT", "MTEXT"):
        s = e.dxf.text if t == "TEXT" else e.plain_text()
        return f"{t} '{s[:50]}'"
    return f"{t} [{e.dxf.layer}]"


def _text_boxes(e, cache):
    """(label, (x0, y0, x1, y1)) for a TEXT, or for the text inside a DIMENSION."""
    if e.dxftype() == "TEXT":
        items = [e]
    elif e.dxftype() == "DIMENSION":
        items = [v for v in e.virtual_entities() if v.dxftype() in ("TEXT", "MTEXT")]
    else:
        return []
    out = []
    for it in items:
        b = bbox.extents([it], cache=cache if it is e else None)
        if not b.has_data:
            continue
        (x0, y0, _), (x1, y1, _) = b.extmin, b.extmax
        # shave a margin so glyphs that merely touch are not reported
        s = 0.12 * min(x1 - x0, y1 - y0)
        out.append((_label(it) if it is e else f"DIM '{_label(it)[6:]}",
                    (x0 + s, y0 + s, x1 - s, y1 - s)))
    return out


def layout_check(doc, sc):
    frame = getattr(doc, "hz_frame_handles", set())
    fx0, fy0 = MARGIN_L * sc, MARGIN * sc
    fx1, fy1 = (A3_W - MARGIN) * sc, (A3_H - MARGIN) * sc
    tb = ((A3_W - MARGIN - TB_W) * sc, MARGIN * sc,
          (A3_W - MARGIN) * sc, (MARGIN + TB_H) * sc)
    cache = bbox.Cache()
    outside, in_tb, boxes = [], [], []
    for e in doc.modelspace():
        if e.dxf.handle in frame:
            continue
        b = bbox.extents([e], cache=cache)
        if not b.has_data:
            continue
        (x0, y0, _), (x1, y1, _) = b.extmin, b.extmax
        if x0 < fx0 - 1 or y0 < fy0 - 1 or x1 > fx1 + 1 or y1 > fy1 + 1:
            outside.append(_label(e))
        if x1 > tb[0] + 1 and x0 < tb[2] - 1 and y1 > tb[1] + 1 and y0 < tb[3] - 1:
            in_tb.append(_label(e))
        boxes += _text_boxes(e, cache)
    overlaps = []
    for (la, a), (lb, b) in itertools.combinations(boxes, 2):
        if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
            overlaps.append(f"{la}  x  {lb}")
    return outside, in_tb, overlaps


def build(names, strict=False):
    os.makedirs(GRAFIKA, exist_ok=True)
    made, bad = [], 0
    print("DXF + extents checks:")
    for name in names:
        fn, sc = H.SHEETS[name]
        doc = fn()
        B.check_extents(doc, name, sc)          # hard gate: SystemExit if off the A3 sheet
        outside, in_tb, overlaps = layout_check(doc, sc)
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
