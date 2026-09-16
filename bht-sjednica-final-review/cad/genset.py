# -*- coding: utf-8 -*-
"""
Obris agregata i spremnika goriva — zajednički za obje lokacije.

M-01 (Sjednica) i H-04 (Hamzići) su do sada prikazivali agregat i spremnik kao
obične pravougaonike, bez ijedne kote na samoj opremi.  Ovaj modul crta oboje kao
obris sa prepoznatljivim sklopovima i nosi kotni lanac, pa se oba lista crtaju iz
istog izvora — isto kao što single_line.py crta E-01 i H-05.

**Zašto nije preuzeto iz isporučenih DWG-ova.**  U EQUIPEMENT/GENSET/ stoje
FG_Wilson_P_22-6_TOP_VIEW.dwg i _SHORT_SIDE_GEN_VIEW.dwg.  Oba su automatski
trasirana iz rastera: vanjski obris tlocrta ima 928 tjemena za oblik koji je
pravougaonik, a cijela površina je posuta mrljama traga.  Odnos stranica tog
obrisa je 1072 : 510 = 2,10, dok je stvarni skid 1550 : 620 = 2,50 — raster nije
imao kvadratni piksel, pa je trag i geometrijski iskrivljen.  (Uz to su
FG_Wilson_500L_TANK_LONG_SIDE_VIEW.pdf i FG_Wilson_P_22-6_LONG_SIDE_VIEW.pdf
bajt-identični, tj. spremnik nema svoj bočni pogled.)  Takav trag se ne smije
kotirati, pa je obris ovdje nacrtan parametarski.

**Šta je obavezujuće.**  Kotira se isključivo gabarit skida 1550 × 620 × 1020 mm
i masa, koji su očitani iz tehničkog lista proizvođača (EQUIPEMENT/GENSET/P18-6.pdf,
str. 1: Length 1550, Width 620, Height 1020, Weight wet 372 kg) i stoje u
design.json → genset.  Podjela na radijator / motor / generator / komandni ormar
je načelni raspored sklopova prema općem rasporedu proizvođača, prikazan da bi se
čitao smjer strujanja i pristup opremi; te podjele se NE kotiraju i nisu zahtjev.
Isto važi za spremnik: kotira se 1050 × 600 × 1310 i korito 1150 × 640
(design.json → tank), a priključci su prikazani načelno.
"""
from __future__ import annotations

import math

from ezdxf.enums import TextEntityAlignment as TA

from bht_frame import _txt

# --------------------------------------------------------------------------
# Raspored sklopova na skidu, u lokalnim koordinatama:
#   u — uzduž skida, od čela RADIJATORA (0) prema generatoru (skid_L)
#   v — poprijeko skida (0 .. skid_W)
# Sve vrijednosti su načelne i ne kotiraju se; kotira se samo gabarit.
# --------------------------------------------------------------------------
FRAME_IN = 60      # unutrašnja ivica čeličnog rama skida
M_IN = 45          # bok mašine uvučen od ivice skida
RAD_U = 210        # radijator sa zaštitnom mrežom
FAN_U, FAN_R = 300, 185    # ventilator radijatora
ENG_U = (210, 930)         # motor sa kućištem zamašnjaka
ALT_U = (960, 1330)        # generator
ALT_IN = 80                # generator je uži od motora
CP_U = (1080, 1400)        # komandni ormar, bočno nad generatorom
CP_D = 165                 # njegova dubina u tlocrtu
EXH_U = 920                # izlaz izduva sa motora  (M-01 diže vertikalu na ovoj osi)
FUEL_U = (690, 780)        # dovod i povrat goriva
TB_U = (1330, 1450)        # priključna kutija generatora

# Visinski raspored (bočni pogled): skid_H = 1020 je vrh komandnog ormara.
BASE_H = 120       # čelični ram skida
RAD_H = 900        # jezgro radijatora
ENG_H = 760        # blok motora
HUMP_U = (520, 780)        # filter zraka / usisna grana
HUMP_H = 900
ALT_H = 700
CP_Z = 700         # donja ivica komandnog ormara


