# -*- coding: utf-8 -*-
"""
Tender drawings for BS Hamzići (Čitluk), in the style of the BS Sjednica package.

    H-01  Situacija — postojeće stanje              1:100
    H-02  Situacija — buduće stanje                 1:100
    H-03  Presjek A–A kroz FN polje                 1:30
    H-04  Agregat u kontejneru — osnova i presjek   1:25
    H-05  Jednopolna šema novog GRO                 —

Frame, title block, layers, text and dimension styles are the Sjednica ones
(bht-sjednica-final-review/cad/bht_frame.py) and so are the drawing helpers
(build_drawings.py: rect, hatch_rect, solid_rect, dim_h, dim_v, leader, legend,
note_block).  Both modules are imported, never copied.  build_drawings loads the
Sjednica site_geometry.json when it is imported; that GEO is never used here.

S-03, M-01 and E-01 in sheets_new.py are closures with the Sjednica values
written into them - fence 2100 mm, the Sjednica 38 m tower taper, a container
lying E-W with its door on the east wall, the Sjednica title block - so none of
them can be called with a patched design dict.  H-03, H-04 and H-05 are
equivalents of them, with every Hamzići coordinate derived from this folder's
design.json and site_geometry.json.

Frame convention: slab-local millimetres, origin = the plan SW corner of the
existing 5400 x 5400 slab, +X = plan east, +Y = plan north.  The compound is
drawn square to the sheet, and plan north is TRUE NORTH-WEST (Google Maps,
Investor 11.09.2026): plan N / E / S / W are the true SZ / SI / JI / JZ sides
and the north arrow is turned 45°.  In the code NORTH / SOUTH / EAST / WEST
mean the plan sides; every text on the sheets names the true side (SIDE).  The
certified 2017 drawing is rotated about 180° against the site.
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SJ_CAD = os.path.join(os.path.dirname(os.path.dirname(HERE)),
                      "bht-sjednica-final-review", "cad")
if SJ_CAD not in sys.path:
    sys.path.insert(0, SJ_CAD)

from ezdxf.enums import TextEntityAlignment as TA                  # noqa: E402

from bht_frame import (A3_H, A3_W, MARGIN, MARGIN_L, TB_H, TB_W,   # noqa: E402
                       draw_frame, new_doc, north_arrow, scale_bar, _txt)
import build_drawings as B                                          # noqa: E402

rect, solid_rect, hatch_rect = B.rect, B.solid_rect, B.hatch_rect
dim_h, dim_v, leader = B.dim_h, B.dim_v, B.leader
legend, note_block = B.legend, B.note_block


def _load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return json.load(fh)


GEO = _load("site_geometry.json")
D = _load("design.json")

# --------------------------------------------------------------------------
# Values the two JSON files do not carry.  Each one is stated on the sheet that
# depends on it and listed in the build report.
# --------------------------------------------------------------------------
ARRAY_GAP = 400          # clear gap between stands (4 x 2278 + 3 x 400 = 10 312)
MIN_CLEAR = 100          # strips must stay >= ~0,1 m off the slab and inside the lease
FRAME_W = 740            # load-spreading frame under the 620 mm skid (as Sjednica M-01)
FRAME_H = 60             # its height, drawn schematically in section 1-1
PLENUM = 120             # radiator face -> inner face of the south wall (Sjednica M-01 gap)
DIS_Z0 = 300             # bottom of the combined Stulz discharge opening (to be measured)
HOOD_W, HOOD_D = 700, 600   # deflector hood over the discharge, outside the south wall
HOOD_Z = 1300            # its top louvre: the warm air leaves UPWARDS, not onto the PV array
LEG_CLEAR = 1000         # hood -> south tower legs, minimum
INTAKE_Y = 1500          # intake centre on the SI (plan-east) wall: alternator end, south of the tray
EXH_X = 250              # exhaust through the JI (plan-south) wall, in the JZ passage west of the hood
EXH_Y = 1000             # engine outlet, container-relative Y (schematic)
EXH_Z = 2300             # exhaust "≈+2,30 m", under the +3,0 m platform
EXH_OUT = 400            # exhaust pipe projects beyond the JI wall
GRO_W, GRO_D, GRO_H = 500, 250, 800   # the north wall west of the door is only 595 mm
GRO_Z = 1000             # underside of the GRO (section 1-1)
FAN_D = 315              # room fan Ø315
FAN_X = 1850             # room fan centre on the JI (plan-south) wall, east of the hood
FAN_Z = 1950             # underside of the fan ("gore")
DCB_W, DCB_H, DCB_D = 300, 200, 150   # DC razvod -48 V box (coordinator: ≈300 × 200 × 150)
DCB_GAP = 120            # door's east jamb -> DC razvod box
DCB_Z = 1600             # underside of the DC razvod box
SLAB_T = 300             # slab thickness drawn in section A-A (not in the inputs)
EARTH_RINGS = tuple(GEO["earth_rings"]["offset_from_slab_mm"])    # 3.6.9, at 0,8 m
TERRAIN = GEO["terrain"]["level_mm"]                               # -200 vs slab top
FENCE_ABOVE_GROUND = GEO["fence"]["height"] - TERRAIN              # 1800 + 200
# from the terrain; design.json array.above_fence carries the same figure
PV_OVER_FENCE = D["array"]["top_edge"] - FENCE_ABOVE_GROUND        # 934
PLAN_NORTH = GEO["orientation"]["plan_north_bearing_deg"]          # 315: plan up = true NW
SIDE = {"N": "SZ", "E": "SI", "S": "JI", "W": "JZ"}                # plan side -> true side
CAB_FRONT_CLEAR = 600    # free space in front of an outdoor cabinet (door side)
if SIDE != {k[5:6].upper(): v for k, v in GEO["orientation"]["sides"].items()}:
    raise SystemExit("SIDE disagrees with site_geometry.json orientation.sides")

OBJEKAT = "BS HAMZIĆI (ČITLUK) — autonomni hibridni sistem napajanja"
SIFRA = "BHT-HAMZICI-2026"


def minus(v, nd=2):
    """-200 -> '−0,20' with a true minus sign."""
    return ("−" if v < 0 else "+") + dec(abs(v), nd)


def site_checks():
    """Tank vent and outdoor-cabinet rules set by the coordinator (11.09.2026).

    Vent >= 3 m straight line from the exhaust termination and from the intake
    louvre centre, >= 1 m horizontally from the ICC360, below the +3,0 platform
    and clear of the door swing.  ICC360 and MTS inside the fence on the JZ side
    (Investor 11.09.2026), clear of the tower legs and of each other, with
    >= 0,6 m free in front of them.  Returns the distances; raises SystemExit if
    a rule is broken.
    """
    L = interior()
    cx0, cy0 = GEO["container"]["origin"]
    E = (cx0 + L["exh_x"], cy0 - EXH_OUT, EXH_Z)
    I = (cx0 + L["cw"], cy0 + sum(L["intake"]) / 2, sum(L["intake_z"]) / 2)
    tv = GEO["tank_vent"]
    V = (*tv["termination"], tv["termination_z_mm"])
    (ix, iy), (iw, ih) = GEO["icc360"]["footprint"]["origin"], GEO["icc360"]["footprint"]["size"]
    dx = max(ix - V[0], 0, V[0] - (ix + iw))
    dy = max(iy - V[1], 0, V[1] - (iy + ih))
    r = {"vent_exhaust": math.dist(V, E), "vent_intake": math.dist(V, I),
         "vent_icc360": math.hypot(dx, dy), "exhaust_intake": math.dist(E, I)}
    hx, hy, hw, hd = L["hood"]
    lf = GEO["tower"]["leg_footprint"][0]
    legs = GEO["tower"]["legs_centres"]
    r["hood_leg"] = min(
        math.hypot(max(lx_ - lf / 2 - (cx0 + hx + hw), 0, cx0 + hx - (lx_ + lf / 2)),
                   max(ly_ - lf / 2 - (cy0 + hy + hd), 0, cy0 + hy - (ly_ + lf / 2)))
        for lx_, ly_ in legs)
    A = array_layout()
    fence_x = GEO["fence"]["origin"][0]
    edge = A["fx0"] + A["proj"]                   # the PV field's high (JZ-fence) edge
    r["array_fence"] = fence_x - edge
    r["wall_array"] = cx0 - edge
    bad = []
    if r["hood_leg"] < LEG_CLEAR:
        bad.append("deflector hood closer than 1 m to a tower leg")
    if r["vent_exhaust"] < 3000 or r["vent_intake"] < 3000:
        bad.append("tank vent closer than 3 m to the exhaust or the intake")
    if r["vent_icc360"] < 1000:
        bad.append("tank vent closer than 1 m to the ICC360")
    if V[2] >= GEO["tower"]["platforms_m"][0] * 1000:
        bad.append("tank vent reaches the +3,0 m platform")
    if r["exhaust_intake"] < 3000:
        bad.append("exhaust termination closer than 3 m to the intake")
    # the door hinges on its east jamb and swings out to the west (plan)
    (dhx, dhy), op = GEO["container"]["door"]["hinge"], GEO["container"]["door"]["opening"]
    if V[0] <= dhx and V[1] >= dhy and math.hypot(V[0] - dhx, V[1] - dhy) < op:
        bad.append("tank vent stand-pipe inside the door swing")
    boxes = {}
    for key in ("icc360", "mts"):
        cab = GEO[key]
        (bx, by), (bw, bh) = cab["footprint"]["origin"], cab["footprint"]["size"]
        boxes[key] = (bx, by, bw, bh)
        for lx_, ly_ in legs:
            if bx < lx_ + lf / 2 and lx_ - lf / 2 < bx + bw and by < ly_ + lf / 2 \
                    and ly_ - lf / 2 < by + bh:
                bad.append(f"{key} overlaps a tower leg")
        if bx < fence_x + 50 or bx + bw > cx0:
            bad.append(f"{key} not between the JZ fence and the container")
        r[f"{key}_front"] = cx0 - (bx + cab["size_mm"]["D"])
        if r[f"{key}_front"] < CAB_FRONT_CLEAR:
            bad.append(f"less than {CAB_FRONT_CLEAR} mm in front of the {key}")
    (ax, ay, aw, ah), (mx, my, mw, mh) = boxes["icc360"], boxes["mts"]
    if ax < mx + mw and mx < ax + aw and ay < my + mh and my < ay + ah:
        bad.append("ICC360 and MTS overlap")
    if bad:
        raise SystemExit("site checks: " + "; ".join(bad))
    return r


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def dec(v, nd=2):
    """millimetres -> metres with a decimal comma: 1800 -> '1,80'."""
    return f"{v / 1000:.{nd}f}".replace(".", ",")


def mmc(v):
    """millimetres, with a decimal comma only when needed: 137.5 -> '137,5'."""
    return f"{v:.0f}" if abs(v - round(v)) < 1e-6 else f"{v:.1f}".replace(".", ",")


def _sheet(sc, naziv, broj, razmjera):
    doc = new_doc()
    msp = doc.modelspace()
    draw_frame(msp, sc, naziv=naziv, broj=broj, razmjera=razmjera,
               objekat=OBJEKAT, sifra=SIFRA)
    name = f"M {int(sc)}"
    if name not in doc.dimstyles:
        # bht_frame defines M 20/30/50/100/200 only; without this a 1:25 sheet's
        # dimensions fall back to 'Standard' and print 0,1 mm high (Sjednica M-01
        # carries exactly that defect)
        ds = doc.dimstyles.duplicate_entry("M 20", name)
        ds.dxf.dimscale = float(sc)
    # everything drawn so far is frame + title block; the build's layout check
    # skips these entities
    doc.hz_frame_handles = {e.dxf.handle for e in msp}
    return doc, msp


def ltype(e, name, sc, k=3.0):
    """Give an entity a linetype that actually shows on the plot.

    The ezdxf patterns are a few model units long, so at 1:100 they plot as a
    solid line unless scaled - the Sjednica ring earth printed solid for exactly
    that reason.  (ACAD_ISO03W100, the 'Sakriveno' layer's type, is not loaded by
    new_doc, so that layer falls back to Continuous and needs this as well.)
    """
    e.dxf.linetype = name
    e.dxf.ltscale = k * sc
    return e


def lead(msp, tip, text, elbow, sc, h=2.2):
    """leader() with an absolute elbow point instead of an offset."""
    leader(msp, tip, text, elbow[0] - tip[0], elbow[1] - tip[1], sc, h=h)


def arrow(msp, pts, color=4, size=160, layer="Ventilacija", lw=35):
    """Polyline with a filled arrow head at its last point (as Sjednica M-01)."""
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer, "color": color,
                                        "lineweight": lw})
    (x1, y1), (x0, y0) = pts[-1], pts[-2]
    ang = math.atan2(y1 - y0, x1 - x0)
    a1 = (x1 - size * math.cos(ang - 0.42), y1 - size * math.sin(ang - 0.42))
    a2 = (x1 - size * math.cos(ang + 0.42), y1 - size * math.sin(ang + 0.42))
    msp.add_solid([a1, (x1, y1), a2], dxfattribs={"layer": layer, "color": color})


def dim_free(msp, p1, p2, base, sc, angle=0, text="<>", loc=None):
    """Linear dimension between two arbitrary points (optional text location)."""
    kw = {"location": loc} if loc is not None else {}
    d = msp.add_linear_dim(base=base, p1=p1, p2=p2, angle=angle,
                           dimstyle=f"M {int(sc)}", text=text,
                           dxfattribs={"layer": "Kote"}, **kw)
    d.render()
    return d


# --------------------------------------------------------------------------
# layouts shared between sheets, so the plan, the section and the detail can
# never drift apart (the Sjednica S-02 / M-01 pair did, twice)
# --------------------------------------------------------------------------

def strip_w_txt(fnd):
    """Strip width for a callout: one figure for the constant section adopted on the
    reviewer's comment (27.08.2026), top/base only if a taper is ever reinstated."""
    swt, swb = fnd["strip_w_top"], fnd["strip_w_base"]
    return f"{swt}" if swt == swb else f"{swt}/{swb}"

