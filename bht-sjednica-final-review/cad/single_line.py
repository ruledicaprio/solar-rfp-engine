# -*- coding: utf-8 -*-
"""
The single-line scheme, drawn once and used by both sites.

E-01 (Sjednica) and H-05 (Hamzići) show the SAME system: the PV DC chain into the
Buyer's Huawei ICC360, the new GRO on the AC side - live only while the DEA runs -
and the new DC razvod -48 V that carries the always-on loads. They used to be two
independent drawings and drifted apart: E-01 was a block diagram with 11 hatched
elements and no consumers at all, H-05 had 22, the GRO internals and every load
named. Worse, E-01 left the DC SPD boxes and the TK-load box unhatched, so the
supply boundary could not be read off them.

Both sheets are now this one function. What genuinely differs per site - the wall a
box sits on, the cable route, the earthing arrangement - comes in through `cfg`;
nothing else may diverge.

Supply convention, identical on both sheets - a band along the BOTTOM EDGE of each
box, not a hatch across its face:
    ANSI31, single 45° lines  = the Contractor supplies and installs it
    ANSI37, cross-hatch       = the BUYER supplies it, the Contractor installs and
                                connects it only (Prilog I 4.9, Prilog II 5.19)
Across the whole face the pattern came out as two or three long diagonals through
the labels at this scale - it read as neither hatch nor text. In a 180-unit band it
is dense enough to be recognised as a pattern and the face stays clean.

`B` is the build_drawings module, passed in rather than imported, because
build_drawings imports the sheet modules - importing it back here would be a cycle.
"""
from __future__ import annotations

from ezdxf.enums import TextEntityAlignment as TA

from bht_frame import _txt


def dec(v, nd=2):
    """millimetres -> metres with a decimal comma: 1800 -> '1,80'.

    Same helper as sheets_hamzici.dec; the call sites below scale by 1000 first,
    so kWp and kW come out as '3,51' and '9,5'.
    """
    return f"{v / 1000:.{nd}f}".replace(".", ",")


def ltype(e, name, sc, k=3.0):
    """Dashed/─ line type on an entity, scaled to the sheet."""
    e.dxf.linetype = name
    e.dxf.ltscale = sc * k
    return e


BAND_H = 180        # visina trake isporuke; 3,6 mm na 1:50


