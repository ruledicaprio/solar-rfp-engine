# -*- coding: utf-8 -*-
"""
Builds the tender drawings for BS Sjednica (Bileća).

Drawing frame, layers, text styles and dimension styles come from `bht_frame.py`,
which mirrors the certified site project.  Existing-state geometry comes from
`site_geometry.json`, measured out of that project's own DWGs.  The new works
come from `design.json`, which carries the numbers settled by the three expert
review passes.

Sheets:
    S-01  Postojeće stanje                 1:50
    S-02  Buduće stanje                    1:50
    S-03  Presjek A-A                      1:30
    M-01  Agregat u kontejneru             1:25
    E-01  Jednopolna shema                 -

Model space is millimetres at 1:1; the sheet frame is scaled by the plot
denominator, following the site project's convention.

Drawing frame convention for these sheets: +X = EAST, +Y = NORTH.
"""
from __future__ import annotations

import json
import math
import os
import sys

import ezdxf
from ezdxf.enums import TextEntityAlignment as TA

from bht_frame import (A3_H, A3_W, MARGIN, MARGIN_L, TB_W, draw_frame, new_doc,
                       north_arrow, scale_bar, _txt)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
from paths import GRAFIKA as OUT                                    # noqa: E402

GEO = json.load(open(os.path.join(HERE, "site_geometry.json"), encoding="utf-8"))


def _design():
    p = os.path.join(HERE, "design.json")
    if not os.path.exists(p):
        raise SystemExit("design.json is missing - it is written from the expert findings")
    return json.load(open(p, encoding="utf-8"))


# --------------------------------------------------------------------------
# small drawing helpers
# --------------------------------------------------------------------------
def rect(msp, x, y, w, h, layer, color=None, close=True, lw=None):
    at = {"layer": layer}
    if color is not None:
        at["color"] = color
    if lw is not None:
        at["lineweight"] = lw
    return msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                              close=close, dxfattribs=at)