def array_layout():
    """PV stands and their strips in the true-SW band (plan west), slab-local mm.

    One row of separate stands along the band (plan Y), each facing true SW
    (plan -X): the low edge toward the lease line, the high edge toward the JZ
    fence.  The strips run across the band (plan X), two under each stand.  A
    stand occupies x fx0 .. fx0+proj and y ay .. ay+fw."""
    sup, arr, fnd = D["support"], D["array"], D["foundation"]
    (lx, ly), (lw, lh) = GEO["parcel"]["lease"]["origin"], GEO["parcel"]["lease"]["size"]
    S = GEO["slab"]["size"][0]
    fw, proj, n = sup["field_w"], sup["proj"], arr["count"]
    sl, sp = fnd["strip_l"], sup["strip_spacing"]
    west = GEO["parcel"]["strips_outside_slab_mm"]["west"]

    if abs(west + lx) > 1:
        raise SystemExit("strips_outside_slab_mm.west disagrees with the lease origin")

    total = n * fw + (n - 1) * ARRAY_GAP
    ymid = S / 2
    y0 = ymid - total / 2
    margin = (west - sl) / 2             # strip end to lease edge = strip end to slab
    sx0 = -west + margin                 # lease-side (JZ) ends of all strips
    fx0 = sx0 + (sl - proj) / 2          # low (JZ) edge of the field
    stands = [y0 + i * (fw + ARRAY_GAP) for i in range(n)]
    strips = [ay + fw / 2 + s * sp / 2 for ay in stands for s in (-1, 1)]

    bad = []
    if margin < MIN_CLEAR:
        bad.append(f"strips only {margin:.0f} mm from the slab / lease edge")
    if y0 < ly or y0 + total > ly + lh:
        bad.append("row longer than the lease")
    if fx0 + proj > GEO["fence"]["origin"][0]:
        bad.append("field oversails the JZ fence")
    if sp / 2 + fnd["strip_w_base"] / 2 > fw / 2:
        bad.append("strip base wider than the stand")
    if bad:
        raise SystemExit("PV layout: " + "; ".join(bad))

    return {"fw": fw, "proj": proj, "sl": sl, "sp": sp, "total": total,
            "ymid": ymid, "y0": y0, "margin": margin, "sx0": sx0, "fx0": fx0,
            "stands": stands, "strips": strips,
            "section_y": strips[3]}       # A-A runs along PV-2's plan-north strip


def interior():
    """Container layout, container-relative: external plan-SW corner = (0, 0),
    +X plan east (true SI), +Y plan north (true SZ).  Used by H-02 (at 1:100)
    and H-04 (at 1:25).

    The Stulz is centred on the JI (plan-south) wall (Investor, 11.09.2026), so
    the genset stands on the container's centre line, long axis SZ-JI, radiator
    at the Stulz cut-outs; a hood outside turns the warm air upwards.  Tank tray
    in the true-north corner (SZ x SI walls), intake on the SI wall just south
    of it at the alternator end, exhaust out through the JI wall from the JZ
    passage, room fan high on the JI wall east of the hood (Investor
    11.09.2026).  Rectangles are (x, y, width along X, depth along Y)."""
    c = GEO["container"]
    (cx0, cy0), (cw, ch) = c["origin"], c["external"]
    t = c["wall_panel_thickness"]
    g, tk, v = D["genset"], D["tank"], D["ventilation"]
    kada = tk["kada"]
    st_w, st_d, st_h = GEO["stulz"]["size_mm_estimated"]

    L = {"cw": cw, "ch": ch, "t": t}
    L["door"] = (c["door"]["span_x"][0] - cx0, c["door"]["span_x"][1] - cx0)
    L["hinge"] = (c["door"]["hinge"][0] - cx0, c["door"]["hinge"][1] - cy0)
    L["door_op"] = c["door"]["opening"]

    # the radiator axis is the axis of the Stulz cut-outs, centred on the JI wall
    axis = cw / 2
    L["axis"] = axis                                         # an X value
    L["stulz"] = (axis - st_w / 2, -st_d, st_w, st_d)        # outside the JI wall
    dis = v["discharge_mm"]
    L["discharge"] = (axis - dis[1] / 2, axis + dis[1] / 2)  # X range in the JI wall
    L["dis_z"] = (DIS_Z0, DIS_Z0 + dis[0])
    L["hood"] = (axis - HOOD_W / 2, -HOOD_D, HOOD_W, HOOD_D)

    sx0 = axis - g["skid_W"] / 2
    sy0 = t + PLENUM
    L["skid"] = (sx0, sy0, g["skid_W"], g["skid_L"])
    fm = (FRAME_W - g["skid_W"]) / 2
    L["frame"] = (sx0 - fm, sy0 - fm, FRAME_W, g["skid_L"] + 2 * fm)
    sx1, sy1 = sx0 + g["skid_W"], sy0 + g["skid_L"]

    # tank tray in the true-north corner, against the SI wall and the SZ wall;
    # the intake sits just south of it on the SI wall, at the alternator end
    L["kada"] = (cw - t - kada["W"], ch - t - kada["L"], kada["W"], kada["L"])
    kx, ky = L["kada"][:2]
    L["tank"] = (kx + (kada["W"] - tk["W"]) / 2, ky + (kada["L"] - tk["L"]) / 2,
                 tk["W"], tk["L"])
    iw, ih = v["intake_mm"]
    L["intake"] = (INTAKE_Y - iw / 2, INTAKE_Y + iw / 2)     # Y range in the SI wall
    L["intake_z"] = (300, 300 + ih)          # "donja ivica +0,30 m od poda"
    L["fan"] = (FAN_X - FAN_D / 2, FAN_X + FAN_D / 2)       # X range in the JI wall

    # exhaust: engine outlet on the JZ side of the skid, up to +2,30, across to the
    # JZ passage, along it to the JI wall and out; silencer in line on that run
    L["exh_x"] = EXH_X
    L["exh"] = [(sx0 + 120, EXH_Y), (EXH_X, EXH_Y), (EXH_X, -EXH_OUT)]
    L["silencer"] = (EXH_Y - 650, EXH_Y - 150)              # Y range on the JZ run

    wall_w = L["door"][0] - t                               # SZ wall west of the door
    L["gro"] = (t + (wall_w - GRO_W) / 2, ch - t - GRO_D, GRO_W, GRO_D)
    L["gro_wall"] = wall_w
    # DC razvod -48 V east of the door, above the tank; ceiling LED luminaires (one
    # AC from GRO F2, one 48 V DC from D5); light switch by the door.  F1 and the
    # -48 V from the ICC360 come in through the JZ wall and run up to the SZ wall.
    L["dcbox"] = (L["door"][1] + DCB_GAP, ch - t - DCB_D, DCB_W, DCB_D)
    L["lights"] = {"AC": (sx1 + 390, 1050), "DC": (700, 2250)}  # AC one clear of the tank
    L["switch"] = (L["door"][1] + 60, ch - t)
    ic = GEO["icc360"]["footprint"]
    L["cable_y"] = ic["origin"][1] + ic["size"][1] / 2 - cy0  # entry in the JZ wall

    # clearances, measured to the skid (the frame is flat and walkable)
    fx, fy, fwid, fdep = L["frame"]
    L["clr"] = {"west": sx0 - t, "east": cw - t - sx1, "south": PLENUM,
                "north_gro": L["gro"][1] - sy1, "north_wall": ch - t - sy1,
                "tray_frame": ky - (fy + fdep),
                "doorway": min(L["door"][1], kx) - L["door"][0]}

    bad = []
    if fx < t or fy < t or fx + fwid > cw - t or fy + fdep > ch - t:
        bad.append("genset frame outside the room")
    if L["clr"]["tray_frame"] < 0 and kx < fx + fwid:
        bad.append("drip tray overlaps the genset frame")
    if L["intake"][1] > ky:
        bad.append("intake is not south of the drip tray")
    if wall_w < GRO_W:
        bad.append(f"GRO {GRO_W} mm does not fit the {wall_w:.0f} mm of wall")
    if L["fan"][0] <= L["hood"][0] + HOOD_W or L["fan"][1] > cw - t:
        bad.append("room fan is not on the JI wall east of the hood")
    if L["discharge"][0] < t or L["discharge"][1] > cw - t:
        bad.append("discharge opening runs into a corner")
    if EXH_X - 130 < t or EXH_X + 130 > fx:
        bad.append("exhaust run and silencer do not fit the JZ passage")
    if L["dcbox"][0] + DCB_W > cw - t:
        bad.append("DC razvod does not fit on the wall east of the door")
    if L["dcbox"][0] - (L["gro"][0] + GRO_W) < 300:
        bad.append("DC razvod closer than 0,3 m to the GRO")
    if L["clr"]["north_gro"] < 800:
        bad.append("less than 0,8 m in front of the GRO")
    if L["clr"]["doorway"] < g["skid_W"] + 100:
        bad.append("drip tray narrows the doorway below the skid width")
    if bad:
        raise SystemExit("container layout: " + "; ".join(bad))
    return L


def plan_equipment(msp, X0, Y0, L, sc, detail):
    """Genset, tank, GRO, openings and exhaust in plan; (X0, Y0) = container plan-SW."""
    t, cw = L["t"], L["cw"]
    sx, sy, sl, sw = L["skid"]
    if detail:
        fx, fy, fw, fd = L["frame"]
        rect(msp, X0 + fx, Y0 + fy, fw, fd, "Konstrukcija", color=5, lw=35)
    rect(msp, X0 + sx, Y0 + sy, sl, sw, "Agregat", color=30, lw=50)
    if detail:
        # radiator band at the JI end, sheet-metal plenum from it to the wall
        rect(msp, X0 + sx, Y0 + sy, sl, 180, "Agregat", color=4, lw=35)
        rect(msp, X0 + sx, Y0 + t, sl, sy - t, "Ventilacija", color=4, lw=35)
    d0, d1 = L["discharge"]
    solid_rect(msp, X0 + d0, Y0, d1 - d0, t, "Ventilacija", 4)
    # deflector hood outside the JI wall; the warm air leaves upwards
    hx, hy, hw, hd = L["hood"]
    rect(msp, X0 + hx, Y0 + hy, hw, hd, "Ventilacija", color=4, lw=50 if detail else 35)
    if detail:
        for r_ in (90, 18):                                  # "up" symbol
            msp.add_circle((X0 + hx + hw / 2, Y0 + hy + hd / 2), r_,
                           dxfattribs={"layer": "Ventilacija", "color": 4})
    i0, i1 = L["intake"]
    solid_rect(msp, X0 + cw - t, Y0 + i0, t, i1 - i0, "Ventilacija", 4)
    f0, f1 = L["fan"]
    solid_rect(msp, X0 + f0, Y0, f1 - f0, t, "Ventilacija", 4)

    kx, ky, kw, kh = L["kada"]
    rect(msp, X0 + kx, Y0 + ky, kw, kh, "Agregat", color=1 if detail else 30, lw=35)
    if detail:
        tx, ty, tw, th = L["tank"]
        rect(msp, X0 + tx, Y0 + ty, tw, th, "Agregat", color=30, lw=35)
    gx, gy, gw, gd = L["gro"]
    if not detail:
        solid_rect(msp, X0 + gx, Y0 + gy, gw, gd, "Novi1", 30)
    rect(msp, X0 + gx, Y0 + gy, gw, gd, "Novi1", color=30, lw=50)

    # exhaust: engine outlet on the JZ side of the skid, up to +2,30 (section),
    # across to the JZ passage and out through the JI wall; silencer in line
    msp.add_lwpolyline([(X0 + x, Y0 + y) for x, y in L["exh"]],
                       dxfattribs={"layer": "Ventilacija", "color": 1,
                                   "lineweight": 50 if detail else 35})
    if detail:
        s0, s1 = L["silencer"]
        rect(msp, X0 + L["exh_x"] - 130, Y0 + s0, 260, s1 - s0, "Ventilacija", color=1,
             lw=35)


# --------------------------------------------------------------------------
# site plan, shared by H-01 and H-02 (1:100)
# --------------------------------------------------------------------------
PLAN_O = (12300, 13500)          # sheet position of the slab's SW corner


def P(x, y):
    """slab-local -> sheet coordinates on the 1:100 plans."""
    return (PLAN_O[0] + x, PLAN_O[1] + y)


