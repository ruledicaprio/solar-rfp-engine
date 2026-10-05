# -*- coding: utf-8 -*-
"""
Pogled sa jugozapada — zajednički za S-04 (Sjednica) i H-06 (Hamzići).

Ovo je prava ortogonalna elevacija, ne kosi pogled. Oba kompleksa su zakrenuta
45° i oba se crtaju pravougaono na sebe, pa je jugozapad kod oba jedna od osa
plana — na Sjednici plan-JUG, na Hamzićima plan-ZAPAD. Pogled u pravcu azimuta
45° (sa JZ prema SI) je zato obično preslikavanje (u, z), bez perspektive i bez
skraćenja po visini: sve visine i sve širine na listu su mjerljive.

Skrivene linije se ne uklanjaju; crta se od najdaljeg ka najbližem (slikarski
algoritam), a elemenata je malo i poredak je na obje lokacije isti:

    stub  →  kontejner  →  ploča  →  ograda  →  FN polje

FN polje stoji izvan ograde na JZ strani, dakle najbliže posmatraču, i zato se
crta posljednje. Noge stuba su šire od kontejnera na obje lokacije (4200 prema
3005 na Sjednici, 3700 prema 3005 na Hamzićima), pa kontejner stoji između nogu
i ništa se ne preklapa što bi tražilo uklanjanje linija.

Paneli su nagnuti 45° i gledaju u 225°, dakle pravo u posmatrača, ali je pravac
gledanja vodoravan — u ovoj projekciji se zato vide skraćeno po visini: puna
širina 2278 mm, a po visini samo uspon, od donje do gornje ivice (500 → 2934).

Stub je prava geometrija iz ovjerenog projekta lokacije (sloj `Silueta stuba`),
pripremljena u cad/tower_profile.json — v. rfp-hybrid-solar-td/tools/extract_tower.py.
Visina stuba se ovdje NE kotira: silueta iz dispozicije mjeri između krajnjih
radnih tačaka (37 800 odnosno 32 500 mm) i to nije isto što i nazivnih 38 odnosno
32 m iz ovjerenog projekta. Kotiraju se samo veličine koje ova TD i propisuje.
"""
from __future__ import annotations

import json
import os

from ezdxf.enums import TextEntityAlignment as TA

from bht_frame import _txt