def draw(msp, SC, D, B, cfg):
    """Draw the scheme into `msp`. `cfg` carries only the per-site differences."""
    rect, hatch_rect, note_block = B.rect, B.hatch_rect, B.note_block
    LY = "Sema"
    arr, ctl = D["array"], D["control"]
    per_string = arr["modules_total"] // 2
    wp = int(round(arr["kWp"] * 1000 / arr["modules_total"]))
    cap_w = dec(ctl["rect_cap_ac_kw"] * 1000, 1)

    def band(x, y, w, h, pattern, scale):
        """Traka isporuke uz donju ivicu kutije, umjesto šrafure preko cijelog lica.

        Preko cijele kutije šrafura je na ovom mjerilu davala dvije-tri velike
        dijagonale koje su išle kroz natpise: nije se čitala ni kao šrafura ni
        kao tekst.  U traci je gušća, pa se prepoznaje kao uzorak, a lice kutije
        ostaje čisto."""
        hb = min(BAND_H, 0.25 * h)
        hatch_rect(msp, x, y, w, hb, LY, pattern, scale, 8)
        msp.add_line((x, y + hb), (x + w, y + hb),
                     dxfattribs={"layer": LY, "color": 8})

    def box(x, y, w, h, label, sub="", sub2="", color=7, new=False, kupac=False):
        if new:
            band(x, y, w, h, "ANSI31", SC * 0.5)
        if kupac:
            band(x, y, w, h, "ANSI37", SC * 0.6)
        rect(msp, x, y, w, h, LY, color=color, lw=50)
        n = 1 + bool(sub) + bool(sub2)
        yy = y + h / 2 + (n - 1) * 95
        _txt(msp, label, x + w / 2, yy, 1.9 * SC, color=7, align=TA.MIDDLE_CENTER)
        for s in (sub, sub2):
            if s:
                yy -= 190
                _txt(msp, s, x + w / 2, yy, 1.5 * SC, color=8, align=TA.MIDDLE_CENTER)

    def wire(*pts, color=7, lw=35):
        msp.add_lwpolyline(pts, dxfattribs={"layer": LY, "color": color,
                                            "lineweight": lw})

    def enclosure(x, y, w, h, color, title, sub=""):
        e = rect(msp, x, y, w, h, LY, color=color, lw=35)
        ltype(e, "DASHED", SC, 2)
        _txt(msp, title, x + 150, y + h - 250, 1.8 * SC, color=7)
        if sub:
            _txt(msp, sub, x + 150, y + h - 420, 1.4 * SC, color=8)

    # ---- PV DC chain: 2 strings x 6, DC SPD at the array, PVDB, 2 x iSSU -----
    kwp_s = dec(arr["kWp"] * 1000 / 2)
    box(1300, 12800, 2600, 1000, "STRING 1", f"{per_string} × {wp} Wp = {kwp_s} kWp",
        color=5, kupac=True)
    box(1300, 11350, 2600, 1000, "STRING 2", f"{per_string} × {wp} Wp = {kwp_s} kWp",
        color=5, kupac=True)
    _txt(msp, "nosači PV-1 + PV-2", 1300, 12600, 1.6 * SC, color=8)
    _txt(msp, "nosači PV-3 + PV-4", 1300, 11150, 1.6 * SC, color=8)
    # the DC SPDs are the Contractor's supply (Prilog II 5.13) - E-01 used to leave
    # these two boxes unhatched, which is what made the two sheets disagree
    box(4500, 12800, 1900, 1000, "SPD DC tip 2", "na polju · string 1", color=1, new=True)
    box(4500, 11350, 1900, 1000, "SPD DC tip 2", "na polju · string 2", color=1, new=True)
    box(7100, 11900, 2600, 1300, "PVDB 500-15-2B", "IP55 · 2 rute", "DC SPD tip 2",
        color=5, kupac=True)
    wire((3900, 13300), (4500, 13300), color=5)
    wire((3900, 11850), (4500, 11850), color=5)
    wire((6400, 13300), (6750, 13300), (6750, 12850), (7100, 12850), color=5)
    wire((6400, 11850), (6750, 11850), (6750, 12250), (7100, 12250), color=5)
    wire((9700, 12850), (11200, 12850), (11200, 13300), (12000, 13300), color=5)
    wire((9700, 12250), (11400, 12250), (11400, 11900), (12000, 11900), color=5)

    # ---- Huawei ICC360-HA1-C1, the Buyer's equipment -------------------------
    enclosure(11600, 6700, 4800, 7500, 30, cfg["huawei_title"], cfg["huawei_sub"])
    box(12000, 12900, 2000, 800, "iSSU S4875G2", "MPPT · ruta 1", color=30, kupac=True)
    box(12000, 11500, 2000, 800, "iSSU S4875G2", "MPPT · ruta 2", color=30, kupac=True)
    box(12000, 9300, 2000, 1100, "ISPRAVLJAČI", "R4875 · AC → −48 V",
        f"ulaz ≤{cap_w} kW (SMU)", color=30, kupac=True)
    wire((14700, 7400), (14700, 13400), lw=70)
    _txt(msp, "−48 V DC", 14780, 13450, 1.6 * SC, color=7)
    for y in (13300, 11900, 9850):
        wire((14000, y), (14700, y), color=30)
    box(15000, 12700, 1250, 900, "BATERIJA", "LFP −48 V", color=5, kupac=True)
    # the TK load and the spare outlet are the Buyer's too - E-01 drew the TK load
    # as a grey solid, which read as neither party's supply
    box(15000, 10900, 1250, 900, "DC TK", "oprema TK", color=7, kupac=True)
    box(15000, 7700, 1250, 1000, "DC IZLAZ", "rezerva, prekidač", color=7, kupac=True)
    for y in (13150, 11350, 8200):
        wire((14700, y), (15000, y))

    # ---- new GRO (AC): the DEA is the only AC source -------------------------
    # QS stands between the set and the changeover; Q1 is the incomer breaker.
    # Both were in BOQ 5.6 all along but on neither sheet, so the predmjer and the
    # scheme disagreed about what is in the board. QS is 4-pole and Q1 replaces the
    # three single-pole C 32 A devices that RED-09 (03-electrical.md) rejected.
    box(1300, 9300, 2000, 1300, "DEA 18 kVA", "400/230 V · 14,4 kW", "PMG ili AREP/AUX",
        color=30, new=True)
    box(3500, 9500, 1000, 800, "QS", "4p · 0-1 · 50 A", color=30, new=True)
    msp.add_circle((4200, 8900), 60, dxfattribs={"layer": LY, "color": 7})
    _txt(msp, "poz. 2 — rezerva", 3450, 8700, 1.5 * SC, color=8)
    enclosure(3400, 5000, 7700, 5900, 30, cfg["gro_title"], cfg["gro_sub"])
    box(4700, 9500, 2200, 900, "Q0 SKLOPKA IZVORA", "4p · 1-0-2 · 50 A",
        "1 DEA · 0 · 2 rezerva", color=30, new=True)
    wire((3300, 10100), (3500, 10100), color=30)
    wire((4500, 10100), (4700, 10100), color=30)
    wire((4260, 8900), (4500, 8900), (4500, 9550), (4700, 9550), color=30)
    _txt(msp, "1", 4580, 10150, 1.4 * SC, color=8)
    _txt(msp, "2", 4580, 9600, 1.4 * SC, color=8)
    box(4700, 8300, 2200, 900, "Q1 · MCCB 4p (3P+N)", "32 A · podesivo magnetno",
        color=30, new=True)
    box(4700, 7200, 2200, 900, "FI0 · RCD 4p", "50 A/300 mA · S-tip, tip A",
        color=30, new=True)
    wire((5800, 9500), (5800, 9200), color=30)
    wire((5800, 8300), (5800, 8100), color=30)
    wire((5800, 9350), (7500, 9350), color=1)
    box(7500, 8900, 2300, 900, "SPD AC tip 1+2", "Iimp ≥12,5 kA/pol · Up ≤1,5 kV",
        color=1, new=True)
    wire((5800, 7200), (5800, 7000), color=30)
    wire((4600, 7000), (10900, 7000), color=7, lw=100)
    _txt(msp, "L1 L2 L3 N · 400/230 V", 9100, 7090, 1.4 * SC, color=8)
    for c_, dy in ((2, 0), (3, -60)):
        wire((4600, 5300 + dy), (10900, 5300 + dy), color=c_, lw=50)
    _txt(msp, "PE / GSI", 4650, 5380, 1.4 * SC, color=7)
    wire((4800, 7000), (4800, 5300), color=3, lw=50)
    rect(msp, 4650, 6000, 300, 300, LY, color=3, lw=35)
    _txt(msp, "jedini spoj N–PE (TN-S)", 5000, 5600, 1.4 * SC, color=7)
    wire((8650, 8900), (8650, 5300), color=1)
    feeders = [(6350, "F2 · RCBO", "16 A / 30 mA, A", "RASVJETA AC", "1 svjetiljka", "NOVO"),
               (7400, "F3 · RCBO", "16 A / 30 mA, A", "UTIČNICE", "kontejnera", "NOVO"),
               (8450, "F4", "1p C 16 A", "POMOĆNI", "potrošači DEA", "AC"),
               (9500, "F5", "1p C 16 A", "REZERVA", "", "")]
    for x, b1, b2, l1, l2, l3 in feeders:
        wire((x, 7000), (x, 6600), color=30)
        box(x - 450, 5700, 900, 900, b1, b2, color=30, new=True)
        wire((x, 5700), (x, 4700), color=30)
        box(x - 500, 3300, 1000, 1400, l1, l2, l3, color=7, new=True)
    wire((10550, 7000), (10550, 6600), color=30)
    box(10100, 5700, 900, 900, "F1", "3p C 20 A", color=30, new=True)
    wire((11000, 6150), (11350, 6150), (11350, 9850), (12000, 9850), color=30)
    _txt(msp, cfg["f1_route"], 11300, 6500, 1.3 * SC, color=8, rotation=90)

    # ---- new DC razvod -48 V, the always-on loads ----------------------------
    enclosure(16900, 3300, 3450, 7300, 30, "DC RAZVOD −48 V — NOVO",
              "trajni potrošači (≤25 W prosječno)")
    _txt(msp, cfg["dc_wall"], 17050, 9880, 1.3 * SC, color=8)
    wire((16250, 8200), (16650, 8200), (16650, 9600), (17300, 9600), color=5)
    _txt(msp, cfg["dc_feed"], 16600, 7200, 1.3 * SC, color=8, rotation=90)
    wire((17300, 9600), (17300, 3950), lw=70)
    # "rasvjeta stuba", not "rasvjeta prepreke" (Naručilac, 15.09.2026)
    rows = [(8750, "D1", "2p 6 A DC", "RASVJETA STUBA", "LED 48 V DC, fotoćelija",
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
        box(18600, y - 50, 1650, 1000, l1, l2, l3, color=7, new=True)
    e = msp.add_lwpolyline([(20300, 8150), (20300, 6050)],
                           dxfattribs={"layer": LY, "color": 1, "lineweight": 35})
    ltype(e, "DASHED", SC, 1)
    _txt(msp, "blokada pri požaru", 20290, 6400, 1.2 * SC, color=1, rotation=90)

    # ---- earth ---------------------------------------------------------------
    for c_, dy in ((2, 0), (3, -70)):
        wire((1300, 3050 + dy), (20350, 3050 + dy), color=c_, lw=70)
    for x, ytop in ((2600, 9300), (10900, 5300), (13500, 6700), (18600, 3300)):
        wire((x, 3050), (x, ytop), color=2, lw=50)
    _txt(msp, cfg["earth_text"], 1300, 2760, 1.6 * SC, color=7)

    note_block(msp, 1300, 2450, SC, "NAPOMENE:", h=1.5, lines=[
        "1  DEA je jedini izvor izmjeničnog napona; trajni potrošači su na DC razvodu −48 V.",
        "2  Sistem TN-S, spoj N–PE samo u novom GRO; R ≤ 10 Ω. Odvodnici: AC tip 1+2, DC tip 2.",
        "3  DEA sa pobudom PMG ili AREP/AUX; RCD 50 A / 300 mA, najmanje tip A, S-tip.",
        f"4  Ulaz ispravljača ograničen je na {cap_w} kW tokom rada DEA. {cfg['note4_tail']}",
        f"5  FN: {arr['modules_total']} modula = 2 stringa × {per_string}; pri požaru DEA se zaustavlja.",
        "6  Nazivne struje su orijentacione; potvrđuje ih Izvođač.",
    ])
    # uzorci u legendi su umanjene kutije, sa istom trakom uz donju ivicu
    for lx, pat, sc_, txt in (
            (1300, "ANSI31", SC * 0.5,
             "isporuka i montaža Izvođača (DEA, GRO, DC razvod −48 V)"),
            (7300, "ANSI37", SC * 0.6,
             "oprema Kupca (FN, PVDB, iSSU, baterije, ICC360)")):
        hatch_rect(msp, lx, 700, 700, 150, LY, pat, sc_, 8)
        msp.add_line((lx, 850), (lx + 700, 850),
                     dxfattribs={"layer": LY, "color": 8})
        rect(msp, lx, 700, 700, 500, LY, color=8)
        _txt(msp, txt, lx + 850, 890, 1.6 * SC, color=7)
