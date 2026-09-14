# -*- coding: utf-8 -*-
"""
Shared CAD scaffolding for the BS Sjednica (Bileća) tender drawings.

Layers, text styles, dimension styles and the title block ("Sastavnica") are
reproduced from the existing certified site project
`SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m`, whose profile was extracted to
`cad/style_profile.json`.  Following that project's convention, geometry is drawn
in model space in millimetres at 1:1 and the sheet frame is scaled up by the plot
scale, so a 1:50 A3 sheet is a 21000 x 14850 mm rectangle in model space.

The BH Telecom mark in the title block is traced from `cad/bht-logo.svg`
(cairosvg is unusable here - its cairo DLL is missing - so the path data is parsed
and the Béziers flattened directly).
"""
from __future__ import annotations

import os
import re

import ezdxf
from ezdxf.enums import TextEntityAlignment

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_LOGO = os.path.join(HERE, "bht-logo.svg")

BHT_ORANGE = 30          # ACI ~ #f5821f
A3_W, A3_H = 420.0, 297.0
MARGIN_L, MARGIN = 20.0, 10.0          # left margin is wider for binding
TB_W, TB_H = 180.0, 48.0               # title block, bottom right

# name -> (aci colour, linetype).  Names match the site project exactly so the
# sheets can be xref'd or copied into it without layer proliferation.
LAYERS = {
    "Okvir":          (3,   "Continuous"),   # sheet frame + title block
    "Tekst":          (253, "Continuous"),
    "Kote":           (7,   "Continuous"),
    "Kote blok":      (7,   "Continuous"),
    "Objekat":        (6,   "Continuous"),   # container, existing building
    "Konstrukcija":   (5,   "Continuous"),   # steelwork, supports
    "Panel":          (110, "Continuous"),   # PV modules
    "Kabal":          (7,   "Continuous"),
    "Osovina":        (6,   "CENTER"),
    "Orijentacija":   (1,   "Continuous"),   # north arrow
    "DEBELA":         (7,   "Continuous"),
    "pozicije":       (7,   "Continuous"),
    "Novi1":          (30,  "Continuous"),
    "plavi":          (5,   "Continuous"),
    # added for this package - none of these exist in the site project
    "Temelj":         (32,  "Continuous"),   # new reinforced concrete footings
    "Uzemljenje":     (2,   "DASHED"),       # earthing
    "Ograda":         (8,   "Continuous"),   # existing fence
    "Agregat":        (30,  "Continuous"),   # genset, fuel tank
    "Ventilacija":    (4,   "Continuous"),   # louvres, ducts, exhaust
    "Sema":           (7,   "Continuous"),   # single line diagram
    "Legenda":        (7,   "Continuous"),
    "Izvod":          (253, "Continuous"),   # leader callouts (line + label)
    "Kota_tekst":     (7,   "Continuous"),
    "Sakriveno":      (15,  "ACAD_ISO03W100"),
}

# text style -> font file, as used by the site project
STYLES = {
    "Standard": "times.ttf",
    "20":       "arial.ttf",
    "50":       "ARIALN.TTF",
    "RomanS":   "arial.ttf",
}

DIM_SCALES = (20, 30, 50, 100, 200)      # "M 20" ... "M 200"; M 30 is new


# --------------------------------------------------------------------------
# BH Telecom logo: SVG path data -> flattened polygons
# --------------------------------------------------------------------------
def _flatten_cubic(p0, p1, p2, p3, n=12):
    out = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        out.append((
            u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
            u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1],
        ))
    return out


