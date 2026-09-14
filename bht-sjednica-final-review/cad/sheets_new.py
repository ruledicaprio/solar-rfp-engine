# -*- coding: utf-8 -*-
"""
Sheets S-02, S-03, M-01 and E-01.

Geometry comes from `design.json`, which carries the numbers settled by the three
expert reviews and by the Investor's site corrections (`review/05-site-corrections.md`).
S-01 lives in build_drawings.py; this module is imported by it.
"""
from __future__ import annotations

import math

from ezdxf.enums import TextEntityAlignment as TA

from bht_frame import draw_frame, new_doc, north_arrow, scale_bar, _txt


FAN_D = 315        # room fan, EC 48 V DC - design.json ventilation.room_fan_m3h


def strip_w_txt(fnd):
    """Strip width for a callout: one figure for the constant section adopted on the
    reviewer's comment (27.08.2026), top/base only if a taper is ever reinstated."""
    swt, swb = fnd["strip_w_top"], fnd["strip_w_base"]
    return f"{swt}" if swt == swb else f"{swt}/{swb}"


def register(B):
    """B is the build_drawings module - reuse its helpers so style stays identical."""
    rect, solid_rect, hatch_rect = B.rect, B.solid_rect, B.hatch_rect
    dim_h, dim_v, leader = B.dim_h, B.dim_v, B.leader
    legend, note_block, site_plan = B.legend, B.note_block, B.site_plan
    _design, GEO = B._design, B.GEO

    # ------------------------------------------------------------------ S-02
    def sheet_s02():
        SC = 50
        D = _design()
        doc = new_doc()
        msp = doc.modelspace()
        draw_frame(msp, SC, naziv="Situacija — BUDUĆE STANJE (LOT 1 + LOT 2)",
                   broj="S-02", razmjera="1:50")

        # PY set so the 9,40 m parcel boundary stays inside the 14850-unit sheet
        # height at 1:50 (it used to overrun the top edge by 150)
        PX, PY = 2600, 5350
        ox, oy = PX + 8000 - 2750, PY + 4700 - 2750
        k = site_plan(msp, ox, oy, SC)
        cx, cy, CW, CH = k["cont"]
        F = k["fence"][2]
        px, py, pw, ph = k["parcel"]

        sup, arr, fnd = D["support"], D["array"], D["foundation"]
        fw, proj, n = sup["field_w"], sup["proj"], arr["count"]
        strip_txt = f"{strip_w_txt(fnd)} × {fnd['strip_l']}"
        # The array stands clear of the compound in the open ground on its true-SW
        # side (plan south) - the whole field, not just the footings, so nothing
        # oversails the fence. Separate stands in one row, 400 mm apart
        # (4x3L, Investor 11.09.2026: small plates rather than one sail).
        ay = oy - proj - 400
        mid = ox + F / 2
        gap = 400
        total_w = n * fw + (n - 1) * gap
        axs = [mid - total_w / 2 + i * (fw + gap) for i in range(n)]

        for i, ax in enumerate(axs, 1):
            rect(msp, ax, ay, fw, proj, "Panel", color=110, lw=70)
            # cross-hatch reads as a module field at 1:50. ANSI37 (the ANSI31
            # family already used on this package) renders reliably; NET came out
            # as a solid fill through the plot backend.
            hatch_rect(msp, ax, ay, fw, proj, "Panel", "ANSI37", SC * 1.2, 110)
            for r in range(1, sup["rows"]):
                msp.add_line((ax, ay + proj * r / sup["rows"]),
                             (ax + fw, ay + proj * r / sup["rows"]),
                             dxfattribs={"layer": "Panel", "color": 8})
            for c in range(1, sup["cols"]):
                msp.add_line((ax + fw * c / sup["cols"], ay),
                             (ax + fw * c / sup["cols"], ay + proj),
                             dxfattribs={"layer": "Panel", "color": 8})
            # strips run across the row under the full horizontal projection of
            # the panel, two per stand at the strip spacing
            sl, sw = sup["strip_l"], sup["strip_w"]
            for so in (fw / 2 - sup["strip_spacing"] / 2,
                       fw / 2 + sup["strip_spacing"] / 2):
                rect(msp, ax + so - sw / 2, ay - (sl - proj) / 2, sw, sl,
                     "Temelj", color=32, lw=35)
            _txt(msp, f"PV-{i}  ·  {sup['modules_each']} × 585 Wp", ax + fw / 2,
                 ay - 450, 2.2 * SC, layer="Tekst", color=7, align=TA.CENTER)

        # DC: each stand to a collector along the fence, one run into the container
        msp.add_lwpolyline([(axs[0] + fw / 2, oy - 380), (axs[-1] + fw / 2, oy - 380)],
                           dxfattribs={"layer": "Kabal", "color": 2, "lineweight": 35})
        msp.add_lwpolyline([(mid, oy - 380), (mid, cy + 150)],
                           dxfattribs={"layer": "Kabal", "color": 2, "lineweight": 35})
        for ax in axs:
            msp.add_lwpolyline([(ax + fw / 2, ay + proj), (ax + fw / 2, oy - 380)],
                               dxfattribs={"layer": "Kabal", "color": 2,
                                           "lineweight": 35})

        v = D["ventilation"]
        # Interior repeats M-01 exactly: skid CENTRED in the free floor with its
        # 720 mm service corridors north and south, tank in the SE corner south
        # of the door. These offsets must track M-01's gx/gy - S-02 was left at
        # the old SW-corner position when M-01 was recentred.
        g, tk = D["genset"], D["tank"]
        gx, gy = cx + 180, cy + 840

        # cross-flow layout (see M-01 / design.json ventilation.layout):
        # intake NORTH wall east end, discharge WEST wall ON THE RADIATOR AXIS.
        # The discharge y is DERIVED from gy, exactly as M-01 derives its dy_c -
        # it used to be hard-coded at cy+130, which was the axis while the skid
        # stood in the SW corner, and it stayed there when the skid was recentred,
        # leaving the louvre 720 mm off the radiator it serves. Anything keyed to
        # the genset position must be computed from gx/gy, never written out.
        dy_c = gy + g["skid_W"] / 2
        solid_rect(msp, cx + 2150, cy + CH - 60, v["intake_mm"][0], 60,
                   "Ventilacija", 4)
        solid_rect(msp, cx, dy_c - v["discharge_mm"][0] / 2, 60,
                   v["discharge_mm"][0], "Ventilacija", 4)
        # room fan: plan EAST wall (true JI), north of the door - same position as
        # M-01 draws it. S-02 used to name it inside the west-wall leader and put no
        # marker on the wall it actually sits in.
        solid_rect(msp, cx + CW - 60, cy + 1900 - FAN_D / 2, 60, FAN_D,
                   "Ventilacija", 4)

        rect(msp, gx, gy, g["skid_L"], g["skid_W"], "Agregat", color=30, lw=50)
        _txt(msp, "DEA 18 kVA", gx + g["skid_L"] / 2, gy + g["skid_W"] / 2,
             1.7 * SC, layer="Tekst", color=7, align=TA.MIDDLE_CENTER)
        # tank only - the drip tray is an M-01 detail and clutters a 1:50 site plan
        tkx, tky = cx + 1845, cy + 80
        rect(msp, tkx, tky, tk["L"], tk["W"], "Agregat", color=30)
        _txt(msp, "500 l", tkx + tk["L"] / 2, tky + tk["W"] / 2,
             1.7 * SC, layer="Tekst", color=7, align=TA.MIDDLE_CENTER)

        dim_h(msp, axs[0], axs[0] + fw, ay, SC, off=-1000)
        dim_v(msp, ay, ay + proj, axs[0], SC, off=-1000)
        # parcel width dimensioned along the top: below the plot there is now the
        # array, its labels and the legend
        dim_h(msp, px, px + pw, py + ph, SC, off=700)
        dim_v(msp, py, py + ph, px + pw, SC, off=1400)

        leader(msp, (cx + 2400, cy + CH - 30),
               "usisna žaluzina 500 × 700 mm — SI zid", 2600, 1500, SC)
        leader(msp, (cx + 30, cy + 730),
               "kanal + žaluzina 600 × 600 i izduv DN 50 — SZ", -1900, 2000, SC)
        leader(msp, (cx + CW - 30, cy + 1900), f"ventilator Ø{FAN_D} — JI",
               1400, 900, SC)
        leader(msp, (mid, oy - 380), "DC trasa PEHD Ø50 → PVDB",
               total_w / 2 + 500, -1250, SC)
        # to the right of the array: to the left it landed on the scale bar
        leader(msp, (axs[-1] + fw - 400, ay + 300),
               f"trake 2 × {n} kom, {strip_txt}", 1200, -700, SC)

        north_arrow(msp, 19500, 11700, 1700,
                    plan_north=D["orientation"]["plan_north_bearing_deg"])
        scale_bar(msp, 1200, 3620, SC, total_m=5, step_m=1)
        # legend bottom-left, notes directly under it - the notes used to sit at
        # x=7900 where the panel-width dimension text ran into them
        bot = legend(msp, 1200, 2900, SC, [
            (110, f"LOT 1 — nosači FN panela PV-1..PV-{n} (po {sup['modules_each']} × 585 Wp, "
                  f"položeno, 45°, azimut {arr['azimuth_deg']}° JZ) — 2 stringa × 6"),
            (32,  f"LOT 1 — AB temeljne trake {strip_txt} mm, dubina {fnd['strip_d']}, "
                  f"razmak {sup['strip_spacing']} mm"),
            (2,   "LOT 1 — DC trasa u PEHD Ø50 do PVDB"),
            (30,  "LOT 2 — DEA 18 kVA u skid izvedbi i dvoplašni spremnik 500 l"),
            (4,   "LOT 2 — usisna žaluzina (SI); kanal, žaluzina i izduv (SZ); ventilator (JI)"),
        ])
        note_block(msp, 1200, bot - 180, SC, "NAPOMENE:", [
            "1  Vjetar qp ≥ 1,20 kN/m²; nosač CUSTOM izrade, proračun dostavlja Ponuđač.",
            f"2  Temelji IZVAN ograde; ivica panela +{arr['bottom_edge'] / 1000:.2f} / "
            f"+{arr['top_edge'] / 1000:.2f} m.".replace(".", ",", 2),
            "3  Zahtjevi: Prilog I, Tačke 3 i 4.",
        ])
        return doc

    # ------------------------------------------------------------------ S-03
    def sheet_s03():
        SC = 30
        D = _design()
        doc = new_doc()
        msp = doc.modelspace()
        draw_frame(msp, SC, naziv="Presjek A–A kroz nosač FN panela", broj="S-03",
                   razmjera="1:30")

        sup, arr = D["support"], D["array"]
        C_H = D["container"]["height"]
        proj = sup["proj"]
        b, top = arr["bottom_edge"], arr["top_edge"]
        # A3 window at 1:30 is 600..12300 x 300..8610, title block x>6900 below
        # y=1740. The panel reaches +4736 above the ground line, so the ground line
        # sits at 2600 and the notes go bottom-left, clear of the title block.
        GX, GY = 2200, 2600
        msp.add_line((GX - 1400, GY), (GX + 9700, GY),
                     dxfattribs={"layer": "Objekat", "color": 8, "lineweight": 50})
        for i in range(26):
            x = GX - 1200 + i * 450
            msp.add_line((x, GY), (x - 150, GY - 150),
                         dxfattribs={"layer": "Objekat", "color": 8})

        x0, y0 = GX + 500, GY + b
        x1, y1 = x0 + proj, GY + top
        msp.add_lwpolyline([(x0, y0), (x1, y1)],
                           dxfattribs={"layer": "Panel", "color": 5, "lineweight": 70})
        msp.add_lwpolyline([(x0, y0 - 80), (x1, y1 - 80)],
                           dxfattribs={"layer": "Panel", "color": 8})
        msp.add_line((x0, y0), (x0, GY), dxfattribs={"layer": "Konstrukcija", "color": 5})
        msp.add_line((x1, y1), (x1, GY), dxfattribs={"layer": "Konstrukcija", "color": 5})
        msp.add_line((x0, y0), (x1, GY), dxfattribs={"layer": "Konstrukcija", "color": 8})
        # ONE strip in this section, not two pads under the panel ends: the two
        # 450 x 3300 strips run NORTH-SOUTH at 1600 mm centres EAST-WEST, so
        # section A-A sees one of them over its full length and the other
        # directly behind the section plane.
        sl, sw = sup["strip_l"], sup["strip_w"]
        fnd_x = x0 - (sl - proj) / 2
        rect(msp, fnd_x, GY - 900, sl, 900, "Temelj", color=32, lw=50)
        hatch_rect(msp, fnd_x, GY - 900, sl, 900, "Temelj", "ANSI31",
                   SC * 0.35, 32)

        # Fence, cut by the section plane, drawn to the certified elevation
        # '461 Graficki dio TEMELJ i OGRADA/04 Ograda.dwg': post 50x50x3 to
        # +2,10 on a footing down to -1,50, framed mesh infill starting +0,20.
        FH, FI = 2100, 200
        fx = x1 + 400
        solid_rect(msp, fx - 25, GY, 50, FH, "Ograda", 8)
        rect(msp, fx - 25, GY, 50, FH, "Ograda", color=8, lw=70)
        rect(msp, fx - 200, GY - 1500, 400, 1500, "Ograda", color=8, lw=50)
        hatch_rect(msp, fx - 200, GY - 1500, 400, 1500, "Ograda", "ANSI31",
                   SC * 0.35, 8)
        # frame rails 30x30 top and bottom of the infill, mesh between them
        for ry in (GY + FI, GY + FH - 30):
            rect(msp, fx - 15, ry, 30, 30, "Ograda", color=8, lw=50)
        hatch_rect(msp, fx - 15, GY + FI + 30, 30, FH - FI - 60, "Ograda",
                   "ANSI37", SC * 0.5, 8)

        # existing slab and container north of the fence, so the section shows what
        # the panel actually oversails
        S_, CH_ = 5400, 2300
        H_LO, H_HI = C_H, D["container"]["height_high_eave"]
        sx_ = fx + 50
        rect(msp, sx_, GY - 300, S_, 300, "Objekat", color=254, lw=35)
        hatch_rect(msp, sx_, GY - 300, S_, 300, "Objekat", "ANSI31", SC * 0.5, 8)

        # true elevation rather than a box: the certified K2 facade gives a 10 %
        # mono-pitch roof, +2,63 at one eave and +2,89 at the other, and the slope
        # runs across the 2300 mm face that this section looks at
        cx_ = sx_ + (S_ - CH_) / 2
        ov = 120                                        # roof overhang, both eaves
        msp.add_lwpolyline([(cx_, GY), (cx_ + CH_, GY),
                            (cx_ + CH_, GY + H_HI), (cx_, GY + H_LO)],
                           close=True,
                           dxfattribs={"layer": "Objekat", "color": 6,
                                       "lineweight": 50})
        msp.add_lwpolyline([(cx_ - ov, GY + H_LO - 40), (cx_ + CH_ + ov, GY + H_HI - 40),
                            (cx_ + CH_ + ov, GY + H_HI + 60), (cx_ - ov, GY + H_LO + 60)],
                           close=True,
                           dxfattribs={"layer": "Objekat", "color": 6,
                                       "lineweight": 50})
        _txt(msp, "postojeći kontejner", cx_ + CH_ / 2, GY + H_LO / 2 + 120,
             2.0 * SC, layer="Tekst", color=7, align=TA.CENTER)
        _txt(msp, f"{CH_} mm · krov u nagibu 10 %", cx_ + CH_ / 2,
             GY + H_LO / 2 - 260, 1.7 * SC, layer="Tekst", color=8, align=TA.CENTER)
        for lvl, lab, xx in ((H_LO, "+2,63", cx_ - ov), (H_HI, "+2,89", cx_ + CH_ + ov)):
            _txt(msp, lab, xx, GY + lvl + 130, 1.7 * SC, layer="Kota_tekst",
                 color=8, align=TA.CENTER)
        _txt(msp, "postojeća AB ploča 5,40 × 5,40 m", sx_ + S_ / 2, GY - 620,
             1.7 * SC, layer="Tekst", color=8, align=TA.CENTER)

        # Base segment of the 38 m lattice tower, drawn to the certified taper
        # (4200 mm at grade narrowing linearly to 1200 mm at 24,60 m per
        # site_geometry.json). The container stands between its legs, so showing
        # it is what makes the section read as the real structure.
        TB, TT, TH = GEO["tower"]["base"][0], GEO["tower"]["top"][0], 24600.0
        tcx_ = sx_ + S_ / 2
        top_ = 5000.0

        def half(h):
            return (TB - (TB - TT) * h / TH) / 2.0

        for s in (-1, 1):
            msp.add_lwpolyline([(tcx_ + s * half(0), GY),
                                (tcx_ + s * half(top_), GY + top_)],
                               dxfattribs={"layer": "Konstrukcija", "color": 5,
                                           "lineweight": 50})
            solid_rect(msp, tcx_ + s * half(0) - 130, GY - 300, 260, 300,
                       "Konstrukcija", 5)
        # local names only - `b` and `lvl` belong to the panel levels below and
        # were being clobbered here, which printed the bottom panel edge as
        # +4,60 instead of +1,50
        brc = [0, 1150, 2300, 3450, 4600]
        for ba, bb in zip(brc, brc[1:]):
            msp.add_line((tcx_ - half(ba), GY + ba), (tcx_ + half(ba), GY + ba),
                         dxfattribs={"layer": "Konstrukcija", "color": 5})
            for s in (-1, 1):                           # bracing, alternating
                msp.add_line((tcx_ + s * half(ba), GY + ba),
                             (tcx_ - s * half(bb), GY + bb),
                             dxfattribs={"layer": "Konstrukcija", "color": 5})
        msp.add_line((tcx_ - half(brc[-1]), GY + brc[-1]),
                     (tcx_ + half(brc[-1]), GY + brc[-1]),
                     dxfattribs={"layer": "Konstrukcija", "color": 5})
        _txt(msp, "antenski stub h=38 m — baza 4,20 × 4,20 m", tcx_,
             GY + top_ + 200, 1.8 * SC, layer="Tekst", color=8, align=TA.CENTER)

        for lvl, lab in ((b, f"donja ivica panela  +{b / 1000:.2f}".replace(".", ",")),
                         (FH, f"kota ograde  +{FH / 1000:.2f}".replace(".", ",")),
                         (top, f"gornja ivica panela  +{top / 1000:.2f}".replace(".", ","))):
            # stop short of the container so the level captions do not land on it
            msp.add_line((GX - 1100, GY + lvl), (cx_ - 320, GY + lvl),
                         dxfattribs={"layer": "Sakriveno", "color": 8})
            _txt(msp, lab, cx_ - 380, GY + lvl - 50, 2.0 * SC,
                 layer="Kota_tekst", color=7, align=TA.RIGHT)

        # above the field, so its extension lines stay out of the notes
        dim_h(msp, x0, x1, GY + top, SC, off=450)
        dim_v(msp, GY, GY + top, GX - 1100, SC, off=-400)
        _txt(msp, "45°", x0 + 700, GY + b + 500, 2.6 * SC, layer="Kote", color=7)
        # kept above y=1740 so they clear the title block, which starts at x=6900
        _txt(msp, "S J E V E R O I S T O K  →", fx + 500, GY - 480, 2.4 * SC,
             layer="Orijentacija", color=1)
        _txt(msp, "←  J U G O Z A P A D", GX - 1100, GY - 480, 2.4 * SC,
             layer="Orijentacija", color=1)
        leader(msp, (fx, GY + 1300), "postojeća ograda h=2,10 m",
               900, 2400, SC)

        fnd = D["foundation"]
        note_block(msp, 700, 1500, SC, "OBJAŠNJENJA:", [
            f"1  Polje: {sup['rows']} reda × {sup['cols']} modul 585 Wp, položeno; projekcija "
            f"{proj} mm pri 45°; {arr['count']} odvojena nosača u nizu.",
            f"2  Dvije trake po nosaču {strip_w_txt(fnd)} × {fnd['strip_l']} mm, d = "
            f"{fnd['strip_d']} mm, razmak {sup['strip_spacing']} mm; C30/37, armatura B500B.",
            f"3  Donja ivica panela +{b / 1000:.2f} m, gornja +{top / 1000:.2f} m."
            .replace(".", ",", 2),
            "4  Postojeća ograda h = 2,10 m (projekat lokacije, 04 Ograda).",
        ])
        return doc

    # ------------------------------------------------------------------ M-01
    def sheet_m01():
        SC = 25
        D = _design()
        doc = new_doc()
        msp = doc.modelspace()
        draw_frame(msp, SC, naziv="DEA u postojećem kontejneru — osnova i presjek",
                   broj="M-01", razmjera="1:25")
        C, g, tk, v = D["container"], D["genset"], D["tank"], D["ventilation"]
        CW, CH = C["ext"]
        t = C["wall"]

        # Plan and section both sit inside the A3 window (500..10250 x 250..7175 at
        # 1:25); the title block occupies x>5750 below y=1450. Keeping to it is what
        # makes the sheet plot at a true 1:25 instead of being shrunk to fit.
        ox, oy = 1900, 3600
        rect(msp, ox, oy, CW, CH, "Objekat", color=6, lw=50)
        rect(msp, ox + t, oy + t, CW - 2 * t, CH - 2 * t, "Objekat", color=6)
        for hx, hy, hw, hh in ((ox, oy, CW, t), (ox, oy + CH - t, CW, t),
                               (ox, oy + t, t, CH - 2 * t),
                               (ox + CW - t, oy + t, t, CH - 2 * t)):
            solid_rect(msp, hx, hy, hw, hh, "Objekat", 8)
        _txt(msp, "OSNOVA  —  kontejner je PRAZAN", ox, oy + CH + 520, 2.6 * SC,
             layer="Tekst", color=7)

        lay = tk["kada"]

        def arrow(pts, color=4):
            msp.add_lwpolyline(pts, dxfattribs={"layer": "Ventilacija",
                                                "color": color, "lineweight": 35})
            (x1, y1), (x0, y0) = pts[-1], pts[-2]
            ang = math.atan2(y1 - y0, x1 - x0)
            a1 = (x1 - 160 * math.cos(ang - 0.42), y1 - 160 * math.sin(ang - 0.42))
            a2 = (x1 - 160 * math.cos(ang + 0.42), y1 - 160 * math.sin(ang + 0.42))
            msp.add_solid([a1, (x1, y1), a2],
                          dxfattribs={"layer": "Ventilacija", "color": color})

        # Interior mirrored N-S (Rev 4): the intake takes air from the NORTH face,
        # which is the shaded side and therefore the coolest air available, while
        # the radiator discharge and the exhaust stay WEST - so nothing is blown at
        # the outdoor cabinets and EL RED-03 stays closed. Genset in the middle,
        # radiator end WEST; tank on the SOUTH wall; GRO on the NORTH wall beside
        # the intake, next to the cabinets it feeds.
        # Rev 7: the 110 % bund is gone - the tank is DOUBLE-SKINNED, so the
        # interstitial space is the secondary containment and only a drip tray
        # (kada) is needed. That is what frees the floor.
        #
        # Rev 7b: the skid is CENTRED in the free floor rather than pushed into
        # the SW corner. It was drawn with its load-spreading frame flush against
        # the west and south walls, which left no way to service two sides of the
        # machine - and the container is empty, so there was never a reason for
        # it. Free depth is 2180 - 740 (frame) = 1440, split evenly:
        #
        #   SOUTH  720 mm service corridor, full length, clear of the kada
        #   NORTH  720 mm (520 clear where the GRO stands proud of the wall)
        #   EAST   1155 mm to the wall - the alternator and control-panel end
        #   WEST   60 mm: the radiator end, which discharges into the duct and
        #          is not serviced from that face
        #
        # gx is held at ox+180 so the frame stops at ox+1790, just short of the
        # kada at ox+1795 - the two never overlap in plan.
        gx, gy = ox + 180, oy + 840
        rect(msp, gx - 60, gy - 60, g["skid_L"] + 120, g["skid_W"] + 120,
             "Konstrukcija", color=5, lw=35)
        rect(msp, gx, gy, g["skid_L"], g["skid_W"], "Agregat", color=30, lw=50)
        _txt(msp, "DEA 18 kVA / 14,4 kW, skid", gx + g["skid_L"] / 2,
             gy + g["skid_W"] / 2, 1.9 * SC, layer="Tekst", color=7,
             align=TA.MIDDLE_CENTER)
        # radiator end (WEST) marked as a band across the skid
        rect(msp, gx, gy, 180, g["skid_W"], "Agregat", color=4, lw=35)
        _txt(msp, "RADIJATOR", gx + 90, gy + g["skid_W"] + 130, 1.4 * SC,
             layer="Tekst", color=8, align=TA.CENTER)

        # radiator duct straight out the WEST wall + discharge louvre 600x600
        dy_c = gy + g["skid_W"] / 2                       # radiator axis
        rect(msp, ox + t, dy_c - 300, gx - ox - t, 600, "Ventilacija", color=4,
             lw=35)
        solid_rect(msp, ox, dy_c - 300, t, 600, "Ventilacija", 4)

        # intake louvre 500 wide in the NORTH wall, east end - clear of both the
        # GRO inside and the outdoor cabinets outside (those sit at x 250..1770)
        solid_rect(msp, ox + 2150, oy + CH - t, v["intake_mm"][0], t,
                   "Ventilacija", 4)

        # new GRO against the NORTH wall, west of the intake
        grw, grd = 800, 200
        rect(msp, ox + 350, oy + CH - t - grd, grw, grd, "Novi1", color=30, lw=50)
        _txt(msp, "GRO", ox + 350 + grw / 2, oy + CH - t - grd / 2 - 55,
             1.6 * SC, layer="Tekst", color=7, align=TA.CENTER)
        # new DC razvod -48 V for the always-on loads, beside the GRO
        solid_rect(msp, ox + 1300, oy + CH - t - 150, 300, 150, "Novi1", 30)
        rect(msp, ox + 1300, oy + CH - t - 150, 300, 150, "Novi1", color=30, lw=50)
        leader(msp, (ox + 1450, oy + CH - t - 75), "DC razvod −48 V", -300, 800, SC)

        # Exhaust DN50 riser at the WEST wall, NORTH of the radiator duct. The
        # duct band moved with the skid to oy+850..oy+1450, so the riser had to
        # move clear of it - it used to sit at oy+1100, which is now inside it.
        exh_y = oy + 1800
        msp.add_circle((ox + t + 90, exh_y), 60,
                       dxfattribs={"layer": "Ventilacija", "color": 1})

        # Tank in its drip tray (kada) in the SE corner. The east door spans
        # oy+700..oy+1600, so the tray stops exactly at its south jamb: the
        # doorway and the route the 620 mm skid takes to its place both stay
        # clear, which is the whole point of moving the tank here.
        bx, by = ox + 1795, oy + t
        rect(msp, bx, by, lay["L"], lay["W"], "Agregat", color=1, lw=35)
        tx, ty = bx + (lay["L"] - tk["L"]) / 2, by + (lay["W"] - tk["W"]) / 2
        rect(msp, tx, ty, tk["L"], tk["W"], "Agregat", color=30, lw=35)
        _txt(msp, "spremnik 500 l", tx + tk["L"] / 2, ty + tk["W"] / 2,
             1.7 * SC, layer="Tekst", color=7, align=TA.MIDDLE_CENTER)
        _txt(msp, "dvoplašni", tx + tk["L"] / 2, ty + tk["W"] / 2 - 230,
             1.4 * SC, layer="Tekst", color=8, align=TA.CENTER)

        # tank vent penetration, SOUTH wall east end
        msp.add_circle((ox + 2800, oy + t / 2), 40,
                       dxfattribs={"layer": "Ventilacija", "color": 1})

        # door in the EAST wall with outward swing; room fan above it to the north
        dy0 = oy + CH / 2 - 450
        solid_rect(msp, ox + CW - t, dy0, t, 900, "Objekat", 0)
        msp.add_line((ox + CW, dy0), (ox + CW + 900, dy0),
                     dxfattribs={"layer": "Objekat", "color": 8})
        msp.add_arc(center=(ox + CW, dy0), radius=900, start_angle=0,
                    end_angle=90, dxfattribs={"layer": "Objekat", "color": 8})
        solid_rect(msp, ox + CW - t, oy + 1750, t, 315, "Ventilacija", 4)

        # airflow arrows: in at the NE from the shaded face, down the aisle, out
        # west through the radiator duct
        arrow([(ox + 2400, oy + CH + 350), (ox + 2400, oy + CH - 550)])
        arrow([(ox + 2300, oy + CH - 750), (gx + g["skid_L"] + 200, dy_c + 250)])
        arrow([(ox + t + 150, dy_c), (ox - 500, dy_c)])

        # service clearances, called out on the drawing so no bidder closes them
        _txt(msp, "servisni prostor 720", ox + 820, oy + 350, 1.5 * SC,
             layer="Tekst", color=8, align=TA.CENTER)
        _txt(msp, "servisni prostor 720", ox + 820, oy + 1690, 1.5 * SC,
             layer="Tekst", color=8, align=TA.CENTER)

        dim_h(msp, ox, ox + CW, oy, SC, off=-800)
        dim_v(msp, oy, oy + CH, ox, SC, off=-800)
        dim_h(msp, ox + 2150, ox + 2650, oy + CH, SC, off=350)
        # A dimension chain for the clearances was tried on the east side and
        # removed: that is where the door swings, and the chain crossed the arc.
        # The two in-plan labels above and note 9 carry the figures instead.

        # Callouts stay short and stay on the sheet; the normative wording lives in
        # the notes below and in Prilog I 4.3.
        leader(msp, (ox + 2400, oy + CH - t / 2), "usis 500 × 700 (SI, +0,30)",
               900, 500, SC)
        leader(msp, (ox + t / 2, dy_c), "žaluzina 600 × 600 (SZ)",
               -380, 1500, SC)
        leader(msp, (ox + t + 90, exh_y), "izduv DN 50 (SZ)", -500, 500, SC)
        leader(msp, (bx + lay["L"] / 2, by), "korito (kada) 1150 × 640, rub 200",
               400, -700, SC)
        leader(msp, (ox + 2800, oy), "oduška (JZ)", 700, -400, SC)
        leader(msp, (ox + CW - t / 2, oy + 1900), "ventilator Ø315 (JI)",
               600, 350, SC)
        leader(msp, (gx + 300, gy - 60), "roštilj ispod skida",
               -700, -900, SC)
        # walls are referenced by cardinal name throughout the TD and Prilog I,
        # so name them on the plan itself
        # note: not tx/ty - those hold the tank origin, which the section reuses
        for label, lx, ly, al in (
                ("S J E V E R O I S T O K", ox + CW / 2, oy + CH + 130, TA.CENTER),
                ("J U G O Z A P A D", ox + CW / 2, oy - 300, TA.CENTER),
                ("S Z", ox - 130, oy + CH / 2 + 400, TA.RIGHT),
                ("J I", ox + CW + 130, oy + CH - 400, TA.LEFT)):
            _txt(msp, label, lx, ly, 2.0 * SC, layer="Orijentacija", color=1,
                 align=al)

        sxo, syo = 6600, 3300
        H = C["height"]
        rect(msp, sxo, syo, CW, H, "Objekat", color=6, lw=50)
        _txt(msp, "PRESJEK 1–1  (pogled prema SI — SZ lijevo)", sxo,
             syo + H + 520, 2.6 * SC, layer="Tekst", color=7)
        msp.add_line((sxo - 500, syo), (sxo + CW + 500, syo),
                     dxfattribs={"layer": "Objekat", "color": 8, "lineweight": 50})

        # genset elevation, radiator end at the WEST (left) wall - same x as the plan
        gxs = sxo + (gx - ox)
        rect(msp, gxs, syo, g["skid_L"], g["skid_H"], "Agregat", color=30, lw=50)
        hatch_rect(msp, gxs, syo, g["skid_L"], g["skid_H"], "Agregat",
                   "ANSI31", SC * 0.3, 30)

        # radiator duct + discharge louvre through the WEST wall
        rect(msp, sxo + t, syo + 380, gxs - sxo - t, 640, "Ventilacija", color=4,
             lw=35)
        solid_rect(msp, sxo, syo + 400, t, 600, "Ventilacija", 4)
        arrow([(sxo + 350, syo + 700), (sxo - 500, syo + 700)])

        # Exhaust: flex off the engine, then the silencer IN LINE on the horizontal
        # run, then the riser up the WEST wall and through the roof. The silencer
        # used to be drawn floating 50 mm above the run and overhanging its east
        # end, which read as a component connected to nothing.
        EY = syo + 1600
        msp.add_lwpolyline([(sxo + 1100, syo + g["skid_H"]), (sxo + 1100, EY),
                            (sxo + 260, EY), (sxo + 260, syo + H + 380)],
                           dxfattribs={"layer": "Ventilacija", "color": 1,
                                       "lineweight": 70})
        rect(msp, sxo + 480, EY - 130, 400, 260, "Ventilacija", color=1, lw=35)
        _txt(msp, "prigušivač", sxo + 920, EY - 60, 1.5 * SC,
             layer="Tekst", color=8)
        _txt(msp, "izduv iznad krova", sxo + 400, syo + H + 200, 1.5 * SC,
             layer="Tekst", color=8)

        # intake louvre on the NORTH wall (behind the section plane) - shown dashed
        # at its true x-position and height
        # drawn in the Ventilacija colour, not dashed-hidden: the tank stands in
        # front of it in this view and two nested dashed rectangles read as one
        rect(msp, sxo + 2150, syo + 300, 500, 700, "Ventilacija", color=4, lw=35)
        # above the 1020 mm genset silhouette and left of the tank outline
        _txt(msp, "usis 500 × 700 (SI, +0,30)", sxo + 1800, syo + 1120,
             1.5 * SC, layer="Tekst", color=8, align=TA.RIGHT)

        # tank in front of the section plane (SOUTH wall), dashed at its plan
        # position - at 1310 mm it stands above the 1020 mm genset silhouette
        rect(msp, sxo + (tx - ox), syo, tk["L"], tk["H"], "Sakriveno", color=8)
        _txt(msp, "spremnik ispred presjeka", sxo + (tx - ox), syo + tk["H"] + 110,
             1.5 * SC, layer="Tekst", color=8)

        # room fan high on the EAST (right) wall
        solid_rect(msp, sxo + CW - t, syo + 1750, t, 315, "Ventilacija", 4)
        _txt(msp, "ventilator", sxo + CW - 700, syo + 2130, 1.5 * SC,
             layer="Tekst", color=8)

        dim_v(msp, syo, syo + H, sxo, SC, off=-700)

        # below the container dimension line at oy-800 = 2800
        # The normative wording lives in Prilog I, Tačka 4; the sheet carries only the
        # dimensions, the positions and the one-line rule (as H-04).
        note_block(msp, 700, 2400, SC, "NAPOMENE:", [
            "1  DEA FG Wilson P18-6 (skid) ili ekv., 18 kVA / 14,4 kW.",
            "2  Usis 500 × 700 SI (+0,30); kanal i žaluzina 600 × 600 te izduv DN 50 SZ; "
            "oduška JZ; ventilator Ø315 JI.",
            "3  Roštilj OBAVEZAN ispod skida i ispod korita.",
            "4  Spremnik DVOPLAŠNI; ispod njega korito 1150 × 640, rub 200 mm.",
            "5  Servisni prolazi 720 mm JZ / 720 mm SI / 1155 mm JI — ne zauzimati.",
            "6  Unos skida 620 mm kroz vrata 900 mm. Kontejner je PRAZAN.",
            "7  DC razvod −48 V na SI zidu uz GRO; trajni potrošači D1–D6 — E-01.",
            "8  Raspored je principijelan; potvrđuje se na licu mjesta. "
            "Zahtjevi: Prilog I, Tačka 4.",
        ])
        return doc

    # ------------------------------------------------------------------ E-01
    def sheet_e01():
        SC = 50
        doc = new_doc()
        msp = doc.modelspace()
        draw_frame(msp, SC, naziv="Jednopolna shema — hibridni sistem napajanja",
                   broj="E-01", razmjera="—")
        L = "Sema"

        def box(x, y, w, h, label, sub="", color=7):
            rect(msp, x, y, w, h, L, color=color, lw=50)
            _txt(msp, label, x + w / 2, y + h / 2 + (150 if sub else -80),
                 2.2 * SC, layer="Tekst", color=7, align=TA.MIDDLE_CENTER)
            if sub:
                _txt(msp, sub, x + w / 2, y + h / 2 - 330, 1.8 * SC,
                     layer="Tekst", color=8, align=TA.MIDDLE_CENTER)
            return (x + w, y + h / 2), (x, y + h / 2)

        def wire(a, b, color=7):
            pts = [a, b] if abs(a[1] - b[1]) < 1 else [a, (b[0], a[1]), b]
            msp.add_lwpolyline(pts, dxfattribs={"layer": L, "color": color,
                                                "lineweight": 35})

        Y = 10200
        # 12 modules wired as 2 strings of 6, not 3 of 4: the priced PVDB500-15-2B
        # has two outputs, and 6 x 51,55 V = 309 V Voc sits inside the iSSU's
        # 85-435 V window. A string therefore spans two supports.
        # The supply boundary is read off the hatch: single 45° lines are what the
        # Contractor supplies and installs, cross-hatch is equipment the BUYER supplies
        # and the Contractor only installs and connects (Prilog I 4.9, Prilog II 5.19).
        # Two PATTERNS, not one pattern turned: the PDF plotter ignores hatch rotation.
        # Hatches go down before the boxes so the outlines stay on top.
        def lot2(x, y, w, h):
            hatch_rect(msp, x, y, w, h, L, "ANSI31", SC * 4, 8)

        def kupac(x, y, w, h):
            hatch_rect(msp, x, y, w, h, L, "ANSI37", SC * 8, 8)

        for _b in ((1600, Y - 700, 2900, 1300),      # STRING 1
                   (1600, Y - 3500, 2900, 1300),     # STRING 2
                   (8400, Y - 2100, 2500, 1300),     # PVDB
                   (11900, Y - 2100, 2600, 1300),    # iSSU
                   (11900, Y - 6200, 2600, 1300),    # ispravljači
                   (15900, Y - 6200, 2500, 1300)):   # baterija
            kupac(*_b)

        s1r, _ = box(1600, Y - 700, 2900, 1300, "STRING 1", "6 × 585 Wp = 3,51 kWp", 5)
        s2r, _ = box(1600, Y - 3500, 2900, 1300, "STRING 2", "6 × 585 Wp = 3,51 kWp", 5)
        _txt(msp, "nosači PV-1 + PV-2", 1600, Y - 900, 1.8 * SC,
             layer="Tekst", color=8)
        _txt(msp, "nosači PV-3 + PV-4", 1600, Y - 3700, 1.8 * SC,
             layer="Tekst", color=8)
        spd1r, spd1l = box(5500, Y - 700, 1900, 1300, "SPD DC", "tip 2 · string 1", 1)
        spd2r, spd2l = box(5500, Y - 3500, 1900, 1300, "SPD DC", "tip 2 · string 2", 1)
        pvdbr, pvdbl = box(8400, Y - 2100, 2500, 1300, "PVDB",
                           "500-15-2B · IP55 · 2 rute", 5)
        issur, issul = box(11900, Y - 2100, 2600, 1300, "iSSU", "S4875G2 · MPPT", 30)
        wire(s1r, spd1l, 5)
        wire(s2r, spd2l, 5)
        wire(spd1r, (pvdbl[0], pvdbl[1] + 300), 5)
        wire(spd2r, (pvdbl[0], pvdbl[1] - 300), 5)
        wire(pvdbr, issul, 5)

        for _x, _y, _w, _h in ((1600, Y - 6200, 2900, 1300),
                               (5500, Y - 6200, 1900, 1300),
                               (8400, Y - 6200, 2500, 1300),
                               (8400, Y - 4300, 2500, 800)):
            lot2(_x, _y, _w, _h)

        gr, _ = box(1600, Y - 6200, 2900, 1300, "DEA 18 kVA", "14,4 kW · skid", 30)
        atsr, atsl = box(5500, Y - 6200, 1900, 1300, "SKLOPKA IZVORA", "1 DEA · 0 · 2 rezerva",
                         30)
        grol, gror = box(8400, Y - 6200, 2500, 1300, "GRO",
                         "sekcije AGREGAT / SOLAR", 30)
        wire(gr, atsl, 30)
        wire(atsr, gror if False else (8400, Y - 5550), 30)
        box(8400, Y - 4300, 2500, 800, "SPD AC  tip 1+2", "", 1)
        msp.add_lwpolyline([(9650, Y - 4900), (9650, Y - 4300)],
                           dxfattribs={"layer": L, "color": 1, "lineweight": 35})

        rectr, rectl = box(11900, Y - 6200, 2600, 1300, "ISPRAVLJAČI",
                           "R4875 · −48 V DC", 30)
        wire((10900, Y - 5550), rectl, 30)
        battr, battl = box(15900, Y - 6200, 2500, 1300, "BATERIJA", "LFP  −48 V", 5)
        dcr, dcl = box(15900, Y - 1100, 2500, 1300, "DC RAZVOD",
                       "potrošači 1,18 kW", 7)
        wire(issur, dcl, 30)
        wire(rectr, battl, 30)
        msp.add_lwpolyline([(17150, Y - 4900), (17150, Y - 1100)],
                           dxfattribs={"layer": L, "color": 7, "lineweight": 50})
        # new DC razvod -48 V for the always-on loads (LOT 2), tapped off the bus
        lot2(18000, Y - 3500, 2000, 1300)
        box(18000, Y - 3500, 2000, 1300, "DC −48 V", "NOVO · D1–D6", 30)
        wire((17150, Y - 2850), (18000, Y - 2850), 30)

        # Earth bar raised so the bonding stubs actually reach the equipment they
        # bond, and drawn as a yellow-green pair - the PE colour convention, and
        # it separates the bar from every other line on the sheet at a glance.
        EB = Y - 7000
        msp.add_lwpolyline([(1600, EB), (18400, EB)],
                           dxfattribs={"layer": "Uzemljenje", "color": 2,
                                       "lineweight": 70})
        msp.add_lwpolyline([(1600, EB - 90), (18400, EB - 90)],
                           dxfattribs={"layer": "Uzemljenje", "color": 3,
                                       "lineweight": 70})
        for x in (3050, 9650, 13200, 17150):
            msp.add_lwpolyline([(x, EB), (x, Y - 6200)],
                               dxfattribs={"layer": "Uzemljenje", "color": 2,
                                           "lineweight": 50})
        _txt(msp, "postojeći prstenasti uzemljivač Fe/Zn 25×4 · R ≤ 10 Ω · nosači FN "
                  "na Cu uže 50 mm²", 1600, EB - 620, 2.3 * SC, layer="Tekst", color=7)

        note_block(msp, 1600, Y - 8100, SC, "NAPOMENE:", h=2.3, lines=[
            "1  Lokacija nije na mreži; DEA je jedini AC izvor. Sklopka: 1 DEA · 0 · 2 rezerva.",
            "2  TN-S, spoj N–PE samo u novom GRO. Odvodnici: AC tip 1+2, DC tip 2 po stringu.",
            "3  FN: 12 modula = 2 stringa × 6 (PV-1 + PV-2, PV-3 + PV-4); PVDB ima 2 rute.",
            "4  DC razvod −48 V (novo), D1–D6: trajni potrošači prema Prilogu I, Tačka 4.5.",
        ])

        # supply-boundary keys, one row along the bottom (as H-05)
        for kx, pat, sc_, txt in ((1600, "ANSI31", 4, "isporuka i montaža Izvođača (LOT 2)"),
                                  (7200, "ANSI37", 8, "oprema Kupca — ugradnja u LOT 2")):
            hatch_rect(msp, kx, Y - 9500, 700, 300, L, pat, SC * sc_, 8)
            rect(msp, kx, Y - 9500, 700, 300, L, color=8)
            _txt(msp, txt, kx + 850, Y - 9420, 2.0 * SC, layer="Tekst", color=7)
        return doc

    return {"S-02": sheet_s02, "S-03": sheet_s03, "M-01": sheet_m01,
            "E-01": sheet_e01}