def site_plan(msp, sc, future):
    """Lease, earthing, slab, fence, tower and container.  +X east, +Y north."""
    par = GEO["parcel"]
    (lx, ly), (lw, lh) = par["lease"]["origin"], par["lease"]["size"]
    S = GEO["slab"]["size"][0]
    fe, c, tw = GEO["fence"], GEO["container"], GEO["tower"]
    (fx, fy), (fw, fh) = fe["origin"], fe["size"]
    (cx, cy), (cw, ch) = c["origin"], c["external"]
    t = c["wall_panel_thickness"]
    L = interior()

    # lease (k.č. 109/1)
    e = msp.add_lwpolyline([P(lx, ly), P(lx + lw, ly), P(lx + lw, ly + lh),
                            P(lx, ly + lh)], close=True,
                           dxfattribs={"layer": "Sakriveno", "color": 8,
                                       "lineweight": 35})
    ltype(e, "PHANTOM", sc, 1.5)
    _txt(msp, f"GRANICA ZAKUPA  {dec(lw)} × {dec(lh)} m = {par['leased_area_m2']} m²",
         *P(lx + 1500, ly + lh - 500), 2.0 * sc, color=8)
    _txt(msp, par["cadastral"], *P(lx + 1500, ly + lh - 850), 2.0 * sc, color=8)

    # existing earth rings at 0,8 m (3.6.9), dashed so they read as buried
    for off in EARTH_RINGS:
        e = rect(msp, *P(-off, -off), S + 2 * off, S + 2 * off, "Uzemljenje")
        ltype(e, "DASHED", sc)

    solid_rect(msp, *P(0, 0), S, S, "Objekat", 254)
    rect(msp, *P(0, 0), S, S, "Objekat", color=8)
    fs = tw["footings"]["size"][0]
    for lcx, lcy in tw["legs_centres"]:
        e = rect(msp, *P(lcx - fs / 2, lcy - fs / 2), fs, fs, "Sakriveno", color=8)
        ltype(e, "DASHED", sc, 1.5)

    # fence with the gate gap on the NORTH line
    gx0, gx1 = fe["gate"]["span_x"]
    top = fy + fh
    msp.add_lwpolyline([P(gx0, top), P(fx, top), P(fx, fy), P(fx + fw, fy),
                        P(fx + fw, top), P(gx1, top)],
                       dxfattribs={"layer": "Ograda", "color": 8, "lineweight": 50})
    for gx in (gx0, gx1):
        solid_rect(msp, *P(gx - 35, top - 35), 70, 70, "Ograda", 8)
    # Drawn opening OUTWARD: swung in, the 1300 mm leaf would strike the
    # container's north wall, which stands only 1247,5 mm inside the fence.
    (hx, hy), leaf = fe["gate"]["hinge"], fe["gate"]["leaf"]
    msp.add_line(P(hx, hy), P(hx, hy + leaf), dxfattribs={"layer": "Ograda", "color": 8})
    msp.add_arc(center=P(hx, hy), radius=leaf, start_angle=0, end_angle=90,
                dxfattribs={"layer": "Ograda", "color": 8})

    # tower legs and outline (the platform P I at +3,0 m spans it)
    lf = tw["leg_footprint"][0]
    legs = tw["legs_centres"]
    for lcx, lcy in legs:
        solid_rect(msp, *P(lcx - lf / 2, lcy - lf / 2), lf, lf, "Konstrukcija", 5)
    ring = sorted(legs, key=lambda p: math.atan2(p[1] - S / 2, p[0] - S / 2))
    e = msp.add_lwpolyline([P(*p) for p in ring], close=True,
                           dxfattribs={"layer": "Osovina", "color": 8})
    ltype(e, "CENTER", sc, 2)

    # container, 60 mm walls, north wall split at the door
    X0, Y0 = P(cx, cy)
    rect(msp, X0, Y0, cw, ch, "Objekat", color=6, lw=50)
    rect(msp, X0 + t, Y0 + t, cw - 2 * t, ch - 2 * t, "Objekat", color=6)
    d0, d1 = L["door"]
    for x, y, w, h in ((0, 0, cw, t), (0, t, t, ch - 2 * t),
                       (cw - t, t, t, ch - 2 * t),
                       (0, ch - t, d0, t), (d1, ch - t, cw - d1, t)):
        solid_rect(msp, X0 + x, Y0 + y, w, h, "Objekat", 8)
    (hxr, hyr), op = L["hinge"], L["door_op"]
    msp.add_line((X0 + hxr, Y0 + hyr), (X0 + hxr, Y0 + hyr + op),
                 dxfattribs={"layer": "Objekat", "color": 8})
    msp.add_arc(center=(X0 + hxr, Y0 + hyr), radius=op, start_angle=90,
                end_angle=180, dxfattribs={"layer": "Objekat", "color": 8})

    if not future:
        # existing Stulz wall unit, crossed out: it is removed
        sx_, sy_, sw_, sh_ = L["stulz"]
        a, b = X0 + sx_, Y0 + sy_
        rect(msp, a, b, sw_, sh_, "Objekat", color=1, lw=35)
        msp.add_line((a, b), (a + sw_, b + sh_), dxfattribs={"layer": "Objekat", "color": 1})
        msp.add_line((a, b + sh_), (a + sw_, b), dxfattribs={"layer": "Objekat", "color": 1})
    else:
        plan_equipment(msp, X0, Y0, L, sc, detail=False)
        sx, sy, sl, sw = L["skid"]
        _txt(msp, "DEA", X0 + sx + sl / 2 - 150, Y0 + sy + sw / 2, 1.6 * sc, color=7,
             align=TA.MIDDLE_CENTER)
        tx, ty, tw_, th = L["tank"]
        _txt(msp, "500 l", X0 + tx + tw_ / 2, Y0 + ty + th / 2, 1.4 * sc, color=7,
             align=TA.MIDDLE_CENTER, rotation=90)
    return {"L": L, "X0": X0, "Y0": Y0}


def plan_dims(msp, sc, container_dims=True, lease_v=True):
    """Lease, the four strips outside the slab, and (H-01) the container."""
    par = GEO["parcel"]
    (lx, ly), (lw, lh) = par["lease"]["origin"], par["lease"]["size"]
    S = GEO["slab"]["size"][0]
    st = par["strips_outside_slab_mm"]
    for k, v in (("north", ly + lh - S), ("south", -ly), ("east", lx + lw - S),
                 ("west", -lx)):
        if abs(st[k] - v) > 1:
            raise SystemExit(f"strip {k}: json says {st[k]}, lease gives {v}")
    dim_h(msp, *(P(lx, 0)[0], P(lx + lw, 0)[0]), P(0, ly + lh)[1], sc, off=1000)
    if lease_v:                              # H-02 chains the JZ band instead
        dim_v(msp, P(0, ly)[1], P(0, ly + lh)[1], P(lx, 0)[0], sc, off=-700)
    xs = P(lx + lw - 1100, 0)[0]             # N and S strips, SI part (JZ holds the PV)
    dim_v(msp, P(0, S)[1], P(0, ly + lh)[1], xs, sc, off=0)
    dim_v(msp, P(0, ly)[1], P(0, 0)[1], xs, sc, off=0)
    A = array_layout()                       # E and W strips, through a gap of the PV row
    gaps = [ay + A["fw"] + ARRAY_GAP / 2 for ay in A["stands"][:-1]]
    ye = P(0, min(gaps, key=lambda g_: abs(g_ - (S - 1300))))[1]
    dim_h(msp, P(lx, 0)[0], P(0, 0)[0], ye, sc, off=0)
    dim_h(msp, P(S, 0)[0], P(lx + lw, 0)[0], ye, sc, off=0)
    if container_dims:
        c = GEO["container"]
        (cx, cy), (cw, ch) = c["origin"], c["external"]
        dim_h(msp, P(cx, 0)[0], P(cx + cw, 0)[0], P(0, cy)[1], sc, off=-600)
        dim_v(msp, P(0, cy)[1], P(0, cy + ch)[1], P(cx, 0)[0], sc, off=-500)


WX, EX = 7600, 21800             # elbow x of west / east callouts on the plans
NOTES_X = 28000                  # right-hand note column on the plans


def _orientation_note(msp, sc, y):
    return note_block(msp, NOTES_X, y, sc, "NAPOMENA — ORIJENTACIJA:", [
        "Prema Google Maps (Naručilac 11.09.2026) kompleks je zakrenut 45°: vrata",
        "kontejnera i kapija gledaju na SJEVEROZAPAD (SZ), klima-uređaj Stulz na JI.",
        "Crtež je pravougaon na kompleks (gore SZ, desno SI, dolje JI, lijevo JZ);",
        "strelica pokazuje pravi sjever. Ovjereni crtež lokacije iz 2017",
        "(GP-BS-10472-291, 01_Situacija 1_200) zakrenut je ≈180° u odnosu na teren.",
        "Orijentaciju potvrđuje Ponuđač obilaskom lokacije.",
    ])


# --------------------------------------------------------------------------
# H-01  Postojeće stanje                                               1:100
# --------------------------------------------------------------------------
def sheet_h01():
    SC = 100
    doc, msp = _sheet(SC, "Situacija — POSTOJEĆE STANJE", "H-01", "1:100")
    k = site_plan(msp, SC, future=False)
    plan_dims(msp, SC)
    L = k["L"]
    tw, fe = GEO["tower"], GEO["fence"]
    (cx, cy), (cw, ch) = GEO["container"]["origin"], GEO["container"]["external"]
    ly = GEO["parcel"]["lease"]["origin"][1]
    S = GEO["slab"]["size"][0]
    fs = tw["footings"]["size"][0]
    lf = tw["leg_footprint"][0]
    (lcx, lcy) = tw["legs_centres"][0]

    # west
    lead(msp, P(400, S - fs), f"temelji stuba {dec(fs)} × {dec(fs)} m",
         (WX, P(0, 6300)[1]), SC)
    lead(msp, P(cx + 350, cy + 2300), "kontejner K2 — PRAZAN",
         (WX, P(0, 4300)[1]), SC)
    lead(msp, P(fe["origin"][0], 2600),
         f"ograda h = {dec(fe['height'])} m od ploče",
         (WX, P(0, 2900)[1]), SC)
    lead(msp, P(-EARTH_RINGS[1], 1500), "uzemljivač — 2 prstena na 0,8 m",
         (WX, P(0, 1400)[1]), SC)
    lead(msp, P(lcx - lf / 2, lcy), f"noge stuba h = {tw['height'] // 1000} m, {lf} × {lf} mm",
         (WX, P(0, -300)[1]), SC)
    # east
    gx0 = fe["gate"]["hinge"][0]
    gr = fe["gate"]["leaf"]
    lead(msp, P(gx0 + gr * 0.707, fe["gate"]["hinge"][1] + gr * 0.707),
         f"kapija {dec(gr)} m (otvara se van)", (EX, P(0, 7900)[1]), SC)
    (hxr, hyr), op = L["hinge"], L["door_op"]
    dw, dh = GEO["container"]["door"]["size_mm"]
    lead(msp, P(cx + hxr - op * 0.707, cy + hyr + op * 0.707),
         f"vrata {dw} × {dh} mm (SZ)", (EX, P(0, 6800)[1]), SC)
    lead(msp, P(tw["legs_centres"][1][0], 3200),
         f"platforma P I +{dec(tw['platforms_m'][0] * 1000, 1)} m iznad krova",
         (EX, P(0, 5700)[1]), SC)
    sx_, sy_, sw_, sh_ = L["stulz"]
    lead(msp, P(cx + sx_ + sw_, cy + sy_ + sh_ / 2), "klima-uređaj Stulz WDE80 — DEMONTIRA SE",
         (EX, P(0, 2400)[1]), SC)
    lead(msp, P(S - 300, 300), f"AB ploča {dec(S)} × {dec(S)} m", (EX, P(0, 400)[1]), SC)

    _txt(msp, "J U G O I S T O K", *P(S / 2, ly - 1000), 3.2 * SC, layer="Orijentacija",
         color=1, align=TA.CENTER)
    north_arrow(msp, 39000, 25200, 2000, plan_north=PLAN_NORTH)
    scale_bar(msp, 2600, 3000, SC, total_m=10, step_m=1)
    legend(msp, 2600, 7800, SC, [
        (8,   f"postojeća ograda {dec(fe['size'][0])} × {dec(fe['size'][1])} m, "
              f"h = {dec(fe['height'])} m od ploče ({dec(FENCE_ABOVE_GROUND)} m od terena)"
              f" — kapija {dec(gr)} m na SZ strani"),
        (254, f"postojeća AB ploča {dec(S)} × {dec(S)} m"),
        (6,   f"postojeći kontejner K2 {cw} × {ch} mm — vrata na SZ strani"),
        (5,   f"noge rešetkastog stuba h = {tw['height'] // 1000} m, "
              f"baza {dec(tw['base'][0])} × {dec(tw['base'][1])} m"),
        (1,   "klima-uređaj Stulz WDE80 (JI zid, u sredini) — demontira se"),
        (2,   "postojeći uzemljivač FeZn 25×4 mm (isprekidano — u tlu)"),
    ])

    y = _orientation_note(msp, SC, 23000)
    note_block(msp, NOTES_X, y - 700, SC, "NAPOMENE:", [
        "1  Geometrija iz ovjerenog projekta lokacije GP-BS-10472-291 (2017): 01_Situacija 1_200,",
        "    04_Ograda, 01 Osnova, 04 Fasade, 01_Dispozicija S32 m, 3.6.9 Plan uzemljivača objekta.",
        f"2  Zakup {dec(12000)} × {dec(12500)} m = 150 m²: {GEO['parcel']['cadastral']}.",
        "3  Kontejner je PRAZAN; na jugoistočnom (JI) zidu, u sredini, je samo klima-uređaj "
        "Stulz WDE80",
        "    (≈700 × 500 × 2200 mm, procjena s fotografija; Naručilac 11.09.2026).",
        "    Mjere uređaja i otvora u zidu uzimaju se na obilasku lokacije.",
        f"4  Rešetkasti stub h = {tw['height'] // 1000} m; platforma P I na +3,0 m je iznad krova",
        "    kontejnera (+2,63 / +2,89 m) — izduv agregata ne može završiti iznad krova.",
        "5  Uzemljivač FeZn 25×4 mm: prsten u temeljima stopa stuba i dva prstena na dubini",
        "    0,8 m oko ploče (kvadrati 7,50 i 10,00 m prema 3.6.9).",
        "6  Kapija se otvara prema van: krilo 1,30 m udarilo bi u kontejner (1,25 m od ograde).",
        f"7  Teren uz ploču je na {minus(TERRAIN)} m (04_Ograda): ograda je {dec(fe['height'])} m "
        f"iznad ploče, {dec(FENCE_ABOVE_GROUND)} m iznad terena.",
    ])
    return doc