# --------------------------------------------------------------------------
def _xf(x, y, radiator, sl, sw):
    """f(u, v) -> (X, Y): lokalni sistem skida u koordinate lista.

    `radiator` je strana lista na koju gleda čelo radijatora: W / E / S / N.
    U svakom slučaju je riječ o rotaciji, nikad o zrcaljenju, pa natpisi i
    redoslijed sklopova ostaju isti kao na drugom listu.
    """
    if radiator == "W":
        return lambda u, v: (x + u, y + v)
    if radiator == "E":
        return lambda u, v: (x + sl - u, y + sw - v)
    if radiator == "S":
        return lambda u, v: (x + sw - v, y + u)
    if radiator == "N":
        return lambda u, v: (x + v, y + sl - u)
    raise ValueError(f"radiator={radiator!r}, očekivano W/E/S/N")


def _poly(msp, f, pts, layer, color, lw=None, close=True):
    at = {"layer": layer, "color": color}
    if lw is not None:
        at["lineweight"] = lw
    return msp.add_lwpolyline([f(u, v) for u, v in pts], close=close,
                              dxfattribs=at)


def _box(msp, f, u0, v0, u1, v1, layer, color, lw=None):
    return _poly(msp, f, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)],
                 layer, color, lw)


# --------------------------------------------------------------------------
def plan(msp, B, x, y, sc, D, radiator="W", labels=True, dims=True,
         detail=2):
    """Tlocrt agregata; (x, y) = donji lijevi ugao pravougaonika skida na listu.

    Kod `radiator` "W"/"E" skid leži dužinom po X (gabarit sl × sw), kod "S"/"N"
    po Y (gabarit sw × sl) — isto kao što su ga oba lista i do sada postavljala.

    `detail` je nivo razrade, jer se isti obris crta u tri mjerila:
        2 — 1:25 (M-01, H-04): sve, sa priključcima i ventilatorom
        1 — 1:50 (S-02): skid, radijator, motor i generator
        0 — 1:100 (H-02): samo skid sa čelom radijatora

    Vraća rječnik karakterističnih tačaka u koordinatama lista, da pozivna
    mjesta mogu na njih zakačiti izvode.
    """
    detail = int(detail)
    g = D["genset"]
    sl, sw = g["skid_L"], g["skid_W"]
    f = _xf(x, y, radiator, sl, sw)
    mid = sw / 2

    # čelični ram skida — nosivi element, najdeblja linija
    _box(msp, f, 0, 0, sl, sw, "Agregat", 30, 50)
    if detail >= 2:
        _box(msp, f, FRAME_IN, FRAME_IN, sl - FRAME_IN, sw - FRAME_IN,
             "Agregat", 30, 25)

    # radijator na čelu + ventilator iza njega: odavde se čita smjer strujanja
    _box(msp, f, 0, M_IN, RAD_U, sw - M_IN, "Agregat", 4, 35)
    if detail >= 2:
        for k in range(1, 5):                       # lamele jezgra radijatora
            vk = M_IN + k * (sw - 2 * M_IN) / 5
            msp.add_line(f(20, vk), f(RAD_U - 20, vk),
                         dxfattribs={"layer": "Agregat", "color": 4})
        cx, cy = f(FAN_U, mid)
        msp.add_circle((cx, cy), FAN_R,
                       dxfattribs={"layer": "Ventilacija", "color": 4})
        msp.add_circle((cx, cy), FAN_R * 0.22,
                       dxfattribs={"layer": "Ventilacija", "color": 4})

    # motor, generator, komandni ormar
    if detail >= 1:
        _box(msp, f, ENG_U[0], M_IN, ENG_U[1], sw - M_IN, "Agregat", 30, 35)
        _box(msp, f, ALT_U[0], ALT_IN, ALT_U[1], sw - ALT_IN, "Agregat", 30, 35)
    if detail >= 2:
        _box(msp, f, TB_U[0], mid - 90, TB_U[1], mid + 90, "Agregat", 30, 25)
        _box(msp, f, CP_U[0], sw - M_IN - CP_D, CP_U[1], sw - M_IN,
             "Agregat", 30, 35)
        # priključci: izduv sa motora, dovod i povrat goriva
        msp.add_circle(f(EXH_U, sw - M_IN - 70), 45,
                       dxfattribs={"layer": "Ventilacija", "color": 1})
        for u in FUEL_U:
            msp.add_circle(f(u, M_IN + 60), 35,
                           dxfattribs={"layer": "Agregat", "color": 1})

    if labels:
        along = radiator in ("W", "E")
        rot = 0 if along else 90
        for u0, u1, txt in ((ENG_U[0], ENG_U[1], "MOTOR"),
                            (ALT_U[0], ALT_U[1], "GENERATOR")):
            px, py = f((u0 + u1) / 2, mid)
            _txt(msp, txt, px, py, 1.3 * sc, layer="Tekst", color=7,
                 align=TA.MIDDLE_CENTER, rotation=rot)

    if dims:
        _dim_chain(msp, B, x, y, sc, radiator, sl, sw)

    return {
        "exhaust": f(EXH_U, sw - M_IN - 70),
        "fuel": [f(u, M_IN + 60) for u in FUEL_U],
        "radiator_face": f(0, mid),
        "panel": f((CP_U[0] + CP_U[1]) / 2, sw - M_IN - CP_D / 2),
    }