def hatch_rect(msp, x, y, w, h, layer, pattern="ANSI31", scale=200, color=8):
    ht = msp.add_hatch(color=color, dxfattribs={"layer": layer})
    ht.set_pattern_fill(pattern, scale=scale)
    ht.paths.add_polyline_path([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                               is_closed=True)
    return ht


def solid_rect(msp, x, y, w, h, layer, color):
    ht = msp.add_hatch(color=color, dxfattribs={"layer": layer})
    ht.paths.add_polyline_path([(x, y), (x + w, y), (x + w, y + h), (x, y + h)],
                               is_closed=True)
    return ht


def dim_h(msp, x1, x2, y, scale, above=True, text=None, off=None):
    """Horizontal linear dimension between x1 and x2 at height y."""
    off = off if off is not None else (3.0 * scale if above else -3.0 * scale)
    d = msp.add_linear_dim(base=(0, y + off), p1=(x1, y), p2=(x2, y),
                           dimstyle=f"M {int(scale)}",
                           text=text or "<>",
                           dxfattribs={"layer": "Kote"})
    d.render()
    return d


def dim_v(msp, y1, y2, x, scale, text=None, off=None):
    off = off if off is not None else 3.0 * scale
    d = msp.add_linear_dim(base=(x + off, 0), p1=(x, y1), p2=(x, y2),
                           angle=90, dimstyle=f"M {int(scale)}",
                           text=text or "<>", dxfattribs={"layer": "Kote"})
    d.render()
    return d


def leader(msp, tip, text, dx, dy, scale, layer="Izvod", h=2.2):
    """Simple leader: tip -> elbow -> horizontal tail, text at the tail end."""
    ex, ey = tip[0] + dx, tip[1] + dy
    tail = 2.0 * scale * (1 if dx >= 0 else -1)
    msp.add_lwpolyline([tip, (ex, ey), (ex + tail, ey)],
                       dxfattribs={"layer": layer, "color": 8})
    msp.add_circle(tip, 0.4 * scale, dxfattribs={"layer": layer, "color": 8})
    _txt(msp, text, ex + tail + (0.6 * scale if dx >= 0 else -0.6 * scale),
         ey - 0.35 * h * scale, h * scale, layer=layer, color=7,
         align=TA.LEFT if dx >= 0 else TA.RIGHT)


def legend(msp, x, y, scale, rows, title="LEGENDA", cols=1, col_w=None):
    """rows = [(color, label), ...]; x,y = top-left in model units."""
    step = 3.4 * scale
    col_w = col_w or 52.0 * scale
    _txt(msp, title, x, y, 2.8 * scale, layer="Legenda", color=7)
    top = y - 3.4 * scale
    per = -(-len(rows) // cols)
    for i, (color, label) in enumerate(rows):
        cx = x + (i // per) * col_w
        yy = top - (i % per) * step
        solid_rect(msp, cx, yy, 3.2 * scale, 1.7 * scale, "Legenda", color)
        rect(msp, cx, yy, 3.2 * scale, 1.7 * scale, "Legenda", color=8)
        _txt(msp, label, cx + 4.2 * scale, yy + 0.1 * scale, 2.0 * scale,
             layer="Legenda", color=7)
    return top - per * step


def note_block(msp, x, y, scale, title, lines, h=2.1):
    # colour 7, not the grey 8 it used to be: at note size the grey printed too
    # faint to read on a plotted A3 sheet
    _txt(msp, title, x, y, 2.6 * scale, layer="Tekst", color=7)
    yy = y - 2.4 * scale
    for ln in lines:
        _txt(msp, ln, x, yy, h * scale, layer="Tekst", color=7)
        yy -= h * 1.45 * scale
    return yy


# --------------------------------------------------------------------------
# shared site plan drawing (used by S-01 and S-02)
# --------------------------------------------------------------------------
def site_plan(msp, ox, oy, scale, future=False, d=None):
    """
    Draw the existing compound with its SW fence corner at (ox, oy).
    +X = EAST, +Y = NORTH.  Returns a dict of key coordinates.
    """
    F = GEO["fence"]["size"][0]                 # 5500
    S = GEO["slab"]["size"][0]                  # 5400
    off = GEO["fence"]["offset_outside_slab"]   # 50
    CW, CH = 3005, 2300                         # container E-W, N-S
    t = GEO["container"]["wall_panel_thickness"]

    sx, sy = ox + off, oy + off                 # slab SW corner
    cx = sx + (S - CW) / 2.0                    # container SW corner
    cy = sy + (S - CH) / 2.0

    # --- parcel boundary (~150 m2 leased) --------------------------------
    # The plot is not centred on the compound: the compound sits near its north
    # edge, which is what leaves the open ground to the south (the front area)
    # for the PV array.
    pw, ph = 16000, 9400
    px, py = ox + F / 2 - pw / 2, oy + F + 100 - ph
    msp.add_lwpolyline([(px, py), (px + pw, py), (px + pw, py + ph), (px, py + ph)],
                       close=True,
                       dxfattribs={"layer": "Sakriveno", "color": 8})
    _txt(msp, "GRANICA ZAKUPLJENE PARCELE  ≈150 m²  (dio k.č. 1/1, k.o. Granica 2)",
         px + 200, py + ph - 700, 2.0 * scale, layer="Tekst", color=8)

    # --- existing ring earth --------------------------------------------
    e = 700
    msp.add_lwpolyline([(ox - e, oy - e), (ox + F + e, oy - e),
                        (ox + F + e, oy + F + e), (ox - e, oy + F + e)],
                       close=True, dxfattribs={"layer": "Uzemljenje"})

    # --- slab and fence --------------------------------------------------
    solid_rect(msp, sx, sy, S, S, "Objekat", 254)
    rect(msp, sx, sy, S, S, "Objekat", color=8)
    rect(msp, ox, oy, F, F, "Ograda", color=8, lw=50)

    # gate on the EAST fence, 1000 clear
    gw = GEO["fence"]["gate"]["clear_width"]
    gy = oy + F / 2 - gw / 2
    msp.add_lwpolyline([(ox + F, gy), (ox + F, gy + gw)],
                       dxfattribs={"layer": "Ograda", "color": 0})
    msp.add_arc(center=(ox + F, gy), radius=gw, start_angle=0, end_angle=90,
                dxfattribs={"layer": "Ograda", "color": 8})
    msp.add_line((ox + F, gy), (ox + F + gw, gy),
                 dxfattribs={"layer": "Ograda", "color": 8})

    # --- container with 60 mm sandwich walls -----------------------------
    rect(msp, cx, cy, CW, CH, "Objekat", color=6, lw=50)
    rect(msp, cx + t, cy + t, CW - 2 * t, CH - 2 * t, "Objekat", color=6)
    for hx, hy, hw, hh in ((cx, cy, CW, t), (cx, cy + CH - t, CW, t),
                           (cx, cy + t, t, CH - 2 * t),
                           (cx + CW - t, cy + t, t, CH - 2 * t)):
        solid_rect(msp, hx, hy, hw, hh, "Objekat", 8)

    # door in the EAST wall, opens outward
    dw = 900
    dy0 = cy + CH / 2 - dw / 2
    msp.add_lwpolyline([(cx + CW - t, dy0), (cx + CW, dy0),
                        (cx + CW, dy0 + dw), (cx + CW - t, dy0 + dw)],
                       close=True, dxfattribs={"layer": "Objekat", "color": 0})
    msp.add_line((cx + CW, dy0), (cx + CW + dw, dy0),
                 dxfattribs={"layer": "Objekat", "color": 8})
    msp.add_arc(center=(cx + CW, dy0), radius=dw, start_angle=0, end_angle=90,
                dxfattribs={"layer": "Objekat", "color": 8})

    # --- tower legs: 4200 x 4200 base, container sits between them -------
    T = GEO["tower"]["base"][0]
    tcx, tcy = sx + S / 2, sy + S / 2
    legs = [(tcx - T / 2, tcy - T / 2), (tcx + T / 2, tcy - T / 2),
            (tcx + T / 2, tcy + T / 2), (tcx - T / 2, tcy + T / 2)]
    for lx, ly in legs:
        solid_rect(msp, lx - 130, ly - 130, 260, 260, "Konstrukcija", 5)
        rect(msp, lx - 130, ly - 130, 260, 260, "Konstrukcija", color=5)
    msp.add_lwpolyline(legs + [legs[0]], close=False,
                       dxfattribs={"layer": "Osovina", "color": 8})

    # --- outdoor cabinets on the NORTH side -------------------------------
    # TWO cabinets stand here and both must be drawn: the hybrid power cabinet
    # ICC360-HA1-C1 (per the Huawei quotation, replacing the ICC330-H1 this used
    # to name) and the existing TK equipment cabinet MTS9302A, which is a
    # separate procurement and never went away. Rev 7 dropped the second box by
    # mistake when the pair collapsed to one name.
    cab = [("ICC360-HA1-C1", 650, 650), ("MTS9302A", 600, 600)]
    bx = cx + 250
    for name, w, h in cab:
        by = cy + CH + 180
        rect(msp, bx, by, w, h, "Novi1", color=30, lw=35)
        solid_rect(msp, bx, by, w, h, "Novi1", 30)
        bx += w + 220

    return {"slab": (sx, sy, S), "cont": (cx, cy, CW, CH), "fence": (ox, oy, F),
            "tower_c": (tcx, tcy), "parcel": (px, py, pw, ph),
            "gate_y": gy, "door_y": dy0}


# --------------------------------------------------------------------------
# S-01  Postojeće stanje
# --------------------------------------------------------------------------
def sheet_s01():
    SC = 50
    doc = new_doc()
    msp = doc.modelspace()
    (wx0, wy0), (wx1, wy1) = draw_frame(
        msp, SC,
        naziv="Situacija — POSTOJEĆE STANJE",
        broj="S-01", razmjera="1:50")

    # parcel is placed first, then the compound is derived from it, so the
    # 16.00 x 9.40 m plot fills the drawing window at 1:50
    PX, PY = 2600, 4500
    ox, oy = PX + 8000 - 2750, PY + 4700 - 2750
    k = site_plan(msp, ox, oy, SC)
    sx, sy, S = k["slab"]
    cx, cy, CW, CH = k["cont"]
    F = k["fence"][2]
    px, py, pw, ph = k["parcel"]

    # dimensions
    dim_h(msp, ox, ox + F, oy + F, SC, off=900)
    dim_v(msp, sy, sy + S, sx + S, SC, off=900)
    dim_h(msp, cx, cx + CW, cy, SC, off=-1100)
    dim_v(msp, cy, cy + CH, cx, SC, off=-1100)
    dim_h(msp, px, px + pw, py, SC, off=-1400)
    dim_v(msp, py, py + ph, px + pw, SC, off=1400)

    # annotation - leaders aim into the free strips west and east of the compound
    leader(msp, (cx + CW / 2, cy + CH / 2), "postojeći kontejner za TK opremu",
           -3400, -2400, SC)
    leader(msp, (cx + CW + 350, cy + CH / 2 + 250),
           "ULAZNA VRATA 900 × 2000 mm (ISTOČNA strana)", 2100, 1250, SC)
    leader(msp, (cx + 700, cy + CH + 480),
           "vanjski ormari (SI): Huawei ICC360-HA1-C1 i MTS9302A",
           -3400, 1750, SC)
    leader(msp, (k["tower_c"][0] - 2100, k["tower_c"][1] - 2100),
           "noge rešetkastog antenskog stuba h=38 m,", -3050, -1450, SC)
    _txt(msp, "baza 4,20 × 4,20 m", k["tower_c"][0] - 5250,
         k["tower_c"][1] - 3900, 2.2 * SC, layer="Tekst", color=7, align=TA.RIGHT)
    leader(msp, (ox + F + 500, oy + F / 2 - 500),
           "KAPIJA, svijetla širina 1,00 m", 1900, -1600, SC)
    leader(msp, (ox - 700, oy + F - 900),
           "postojeći prstenasti uzemljivač Fe/Zn 25×4 mm", -2300, 900, SC)

    _txt(msp, "slobodna površina parcele — prostor za buduće nosače FN panela",
         ox + F / 2, py + 750, 2.2 * SC, layer="Tekst", color=8, align=TA.CENTER)
    _txt(msp, "J U G O Z A P A D", ox + F / 2, py - 1900, 3.2 * SC, layer="Orijentacija",
         color=1, align=TA.CENTER)

    north_arrow(msp, 19500, 11700, 1700,
                plan_north=_design()["orientation"]["plan_north_bearing_deg"])
    scale_bar(msp, 1300, 3700, SC, total_m=5, step_m=1)

    legend(msp, 1300, 3050, SC, [
        (8,   "postojeća ograda h=2,10 m sa kapijom (svijetla širina 1,00 m)"),
        (254, "postojeća AB temeljna ploča 5,40 × 5,40 m"),
        (6,   "postojeći kontejner za TK opremu — vrata na JI"),
        (5,   "noge antenskog stuba, baza 4,20 × 4,20 m"),
        (30,  "vanjski ormari: ICC360-HA1-C1 (hibridni sistem) i MTS9302A (TK)"),
        (2,   "postojeći prstenasti uzemljivač Fe/Zn 25×4 mm"),
    ])

    note_block(msp, 6400, 3950, SC, "NAPOMENA:", [
        "Geometrija preuzeta iz ovjerenog projekta lokacije",
        "(SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m, 01 Situacija 1_200).",
    ])
    return doc


SHEETS = {"S-01": sheet_s01}

# S-02 / S-03 / M-01 / E-01 live in sheets_new.py; they reuse the helpers above
# so every sheet shares one style definition.
import sheets_new                                                   # noqa: E402
SHEETS.update(sheets_new.register(sys.modules[__name__]))


def check_extents(doc, name, scale):
    """Nothing may be drawn outside the A3 sheet.

    export.py plots with fit_page=True, so content beyond the frame does not spill
    off the page - it silently shrinks the whole sheet instead, and the drawing
    then prints at some scale other than the one in the title block. That is how
    M-01 and S-03 stopped being true A3 without anyone noticing, so it is checked
    here rather than left to the eye.
    """
    w, h = A3_W * scale, A3_H * scale
    xs, ys = [], []
    for e in doc.modelspace():
        t = e.dxftype()
        if t == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points()]
        elif t == "LINE":
            pts = [(e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)]
        elif t in ("TEXT", "CIRCLE"):
            a = e.dxf.insert if t == "TEXT" else e.dxf.center
            pts = [(a.x, a.y)]
        else:
            continue
        xs += [p[0] for p in pts]
        ys += [p[1] for p in pts]
    if not xs:
        return
    bad = []
    if min(xs) < -1 or max(xs) > w + 1:
        bad.append(f"x {min(xs):.0f}..{max(xs):.0f} vs 0..{w:.0f}")
    if min(ys) < -1 or max(ys) > h + 1:
        bad.append(f"y {min(ys):.0f}..{max(ys):.0f} vs 0..{h:.0f}")
    if bad:
        raise SystemExit(f"{name}: content outside the A3 sheet — " + "; ".join(bad))


SHEET_SCALE = {"S-01": 50, "S-02": 50, "S-03": 30, "M-01": 25, "E-01": 50}


def build(names=None):
    os.makedirs(OUT, exist_ok=True)
    made = []
    for name in (names or SHEETS):
        doc = SHEETS[name]()
        check_extents(doc, name, SHEET_SCALE[name])
        p = os.path.join(OUT, f"{name}.dxf")
        doc.saveas(p)
        made.append(p)
        print("wrote", p)
    return made


if __name__ == "__main__":
    import sys
    build(sys.argv[1:] or None)