# --------------------------------------------------------------------------
# H-02  Buduće stanje                                                  1:100
# --------------------------------------------------------------------------
def sheet_h02():
    SC = 100
    doc, msp = _sheet(SC, "Situacija — BUDUĆE STANJE", "H-02", "1:100")
    k = site_plan(msp, SC, future=True)
    plan_dims(msp, SC, container_dims=False, lease_v=False)
    L, X0, Y0 = k["L"], k["X0"], k["Y0"]
    A = array_layout()
    sup, arr, fnd = D["support"], D["array"], D["foundation"]
    fw, proj, sl, fx0, n = A["fw"], A["proj"], A["sl"], A["fx0"], arr["count"]
    swt = fnd["strip_w_top"]
    (lx, ly), (lw, lh) = GEO["parcel"]["lease"]["origin"], GEO["parcel"]["lease"]["size"]
    west = GEO["parcel"]["strips_outside_slab_mm"]["west"]
    cx = GEO["container"]["origin"][0]
    cw = L["cw"]

    # one row of separate stands in the JZ band, each facing true SW (plan west):
    # low edge toward the lease line, module rows parallel to it
    for i, ay in enumerate(A["stands"], 1):
        x, y = P(fx0, ay)
        rect(msp, x, y, proj, fw, "Panel", color=110, lw=70)
        hatch_rect(msp, x, y, proj, fw, "Panel", "ANSI37", SC * 1.2, 110)
        for r_ in range(1, sup["rows"]):
            xr = x + proj * r_ / sup["rows"]
            msp.add_line((xr, y), (xr, y + fw), dxfattribs={"layer": "Panel", "color": 8})
        _txt(msp, f"PV-{i}", *P((lx + fx0) / 2, ay + fw / 2), 2.0 * SC, color=7,
             align=TA.MIDDLE_CENTER, rotation=90)
    for sya in A["strips"]:
        rect(msp, *P(A["sx0"], sya - swt / 2), sl, swt, "Temelj", color=32, lw=35)

    # strings along the row at mid-depth, then ONE short trench under the JZ fence
    # to the PVDB beside the ICC360, between the two cabinets
    ic, mt = GEO["icc360"], GEO["mts"]
    (ix, iy), (iw, ih) = ic["footprint"]["origin"], ic["footprint"]["size"]
    xc = fx0 + proj / 2
    msp.add_lwpolyline([P(xc, A["stands"][0] + fw / 2), P(xc, A["stands"][-1] + fw / 2)],
                       dxfattribs={"layer": "Kabal", "color": 2, "lineweight": 35})
    yt = (iy + ih + mt["footprint"]["origin"][1]) / 2
    e = msp.add_lwpolyline([P(xc, yt), P(ix, yt)],
                           dxfattribs={"layer": "Kabal", "color": 2, "lineweight": 50})
    ltype(e, "DASHED", SC)

    # section A-A along PV-2's plan-north strip, looking true SZ (plan north)
    ys = A["section_y"]
    for x_from, x_to in ((lx - 150, lx - 750), (lx + lw + 150, lx + lw + 750)):
        e = msp.add_lwpolyline([P(x_from, ys), P(x_to, ys)],
                               dxfattribs={"layer": "Osovina", "color": 1, "lineweight": 70})
        ltype(e, "CENTER", SC, 1.5)
        arrow(msp, [P(x_to, ys), P(x_to, ys + 700)], color=1, size=220,
              layer="Osovina", lw=50)
        _txt(msp, "A", *P(x_to + (-300 if x_to < 0 else 300), ys + 350), 3.0 * SC,
             layer="Orijentacija", color=1, align=TA.MIDDLE_CENTER)

    # Huawei ICC360-HA1-C1 and the MTS outdoors on the slab, JZ side, behind the
    # PV row and in its shade, fronts to the container (Investor 11.09.2026)
    for key, lab in (("icc360", "ICC360"), ("mts", "MTS")):
        cab = GEO[key]
        (bx, by), (bw, bh) = cab["footprint"]["origin"], cab["footprint"]["size"]
        body = cab["size_mm"]["D"]
        solid_rect(msp, *P(bx, by), body, bh, "Novi1", 30)
        rect(msp, *P(bx, by), body, bh, "Novi1", color=30, lw=50)
        if bw > body:                                  # the door, open
            rect(msp, *P(bx + body, by), bw - body, bh, "Novi1", color=30, lw=35)
        _txt(msp, lab, *P(bx + body / 2, by + bh / 2), 1.5 * SC, color=7,
             align=TA.MIDDLE_CENTER, rotation=90)
    # F1 and the -48 V from the ICC360 into the container through the JZ wall
    e = msp.add_lwpolyline([P(ix + ic["size_mm"]["D"], iy + 120), P(cx, iy + 120)],
                           dxfattribs={"layer": "Kabal", "color": 30, "lineweight": 35})
    ltype(e, "DASHED", SC, 1)
    # tank vent: out through the SZ wall east of the door, stand-pipe by the fence
    tv = GEO["tank_vent"]
    e = msp.add_lwpolyline([P(*tv["wall_exit"]), P(*tv["termination"])],
                           dxfattribs={"layer": "Ventilacija", "color": 1, "lineweight": 35})
    ltype(e, "DASHED", SC, 1.5)
    msp.add_circle(P(*tv["termination"]), 90, dxfattribs={"layer": "Ventilacija", "color": 1})

    # the row along the band: lease edge | stands | gaps | lease edge
    xd = P(lx, 0)[0] - 300
    pts = [(lx, ly)] + [(fx0, v) for ay in A["stands"] for v in (ay, ay + fw)] \
        + [(lx, ly + lh)]
    for a, b in zip(pts, pts[1:]):
        dim_free(msp, P(*a), P(*b), (xd, 0), SC, angle=90, text=mmc(b[1] - a[1]))
    y0_ = A["stands"][0]
    dim_free(msp, P(A["sx0"], y0_), P(A["sx0"] + sl, y0_), (0, P(0, y0_ - 450)[1]), SC)
    dim_free(msp, P(fx0, y0_), P(fx0 + proj, y0_), (0, P(0, y0_ - 900)[1]), SC)

    # west callouts (the texts run left of WX, so they stay short)
    lead(msp, P(A["sx0"] + 40, A["strips"][0]), f"temeljne trake ({len(A['strips'])} kom)",
         (WX, P(0, -2900)[1]), SC)
    lead(msp, P(A["sx0"] + 40, A["strips"][1]),
         f"trake {mmc(A['margin'])} mm od zakupa i od ploče", (WX, P(0, -1300)[1]), SC)
    lead(msp, P(-EARTH_RINGS[1], A["strips"][2]), "prsteni uzemljivača × trake (LOT 1)",
         (WX, P(0, 700)[1]), SC)
    lead(msp, P(fx0 + 300, yt), "DC trasa Ø50 → PVDB / ICC360",
         (WX, P(0, 3700)[1]), SC)
    # east callouts
    lead(msp, P(*tv["termination"]), "odušak spremnika (SZ) — principijelno",
         (EX, P(0, 7300)[1]), SC)
    sx, sy, sl_, sw_ = L["skid"]
    lead(msp, (X0 + sx + sl_, Y0 + sy + sw_ - 200), "DEA, spremnik, GRO — v. H-04",
         (EX, P(0, 5000)[1]), SC)
    lead(msp, (X0 + cw - L["t"] / 2, Y0 + sum(L["intake"]) / 2), "usis 500 × 700 (SI, novo)",
         (EX, P(0, 3700)[1]), SC)
    lead(msp, (X0 + FAN_X, Y0 + L["t"] / 2), "ventilator Ø315 — izvlačni (JI)",
         (EX, P(0, 1100)[1]), SC)
    hx, hy, hw, hd = L["hood"]
    lead(msp, (X0 + hx + hw, Y0 + hy + hd / 2), "izlaz zraka — otvori Stulz, hauba naviše",
         (EX, P(0, -300)[1]), SC)
    lead(msp, (X0 + L["exh_x"], Y0 - EXH_OUT),
         f"izduv NO 50 (JI), ≈+{dec(EXH_Z)}, ≥{dec(EXH_OUT)} m od zida",
         (EX, P(0, -1700)[1]), SC)

    north_arrow(msp, 39000, 25200, 2000, plan_north=PLAN_NORTH)
    scale_bar(msp, 2600, 3000, SC, total_m=10, step_m=1)
    legend(msp, 2600, 7800, SC, [
        (110, f"FN nosači PV-1..PV-{n} — po {sup['modules_each']} × 585 Wp (1 × 3, položeno), "
              f"{arr['tilt_deg']}°, azimut {arr['azimuth_deg']}° (JZ) — 2 stringa × 6"),
        (32,  f"AB temeljne trake {strip_w_txt(fnd)} × {sl} mm, "
              f"d = {fnd['strip_d']} mm, razmak {A['sp']} mm — {len(A['strips'])} kom"),
        (2,   "DC trasa u PEHD Ø50 (isprekidano) — od polja do PVDB uz ICC360"),
        (30,  "DEA 18 kVA (skid), spremnik 500 l u koritu, novi GRO"),
        (4,   "usis 500 × 700 (SI), izlaz zraka kroz otvore Stulz (JI) i haubu naviše, "
              "ventilator Ø315 (JI)"),
        (1,   "izduv NO 50 (JI, ≈+2,30 m); odušak spremnika (SZ, isprekidano); presjek A–A"),
        (30,  "Huawei ICC360-HA1-C1 i MTS vani na ploči (JZ), iza FN polja — principijelno"),
    ])

    y = _orientation_note(msp, SC, 23000)
    b_, top_ = arr["bottom_edge"], arr["top_edge"]
    note_block(msp, NOTES_X, y - 700, SC, "NAPOMENE:", [
        f"1  Nosači su okrenuti prema JUGOZAPADU (azimut {arr['azimuth_deg']}°), nagib "
        f"{arr['tilt_deg']}°; donja ivica panela +{dec(b_)} m,",
        f"    gornja +{dec(top_)} m — {dec(PV_OVER_FENCE)} m iznad vrha ograde (ograda "
        f"{dec(GEO['fence']['height'])} m iznad ploče = {dec(FENCE_ABOVE_GROUND)} m iznad terena).",
        f"2  {n} odvojena nosača u jednom nizu (Naručilac 11.09.2026): {n} × {mmc(fw)} + "
        f"{n - 1} × {ARRAY_GAP} = {mmc(A['total'])} mm,",
        f"    u pojasu JZ {dec(west)} × {dec(lh)} m, centrirano na ploču; sve je unutar "
        "granice zakupa.",
        f"3  Temeljne trake {strip_w_txt(fnd)} × {sl} mm, d = {fnd['strip_d']} mm, "
        f"na podložnom betonu {fnd['blinding_thk']} mm,",
        f"    pravac JZ–SI; {mmc(A['margin'])} mm od granice zakupa i od ploče.",
        f"4  Postojeći prsteni uzemljivača (0,8 m; {dec(EARTH_RINGS[0])} i {dec(EARTH_RINGS[1])} m "
        "od ploče): ukrštanja sa temeljnim trakama —",
        "    lociranje, otkopavanje i premještanje ili premoštavanje prstena (LOT 1).",
        "5  Vjetar qp ≥ 1,20 kN/m² — nosač CUSTOM izrade; ovjereni statički proračun",
        "    dostavlja Ponuđač.",
        "6  Raspored u kontejneru prema H-04; izlaz zraka kroz otvore Stulz (JI) i haubu naviše.",
        "7  Ormari ICC360-HA1-C1 i MTS — principijelno, potvrđuju se na licu mjesta; iza FN",
        "    polja, u njegovoj sjeni; napajanje iz GRO (izvod F1) kroz JZ zid. Odušak spremnika",
        "    kroz SZ zid — principijelno, konačno prema elaboratu zaštite od požara",
        "    (≥3 m od izduva i usisa, ≥1 m od ormara).",
    ])
    return doc