def load_profile(cad_dir):
    with open(os.path.join(cad_dir, "tower_profile.json"), encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
def _ground(msp, B, u0, u1, z, sc, layer="Objekat"):
    """Linija terena sa kosim šrafom ispod nje."""
    msp.add_line((u0, z), (u1, z),
                 dxfattribs={"layer": layer, "color": 8, "lineweight": 50})
    step = 12.0 * sc
    n = max(2, int((u1 - u0) / step))
    for i in range(n + 1):
        u = u0 + i * (u1 - u0) / n
        msp.add_line((u, z), (u - 4.0 * sc, z - 4.0 * sc),
                     dxfattribs={"layer": layer, "color": 8})


def _tower(msp, B, tp, u_axis, z0, sc, cut=None, layer="Konstrukcija", color=5):
    """Silueta stuba iz ovjerenog projekta, na osi u_axis, bazom na z0.

    `cut` prekida stub na toj visini i stavlja oznaku prekida, kako se jarboli i
    crtaju.  Cijeli stub se ne prikazuje: 38 m i tri metra visoko FN polje ne
    stanu na isti list u mjerilu u kojem se oboje čita, a predmet ovog lista je
    prizemlje.  Visina stuba stoji u napomeni i u ovjerenom projektu lokacije.
    """
    att = {"layer": layer, "color": color, "lineweight": 18}
    for pts in tp["polylines"]:
        for (u0, w0), (u1, w1) in zip(pts, pts[1:]):
            if cut is not None:
                if w0 > cut and w1 > cut:
                    continue
                if w0 > cut or w1 > cut:            # duž siječe liniju prekida
                    t = (cut - w0) / (w1 - w0)
                    um = u0 + t * (u1 - u0)
                    if w0 > cut:
                        u0, w0 = um, cut
                    else:
                        u1, w1 = um, cut
            msp.add_line((u_axis + u0, z0 + w0), (u_axis + u1, z0 + w1),
                         dxfattribs=att)
    if cut is None:
        return
    half = max(abs(u) for s_ in tp["polylines"] for u, w in s_ if w <= cut) + 150
    pts = [(u_axis - half, z0 + cut)]
    n = 10
    for i in range(n + 1):
        u = u_axis - half + i * 2 * half / n
        pts.append((u, z0 + cut + (1 if i % 2 else -1) * 0.5 * sc))
    pts.append((u_axis + half, z0 + cut))
    msp.add_lwpolyline(pts, dxfattribs={"layer": layer, "color": 8})


def _fence(msp, B, u0, w, z, h, sc):
    """Ograda u pogledu: stubići na rasteru, okvir i ispuna od +0,20."""
    infill = 200
    B.hatch_rect(msp, u0, z + infill, w, h - infill - 30, "Ograda", "ANSI37",
                 sc * 1.6, 8)
    B.rect(msp, u0, z, w, h, "Ograda", color=8, lw=50)
    msp.add_line((u0, z + infill), (u0 + w, z + infill),
                 dxfattribs={"layer": "Ograda", "color": 8})
    post = 1335                                   # kv. 50×50 na 1335 mm
    n = max(1, int(round(w / post)))
    for i in range(n + 1):
        u = u0 + i * w / n
        B.rect(msp, u - 25, z, 50, h, "Ograda", color=8, lw=70)


def _container(msp, B, u0, w, z, h_lo, h_hi, sc):
    """Kontejner u pogledu.

    Pad krova od 10 % kod obje lokacije ide u dubinu ovog pogleda — na Sjednici
    po osi plan-Y (v. presjek na S-03), na Hamzićima po osi plan-X (v. presjek
    1-1 na H-04) — pa se lice vidi kao pravougaonik: gornja ivica je dalja, viša
    streha, a bliža, niža streha je linija preko lica."""
    ov = 120
    B.rect(msp, u0, z, w, h_hi, "Objekat", color=6, lw=50)
    msp.add_line((u0, z + h_lo), (u0 + w, z + h_lo),
                 dxfattribs={"layer": "Objekat", "color": 6})
    B.rect(msp, u0 - ov, z + h_hi - 40, w + 2 * ov, 100, "Objekat", color=6, lw=50)


def _stand(msp, B, u0, w, z, b, top, sc, tag=None):
    """Jedan nosač: lice panela (skraćeno po visini) i noge do tla."""
    B.hatch_rect(msp, u0, z + b, w, top - b, "Panel", "ANSI37", sc * 2.6, 110)
    B.rect(msp, u0, z + b, w, top - b, "Panel", color=110, lw=70)
    for r in (1, 2):                                # tri modula u nizu
        zr = z + b + r * (top - b) / 3
        msp.add_line((u0, zr), (u0 + w, zr),
                     dxfattribs={"layer": "Panel", "color": 8})
    for u in (u0 + 0.16 * w, u0 + 0.84 * w):        # noge nosača
        msp.add_line((u, z), (u, z + b + 60),
                     dxfattribs={"layer": "Konstrukcija", "color": 5,
                                 "lineweight": 50})
    if tag:
        _txt(msp, tag, u0 + w / 2, z + b - 320, 1.6 * sc, layer="Tekst", color=7,
             align=TA.CENTER)


# --------------------------------------------------------------------------
def draw(msp, B, sc, D, cfg):
    """Nacrtaj pogled. `cfg` nosi sve u koordinatama pogleda: u vodoravno, z visina
    iznad gornje ivice ploče. Vraća rječnik karakterističnih kota."""
    arr = D["array"]
    b, top = arr["bottom_edge"], arr["top_edge"]
    Z = cfg["z0"]                                   # gornja ivica ploče na listu
    terr = cfg["terrain"]                           # teren u odnosu na ploču (≤0)

    # 1) teren i ploča — sve ostalo stoji na njima
    _ground(msp, B, cfg["view"][0], cfg["view"][1], Z + terr, sc)
    su0, sw, sd = cfg["slab"]
    B.rect(msp, su0, Z - sd, sw, sd, "Objekat", color=254, lw=35)
    B.hatch_rect(msp, su0, Z - sd, sw, sd, "Objekat", "ANSI31", sc * 0.5, 8)

    # 2) stub, pa kontejner između njegovih nogu
    _tower(msp, B, cfg["tower"], cfg["u_axis"], Z, sc, cut=cfg.get("cut"))
    cu0, cw = cfg["container"]
    _container(msp, B, cu0, cw, Z, cfg["c_lo"], cfg["c_hi"], sc)

    # 3) ograda, pa FN polje ispred nje
    # Temeljne trake su u nivou ploče na obje lokacije, pa nosači stoje na Z, a ne
    # na terenu; gdje je teren niži (Hamzići, −0,20) traka viri iznad njega.
    fu0, fw_, fh = cfg["fence"]
    _fence(msp, B, fu0, fw_, Z + terr, fh, sc)
    sw_, sp = D["foundation"]["strip_w_top"], D["support"]["strip_spacing"]
    for u0, tag in cfg["stands"]:
        if terr < 0:                                # dvije trake po nosaču, poprečno
            uc = u0 + cfg["stand_w"] / 2
            for du in (-sp / 2, sp / 2):
                B.rect(msp, uc + du - sw_ / 2, Z + terr, sw_, -terr, "Temelj",
                       color=32, lw=35)
        _stand(msp, B, u0, cfg["stand_w"], Z, b, top, sc, tag=tag)

    # 4) kote: samo ono što ova TD propisuje, od gornje ivice ploče
    us = [u for u, _ in cfg["stands"]]
    B.dim_h(msp, min(us), max(us) + cfg["stand_w"], Z + terr, sc, off=-7.0 * sc)
    B.dim_v(msp, Z, Z + b, cfg["dim_u"], sc, off=0)
    B.dim_v(msp, Z, Z + top, cfg["dim_u"] + 4.0 * sc, sc, off=0)
    B.dim_v(msp, Z, Z + fh + terr, cfg["dim_u"] + 8.0 * sc, sc, off=0)

    # strane svijeta na krajevima pogleda, kao na ostalim listovima
    _txt(msp, cfg["left"], cfg["view"][0] + 200, Z + terr - 9.0 * sc, 2.2 * sc,
         layer="Orijentacija", color=1)
    _txt(msp, cfg["right"], cfg["view"][1] - 200, Z + terr - 9.0 * sc, 2.2 * sc,
         layer="Orijentacija", color=1, align=TA.RIGHT)
    return {"z_ground": Z + terr, "z_panel_top": Z + terr + top}
