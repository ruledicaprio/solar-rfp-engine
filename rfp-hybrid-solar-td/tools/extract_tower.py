# -*- coding: utf-8 -*-
"""
Izvlači siluetu antenskog stuba iz ovjerenih DWG-ova u cad/tower_profile.json.

Listovi S-04 i H-06 (pogled sa jugozapada) crtaju stub kao pravu geometriju, a ne
kao shematski trapez. Geometrija je u ovjerenim projektima lokacija, na sloju
`Silueta stuba`:

    Sjednica  …/462 Graficki dio ANTENSKI STUB 38 m/01_ANTENSKI STUB 38 m.dwg
    Hamzići   …/462 Graficki dio ANTENSKI STUB 32 m/01_Dispozicija S32 m.dwg

Ovo se pokreće ručno i samo kad se ovjereni projekat promijeni. Rezultat je mali
JSON koji ide u git, pa build crteža ne traži ni ODA File Converter ni 232 MB
projekta lokacije — isti dogovor kao za site_geometry.json.

Na oba lista stub leži vodoravno, vrhom prema x = 0. Ovdje se uspravlja:

    z = x_baza − x        visina iznad donje ivice nogu
    u = y − y_osa         odstojanje od ose stuba

Kod Hamzića isti sloj nosi i tlocrte platformi, parkirane iznad pogleda. Odvajaju
se po y: pogled je cijeli ispod y = 41 500, tlocrti počinju na 42 131 (razmak od
1 985 mm, jedini takav u fajlu).
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

ODA = r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SITES = {
    "sjednica": {
        "cad": os.path.join(ROOT, "bht-sjednica-final-review", "cad"),
        "dwg": os.path.join(
            ROOT, "bht-sjednica-final-review",
            "SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m",
            "2 - ARHITEKTONSKO GRADJEVINSKI DIO", "6 Graficki dio",
            "462 Graficki dio ANTENSKI STUB 38 m", "01_ANTENSKI STUB 38 m.dwg"),
        "y_max": None,          # cijeli sloj je pogled
        "height_mm": 38000,
    },
    "hamzici": {
        "cad": os.path.join(ROOT, "hamzici-hybrid-solar", "cad"),
        "dwg": os.path.join(
            ROOT, "hamzici-hybrid-solar", "GP BS HAMZIĆI_Čitluk K2 i AS 36 m",
            "4 - ARHITEKTONSKO GRADJEVINSKI DIO", "6 Graficki dio",
            "462 Graficki dio ANTENSKI STUB 32 m", "01_Dispozicija S32 m.dwg"),
        "y_max": 41500,         # iznad toga su tlocrti platformi
        "height_mm": 32000,
    },
}
LAYER = "Silueta stuba"


def to_dxf(paths):
    tmp = tempfile.mkdtemp(prefix="tower_")
    src, dst = os.path.join(tmp, "in"), os.path.join(tmp, "out")
    os.makedirs(src)
    names = {}
    for i, p in enumerate(paths):
        if not os.path.exists(p):
            raise SystemExit(f"nedostaje ovjereni DWG: {p}")
        stem = f"t{i:02d}"
        shutil.copy(p, os.path.join(src, stem + ".dwg"))
        names[p] = os.path.join(dst, stem + ".dxf")
    r = subprocess.run([ODA, src, dst, "ACAD2018", "DXF", "0", "1"],
                       capture_output=True, text=True, timeout=1800)
    if not glob.glob(os.path.join(dst, "*.dxf")):
        raise SystemExit(f"ODA nije ništa proizveo.\n{r.stdout}\n{r.stderr}")
    return names


def polylines(dxf, y_max):
    """Otvoreni nizovi tačaka sa sloja siluete; samo geometrija, bez natpisa."""
    import ezdxf

    out = []
    for e in ezdxf.readfile(dxf).modelspace():
        if e.dxf.layer != LAYER:
            continue
        if e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points("xy")]
            if e.closed and pts:
                pts.append(pts[0])
        elif e.dxftype() == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        else:
            continue                      # MTEXT, ARC na ivicama — ne treba
        if len(pts) < 2:
            continue
        if y_max is not None and max(p[1] for p in pts) > y_max:
            continue                      # tlocrt platforme, ne pogled
        out.append(pts)
    return out


def build(site, cfg, dxf):
    pl = polylines(dxf, cfg["y_max"])
    if not pl:
        raise SystemExit(f"{site}: sloj {LAYER!r} je prazan")
    xs = [p[0] for s in pl for p in s]
    ys = [p[1] for s in pl for p in s]
    x_base, x_top = max(xs), min(xs)

    # osa stuba: sredina cijele siluete, koja je simetrična.  Ne sredina tačaka
    # na samoj bazi: kod Hamzića u pojasu od 50 mm na dnu ima tačaka samo jedna
    # noga, pa je stub ispadao pomaknut za pola baze udesno.
    y_axis = (min(ys) + max(ys)) / 2

    conv = [[[round(p[1] - y_axis, 1), round(x_base - p[0], 1)] for p in s]
            for s in pl]
    zs = [p[1] for s in conv for p in s]
    us = [p[0] for s in conv for p in s]
    top_band = [p[0] for s in conv for p in s if p[1] > max(zs) - 50]

    doc = {
        "_source": os.path.relpath(cfg["dwg"], ROOT).replace("\\", "/"),
        "_layer": LAYER,
        "_note": ("Silueta iz ovjerenog projekta lokacije, uspravljena: z je visina "
                  "iznad donje ivice nogu, u je odstojanje od ose stuba. Generisano "
                  "sa rfp-hybrid-solar-td/tools/extract_tower.py; ne uređivati ručno."),
        "height_mm": cfg["height_mm"],
        "drawn_height_mm": round(x_base - x_top, 1),
        "base_w_mm": round(max(us) - min(us), 1),
        "top_w_mm": round(max(top_band) - min(top_band), 1),
        "polylines": conv,
    }
    out = os.path.join(cfg["cad"], "tower_profile.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"  {site}: {len(conv)} polilinija, nacrtana visina "
          f"{doc['drawn_height_mm']:.0f} (projekat {cfg['height_mm']}), "
          f"baza {doc['base_w_mm']:.0f}, vrh {doc['top_w_mm']:.0f}"
          f"  -> {os.path.relpath(out, ROOT)}")


def main():
    """Bez argumenata obje lokacije; inače samo navedene (npr. `hamzici`)."""
    sites = {k: SITES[k] for k in (sys.argv[1:] or SITES)}
    names = to_dxf([c["dwg"] for c in sites.values()])
    for site, cfg in sites.items():
        build(site, cfg, names[cfg["dwg"]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