# --------------------------------------------------------------------------
# H-03  Presjek A–A kroz FN polje                                       1:30
# --------------------------------------------------------------------------
def sheet_h03():
    """Equivalent of Sjednica S-03.  Section along PV-2's plan-north strip
    (plane y = A['section_y']): the JZ band, the fence, the ICC360 behind the
    stands and the container cut across its width, looking true SZ (plan
    north): JZ on the left, SI on the right.  Levels are from the terrain beside
    the array; the slab top is +0,20 (terrain -0,20 against the slab, 04_Ograda)."""
    SC = 30
    doc, msp = _sheet(SC, "Presjek A–A kroz FN polje", "H-03", "1:30")
    A = array_layout()
    sup, arr, fnd, mod = D["support"], D["array"], D["foundation"], D["module"]
    proj, b, top = A["proj"], arr["bottom_edge"], arr["top_edge"]
    FH = GEO["fence"]["height"]                     # above the slab
    if FH != arr["fence_height"]:
        raise SystemExit("fence height: design.json and site_geometry.json disagree")
    ZS = -TERRAIN                                   # slab top above the terrain
    lx = GEO["parcel"]["lease"]["origin"][0]
    S = GEO["slab"]["size"][0]
    fe_w = GEO["fence"]["origin"][0]
    fe_e = fe_w + GEO["fence"]["size"][0]
    c = GEO["container"]
    (cx, cy), cw = c["origin"], c["external"][0]
    t = c["wall_panel_thickness"]
    H_LO, H_HI = c["heights"]["eave_low"], c["heights"]["eave_high"]
    tw = GEO["tower"]
    L = interior()
    g, tk = D["genset"], D["tank"]
    sx0, sl, fx0 = A["sx0"], A["sl"], A["fx0"]
    fd, bl = fnd["strip_d"], fnd["blinding_thk"]

    # A3 window at 1:30 is 600..12300 x 300..8610; title block x > 6900 below 1740
    GX, GY = 5775, 3300                             # GY = terrain beside the array

    def X(s):                                       # s = slab-local X, SI to the right
        return GX + s

    # terrain at -0,20 against the slab, both sides; hatch ticks clear of strip/slab
    x_l, x_r = X(lx) - 1500, X(fe_e) + 700
    for xa_, xb_ in ((x_l, X(0)), (X(S), x_r)):
        msp.add_line((xa_, GY), (xb_, GY),
                     dxfattribs={"layer": "Objekat", "color": 8, "lineweight": 50})
    x = x_l + 150
    while x < x_r - 100:
        if not (X(sx0) - 100 <= x <= X(sx0 + sl) + 250 or X(0) - 100 <= x <= X(S) + 250):
            msp.add_line((x, GY), (x - 150, GY - 150),
                         dxfattribs={"layer": "Objekat", "color": 8})
        x += 450
    e = msp.add_line((X(lx), GY - 1300), (X(lx), GY + 4300),
                     dxfattribs={"layer": "Sakriveno", "color": 8})
    ltype(e, "PHANTOM", SC, 1.5)
    _txt(msp, "granica zakupa", X(lx) - 80, GY + 4150, 1.7 * SC, color=8, align=TA.RIGHT)

    # foundation strip, full depth, on blinding (seen along its length)
    rect(msp, X(sx0), GY - fd, sl, fd, "Temelj", color=32, lw=50)
    hatch_rect(msp, X(sx0), GY - fd, sl, fd, "Temelj", "ANSI31", SC * 0.35, 32)
    solid_rect(msp, X(sx0) - 50, GY - fd - bl, sl + 100, bl, "Temelj", 254)
    rect(msp, X(sx0) - 50, GY - fd - bl, sl + 100, bl, "Temelj", color=8, lw=35)

    # the two existing earth rings (tapes along the band) cross the strip at 0,8 m
    dr = GEO["earth_rings"]["depth_mm"]
    for off in EARTH_RINGS:
        solid_rect(msp, X(-off) - 40, GY - dr - 40, 80, 80, "Uzemljenje", 2)

    # stand: three modules in landscape along the 45 deg slope, rail, posts, brace
    x0, y0 = X(fx0), GY + b
    x1, y1 = X(fx0 + proj), GY + top
    ang = math.atan2(y1 - y0, x1 - x0)
    ux, uy, nx, ny = math.cos(ang), math.sin(ang), -math.sin(ang), math.cos(ang)
    MW, MT, rows = mod["W"], mod["T"], sup["rows"]
    gap_m = (sup["field_slope"] - rows * MW) / max(rows - 1, 1)
    for r_ in range(rows):
        k0 = r_ * (MW + gap_m)
        p0 = (x0 + ux * k0, y0 + uy * k0)
        p1 = (x0 + ux * (k0 + MW), y0 + uy * (k0 + MW))
        pts = [p0, p1, (p1[0] + nx * MT, p1[1] + ny * MT), (p0[0] + nx * MT, p0[1] + ny * MT)]
        h_ = msp.add_hatch(color=5, dxfattribs={"layer": "Panel"})
        h_.paths.add_polyline_path(pts, is_closed=True)
        msp.add_lwpolyline(pts, close=True,
                           dxfattribs={"layer": "Panel", "color": 5, "lineweight": 50})
    msp.add_line((x0 - nx * 80, y0 - ny * 80), (x1 - nx * 80, y1 - ny * 80),
                 dxfattribs={"layer": "Panel", "color": 8})
    for a_, b_ in (((x0, y0), (x0, GY)), ((x1, y1), (x1, GY)), ((x0, y0), (x1, GY))):
        msp.add_line(a_, b_, dxfattribs={"layer": "Konstrukcija", "color": 5,
                                         "lineweight": 50})
    for xp in (x0, x1):                             # base plates on the strip
        solid_rect(msp, xp - 110, GY, 220, 20, "Konstrukcija", 5)
    msp.add_line((x0, y0), (x0 + 1000, y0), dxfattribs={"layer": "Kote", "color": 8})
    msp.add_arc((x0, y0), 750, 0, math.degrees(ang), dxfattribs={"layer": "Kote", "color": 8})
    _txt(msp, f"{arr['tilt_deg']}°", x0 + 820, y0 + 160, 2.4 * SC, layer="Kote", color=7)

    # fences, cut by the plane: posts 50 outside the slab, on the terrain,
    # 1,80 m above the slab = 2,00 m above the ground
    FT = ZS + FH                                    # fence top above the terrain
    for s in (fe_w, fe_e):
        fx = X(s)
        solid_rect(msp, fx - 25, GY, 50, FT, "Ograda", 8)
        rect(msp, fx - 25, GY, 50, FT, "Ograda", color=8, lw=70)
        for ry in (GY + ZS + 100, GY + FT - 30):
            rect(msp, fx - 15, ry, 30, 30, "Ograda", color=8, lw=50)
    _txt(msp, f"ograda {dec(FH)} m od ploče", X(fe_w) - 90, GY + 150, 1.6 * SC,
         color=7, rotation=90)

    # slab, top at +0,20
    rect(msp, X(0), GY + ZS - SLAB_T, S, SLAB_T, "Objekat", color=254, lw=35)
    hatch_rect(msp, X(0), GY + ZS - SLAB_T, S, SLAB_T, "Objekat", "ANSI31", SC * 0.5, 8)
    _txt(msp, f"postojeća AB ploča {dec(S)} × {dec(S)} m, gornja površina +{dec(ZS)}",
         X(S / 2), GY + ZS - SLAB_T - 300, 1.7 * SC, color=8, align=TA.CENTER)

    # tower in the background (the plan-north legs), schematic; platform P I over the roof
    lf = tw["leg_footprint"][0]
    TOP = 4400
    zp = tw["platforms_m"][0] * 1000
    G0 = GY + ZS                                    # slab top
    legs_x = sorted({p[0] for p in tw["legs_centres"]})
    for s in legs_x:
        rect(msp, X(s) - lf / 2, G0, lf, TOP, "Konstrukcija", color=5, lw=35)
        msp.add_lwpolyline([(X(s) - lf / 2 - 80, G0 + TOP), (X(s) - 60, G0 + TOP + 90),
                            (X(s) + 60, G0 + TOP - 90), (X(s) + lf / 2 + 80, G0 + TOP)],
                           dxfattribs={"layer": "Konstrukcija", "color": 5})
    xa, xb = X(legs_x[0]) + lf / 2, X(legs_x[1]) - lf / 2
    solid_rect(msp, X(legs_x[0]) - lf / 2, G0 + zp, xb - xa + 2 * lf, 80, "Konstrukcija", 5)
    msp.add_line((xa, G0 + zp + 80), (xb, G0 + TOP), dxfattribs={"layer": "Konstrukcija", "color": 5})
    msp.add_line((xb, G0 + zp + 80), (xa, G0 + TOP), dxfattribs={"layer": "Konstrukcija", "color": 5})
    _txt(msp, f"rešetkasti stub h = {tw['height'] // 1000} m — pozadina, šematski",
         (xa + xb) / 2, G0 + TOP + 200, 1.8 * SC, color=8, align=TA.CENTER)
    lead(msp, (X(legs_x[1]) + lf / 2, G0 + zp + 40),
         f"platforma +{dec(zp, 1)}", (X(legs_x[1]) + 450, G0 + zp + 500), SC)

    # the ICC360 behind the stands is cut by the plane; drawn over the tower leg
    ic = GEO["icc360"]
    (ix, iy), (iw, ih) = ic["footprint"]["origin"], ic["footprint"]["size"]
    body, HC = ic["size_mm"]["D"], ic["size_mm"]["H"]
    if not iy <= A["section_y"] <= iy + ih:
        raise SystemExit("section A-A no longer cuts the ICC360 - move one of them")
    solid_rect(msp, X(ix), G0, body, HC, "Novi1", 30)
    rect(msp, X(ix), G0, body, HC, "Novi1", color=30, lw=50)
    e = rect(msp, X(ix + body), G0, iw - body, HC, "Novi1", color=30)
    ltype(e, "DASHED", SC, 1)
    _txt(msp, "ICC360-HA1-C1 (principijelno) — u sjeni FN polja", X(ix) + body / 2 + 25,
         G0 + 120, 1.5 * SC, color=7, rotation=90)

    # container, cut across its width: the JZ and SI walls cut; beyond, the SZ wall
    # with the door, the GRO and the DC razvod, and the tank in the true-north corner
    xc0, xc1 = X(cx), X(cx + cw)
    msp.add_lwpolyline([(xc0, G0), (xc1, G0), (xc1, G0 + H_LO), (xc0, G0 + H_LO)],
                       close=True, dxfattribs={"layer": "Objekat", "color": 6, "lineweight": 50})
    for xw in (xc0, xc1 - t):
        solid_rect(msp, xw, G0, t, H_LO, "Objekat", 8)
    msp.add_lwpolyline([(xc0 - 120, G0 + H_LO), (xc1 + 120, G0 + H_LO),
                        (xc1 + 120, G0 + H_LO + 100), (xc0 - 120, G0 + H_LO + 100)],
                       close=True, dxfattribs={"layer": "Objekat", "color": 6, "lineweight": 35})
    e = msp.add_line((xc0 - 120, G0 + H_HI), (xc1 + 120, G0 + H_HI),
                     dxfattribs={"layer": "Objekat", "color": 6})
    ltype(e, "DASHED", SC, 1.5)
    _txt(msp, f"+{dec(H_LO)} / +{dec(H_HI)} od ploče (krov 10 %)", xc0 + 150,
         G0 + H_HI + 60, 1.5 * SC, layer="Kota_tekst", color=8)
    d0, d1 = L["door"]
    e = rect(msp, xc0 + d0, G0, d1 - d0, c["door"]["size_mm"][1], "Objekat", color=8)
    ltype(e, "DASHED", SC, 1)
    gx, gy, gw, gd = L["gro"]
    rect(msp, xc0 + gx, G0 + GRO_Z, gw, GRO_H, "Novi1", color=30, lw=35)
    _txt(msp, "GRO", xc0 + gx + gw / 2, G0 + GRO_Z + GRO_H + 60, 1.4 * SC, color=8,
         align=TA.CENTER)
    bx_, by_, bw_, bd_ = L["dcbox"]
    rect(msp, xc0 + bx_, G0 + DCB_Z, bw_, DCB_H, "Novi1", color=30, lw=35)
    kx, ky, kw, kh = L["kada"]
    tx, ty, tw_, th = L["tank"]
    rect(msp, xc0 + kx, G0, kw, tk["kada"]["rim_mm"], "Agregat", color=1, lw=35)
    rect(msp, xc0 + tx, G0 + 40, tw_, tk["H"], "Agregat", color=30, lw=50)
    _txt(msp, "spremnik", xc0 + tx + tw_ / 2, G0 + tk["H"] + 110, 1.4 * SC, color=8,
         align=TA.CENTER)
    # the genset, cut across, on its frame
    sx, sy, sw, _ = L["skid"]
    fxf, _, fwid, _ = L["frame"]
    rect(msp, xc0 + fxf, G0, fwid, FRAME_H, "Konstrukcija", color=5, lw=35)
    rect(msp, xc0 + sx, G0 + FRAME_H, sw, g["skid_H"], "Agregat", color=30, lw=50)
    hatch_rect(msp, xc0 + sx, G0 + FRAME_H, sw, g["skid_H"], "Agregat", "ANSI31",
               SC * 0.3, 30)
    _txt(msp, "DEA", xc0 + sx + sw / 2, G0 + FRAME_H + g["skid_H"] + 90, 1.5 * SC,
         color=7, align=TA.CENTER)
    # exhaust: riser beyond the cut, across at +2,30 to the JZ passage, cut there
    (ex_, _), _, _ = L["exh"]
    msp.add_lwpolyline([(xc0 + ex_, G0 + FRAME_H + g["skid_H"]), (xc0 + ex_, G0 + EXH_Z),
                        (xc0 + EXH_X, G0 + EXH_Z)],
                       dxfattribs={"layer": "Ventilacija", "color": 1, "lineweight": 50})
    msp.add_circle((xc0 + EXH_X, G0 + EXH_Z), 70,
                   dxfattribs={"layer": "Ventilacija", "color": 1})
    _txt(msp, f"postojeći kontejner K2 — presjek po širini {cw} mm", (xc0 + xc1) / 2,
         GY + ZS - SLAB_T - 560, 1.6 * SC, color=8, align=TA.CENTER)

    # levels from the terrain, labelled at the left end
    for lvl, lab in ((b, f"donja ivica panela  +{dec(b)}"),
                     (FT, f"vrh ograde  +{dec(FT)}  ({dec(FH)} iznad ploče)"),
                     (top, f"gornja ivica panela  +{dec(top)}")):
        msp.add_line((650, GY + lvl), (X(fe_w) + 150, GY + lvl),
                     dxfattribs={"layer": "Sakriveno", "color": 8})
        _txt(msp, lab, 700, GY + lvl + 40, 1.9 * SC, layer="Kota_tekst", color=7)
    _txt(msp, "teren  ±0,00", 700, GY + 40, 1.9 * SC, layer="Kota_tekst", color=7)

    # dimensions
    dim_free(msp, (1750, GY), (1750, GY + top), (1750, 0), SC, angle=90)
    dim_free(msp, (X(fe_w), GY + FT), (x1, GY + top), (X(fe_w) + 350, 0), SC, angle=90)
    yb = GY - fd - bl
    dim_free(msp, (x0, yb), (x1, yb), (0, yb - 450), SC)
    yc = yb - 900
    dim_free(msp, (X(lx), yb), (X(sx0), yb), (0, yc), SC, text=mmc(A["margin"]),
             loc=(X(lx) - 320, yc + 60))
    dim_free(msp, (X(sx0), yb), (X(sx0 + sl), yb), (0, yc), SC)
    dim_free(msp, (X(sx0 + sl), yb), (X(0), yb), (0, yc), SC, text=mmc(A["margin"]),
             loc=(X(0) + 330, yc + 60))

    # callouts
    km = 1.5 * (MW + gap_m)
    lead(msp, (x0 + ux * km + nx * MT, y0 + uy * km + ny * MT),
         f"FN moduli {mod['model'].split(' /')[0]} {mod['L']} × {MW}, položeno, {rows} reda",
         (X(fx0) + 1500, GY + top + 700), SC)
    lead(msp, (x1, GY + 1400), "nosač — CUSTOM izrada", (x1 - 500, GY + 1900), SC)
    lead(msp, (X(sx0 + sl) - 400, GY - 600),
         f"temeljna traka {strip_w_txt(fnd)} × {sl}, "
         f"d = {fd} — C30/37", (X(sx0 + sl) + 650, GY - 1100), SC)
    lead(msp, (X(-EARTH_RINGS[0]), GY - dr), "2 postojeća prstena FeZn 25×4 na −0,80 — ukrštanje",
         (X(sx0 + sl) + 650, GY - 1450), SC)
    lead(msp, (X(sx0) + 300, GY - fd - bl / 2), f"podložni beton C12/15, d = {bl}",
         (X(sx0) - 350, GY - 1250), SC)
    lead(msp, (xc0 + EXH_X, G0 + EXH_Z - 70), "izduv (presječen) → JI",
         (xc0 + EXH_X + 500, G0 + EXH_Z - 700), SC)

    _txt(msp, "PRESJEK A–A  (osa SZ trake nosača PV-2 — pogled prema SJEVEROZAPADU)",
         700, 8300, 2.6 * SC, color=7)
    _txt(msp, "←  J U G O Z A P A D", 700, GY - 350, 2.4 * SC, layer="Orijentacija", color=1)
    _txt(msp, "S J E V E R O I S T O K  →", X(fe_e) - 1500, GY - 650, 2.4 * SC,
         layer="Orijentacija", color=1)

    note_block(msp, 700, 1250, SC, "OBJAŠNJENJA:", [
        f"1  Polje: {rows} reda × {sup['cols']} modul 585 Wp, položeno; nagib {arr['tilt_deg']}°, "
        f"projekcija {proj} mm; {arr['count']} odvojena nosača u nizu (H-02).",
        f"2  Dvije temeljne trake po nosaču {strip_w_txt(fnd)} × {sl} mm, "
        f"dubina {fd} mm, razmak {A['sp']} mm (druga iza ravni presjeka);",
        f"    beton C30/37 (XC4+XF3), armatura B500B, na podložnom betonu C12/15 d = {bl} mm.",
        f"3  Kote od terena uz FN polje; teren je {minus(TERRAIN)} m ispod ploče (04_Ograda). "
        f"Donja ivica panela +{dec(b)}, gornja +{dec(top)};",
        f"    vrh ograde +{dec(FT)} ({dec(FH)} m iznad ploče) — gornja ivica je "
        f"{dec(PV_OVER_FENCE)} m iznad ograde.",
        "4  Postojeći prsteni uzemljivača na 0,8 m presijecaju traku: lociranje, otkopavanje i",
        "    premještanje ili premoštavanje prstena (LOT 1).",
        f"5  Trake su {mmc(A['margin'])} mm od granice zakupa (JZ) i od ploče (SI); "
        "položaj presjeka na H-02.",
        "6  Stub, platforma P I (+3,0 m), kontejner i ormari šematski; ICC360 i MTS stoje iza "
        "FN polja, u njegovoj sjeni.",
    ])
    return doc