def _dim_chain(msp, B, x, y, sc, radiator, sl, sw):
    """Kotni lanac na samom agregatu: dužina i širina skida.

    Ovo je jedina kota na opremi i jedini podatak koji je obavezujući —
    ostatak obrisa je načelni raspored sklopova.
    """
    if radiator in ("W", "E"):
        B.dim_h(msp, x, x + sl, y + sw, sc, off=2.8 * sc)
        B.dim_v(msp, y, y + sw, x + sl, sc, off=2.8 * sc)
    else:
        B.dim_v(msp, y, y + sl, x + sw, sc, off=2.8 * sc)
        B.dim_h(msp, x, x + sw, y + sl, sc, off=2.8 * sc)


# --------------------------------------------------------------------------
def elev(msp, B, x, z, sc, D, flip=False, labels=False, hatch=True, dims=True):
    """Bočni pogled (uzduž skida); (x, z) = donji lijevi ugao gabarita.

    `flip=True` postavlja čelo radijatora desno — presjek 1–1 na H-04 gleda
    suprotno od presjeka na M-01, pa se ista geometrija samo okrene.
    """
    g = D["genset"]
    sl, sh = g["skid_L"], g["skid_H"]
    if flip:
        def f(u, w):
            return (x + sl - u, z + w)
    else:
        def f(u, w):
            return (x + u, z + w)

    # Sklopovi se šrafiraju pojedinačno, u svom obliku, a ne preko cijelog
    # pravougaonika gabarita: šrafura preko gabarita je prekrivala radijator,
    # motor i generator i agregat je izgledao kao puna kocka.  ANSI31 = isporuka
    # Izvođača, ista šrafura kao na jednopolnoj šemi.
    masses = [
        (0, 0, sl, BASE_H, 30),                       # ram skida
        (0, BASE_H, RAD_U, RAD_H, 4),                 # radijator
        (ENG_U[0], BASE_H, ENG_U[1], ENG_H, 30),      # motor
        (HUMP_U[0], ENG_H, HUMP_U[1], HUMP_H, 30),    # filter zraka
        (ALT_U[0], BASE_H, ALT_U[1], ALT_H, 30),      # generator
        (CP_U[0], CP_Z, CP_U[1], sh, 30),             # komandni ormar
    ]
    for u0, w0, u1, w1, col in masses:
        if hatch:
            ht = msp.add_hatch(color=30, dxfattribs={"layer": "Agregat"})
            ht.set_pattern_fill("ANSI31", scale=sc * 0.3)
            ht.paths.add_polyline_path(
                [f(u0, w0), f(u1, w0), f(u1, w1), f(u0, w1)], is_closed=True)
        _box(msp, f, u0, w0, u1, w1, "Agregat", col, 35)
    for k in range(1, 5):                             # lamele jezgra radijatora
        wk = BASE_H + k * (RAD_H - BASE_H) / 5
        msp.add_line(f(20, wk), f(RAD_U - 20, wk),
                     dxfattribs={"layer": "Agregat", "color": 4})

    # Natpisi u pogledu su podrazumijevano isključeni: preko šrafure se na
    # 1:25 ne čitaju, a tlocrt iznad presjeka ih već nosi.
    if labels:
        px, py = f((ENG_U[0] + ENG_U[1]) / 2, (BASE_H + ENG_H) / 2)
        _txt(msp, "MOTOR", px, py, 1.3 * sc, layer="Tekst", color=7,
             align=TA.MIDDLE_CENTER)
        px, py = f((ALT_U[0] + ALT_U[1]) / 2, (BASE_H + ALT_H) / 2)
        _txt(msp, "GEN.", px, py, 1.3 * sc, layer="Tekst", color=7,
             align=TA.MIDDLE_CENTER)
    if dims:
        B.dim_v(msp, z, z + sh, x + sl if not flip else x, sc,
                off=2.4 * sc if not flip else -2.4 * sc)
    return {"top": z + sh,
            "exhaust": f(EXH_U, ENG_H),
            "panel": f((CP_U[0] + CP_U[1]) / 2, (CP_Z + sh) / 2)}