def _parse_path(d):
    """Relative-only SVG path (m/c/l/h/v/z) -> list of point lists."""
    tokens = re.findall(r"([MmCcLlHhVvZz])|(-?\d*\.?\d+(?:e-?\d+)?)", d)
    subpaths, cur = [], []
    cx = cy = sx = sy = 0.0
    cmd = None
    nums = []

    def flush():
        nonlocal cur
        if len(cur) > 2:
            subpaths.append(cur)
        cur = []

    i = 0
    flat = [(a, b) for a, b in tokens]
    while i < len(flat):
        letter, num = flat[i]
        if letter:
            if letter in "Zz":
                flush()
                cx, cy = sx, sy
                cmd = None
                i += 1
                continue
            cmd = letter
            i += 1
            continue
        # collect the argument run for the current command
        nums = []
        while i < len(flat) and not flat[i][0]:
            nums.append(float(flat[i][1]))
            i += 1
        rel = cmd.islower()
        k = cmd.upper()
        j = 0
        while j < len(nums):
            if k == "M":
                x, y = nums[j], nums[j+1]; j += 2
                cx, cy = (cx + x, cy + y) if rel else (x, y)
                flush()
                sx, sy = cx, cy
                cur = [(cx, cy)]
                k = "L"          # subsequent pairs after moveto are lineto
            elif k == "L":
                x, y = nums[j], nums[j+1]; j += 2
                cx, cy = (cx + x, cy + y) if rel else (x, y)
                cur.append((cx, cy))
            elif k == "H":
                x = nums[j]; j += 1
                cx = cx + x if rel else x
                cur.append((cx, cy))
            elif k == "V":
                y = nums[j]; j += 1
                cy = cy + y if rel else y
                cur.append((cx, cy))
            elif k == "C":
                a, b, c, dd, e, f = nums[j:j+6]; j += 6
                if rel:
                    p1, p2, p3 = (cx+a, cy+b), (cx+c, cy+dd), (cx+e, cy+f)
                else:
                    p1, p2, p3 = (a, b), (c, dd), (e, f)
                cur.extend(_flatten_cubic((cx, cy), p1, p2, p3))
                cx, cy = p3
            else:
                j = len(nums)
    flush()
    return subpaths


def logo_polygons():
    """-> (polygons, width, height) in a y-up box anchored at (0,0)."""
    svg = open(SVG_LOGO, encoding="utf-8").read()
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    tr = re.search(r"matrix\(([^)]+)\)", svg)
    a, b, c, d, e, f = [float(v) for v in tr.group(1).split(",")]

    polys = []
    for m in re.finditer(r'<path\s+d="([^"]+)"\s+style="([^"]*)"', svg):
        fill = re.search(r"fill:(#[0-9a-fA-F]{6})", m.group(2))
        if not fill:
            continue
        white = fill.group(1).lower() == "#ffffff"
        for sp in _parse_path(m.group(1)):
            pts = []
            for x, y in sp:
                X = a * x + c * y + e
                Y = b * x + d * y + f
                pts.append((X, vb[3] - Y))       # SVG y-down -> CAD y-up
            polys.append((pts, white))
    return polys, vb[2], vb[3]


def draw_logo(msp, x, y, width, layer="Okvir"):
    """
    Place the BH Telecom mark with its lower-left corner at (x, y).
    The orange rounded rectangle is emitted first and the white glyphs after it,
    so viewers that honour creation order paint the mark correctly.
    """
    polys, w0, h0 = logo_polygons()
    s = width / w0
    for white in (False, True):                     # orange plate, then glyphs
        for pts, is_white in polys:
            if is_white is not white:
                continue
            p = [(x + px * s, y + py * s) for px, py in pts]
            color = 7 if white else BHT_ORANGE
            hatch = msp.add_hatch(color=color, dxfattribs={"layer": layer})
            hatch.paths.add_polyline_path(p, is_closed=True)
            msp.add_lwpolyline(p, close=True,
                               dxfattribs={"layer": layer, "color": color})
    return width, h0 * s


# --------------------------------------------------------------------------
# document setup
# --------------------------------------------------------------------------
def new_doc():
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4          # millimetres
    doc.header["$MEASUREMENT"] = 1       # metric

    for name, font in STYLES.items():
        if name in doc.styles:
            doc.styles.get(name).dxf.font = font
        else:
            doc.styles.add(name, font=font)

    for name, (color, ltype) in LAYERS.items():
        if ltype not in doc.linetypes:
            ltype = "Continuous"
        doc.layers.add(name, color=color, linetype=ltype)

    for s in DIM_SCALES:
        ds = doc.dimstyles.duplicate_entry("Standard", f"M {s}") \
             if f"M {s}" not in doc.dimstyles else doc.dimstyles.get(f"M {s}")
        ds.dxf.dimscale = float(s)       # matches the site project convention
        ds.dxf.dimtxt = 2.5
        ds.dxf.dimasz = 1.0
        ds.dxf.dimexe = 2.0
        ds.dxf.dimexo = 0.0
        ds.dxf.dimdec = 0
        ds.dxf.dimtxsty = "Standard"
        ds.dxf.dimlunit = 2
        ds.dxf.dimblk = "ARCHTICK"
    return doc