# --------------------------------------------------------------------------
# H-04  Agregat u kontejneru — osnova i presjek 1–1                     1:25
# --------------------------------------------------------------------------
def sheet_h04():
    """Equivalent of Sjednica M-01 for the Hamzići container: 2300 x 3005, door
    in the SZ (plan-north) face.  The Stulz is centred on the JI wall (Investor,
    11.09.2026): the genset stands on the centre line, long axis SZ-JI,
    radiator JI, discharging through the Stulz cut-outs into a hood that turns
    the warm air upwards; intake on the SI wall at the alternator end, tank in
    the true-north corner, exhaust out through the JI wall from the JZ passage,
    under the +3,0 m platform (Investor, 11.09.2026)."""
    SC = 25
    doc, msp = _sheet(SC, "Agregat u kontejneru — osnova i presjek 1–1", "H-04", "1:25")
    L = interior()
    chk = site_checks()
    g, tk = D["genset"], D["tank"]
    kada = tk["kada"]
    cw, ch, t = L["cw"], L["ch"], L["t"]
    c = GEO["container"]
    cx0, cy0 = c["origin"]
    H_LO, H_HI = c["heights"]["eave_low"], c["heights"]["eave_high"]
    sx0, sy0, sw, sl = L["skid"]                    # width along X, length along Y
    sx1, sy1 = sx0 + sw, sy0 + sl
    fx, fy, fwid, fdep = L["frame"]
    kx, ky, kw, kh = L["kada"]
    tx, ty, tw_, th = L["tank"]
    gx, gy, gw, gd = L["gro"]
    bx, by, bw, bd = L["dcbox"]
    hx, hy, hw, hd = L["hood"]
    d0, d1 = L["door"]
    (hgx, hgy), op = L["hinge"], L["door_op"]
    ax = L["axis"]
    i0, i1 = L["intake"]
    iyc = (i0 + i1) / 2
    iz0, iz1 = L["intake_z"]
    f0, f1 = L["fan"]
    dz0, dz1 = L["dis_z"]
    s0, s1 = L["silencer"]
    ex = L["exh_x"]
    dh_ = c["door"]["size_mm"][1]
    tv = GEO["tank_vent"]
    vx = tv["wall_exit"][0] - cx0
    vyt = tv["termination"][1] - cy0

    # A3 window at 1:25 is 500..10250 x 250..7175; title block x > 5750 below 1450
    ox, oy = 1900, 2450
    rect(msp, ox, oy, cw, ch, "Objekat", color=6, lw=50)
    rect(msp, ox + t, oy + t, cw - 2 * t, ch - 2 * t, "Objekat", color=6)
    for x, y, w, h in ((0, 0, cw, t), (0, t, t, ch - 2 * t), (cw - t, t, t, ch - 2 * t),
                       (0, ch - t, d0, t), (d1, ch - t, cw - d1, t)):
        solid_rect(msp, ox + x, oy + y, w, h, "Objekat", 8)
    msp.add_line((ox + hgx, oy + hgy), (ox + hgx, oy + hgy + op),
                 dxfattribs={"layer": "Objekat", "color": 8})
    msp.add_arc(center=(ox + hgx, oy + hgy), radius=op, start_angle=90, end_angle=180,
                dxfattribs={"layer": "Objekat", "color": 8})
    _txt(msp, "vrata", ox + d0 + 380, oy + ch + 330, 1.6 * SC, color=7)
    _txt(msp, f"{c['door']['size_mm'][0]} × {dh_}", ox + d0 + 380, oy + ch + 170,
         1.4 * SC, color=8)

    plan_equipment(msp, ox, oy, L, SC, detail=True)

    # DC razvod -48 V, the two luminaires and the door switch
    solid_rect(msp, ox + bx, oy + by, bw, bd, "Novi1", 30)
    rect(msp, ox + bx, oy + by, bw, bd, "Novi1", color=30, lw=50)
    # label beside the DC one; below the AC one, which sits in the narrow SI passage
    for (lx_, ly_), lab, (dx_, dy_), al in (
            (L["lights"]["AC"], "LED 230 V AC (F2)", (0, -200), TA.CENTER),
            (L["lights"]["DC"], "LED 48 V DC (D5)", (-160, -20), TA.RIGHT)):
        X_, Y_ = ox + lx_, oy + ly_
        msp.add_circle((X_, Y_), 110, dxfattribs={"layer": "Sema", "color": 2})
        for s in (-1, 1):
            msp.add_line((X_ - 78, Y_ - 78 * s), (X_ + 78, Y_ + 78 * s),
                         dxfattribs={"layer": "Sema", "color": 2})
        _txt(msp, lab, X_ + dx_, Y_ + dy_, 1.3 * SC, color=8, align=al)
    swx, swy = L["switch"]
    msp.add_circle((ox + swx, oy + swy - 50), 35, dxfattribs={"layer": "Sema", "color": 2})
    msp.add_line((ox + swx + 25, oy + swy - 75), (ox + swx + 90, oy + swy - 160),
                 dxfattribs={"layer": "Sema", "color": 2})
    _txt(msp, "prekidač (D5)", ox + swx - 60, oy + swy - 300, 1.2 * SC, color=8,
         align=TA.RIGHT)
    # F1 and the -48 V from the ICC360 (outdoors, JZ side) in through the JZ wall,
    # up along it to the SZ wall, to the GRO and on over the door to the DC razvod
    cyr = L["cable_y"]
    e = msp.add_lwpolyline([(ox - 350, oy + cyr), (ox + t + 40, oy + cyr),
                            (ox + t + 40, oy + ch - t - 40), (ox + bx, oy + ch - t - 40)],
                           dxfattribs={"layer": "Kabal", "color": 2, "lineweight": 35})
    ltype(e, "DASHED", SC, 1)
    # tank vent: from the tank up and out through the SZ wall to its stand-pipe
    e = msp.add_lwpolyline([(ox + vx, oy + ty + th - 200), (ox + vx, oy + vyt)],
                           dxfattribs={"layer": "Ventilacija", "color": 1, "lineweight": 35})
    ltype(e, "DASHED", SC, 1.5)
    msp.add_circle((ox + vx, oy + vyt), 60, dxfattribs={"layer": "Ventilacija", "color": 1})

    # labels in the plan
    _txt(msp, "DEA 18 kVA / 14,4 kW", ox + ax - 60, oy + sy0 + sl * 0.55, 1.8 * SC,
         color=7, align=TA.MIDDLE_CENTER, rotation=90)
    _txt(msp, f"skid {sl} × {sw}", ox + ax + 150, oy + sy0 + sl * 0.55, 1.4 * SC,
         color=8, align=TA.MIDDLE_CENTER, rotation=90)
    _txt(msp, "HLADNJAK", ox + ax, oy + sy0 + 90, 1.3 * SC, color=8, align=TA.MIDDLE_CENTER)
    _txt(msp, "spremnik 500 l", ox + tx + tw_ / 2 - 40, oy + ty + 120, 1.6 * SC,
         color=7, rotation=90)
    _txt(msp, "dvoplašni", ox + tx + tw_ / 2 + 160, oy + ty + 120, 1.3 * SC,
         color=8, rotation=90)
    _txt(msp, "GRO", ox + gx + gw / 2, oy + gy + gd / 2, 1.6 * SC, color=7,
         align=TA.MIDDLE_CENTER)
    _txt(msp, "prigušivač", ox + ex + 190, oy + (s0 + s1) / 2, 1.3 * SC, color=8,
         align=TA.MIDDLE_CENTER, rotation=90)
    _txt(msp, "servisni prolaz — SI", ox + sx1 + 390, oy + sy0 + 60, 1.4 * SC,
         color=8, rotation=90)
    for lab, x_, y_, rot in (("SZ", ox + 180, oy + ch + 110, 0),
                             ("JI", ox + 560, oy - 190, 0),
                             ("JZ", ox - 130, oy + 2350, 90),
                             ("SI", ox + cw + 170, oy + 700, 90)):
        _txt(msp, lab, x_, y_, 2.0 * SC, layer="Orijentacija", color=1,
             align=TA.MIDDLE_CENTER, rotation=rot)

    # airflow: in through the SI wall at the alternator end, along the genset to
    # the radiator, out through the Stulz cut-outs into the hood and UP; the room
    # fan in the JI wall is an EXTRACT fan (arrow out)
    arrow(msp, [(ox + cw + 700, oy + iyc), (ox + cw - 400, oy + iyc)], size=130)
    arrow(msp, [(ox + ax + 200, oy + sy0 - 10), (ox + ax + 200, oy - 180)], size=110)
    arrow(msp, [(ox + (f0 + f1) / 2, oy + 250), (ox + (f0 + f1) / 2, oy - 550)], size=110)

    # dimensions: container, passages to the skid, plenum, doorway, GRO working space
    dim_h(msp, ox, ox + cw, oy, SC, off=-850)
    dim_v(msp, oy, oy + ch, ox, SC, off=-300)
    dim_h(msp, ox + t, ox + sx0, oy + 1400, SC, off=0)
    dim_h(msp, ox + sx1, ox + cw - t, oy + 1400, SC, off=0)
    dim_v(msp, oy + t, oy + sy0, ox + sx1 + 180, SC, off=0)
    dim_h(msp, ox + d0, ox + kx, oy + ky + 250, SC, off=0)
    dim_free(msp, (ox + sx0, oy + sy1), (ox + 400, oy + gy), (ox + 1000, 0), SC, angle=90)

    # callouts, JZ side (left)
    WXp = ox - 450
    lead(msp, (ox + gx + 80, oy + gy + gd / 2), f"GRO ≤{GRO_W} × {GRO_D} × {GRO_H}",
         (WXp, oy + 2850), SC, h=1.8)
    lead(msp, (ox + t / 2, oy + cyr), "F1 + DC −48 V (ICC360)", (WXp, oy + 1900), SC, h=1.8)
    lead(msp, (ox + ex - 130, oy + s0 + 100), "prigušivač", (WXp, oy + 1000), SC, h=1.8)
    lead(msp, (ox + ex, oy - EXH_OUT), "izduv NO 50 (JI)", (WXp, oy - 450), SC, h=1.8)
    # callouts, SI side (right)
    EXp = ox + cw + 450
    lead(msp, (ox + bx + bw / 2, oy + by), "DC razvod −48 V (≤25 W)", (EXp, oy + 3150),
         SC, h=1.8)
    lead(msp, (ox + kx + kw - 150, oy + ky + 150),
         f"korito {kada['L']} × {kada['W']}, rub {kada['rim_mm']} (ugao SZ/SI)",
         (EXp, oy + 2500), SC, h=1.8)
    lead(msp, (ox + cw - t / 2, oy + i1 - 60), "usis 500 × 700, +0,30 (SI, novo)",
         (EXp, oy + 1850), SC, h=1.8)
    lead(msp, (ox + (f0 + f1) / 2 + 60, oy + t / 2), "ventilator Ø315 — izvlačni (JI)",
         (EXp, oy + 350), SC, h=1.8)
    lead(msp, (ox + hx + hw, oy + hy + hd / 2), "izlaz: otvori Stulz → hauba naviše",
         (EXp, oy - 450), SC, h=1.8)

    north_arrow(msp, 1000, 5800, 550, plan_north=PLAN_NORTH)
    _txt(msp, "OSNOVA  —  kontejner je PRAZAN; klima-uređaj Stulz se demontira", 600, 6900,
         2.4 * SC, color=7)

    # ---------------------------------------------------------------- section 1-1
    # along the genset axis, looking true SI (plan east): SZ on the left, JI on the
    # right; the SI wall with the intake, the tank and the DC razvod seen beyond
    sxo, syo = 6300, 2650

    def S_(y):                                     # container-relative Y -> sheet x
        return sxo + ch - y

    xh = sxo + ch                                   # outer face of the JI wall
    msp.add_line((sxo - 350, syo), (xh + hd + 250, syo),
                 dxfattribs={"layer": "Objekat", "color": 8, "lineweight": 50})
    msp.add_lwpolyline([(sxo, syo), (xh, syo), (xh, syo + H_LO), (sxo, syo + H_LO)],
                       close=True, dxfattribs={"layer": "Objekat", "color": 6, "lineweight": 50})
    e = msp.add_line((sxo - 100, syo + H_HI), (xh + 100, syo + H_HI),
                     dxfattribs={"layer": "Objekat", "color": 6})
    ltype(e, "DASHED", SC, 1.5)
    # cut walls: SZ open below the door head (the plane runs through the door
    # opening); JI with the discharge opening
    for x_, z0, z1 in ((sxo, dh_, H_LO), (xh - t, 0, dz0), (xh - t, dz1, H_LO)):
        solid_rect(msp, x_, syo + z0, t, z1 - z0, "Objekat", 8)
    solid_rect(msp, xh - t, syo + dz0, t, dz1 - dz0, "Ventilacija", 4)
    # deflector hood outside the JI wall: closed bottom and sides, louvre on top
    msp.add_lwpolyline([(xh, syo + dz0 - 50), (xh + hd, syo + dz0 - 50), (xh + hd, syo + HOOD_Z)],
                       dxfattribs={"layer": "Ventilacija", "color": 4, "lineweight": 50})
    e = msp.add_line((xh + hd, syo + HOOD_Z), (xh, syo + HOOD_Z),
                     dxfattribs={"layer": "Ventilacija", "color": 4})
    ltype(e, "DASHED", SC, 1)
    for k in range(1, 5):                                   # louvre blades
        xk = xh + k * hd / 5
        msp.add_line((xk - 50, syo + HOOD_Z + 40), (xk + 50, syo + HOOD_Z - 40),
                     dxfattribs={"layer": "Ventilacija", "color": 4})
    # beyond the cut: the tank in its tray, the DC razvod on the SZ wall, the
    # intake in the SI wall (behind the genset, dashed), the room fan in the JI wall
    rect(msp, S_(ky + kh), syo, kh, kada["rim_mm"], "Agregat", color=1)
    rect(msp, S_(ty + th), syo + 40, th, tk["H"], "Agregat", color=30)
    rect(msp, S_(by + bd), syo + DCB_Z, bd, DCB_H, "Novi1", color=30)
    e = rect(msp, S_(i1), syo + iz0, i1 - i0, iz1 - iz0, "Ventilacija", color=4, lw=35)
    ltype(e, "DASHED", SC, 1)
    e = rect(msp, xh - t, syo + FAN_Z, t, FAN_D, "Ventilacija", color=4, lw=35)
    ltype(e, "DASHED", SC, 1)
    rect(msp, S_(L["lights"]["DC"][1]) - 200, syo + H_LO - 90, 400, 60, "Sema", color=2)
    # frame, skid (cut along its length), radiator band, plenum to the opening
    rect(msp, S_(fy + fdep), syo, fdep, FRAME_H, "Konstrukcija", color=5, lw=35)
    rect(msp, S_(sy1), syo + FRAME_H, sl, g["skid_H"], "Agregat", color=30, lw=50)
    hatch_rect(msp, S_(sy1), syo + FRAME_H, sl, g["skid_H"], "Agregat", "ANSI31",
               SC * 0.3, 30)
    rect(msp, S_(sy0 + 180), syo + FRAME_H + 100, 180, g["skid_H"] - 150, "Agregat",
         color=4, lw=35)
    msp.add_lwpolyline([(S_(sy0), syo + FRAME_H + 150), (S_(t), syo + dz0),
                        (S_(t), syo + dz1), (S_(sy0), syo + FRAME_H + g["skid_H"] - 50)],
                       close=True, dxfattribs={"layer": "Ventilacija", "color": 4,
                                               "lineweight": 35})
    zm = (dz0 + dz1) / 2
    arrow(msp, [(S_(sy0) - 40, syo + zm), (xh + hd / 2, syo + zm)], size=110)
    arrow(msp, [(xh + hd / 2, syo + zm), (xh + hd / 2, syo + HOOD_Z + 650)], size=130)
    # tower platform P I over the roof, broken at both ends
    zp = GEO["tower"]["platforms_m"][0] * 1000
    xa, xb = sxo - 250, xh + hd + 150
    solid_rect(msp, xa, syo + zp, xb - xa, 80, "Konstrukcija", 5)
    for xz in (xa, xb):
        msp.add_lwpolyline([(xz, syo + zp - 120), (xz - 50, syo + zp + 40), (xz + 50, syo + zp + 40),
                            (xz, syo + zp + 200)], dxfattribs={"layer": "Konstrukcija", "color": 5})

    # section labels
    _txt(msp, "DEA 18 kVA", S_(sy0 + sl / 2), syo + FRAME_H + g["skid_H"] + 90, 1.6 * SC,
         color=7, align=TA.CENTER)
    _txt(msp, f"platforma stuba P I +{dec(zp, 1)} m — izduv ne ide iznad krova", xa + 50,
         syo + zp + 180, 1.5 * SC, color=7)
    _txt(msp, f"krov +{dec(H_LO)} / +{dec(H_HI)}", xh - 100, syo + H_HI + 50, 1.3 * SC,
         layer="Kota_tekst", color=8, align=TA.RIGHT)
    _txt(msp, "spremnik (iza)", S_(ty + th / 2), syo + tk["H"] + 110, 1.3 * SC, color=8,
         align=TA.CENTER)
    _txt(msp, "DC razvod (iza)", S_(by) + 60, syo + DCB_Z + DCB_H / 2 - 20, 1.3 * SC,
         color=8)
    _txt(msp, "vrata (u presjeku)", sxo + t + 60, syo + dh_ - 150, 1.3 * SC, color=8)
    _txt(msp, "ventilator (u zidu JI)", xh - t - 60, syo + FAN_Z + FAN_D + 60, 1.3 * SC,
         color=8, align=TA.RIGHT)
    lead(msp, (S_(iyc), syo + iz0 + 100),
         f"usis {i1 - i0:.0f} × {iz1 - iz0}, +{dec(iz0)} (SI zid, iza agregata)",
         (S_(iyc) - 200, syo - 350), SC, h=1.8)
    lead(msp, (xh - t / 2, syo + dz0 + 100),
         f"izlaz {dz1 - dz0} × {L['discharge'][1] - L['discharge'][0]:.0f} "
         f"(otvori Stulz), +{dec(dz0)}", (xh - 600, syo - 700), SC, h=1.8)
    lead(msp, (xh + 50, syo + dz0 - 50),
         f"hauba {HOOD_W} × {HOOD_D} — izlaz NAVIŠE, rešetka +{dec(HOOD_Z)}",
         (xh - 500, syo - 1100), SC, h=1.8)
    lead(msp, (S_((sy0 + t) / 2), syo + zm + 200), "limeni plenum",
         (S_((sy0 + t) / 2) - 700, syo + 1650), SC, h=1.8)
    dim_v(msp, syo, syo + H_LO, xh, SC, off=750)
    _txt(msp, "PRESJEK 1–1  (os agregata — pogled prema SI, SZ lijevo)", 6000, 6900,
         2.4 * SC, color=7)

    note_block(msp, 600, 1450, SC, "NAPOMENE:", [
        "1  DEA FG Wilson P18-6 (Skid) ili ekv., 18 kVA / 14,4 kW, pobuda PMG ili AREP/AUX; "
        "os SZ–JI u sredini, hladnjak JI.",
        "2  RASPORED (obavezujući): Stulz je u sredini JUGOISTOČNOG (JI) zida — izlaz zraka "
        "hladnjaka kroz njegove otvore,",
        "    spojene/proširene na ≥0,36 m² bruto (npr. 600 × 600), limeni plenum; višak "
        "otvora zatvoriti panelom 60 mm.",
        f"3  Vani hauba {HOOD_W} × {HOOD_D}, zatvorenih bočnih strana, rešetka na vrhu "
        f"(+{dec(HOOD_Z)}): topli zrak ide NAVIŠE.",
        f"4  Usis 500 × 700 na SI zidu (+0,30, novo, uz alternator). Izduv NO 50 iz JZ prolaza "
        f"kroz JI zid na ≈+{dec(EXH_Z)} m,",
        f"    ispod platforme stuba; prigušivač, hvatač iskri, kapa; završetak ≥{dec(EXH_OUT)} m "
        f"od zida ({dec(chk['exhaust_intake'])} m od usisa).",
        f"5  GRO ≤{GRO_W} × {GRO_D} × {GRO_H} mm na SZ zidu, jugozapadno od vrata "
        f"(zid {L['gro_wall']:.0f} mm); roštilj OBAVEZAN pod skidom i koritom.",
        f"6  Spremnik 500 l DVOPLAŠNI u koritu {kada['L']} × {kada['W']}, rub "
        f"{kada['rim_mm']} mm, u SJEVERNOM uglu (SZ × SI zid).",
        f"7  SERVIS: prolazi JZ / SI po {L['clr']['west']:.0f} / {L['clr']['east']:.0f} mm, "
        f"{L['clr']['north_gro']:.0f} mm do GRO; od vrata do korita "
        f"{L['clr']['doorway']:.0f} mm slobodno.",
        "8  Unos: skid 620 mm kroz vrata svijetle širine 990 mm, pravo po osi; najprije "
        "agregat, zatim spremnik.",
        "9  Ventilator Ø315 na JI zidu gore je IZVLAČNI (EC 48 V DC, D4). ICC360-HA1-C1 i MTS "
        "vani na JZ strani (H-02).",
        f"10 Odušak spremnika kroz SZ zid — principijelno: {dec(chk['vent_exhaust'])} m "
        f"od izduva, {dec(chk['vent_intake'])} m od usisa; konačno prema elaboratu ZOP.",
        f"11 DC razvod −48 V ≈{DCB_W} × {DCB_H} × {DCB_D} istočno od vrata: rasvjeta "
        "prepreke, vatrodojava, punjač aku., ventilator, predgrijač, D5.",
        "12 Rasvjeta: LED 230 V AC iz GRO (F2, radi dok DEA radi) i LED 48 V DC (D5) sa "
        "prekidačem uz vrata.",
        "13 Raspored je principijelan — Ponuđač ga potvrđuje na licu mjesta (mjere otvora "
        "Stulz, servisne tačke agregata).",
    ])
    return doc