# --------------------------------------------------------------------------
# Spremnik goriva 500 l, dvoplašni, u prihvatnom koritu
# --------------------------------------------------------------------------
def tank_plan(msp, B, x, y, sc, D, long_axis="x", detail=True, tray=True,
              dims=True):
    """Spremnik u koritu; (x, y) = donji lijevi ugao KORITA.

    `long_axis` je osa lista uzduž koje leži dužina spremnika ("x" ili "y").
    """
    tk = D["tank"]
    kd = tk["kada"]
    tl, tw = tk["L"], tk["W"]
    kl, kw = kd["L"], kd["W"]
    if long_axis == "x":
        kW, kH, tW, tH = kl, kw, tl, tw
    else:
        kW, kH, tW, tH = kw, kl, tw, tl
    tx, ty = x + (kW - tW) / 2, y + (kH - tH) / 2

    if tray:
        B.rect(msp, x, y, kW, kH, "Agregat", color=1, lw=35)
    B.rect(msp, tx, ty, tW, tH, "Agregat", color=30, lw=50)
    if detail:
        # dvostruki plašt: unutrašnji plašt uvučen za međuprostor
        B.rect(msp, tx + 45, ty + 45, tW - 90, tH - 90, "Agregat", color=30,
               lw=25)
        # priključci na gornjoj ploči, u jednom nizu uz uzdužnu osu: nalivanje,
        # oduška, dovod i povrat, plus nadzor međuplašta uz nalivanje.  Načelno,
        # bez kota — spremnik je katalog proizvođača.
        f = [0.16, 0.34, 0.52, 0.70]
        if long_axis == "x":
            spots = [(tx + k * tW, ty + tH - 130, 70 if i == 0 else 45)
                     for i, k in enumerate(f)]
            spots.append((tx + 0.16 * tW, ty + 130, 35))
            gauge = (tx + tW - 170, ty + 120, 60, tH - 240)
        else:
            # niz ide uz lijevi bok: desni nosi natpis "dvoplašni" na H-04
            spots = [(tx + 130, ty + k * tH, 70 if i == 0 else 45)
                     for i, k in enumerate(f)]
            spots.append((tx + tW - 130, ty + 0.16 * tH, 35))
            gauge = (tx + 120, ty + tH - 170, tW - 240, 60)
        for cx, cy, r in spots:
            msp.add_circle((cx, cy), r,
                           dxfattribs={"layer": "Agregat", "color": 1})
        B.rect(msp, *gauge, "Agregat", color=1, lw=25)   # pokazivač nivoa
        # Odvod iz korita nije crtan: korito je od spremnika šire 50 odnosno
        # 20 mm po strani, pa u tom pojasu nema mjesta ni za jedan simbol koji
        # bi se u mjerilu 1:25 čitao.  Zahtjev nosi napomena na listu.
    if dims:
        if long_axis == "x":
            B.dim_h(msp, tx, tx + tW, ty, sc, off=-1.6 * sc)
        else:
            B.dim_v(msp, ty, ty + tH, tx, sc, off=-1.6 * sc)
    return {"tank": (tx, ty, tW, tH)}


def tank_elev(msp, B, x, z, sc, D, view="long", layer="Agregat", color=30,
              detail=True, dims=True):
    """Bočni pogled na spremnik; (x, z) = donji lijevi ugao spremnika."""
    tk = D["tank"]
    w = tk["L"] if view == "long" else tk["W"]
    h = tk["H"]
    B.rect(msp, x, z, w, h, layer, color=color, lw=50)
    if detail:
        # gornja ploča sa priključcima i pokazivač nivoa sa strane
        msp.add_line((x, z + h - 120), (x + w, z + h - 120),
                     dxfattribs={"layer": layer, "color": color})
        for k, r in ((0.16, 70), (0.34, 45), (0.52, 45)):
            cx = x + k * w
            B.rect(msp, cx - r, z + h, 2 * r, 55, layer, color=1, lw=25)
        B.rect(msp, x + w - 150, z + 200, 60, h - 500, layer, color=1, lw=25)
    if dims:
        B.dim_v(msp, z, z + h, x + w, sc, off=1.6 * sc)
    return {"top": z + h}