def _txt(msp, s, x, y, h, layer="Tekst", style="20", color=None,
         align=TextEntityAlignment.LEFT, rotation=0.0):
    e = msp.add_text(s, height=h, rotation=rotation,
                     dxfattribs={"layer": layer, "style": style,
                                 **({"color": color} if color else {})})
    e.set_placement((x, y), align=align)
    return e


# --------------------------------------------------------------------------
# sheet frame + title block
# --------------------------------------------------------------------------
def draw_frame(msp, scale, naziv, broj, razmjera, godina="2026.",
               objekat="BS SJEDNICA (Bileća) — autonomni hibridni sistem napajanja",
               faza="Tenderska dokumentacija — Prilog III",
               sifra="BHT-SJEDNICA-2026",
               projektant="Rusmir Skopljak, dipl. ing. el.",
               ovjerio="Rusmir Skopljak, dipl. ing. el."):
    """
    Draw an A3 frame and the BH Telecom title block, scaled by `scale`
    (the plot denominator), so the sheet lands in model-space millimetres.
    Returns the usable drawing window ((x0, y0), (x1, y1)) in model units.
    """
    S = float(scale)

    def X(v):
        return v * S

    # sheet edge and inner frame
    msp.add_lwpolyline([(0, 0), (X(A3_W), 0), (X(A3_W), X(A3_H)), (0, X(A3_H))],
                       close=True, dxfattribs={"layer": "Okvir", "color": 8})
    fx0, fy0 = X(MARGIN_L), X(MARGIN)
    fx1, fy1 = X(A3_W - MARGIN), X(A3_H - MARGIN)
    msp.add_lwpolyline([(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)],
                       close=True, dxfattribs={"layer": "Okvir", "lineweight": 50})

    # title block frame
    tx0, ty0 = fx1 - X(TB_W), fy0
    tx1, ty1 = fx1, fy0 + X(TB_H)
    msp.add_lwpolyline([(tx0, ty0), (tx1, ty0), (tx1, ty1), (tx0, ty1)],
                       close=True, dxfattribs={"layer": "Okvir", "lineweight": 50})

    # grid: horizontal rules, then verticals limited to the bands they split
    for r in (6.0, 14.0, 22.0, 30.0, 38.0):
        msp.add_line((tx0, ty0 + X(r)), (tx1, ty0 + X(r)),
                     dxfattribs={"layer": "Okvir"})
    for cx, lo, hi in ((118.0, 6.0, 22.0), (62.0, 0.0, 6.0), (118.0, 0.0, 6.0)):
        msp.add_line((tx0 + X(cx), ty0 + X(lo)), (tx0 + X(cx), ty0 + X(hi)),
                     dxfattribs={"layer": "Okvir"})

    def lbl(s, x, y):
        return _txt(msp, s, tx0 + X(x), ty0 + X(y), X(1.9),
                    layer="Okvir", color=8)

    def val(s, x, y, h=2.8):
        return _txt(msp, s, tx0 + X(x), ty0 + X(y), X(h),
                    layer="Tekst", color=7)

    # band 38..48 - logo and issuer
    draw_logo(msp, tx0 + X(4), ty0 + X(39.6), X(17))
    _txt(msp, "BH TELECOM d.d. SARAJEVO", tx0 + X(25), ty0 + X(43.4), X(3.0),
         layer="Tekst", color=7)
    _txt(msp, "Izvršna direkcija za tehnologiju i razvoj servisa",
         tx0 + X(25), ty0 + X(39.6), X(2.2), layer="Okvir", color=8)

    # bands 30..38, 22..30 - full width
    lbl("Investitor:", 3, 35.4);      val("BH Telecom d.d. Sarajevo, Franca Lehara 7, Sarajevo", 3, 31.6, 2.6)
    lbl("Objekat:", 3, 27.4);         val(objekat, 3, 23.6, 2.6)
    # band 14..22 - split at 118
    lbl("Faza:", 3, 19.4);            val(faza, 3, 15.6, 2.6)
    lbl("šifra projekta:", 121, 19.4); val(sifra, 121, 15.6, 2.6)
    # band 6..14 - split at 118
    lbl("Naziv crteža:", 3, 11.4);    val(naziv, 3, 7.4, 3.4)
    lbl("razmjera:", 121, 11.4);      val(razmjera, 121, 7.4, 3.4)
    # band 0..6 - split at 62 and 118
    lbl("Projektant:", 3, 4.2);       val(projektant, 3, 1.0, 2.3)
    # an empty `ovjerio` leaves the ruled field for a wet signature instead of naming
    # the designer as their own checker; the label stays so the field is still marked
    lbl("ovjerio:", 65, 4.2)
    if ovjerio:
        val(ovjerio, 65, 1.0, 2.3)
    lbl("godina / broj crteža:", 121, 4.2)
    val(f"{godina}    {broj}", 121, 1.0, 2.8)

    return (fx0, fy0 + X(TB_H)), (fx1, fy1)