# --------------------------------------------------------------------------
# H-05  Jednopolna šema — novi GRO i DC razvod −48 V                       —
# --------------------------------------------------------------------------
def sheet_h05():
    """Equivalent of Sjednica E-01: the PV DC chain as E-01 draws it, the
    Huawei ICC360, the new GRO (AC, live only while the DEA runs) and the new
    DC razvod -48 V for the always-on loads (user decision 11.09.2026)."""
    SC = 50
    doc, msp = _sheet(SC, "Jednopolna šema — novi GRO i DC razvod −48 V", "H-05", "—")
    LY = "Sema"
    arr, ctl = D["array"], D["control"]
    per_string = arr["modules_total"] // 2
    wp = int(round(arr["kWp"] * 1000 / arr["modules_total"]))

    def box(x, y, w, h, label, sub="", sub2="", color=7, new=False):
        if new:
            hatch_rect(msp, x, y, w, h, LY, "ANSI31", SC * 4, 8)
        rect(msp, x, y, w, h, LY, color=color, lw=50)
        n = 1 + bool(sub) + bool(sub2)
        yy = y + h / 2 + (n - 1) * 95
        _txt(msp, label, x + w / 2, yy, 1.9 * SC, color=7, align=TA.MIDDLE_CENTER)
        for s in (sub, sub2):
            if s:
                yy -= 190
                _txt(msp, s, x + w / 2, yy, 1.5 * SC, color=8, align=TA.MIDDLE_CENTER)

    def wire(*pts, color=7, lw=35):
        msp.add_lwpolyline(pts, dxfattribs={"layer": LY, "color": color, "lineweight": lw})

    def enclosure(x, y, w, h, color, title, sub=""):
        e = rect(msp, x, y, w, h, LY, color=color, lw=35)
        ltype(e, "DASHED", SC, 2)
        _txt(msp, title, x + 150, y + h - 250, 1.8 * SC, color=7)
        if sub:
            _txt(msp, sub, x + 150, y + h - 420, 1.4 * SC, color=8)

    # ---- PV DC chain (as E-01): 2 strings x 6, DC SPD at the array, PVDB, 2 x iSSU
    kwp_s = dec(arr["kWp"] * 1000 / 2)
    box(1300, 12800, 2600, 1000, "STRING 1", f"{per_string} × {wp} Wp = {kwp_s} kWp", color=5)
    box(1300, 11350, 2600, 1000, "STRING 2", f"{per_string} × {wp} Wp = {kwp_s} kWp", color=5)
    _txt(msp, "nosači PV-1 + PV-2", 1300, 12600, 1.6 * SC, color=8)
    _txt(msp, "nosači PV-3 + PV-4", 1300, 11150, 1.6 * SC, color=8)
    box(4500, 12800, 1900, 1000, "SPD DC tip 2", "na polju · string 1", color=1)
    box(4500, 11350, 1900, 1000, "SPD DC tip 2", "na polju · string 2", color=1)
    box(7100, 11900, 2600, 1300, "PVDB 500-15-2B", "IP55 · 2 rute", "DC SPD tip 2", color=5)
    wire((3900, 13300), (4500, 13300), color=5)
    wire((3900, 11850), (4500, 11850), color=5)
    wire((6400, 13300), (6750, 13300), (6750, 12850), (7100, 12850), color=5)
    wire((6400, 11850), (6750, 11850), (6750, 12250), (7100, 12250), color=5)
    wire((9700, 12850), (11200, 12850), (11200, 13300), (12000, 13300), color=5)
    wire((9700, 12250), (11400, 12250), (11400, 11900), (12000, 11900), color=5)

    # ---- Huawei ICC360-HA1-C1 (Buyer's equipment)
    enclosure(11600, 6700, 4800, 7500, 30, "Huawei ICC360-HA1-C1 (oprema Kupca)",
              "vani na ploči, JZ strana — principijelno")
    box(12000, 12900, 2000, 800, "iSSU S4875G2", "MPPT · ruta 1", color=30)
    box(12000, 11500, 2000, 800, "iSSU S4875G2", "MPPT · ruta 2", color=30)
    box(12000, 9300, 2000, 1100, "ISPRAVLJAČI", "R4875 · AC → −48 V",
        f"ulaz ≤{dec(ctl['rect_cap_ac_kw'] * 1000, 1)} kW (SMU)", color=30)
    wire((14700, 7400), (14700, 13400), lw=70)
    _txt(msp, "−48 V DC", 14780, 13450, 1.6 * SC, color=7)
    for y in (13300, 11900, 9850):
        wire((14000, y), (14700, y), color=30)
    box(15000, 12700, 1250, 900, "BATERIJA", "LFP −48 V", color=5)
    box(15000, 10900, 1250, 900, "DC TK", "oprema TK", color=7)
    box(15000, 7700, 1250, 1000, "DC IZLAZ", "rezerva, prekidač", color=7)
    for y in (13150, 11350, 8200):
        wire((14700, y), (15000, y))

    # ---- new GRO (AC) - the DEA is the only AC source
    box(1300, 9300, 2600, 1300, "DEA 18 kVA", "400/230 V · 14,4 kW", "PMG ili AREP/AUX",
        color=30, new=True)
    msp.add_circle((4200, 8900), 60, dxfattribs={"layer": LY, "color": 7})
    _txt(msp, "poz. 2 — rezerva", 4050, 8860, 1.5 * SC, color=8, align=TA.RIGHT)
    enclosure(4400, 5000, 6700, 5900, 30, f"GRO (AC) — NOVO, ≤{GRO_W} × {GRO_D} × {GRO_H} mm",
              "SZ zid kontejnera, jugozapadno od vrata")
    box(4700, 9300, 2200, 1100, "Q0 SKLOPKA IZVORA", "4p · 1-0-2 · 63 A",
        "1 DEA · 0 · 2 rezerva", color=30, new=True)
    wire((3900, 10100), (4700, 10100), color=30)
    wire((4260, 8900), (4500, 8900), (4500, 9550), (4700, 9550), color=30)
    _txt(msp, "1", 4580, 10150, 1.4 * SC, color=8)
    _txt(msp, "2", 4580, 9600, 1.4 * SC, color=8)
    box(4700, 7500, 2200, 1000, "FI0 · RCD 4p", "63 A / 300 mA · S-tip", color=30, new=True)
    wire((5800, 9300), (5800, 8500), color=30)
    wire((5800, 8900), (7500, 8900), color=1)
    box(7500, 8450, 2300, 900, "SPD AC tip 1+2", "Iimp ≥12,5 kA/pol · Up ≤1,5 kV", color=1, new=True)
    wire((5800, 7500), (5800, 7000), color=30)
    wire((4600, 7000), (10900, 7000), color=7, lw=100)
    _txt(msp, "L1 L2 L3 N · 400/230 V", 9100, 7090, 1.4 * SC, color=8)
    # GSI with the one N-PE link and the SPD earth
    for c_, dy in ((2, 0), (3, -60)):
        wire((4600, 5300 + dy), (10900, 5300 + dy), color=c_, lw=50)
    _txt(msp, "PE / GSI", 4650, 5380, 1.4 * SC, color=7)
    wire((4800, 7000), (4800, 5300), color=3, lw=50)
    rect(msp, 4650, 6000, 300, 300, LY, color=3, lw=35)
    _txt(msp, "jedini spoj N–PE (TN-S)", 5000, 5600, 1.4 * SC, color=7)
    wire((8650, 8450), (8650, 5300), color=1)
    feeders = [(6350, "F2 · RCBO", "16 A / 30 mA, A", "RASVJETA AC", "1 svjetiljka", "NOVO"),
               (7400, "F3 · RCBO", "16 A / 30 mA, A", "UTIČNICE", "kontejnera", "NOVO"),
               (8450, "F4", "1p C 16 A", "POMOĆNI", "potrošači DEA", "AC"),
               (9500, "F5", "1p C 16 A", "REZERVA", "", "")]
    for x, b1, b2, l1, l2, l3 in feeders:
        wire((x, 7000), (x, 6600), color=30)
        box(x - 450, 5700, 900, 900, b1, b2, color=30, new=True)
        wire((x, 5700), (x, 4700), color=30)
        box(x - 500, 3300, 1000, 1400, l1, l2, l3, color=7)
    wire((10550, 7000), (10550, 6600), color=30)
    box(10100, 5700, 900, 900, "F1", "3p C 32 A", color=30, new=True)
    wire((11000, 6150), (11350, 6150), (11350, 9850), (12000, 9850), color=30)
    _txt(msp, "F1 kroz JZ zid", 11300, 6500, 1.3 * SC, color=8, rotation=90)

    # ---- new DC razvod -48 V (always-on loads)
    enclosure(16900, 3300, 3450, 7300, 30, "DC RAZVOD −48 V — NOVO",
              "trajni potrošači (≤25 W prosječno)")
    _txt(msp, "SZ zid, sjeveroistočno od vrata", 17050, 9880, 1.3 * SC, color=8)
    wire((16250, 8200), (16650, 8200), (16650, 9600), (17300, 9600), color=5)
    _txt(msp, "−48 V iz ICC360, kroz JZ zid", 16600, 7200, 1.3 * SC, color=8,
         rotation=90)
    wire((17300, 9600), (17300, 3950), lw=70)
    rows = [(8750, "D1", "2p 6 A DC", "RASVJETA PREPREKE", "LED 48 V DC, fotoćelija",
             "nadzor ispada → SMU"),
            (7700, "D2", "2p 6 A DC", "VATRODOJAVA", "DC/DC → centrala",
             "baterije EN 54-4"),
            (6650, "D3", "2p 10 A DC", "PUNJAČ AKU. DEA", "DC/DC, strujni limit",
             "alarm → SMU"),
            (5600, "D4", "2p 10 A DC", "VENTILATOR Ø315", "EC 48 V DC, izvlačni",
             "termostat; stop dok DEA radi"),
            (4550, "D5", "2p 6 A DC", "RASVJETA DC", "LED 48 V DC",
             "prekidač uz vrata"),
            (3500, "D6", "2p 10 A DC", "PREDGRIJAČ DEA", "rashladna tečnost, DC",
             "uključuje ga KOA prije starta")]
    for y, b1, b2, l1, l2, l3 in rows:
        yc = y + 450
        wire((17300, yc), (17550, yc))
        box(17550, y, 900, 900, b1, b2, color=30, new=True)
        wire((18450, yc), (18600, yc))
        box(18600, y - 50, 1650, 1000, l1, l2, l3, color=7)
    e = msp.add_lwpolyline([(20300, 8150), (20300, 6050)],
                           dxfattribs={"layer": LY, "color": 1, "lineweight": 35})
    ltype(e, "DASHED", SC, 1)
    _txt(msp, "blokada pri požaru", 20290, 6400, 1.2 * SC, color=1, rotation=90)

    # ---- earth
    for c_, dy in ((2, 0), (3, -70)):
        wire((1300, 3050 + dy), (20350, 3050 + dy), color=c_, lw=70)
    for x, ytop in ((2600, 9300), (10900, 5300), (13500, 6700), (18600, 3300)):
        wire((x, 3050), (x, ytop), color=2, lw=50)
    _txt(msp, "postojeći uzemljivač FeZn 25×4 (2 prstena na 0,8 m + temelji stuba) · R ≤ 10 Ω "
              "· nosači FN vezani Cu užetom 50 mm² preko bimetalnih spojeva",
         1300, 2760, 1.6 * SC, color=7)

    note_block(msp, 1300, 2450, SC, "NAPOMENE:", h=1.8, lines=[
        "1  Lokacija NIJE na mreži — DEA je jedini AC izvor; izvodi GRO su pod naponom samo dok "
        "DEA radi. Trajni potrošači su na DC razvodu −48 V.",
        "2  TN-S: jedini spoj N–PE je u novom GRO; R ≤ 10 Ω. Odvodnici: AC tip 1+2, DC tip 2 po "
        "stringu, signalni vodovi EN 61643-21.",
        "3  DEA sa nezavisnom pobudom PMG ili AREP/AUX (≥3 × In ≈ 78 A, ≥10 s); RCD 63 A / 300 mA "
        "S-tip je obavezan.",
        f"4  Ulaz ispravljača ograničen na {dec(ctl['rect_cap_ac_kw'] * 1000, 1)} kW dok radi DEA "
        "(SMU). Klima-uređaj Stulz se demontira — nema izvoda za klimatizaciju.",
        f"5  FN: {arr['modules_total']} modula = 2 stringa × {per_string}; PVDB ima 2 rute → "
        "2 × iSSU S4875G2. Požar: STOP DEA i isključenje ventilatora.",
        "6  Nazivne struje F4–F5 i D1–D6 su orijentacione; presjeke i selektivnost potvrđuje "
        "Izvođač. ICC360 — principijelno.",
    ])
    hatch_rect(msp, 1300, 700, 700, 300, LY, "ANSI31", SC * 4, 8)
    rect(msp, 1300, 700, 700, 300, LY, color=8)
    _txt(msp, "isporuka i montaža Izvođača (DEA, GRO, DC razvod −48 V)", 2150, 790,
         1.6 * SC, color=7)
    rect(msp, 7300, 700, 700, 300, LY, color=8)
    _txt(msp, "oprema Kupca (FN, ICC360) i potrošači", 8150, 790, 1.6 * SC, color=7)
    return doc


SHEETS = {"H-01": (sheet_h01, 100), "H-02": (sheet_h02, 100), "H-03": (sheet_h03, 30),
          "H-04": (sheet_h04, 25), "H-05": (sheet_h05, 50)}