def north_arrow(msp, x, y, size, plan_north=0.0):
    """Simple filled north arrow, `size` = overall height in model units.

    `plan_north` is the true bearing of the sheet's up direction, for a compound
    drawn square to the sheet but turned on site (Sjednica 45°, Hamzići 315°,
    Google Maps 11.09.2026). The arrow is turned by it, so it points at true
    north: counter-clockwise on the sheet by `plan_north` degrees.
    """
    from math import cos, radians, sin

    s = size
    c, sn = cos(radians(plan_north)), sin(radians(plan_north))

    def p(dx, dy):
        return (x + dx * c - dy * sn, y + dx * sn + dy * c)

    msp.add_lwpolyline([p(0, s), p(-s*0.22, -s*0.15), p(0, 0), p(s*0.22, -s*0.15)],
                       close=True, dxfattribs={"layer": "Orijentacija"})
    _txt(msp, "N", *p(0, s*1.08), s * 0.34, layer="Orijentacija",
         color=1, align=TextEntityAlignment.MIDDLE_CENTER)


def scale_bar(msp, x, y, scale, total_m=10, step_m=1):
    """Graphical scale bar; `total_m` metres long, drawn in model millimetres."""
    h = 1.6 * scale
    n = int(total_m / step_m)
    for i in range(n):
        x0 = x + i * step_m * 1000.0
        msp.add_lwpolyline([(x0, y), (x0 + step_m*1000, y),
                            (x0 + step_m*1000, y + h), (x0, y + h)],
                           close=True, dxfattribs={"layer": "Okvir"})
        if i % 2 == 0:
            msp.add_hatch(color=7, dxfattribs={"layer": "Okvir"}).paths.add_polyline_path(
                [(x0, y), (x0 + step_m*1000, y), (x0 + step_m*1000, y + h), (x0, y + h)])
        _txt(msp, f"{i*step_m}", x0, y - 2.6*scale, 2.0*scale,
             layer="Okvir", color=8, align=TextEntityAlignment.CENTER)
    _txt(msp, f"{total_m} m", x + total_m*1000, y - 2.6*scale, 2.0*scale,
         layer="Okvir", color=8, align=TextEntityAlignment.CENTER)


if __name__ == "__main__":
    doc = new_doc()
    msp = doc.modelspace()
    draw_frame(msp, 50, "Probni list — provjera okvira", "X-00", "1:50")
    out = os.path.join(HERE, "_frame_test.dxf")
    doc.saveas(out)
    polys, w, h = logo_polygons()
    print(f"logo: {len(polys)} polygons, viewBox {w:.1f} x {h:.1f}")
    print("layers:", len(doc.layers), "| dimstyles:",
          [d.dxf.name for d in doc.dimstyles])
    print("wrote", out)
