# -*- coding: utf-8 -*-
"""
Prezentacija planirane nabavke (BH Telecom predložak, 4:3).

    python tools/build_prezentacija.py <predlozak.pptx> [izlaz.pptx]

Predložak je BH Telecom prezentacija planirane nabavke (npr. "Zamjena sistema
klimatizacije TKC Tuzla 4 sprat.pptx"): zadržavaju se master, naslovni slajd i
slajd "HVALA NA PAŽNJI!", ostali slajdovi se brišu, a novi se crtaju na
rasporedu "Title and Content" prvog mastera (narandžasta traka, bh logo,
oznaka "BH Telecom | Interno"). Brojke su iz TD, Priloga I/II i pvsim.
"""
import copy
import os
import sys

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.opc.packuri import PackURI
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
JOINT = os.path.dirname(HERE)
ROOT = os.path.dirname(JOINT)
GRAF = os.path.join(JOINT, "TD-OUTPUT", "grafika", "prilog1")
P3 = os.path.join(JOINT, "TD-OUTPUT", "3.2 Prilog III TD - Situacije.pdf")

FONT = "Bookman Old Style"
ORANGE = RGBColor(0xEF, 0x88, 0x12)
DARK = RGBColor(0x26, 0x26, 0x26)
GREY = RGBColor(0x5F, 0x5F, 0x5F)
TINT = RGBColor(0xFD, 0xF1, 0xE4)
LIGHT = RGBColor(0xF4, 0xF4, 0xF4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BOTTOM = 5.85         # traka mastera: ≈6,4" desno, val do ≈5,7" uz lijevu ivicu


# --------------------------------------------------------------------------
# osnovni elementi
def run(p, text, size=13, bold=False, color=DARK, italic=False):
    r = p.add_run()
    r.text = text
    f = r.font
    f.name, f.size, f.bold, f.italic = FONT, Pt(size), bold, italic
    f.color.rgb = color
    return r


def bullet(p, char="•", indent=0.22):
    pPr = p._p.get_or_add_pPr()
    pPr.set("marL", str(int(Inches(indent))))
    pPr.set("indent", str(-int(Inches(indent))))
    for tag in ("a:buNone", "a:buChar", "a:buAutoNum"):
        for el in pPr.findall(qn(tag)):
            pPr.remove(el)
    bf = pPr.makeelement(qn("a:buFont"), {"typeface": "Arial"})
    bc = pPr.makeelement(qn("a:buChar"), {"char": char})
    pPr.append(bf)
    pPr.append(bc)


def box(slide, x, y, w, h, paras, size=13, anchor=MSO_ANCHOR.TOP, margin=0.0,
        align=PP_ALIGN.LEFT, space=4):
    """paras: list of str | (str, dict) | list of runs [(text, dict), ...]."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", Inches(margin))
    first = True
    for para in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.space_after = Pt(space)
        if isinstance(para, str):
            para = [(para, {})]
        elif isinstance(para, tuple):
            para = [para]
        opts0 = para[0][1]
        if opts0.get("bullet"):
            bullet(p, indent=opts0.get("indent", 0.22))
        for text, o in para:
            run(p, text, size=o.get("size", size), bold=o.get("bold", False),
                color=o.get("color", DARK), italic=o.get("italic", False))
    return tb


def title(slide, text, sub=None):
    box(slide, 0.4, 0.32, 7.7, 0.6, [(text, {"bold": True, "size": 24})])
    if sub:
        box(slide, 0.4, 0.86, 8.9, 0.35, [(sub, {"size": 12, "color": GREY,
                                                 "italic": True})])


def shape(slide, kind, x, y, w, h, fill=TINT, line=None):
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    return s


def card(slide, x, y, w, h, fill=TINT):
    s = shape(slide, MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h, fill)
    s.adjustments[0] = 0.06
    return s


def badge(slide, x, y, d, text, size=13, fill=ORANGE):
    s = shape(slide, MSO_SHAPE.OVAL, x, y, d, d, fill)
    tf = s.text_frame
    for side in ("left", "right", "top", "bottom"):
        setattr(tf, f"margin_{side}", 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run(p, text, size=size, bold=True, color=WHITE)
    return s


def arrow(slide, x, y, w, h):
    shape(slide, MSO_SHAPE.RIGHT_ARROW, x, y, w, h, ORANGE)


def picture(slide, path, x, y, w=None, h=None):
    """Smjesti sliku u okvir (w, h) bez izobličenja; vraća stvarni okvir."""
    iw, ih = Image.open(path).size
    if w and h:
        if iw / ih > w / h:
            h2 = w * ih / iw
            y, h = y + (h - h2) / 2, h2
        else:
            w2 = h * iw / ih
            x, w = x + (w - w2) / 2, w2
    elif w:
        h = w * ih / iw
    else:
        w = h * iw / ih
    slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    return x, y, w, h


def table(slide, x, y, w, rows, widths, size=11, head_fill=ORANGE, row_h=0.3,
          bold_last=False, align=None, head_h=None):
    n, m = len(rows), len(rows[0])
    gt = slide.shapes.add_table(n, m, Inches(x), Inches(y), Inches(w),
                                Inches(row_h * n))
    tbl = gt.table
    # bez ugrađenog stila: bijelo, tanke sive linije
    tblPr = tbl._tbl.tblPr
    for a in ("firstRow", "bandRow"):
        tblPr.set(a, "0")
    for j, cw in enumerate(widths):
        tbl.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        tbl.rows[i].height = Inches(head_h if (i == 0 and head_h) else row_h)
        for j, val in enumerate(row):
            c = tbl.cell(i, j)
            c.margin_left = c.margin_right = Inches(0.06)
            c.margin_top = c.margin_bottom = Inches(0.01)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.fill.solid()
            head = i == 0
            last = bold_last and i == n - 1
            c.fill.fore_color.rgb = head_fill if head else (TINT if last else WHITE)
            tf = c.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.alignment = (align[j] if align else PP_ALIGN.LEFT)
            run(p, str(val), size=size, bold=head or last,
                color=WHITE if head else DARK)
            _borders(c)
    return tbl


def _borders(cell, color="BFBFBF", w=6350):
    tcPr = cell._tc.get_or_add_tcPr()
    for tag in ("a:lnL", "a:lnR", "a:lnT", "a:lnB"):
        ln = tcPr.makeelement(qn(tag), {"w": str(w)})
        sf = ln.makeelement(qn("a:solidFill"), {})
        clr = sf.makeelement(qn("a:srgbClr"), {"val": color})
        sf.append(clr)
        ln.append(sf)
        tcPr.append(ln)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# --------------------------------------------------------------------------
def prep_template(src):
    prs = Presentation(src)
    sld = prs.slides._sldIdLst
    ids = list(sld)
    keep = {0, len(ids) - 1}            # naslovni i "HVALA NA PAŽNJI!"
    for i, sid in enumerate(ids):
        if i not in keep:
            prs.part.drop_rel(sid.get(qn("r:id")))
            sld.remove(sid)
    # novi slajd dobija ime slideN po broju slajdova; zadržani "HVALA" (slide6)
    # bi se sudario sa novim, pa se privremeno sklanja na visok broj
    prs.slides[1].part.partname = PackURI("/ppt/slides/slide999.xml")
    layout = next(l for l in prs.slide_masters[0].slide_layouts
                  if l.name == "Title and Content")
    return prs, layout


def renumber(prs):
    for i, slide in enumerate(prs.slides, 1):
        slide.part.partname = PackURI(f"/ppt/slides/slide{i}.xml")


def new_slide(prs, layout):
    s = prs.slides.add_slide(layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    return s


def move_last_to_end(prs):
    """Slajd 'HVALA' je drugi u listi; premjesti ga na kraj."""
    sld = prs.slides._sldIdLst
    thanks = list(sld)[1]
    sld.remove(thanks)
    sld.append(thanks)


def edit_title_slide(slide):
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        t = sh.text_frame.text
        if t.startswith("ZAMJENA"):
            _set_lines(sh, ["AUTONOMNI HIBRIDNI SISTEMI NAPAJANJA",
                            "BS SJEDNICA (BILEĆA) I BS HAMZIĆI (ČITLUK)",
                            "",
                            "- prezentacija planirane nabavke (LOT 1 i LOT 2)"],
                       sizes=[24, 20, 12, 16], bold=[True, True, False, False])
        elif "godine" in t:
            _set_lines(sh, ["Oktobar 2026. godine"])
            sh.left, sh.width = Inches(2.5), Inches(5.0)


def _set_lines(sh, lines, sizes=None, bold=None):
    """Zamijeni tekst zadržavajući formatiranje prvog runa svakog paragrafa."""
    tf = sh.text_frame
    paras = list(tf.paragraphs)
    proto = copy.deepcopy(paras[0]._p)
    for p in paras[1:]:
        p._p.getparent().remove(p._p)
    p0 = paras[0]._p
    for k, line in enumerate(lines):
        p = p0 if k == 0 else copy.deepcopy(proto)
        if k:
            p0.getparent().append(p)
        rs = p.findall(qn("a:r"))
        for r in rs[1:]:
            p.remove(r)
        rs[0].find(qn("a:t")).text = line
        rPr = rs[0].find(qn("a:rPr"))
        if rPr is not None and sizes:
            rPr.set("sz", str(sizes[k] * 100))
        if rPr is not None and bold:
            rPr.set("b", "1" if bold[k] else "0")
        for br in p.findall(qn("a:br")):
            p.remove(br)


# --------------------------------------------------------------------------
def s_opis(prs, L, img):
    s = new_slide(prs, L)
    title(s, "Opis investicije")
    B = {"bullet": True}
    box(s, 0.4, 1.05, 5.75, 5.1, [
        ("BS Sjednica (Bileća) i BS Hamzići (Čitluk) nisu priključene na "
         "elektroenergetsku mrežu, niti se priključak očekuje u narednom periodu.", B),
        ("Bez napajanja lokacije se ne mogu pustiti u rad: izostaje pokrivanje "
         "šireg područja i planirano RR čvorište Sjednica.", B),
        ("Rješenje je autonomni (off-grid) hibridni sistem na −48 V DC: "
         "fotonaponsko polje kao primarni izvor, LFP baterije i automatski dizel "
         "agregat kao rezerva.", B),
        ("Huawei oprema (FN moduli, ICC360, baterije, MTS) je posebna nabavka. "
         "Ova nabavka obuhvata infrastrukturu i instalaciju, u dva LOT-a.", B),
        ("Druga iteracija ovakvog rješenja, nakon pozitivnog iskustva na lokaciji "
         "MILNIŠTE_MIKRO (Glamoč).", B),
    ], size=13, space=8)
    x, y, w, h = picture(s, img["sjednica"], 6.4, 1.05, 3.2, 4.75)
    box(s, x, y + h + 0.05, w, 0.3, [("BS Sjednica, 1076 m n.v.",
                                      {"size": 10, "color": GREY, "italic": True})],
        align=PP_ALIGN.CENTER)
    notes(s, "Zašto nabavka: lokacije bez EES-a, bez napajanja nema puštanja u rad. "
             "Huawei dio je već nabavljen kroz projekte RAN-a; ovdje je infrastruktura.")


def s_stanje(prs, L, img):
    s = new_slide(prs, L)
    title(s, "Postojeće stanje lokacija")
    cols = [
        ("BS SJEDNICA — Bileća (RS)", img["sjednica"], [
            "1076 m n.v. · 42,9448° N, 18,3236° E",
            "AB ploča 5,40 × 5,40 m, rešetkasti stub h = 38 m",
            "kontejner K2 3,00 × 2,30 m — prostor za agregat",
            "vanjski ormar Huawei ICC360 uz kontejner",
            "ograda 2,10 m; parcela ≈150 m²",
            "nema priključka na EES",
        ]),
        ("BS HAMZIĆI — Čitluk (FBiH)", img["hamzici"], [
            "493 m n.v. · 43,2880° N, 17,6248° E",
            "AB ploča 5,40 × 5,40 m, rešetkasti stub h = 32 m",
            "kontejner K2 prazan, klima Stulz WDE80 se demontira",
            "ormari ICC360 i MTS na JZ strani, iza FN polja",
            "makadamski prilaz ≈800 m × 3 m",
            "priključak projektovan 2017. nije izveden",
        ]),
    ]
    for k, (head, photo, lines) in enumerate(cols):
        x0 = 0.4 + k * 4.7
        card(s, x0, 1.05, 4.5, 4.3)
        box(s, x0 + 0.2, 1.15, 4.1, 0.35, [(head, {"bold": True, "size": 13,
                                                   "color": ORANGE})])
        picture(s, photo, x0 + 0.2, 1.6, 1.75, 3.6)
        box(s, x0 + 2.05, 1.6, 2.35, 3.7,
            [(t, {"bullet": True, "indent": 0.16}) for t in lines], size=10.5,
            space=5)
    box(s, 0.4, 5.45, 9.2, 0.35, [("Oba objekta imaju otežan prilaz, naročito nakon "
                                   "padavina; obilazak lokacija je dio postupka.",
                                   {"size": 10.5, "italic": True, "color": GREY})])
    notes(s, "Oba objekta: otežan prilaz, naročito nakon padavina; obilazak lokacija "
             "je dio postupka (Tačka 3 TD).")


def s_rjesenje(prs, L):
    s = new_slide(prs, L)
    title(s, "Tehničko rješenje — po lokaciji")
    # blok šema
    blocks = [
        (0.4, 1.15, "FN polje", "12 × iPV585-M2A\n7,02 kWp\n4 nosača × 3 modula"),
        (2.75, 1.15, "Solarni moduli", "PVDB 500 V DC\n2 × S4875G3\n4 kW, AFCI"),
        (5.1, 1.15, "Huawei ICC360", "−48 V DC sabirnica\nkontroler SMU\nLFP 48,6 kWh"),
        (7.45, 1.15, "TK oprema", "≈1,18 kW nazivno\n≈1,33 kW vršno"),
    ]
    for x, y, h1, h2 in blocks:
        card(s, x, y, 2.15, 1.55)
        box(s, x + 0.1, y + 0.1, 1.95, 1.4,
            [(h1, {"bold": True, "size": 12, "color": ORANGE}), (h2, {"size": 10.5})],
            align=PP_ALIGN.CENTER, space=3)
    for x in (2.57, 4.92, 7.27):
        arrow(s, x, 1.77, 0.17, 0.3)
    # agregat ispod ICC360
    card(s, 5.1, 3.05, 2.15, 1.2, LIGHT)
    box(s, 5.2, 3.12, 1.95, 1.1,
        [("Rezerva: DEA 18 kVA", {"bold": True, "size": 12, "color": ORANGE}),
         ("u kontejneru → GRO →\n3 × R4875 (AC/DC)", {"size": 10.5})],
        align=PP_ALIGN.CENTER, space=3)
    shape(s, MSO_SHAPE.UP_ARROW, 6.03, 2.73, 0.3, 0.3, ORANGE)
    # ključni parametri
    B = {"bullet": True, "indent": 0.18}
    box(s, 0.4, 3.05, 4.5, 3.1, [
        ("LOT 1 — FN nosači", {"bold": True, "size": 12}),
        ("4 odvojena nosača × 3 modula, položeno", B),
        ("nagib 45°, jugozapad (azimut 225°)", B),
        ("2 temeljne trake po nosaču, C30/37 XC4+XF3", B),
        ("LOT 2 — agregat i instalacije", {"bold": True, "size": 12}),
        ("DEA 18 kVA / 14,4 kW, skid u kontejneru", B),
        ("dvoplašni spremnik 500 l, korito, protupožarna zaštita", B),
        ("novi GRO, DC razvod −48 V, uzemljenje, SPD", B),
    ], size=11, space=4)
    box(s, 5.1, 4.45, 4.5, 1.4, [
        ("Upravljanje (SMU)", {"bold": True, "size": 12}),
        ("start agregata po SoC: DOD 85 %, stop SoC 60 %", B),
        ("ulaz ispravljača ograničen na 9,5 kW", B),
        ("najkraći rad 1 h; alarmi u NetEco", B),
    ], size=11, space=4)
    notes(s, "Huawei oprema (FN moduli, ICC360, ispravljači, solarni moduli, "
             "baterije) dolazi od Kupca; ponuđač je ugrađuje i povezuje.")


def s_bilans(prs, L):
    s = new_slide(prs, L)
    title(s, "Očekivani energetski bilans",
          "satna simulacija 2005–2023, pvlib + PVGIS-SARAH3, polje JZ 45°")
    stats = [("74,7 %", "77,0 %", "solarni udio u potrošnji"),
             ("≈300 h", "≈270 h", "rad agregata godišnje"),
             ("≈990 l", "≈900 l", "gorivo godišnje")]
    for k, (a, b, lab) in enumerate(stats):
        x = 0.4 + k * 3.1
        card(s, x, 1.3, 2.9, 1.25)
        box(s, x + 0.1, 1.38, 2.7, 0.3, [(lab, {"size": 11, "color": GREY})],
            align=PP_ALIGN.CENTER)
        box(s, x + 0.1, 1.62, 1.35, 0.9, [(a, {"bold": True, "size": 22, "color": ORANGE}),
                                         ("Sjednica", {"size": 10})],
            align=PP_ALIGN.CENTER, space=0)
        box(s, x + 1.45, 1.62, 1.35, 0.9, [(b, {"bold": True, "size": 22, "color": ORANGE}),
                                          ("Hamzići", {"size": 10})],
            align=PP_ALIGN.CENTER, space=0)
    picture(s, os.path.join(GRAF, "energetski-bilans-sjednica.png"), 0.4, 2.75, 5.6, 3.05)
    B = {"bullet": True, "indent": 0.18}
    box(s, 6.2, 2.85, 3.4, 2.9, [
        ("FN proizvodnja ≈9 240 / ≈9 580 kWh/god", B),
        ("u 9 od 10 godina agregat do ≈360 / ≈320 h", B),
        ("spremnik 500 l dopunjava se 2–3 puta godišnje", B),
        ("nepokrivena potrošnja: 0", B),
        ("vrijednosti su informativne (Prilog I, Tačka 8)",
         {"bullet": True, "indent": 0.18, "italic": True, "color": GREY}),
    ], size=10.5, space=5)
    notes(s, "Orijentacija JZ je odluka Naručioca (11.09.2026); prema jugu bi "
             "agregat radio ≈50 h godišnje manje.")


def s_raspored(prs, L, img):
    s = new_slide(prs, L)
    title(s, "Raspored opreme — BS Sjednica",
          "crtež M-01 iz Priloga III; za BS Hamzići crtež H-04")
    picture(s, img["m01"], 0.6, 1.25, 8.8, 4.6)
    notes(s, "Agregat u skid izvedbi na roštilju, spremnik 500 l u koritu, "
             "usis na SI zidu, izlaz toplog zraka kroz SZ zid.")


def s_lotovi(prs, L):
    s = new_slide(prs, L)
    title(s, "Predmet nabavke — dva LOT-a",
          "ponuđač može dostaviti ponudu za jedan ili oba LOT-a")
    lots = [
        ("LOT 1", "Nosači FN panela", "8 kpl (4 po lokaciji)", [
            "pripremni i zemljani radovi, iskop u stijeni",
            "temeljne trake, podložni beton",
            "isporuka i montaža nosača, hemijski ankeri",
            "uzemljenje nosača na postojeći prsten",
            "statički proračun (vjetar, snijeg) — uslov za početak radova",
        ]),
        ("LOT 2", "Agregat i hibridni sistem", "2 agregatska postrojenja 18 kVA", [
            "DEA skid u kontejneru, roštilj, spremnik 500 l",
            "ventilacija, izduv, protupožarna zaštita",
            "GRO, DC razvod −48 V, kablovi, SPD, uzemljenje",
            "preuzimanje opreme Kupca u Azićima, prevoz, montaža FN panela",
            "uvezivanje u NetEco, puštanje u rad, 72 h probni rad, obuka",
            "demontaža klime Stulz (Hamzići)",
        ]),
    ]
    for k, (tag, name, qty, items) in enumerate(lots):
        x0 = 0.4 + k * 4.7
        card(s, x0, 1.35, 4.5, 4.3)
        badge(s, x0 + 0.2, 1.5, 0.75, tag, size=11)
        box(s, x0 + 1.1, 1.5, 3.3, 0.75, [(name, {"bold": True, "size": 14}),
                                          (qty, {"size": 11, "color": GREY})],
            anchor=MSO_ANCHOR.MIDDLE, space=0)
        box(s, x0 + 0.25, 2.45, 4.05, 3.6,
            [(t, {"bullet": True, "indent": 0.18}) for t in items], size=12, space=7)
    notes(s, "Isti opis radova za obje lokacije; Prilog II ima zaseban obrazac "
             "za svaki LOT, sa listom po lokaciji.")


def s_oprema(prs, L):
    s = new_slide(prs, L)
    title(s, "Oprema Kupca — predaje se Ponuđaču",
          "Huawei specifikacija isporuke; preuzimanje u skladištu Azići, Sarajevo")
    rows = [["Oprema", "Po lokaciji", "Ukupno"],
            ["Ormar hibridnog sistema ICC360 (kontroler, razvod 600 A, DC klima)", "1", "2"],
            ["Ispravljački moduli R4875, 4 kW", "3", "6"],
            ["Solarni moduli S4875G3, 4 kW, AFCI", "2", "4"],
            ["FN moduli iPV585-M2A, 585 W", "12", "24"],
            ["FN razdjelna kutija PVDB, AC ulazni modul AIU03, SPD SPM01A", "1 + 1 + 1", "2 + 2 + 2"],
            ["DC/DC pretvarač 13,5 V / 26,8 V (start. akumulator, 24 V potrošači)", "1", "2"],
            ["Senzor nivoa goriva, modul agregata, bežični relej, antena", "komplet", "2 kompleta"],
            ["Kablovi (energetski, FN, signalni) i montažni pribor", "komplet", "2 kompleta"],
            ["LFP baterijski moduli (iz druge nabavke Kupca)", "prema projektu", "—"]]
    table(s, 0.4, 1.3, 9.2, rows, [6.2, 1.4, 1.6], size=10.5, row_h=0.42,
          align=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.CENTER])
    box(s, 0.4, 5.65, 9.2, 0.5, [("Ponuđač (LOT 2) preuzima, prevozi, istovara i "
                                  "ugrađuje; od otpremnice do primopredaje za opremu "
                                  "odgovara Ponuđač.", {"size": 11, "italic": True,
                                                         "color": GREY})])
    notes(s, "Detaljan spisak: Prilog I, Tačka 9 i završna strana Priloga III.")


def s_vrijednost(prs, L):
    s = new_slide(prs, L)
    title(s, "Predračunska vrijednost")
    card(s, 0.4, 1.1, 3.4, 2.0)
    box(s, 0.5, 1.2, 3.2, 1.8, [("100.000,00 KM", {"bold": True, "size": 26,
                                                   "color": ORANGE}),
                                ("bez PDV-a, obje lokacije", {"size": 11}),
                                ("sredstva raspoloživa u 2026.", {"size": 11,
                                                                 "color": GREY})],
        anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.CENTER, space=2)
    table(s, 4.05, 1.1, 5.55, [["LOT", "Predmet", "Iznos (KM)"],
                               ["LOT 1", "Nosači FN panela, 8 kpl", "30.000,00"],
                               ["LOT 2", "Agregatska postrojenja 18 kVA, 2 kpl", "70.000,00"],
                               ["UKUPNO", "", "100.000,00"]],
          [0.9, 3.15, 1.5], size=11, row_h=0.45, bold_last=True,
          align=[PP_ALIGN.LEFT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT])
    box(s, 0.4, 3.2, 9.2, 0.35, [("Izvor: Trogodišnji plan 2025–2027 i Operativni "
                                  "plan 2026, ID TIRS, tačka 14.6.",
                                  {"size": 10.5, "color": GREY})])
    # dinamika
    box(s, 0.4, 3.62, 4, 0.3, [("Dinamika ulaganja", {"bold": True, "size": 12})])
    box(s, 4.4, 3.65, 5.2, 0.3, [("mjeseci: 10–12/2026 i 1–9/2027; radovi u proljeće/ljeto",
                                  {"size": 9.5, "color": GREY, "italic": True})],
        align=PP_ALIGN.RIGHT)
    months = ["10", "11", "12", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    acts = [("Odluka Uprave", {0}),
            ("Zahtjev za nabavku", {0, 1}),
            ("Postupak nabavke i ugovor", {1, 2, 3}),
            ("Realizacija (90 dana / LOT)", {5, 6, 7}),
            ("Primopredaja i plaćanje", {8})]
    head = ["Aktivnost"] + months
    rows = [head] + [[a] + [""] * 12 for a, _ in acts]
    tbl = table(s, 0.4, 3.98, 9.2, rows, [3.2] + [0.5] * 12, size=8.5, row_h=0.3,
                align=[PP_ALIGN.LEFT] + [PP_ALIGN.CENTER] * 12)
    for i, (_, ms) in enumerate(acts, 1):
        for j in ms:
            c = tbl.cell(i, j + 1)
            c.fill.solid()
            c.fill.fore_color.rgb = ORANGE
    notes(s, "Procjena je iz RFI 'Autonomno napajanje za BS' (27.04.2026) i ranijih "
             "nabavki. Provjeriti LOT 2 prema tržišnoj cijeni agregata sa AREP+/EBS "
             "pobudom prije objave.")


def s_elementi(prs, L):
    s = new_slide(prs, L)
    title(s, "Ostali elementi nabavnog zahtjeva")
    rows = [
        ("Postupak", "pregovarački postupak sa objavom obavještenja "
                     "(čl. 10 i 16 Pravilnika o nabavkama)"),
        ("Kriterij", "najniža cijena prihvatljive ponude, za svaki LOT posebno"),
        ("Rok za ponude", "20 dana od slanja poziva"),
        ("Rok realizacije", "90 dana od uvođenja u posao, za svaki LOT; "
                            "uvođenje do 15 dana od potpisa ugovora"),
        ("Plaćanje", "100 %, odgođeno 30 dana od ispravne fakture; fakturiše se "
                     "po završenom LOT-u, uz zapisnik o primopredaji"),
        ("Garancija", "min. 2 godine; postgarantni period min. 5 godina"),
        ("Ugovorna kazna", "0,1 % po danu kašnjenja, 0,5 % po danu za neotklonjene "
                           "nedostatke; ukupno najviše 10 %"),
        ("Primopredaja", "Komisija Kupca na lokaciji, do 15 dana od zahtjeva; "
                         "nedostaci se otklanjaju u roku do 15 dana"),
    ]
    y = 1.05
    for k, (lab, val) in enumerate(rows):
        fill = TINT if k % 2 == 0 else WHITE
        shape(s, MSO_SHAPE.RECTANGLE, 0.4, y, 9.2, 0.56, fill)
        box(s, 0.55, y, 2.2, 0.56, [(lab, {"bold": True, "size": 11.5, "color": ORANGE})],
            anchor=MSO_ANCHOR.MIDDLE)
        box(s, 2.8, y, 6.7, 0.56, [(val, {"size": 11})], anchor=MSO_ANCHOR.MIDDLE,
            space=0)
        y += 0.595
    notes(s, "Kao u predlošku prezentacije planirane nabavke; izvor TD Tačke 3, "
             "4, 7 i 8 i Zahtjev za nabavku.")


def s_tok(prs, L):
    s = new_slide(prs, L)
    title(s, "Tok postupka — od objave do ugovora")
    steps = [
        ("Odluka Uprave", "odobrenje sredstava 100.000 KM, LOT 1 i 2"),
        ("Zahtjev za nabavku", "TD sa Prilozima I–III, komisija, lista ponuđača"),
        ("Objava i poziv", "obavještenje + poziv za 9 potencijalnih ponuđača"),
        ("Obilazak lokacija", "prijava do 15 dana, obilazak do 5 dana prije roka; "
                              "Direkcija Mostar"),
        ("Prijem ponuda", "20 dana od poziva; ponuda za jedan ili oba LOT-a"),
        ("Ocjena ponuda", "kvalifikacija, tehnička prihvatljivost, cijena po LOT-u"),
        ("Pregovori", "o cijeni sa prihvatljivim ponuđačima; konačne ponude"),
        ("Izbor i ugovor", "odluka o izboru po LOT-u, potpis, uvođenje u posao "
                           "do 15 dana"),
    ]
    w, h, gx = 2.1, 2.1, 0.27
    for k, (head, body) in enumerate(steps):
        r, c = divmod(k, 4)
        x = 0.4 + c * (w + gx)
        y = 1.05 + r * (h + 0.3)
        card(s, x, y, w, h)
        badge(s, x + 0.15, y + 0.15, 0.48, str(k + 1), size=14)
        box(s, x + 0.15, y + 0.72, w - 0.3, 0.55, [(head, {"bold": True, "size": 12})],
            space=0)
        box(s, x + 0.15, y + 1.22, w - 0.3, h - 1.3, [(body, {"size": 10})], space=0)
        if c < 3:
            arrow(s, x + w + 0.04, y + 0.27, 0.19, 0.24)
    notes(s, "Rokovi iz Zahtjeva za nabavku (tačka 7) i TD Tačka 3 (obilazak). "
             "Pregovori se vode samo sa ponuđačima čije su ponude prihvatljive.")


def s_uslovi(prs, L):
    s = new_slide(prs, L)
    title(s, "Uslovi za ponuđače i dokazi")
    cells = [
        ("Reference", ["min. 2 ista ili slična ugovora u zadnje 3 godine",
                       "LOT 1: zbirno ≥ 10.000 KM — FN nosači",
                       "LOT 2: zbirno ≥ 20.000 KM — agregatska postrojenja",
                       "za oba LOT-a dokazuje se svaki posebno"]),
        ("Kadrovi", ["min. 3 radnika elektro ili mašinske struke",
                     "min. 1 serviser certificiran od proizvođača nuđenog agregata",
                     "lista osiguranika i izjava za trajanje ugovora"]),
        ("Agregat (LOT 2)", ["autorizacija proizvođača ili ovlaštenog distributera "
                             "za BiH",
                             "ISO 9001 i ISO 14001 proizvođača",
                             "elektro sheme DEA, nacrti spremnika i roštilja"]),
        ("Nosači (LOT 1)", ["statički proračun nosača za odabrane FN panele",
                            "katalog sa označenim dijelovima i materijalom",
                            "Obrazac za cijenu (Prilog II) za svaki LOT, sve stavke "
                            "popunjene"]),
    ]
    for k, (head, items) in enumerate(cells):
        r, c = divmod(k, 2)
        x, y = 0.4 + c * 4.7, 1.05 + r * 2.4
        card(s, x, y, 4.5, 2.25)
        badge(s, x + 0.18, y + 0.18, 0.42, str(k + 1), size=12)
        box(s, x + 0.75, y + 0.18, 3.6, 0.42, [(head, {"bold": True, "size": 13})],
            anchor=MSO_ANCHOR.MIDDLE)
        box(s, x + 0.25, y + 0.72, 4.05, 1.5,
            [(t, {"bullet": True, "indent": 0.16}) for t in items], size=11,
            space=4)
    notes(s, "TD Tačke 5 i 6; ovjerene kopije: sud, upravni organ ili notar.")


def s_realizacija(prs, L):
    s = new_slide(prs, L)
    title(s, "Nakon ugovora — realizacija i primopredaja")
    steps = [("Uvođenje u posao", "do 15 dana od potpisa; predaja gradilišta, "
                                  "građevinski dnevnik"),
             ("Statički proračun", "ovjeren proračun nosača i poda kontejnera — "
                                   "uslov za početak radova"),
             ("Izvođenje", "LOT 1 temelji i nosači; LOT 2 agregat, instalacije, "
                           "montaža FN panela"),
             ("Ispitivanja", "nalaz uzemljenja, FAT agregata, 72 h probni rad, "
                             "obuka osoblja"),
             ("Primopredaja", "Komisija na lokaciji do 15 dana; izvedbena "
                              "dokumentacija; faktura po LOT-u")]
    y0 = 1.35
    shape(s, MSO_SHAPE.RECTANGLE, 0.75, y0 + 0.31, 8.5, 0.06, ORANGE)
    for k, (head, body) in enumerate(steps):
        x = 0.4 + k * 1.86
        badge(s, x + 0.55, y0, 0.68, str(k + 1), size=16)
        box(s, x, y0 + 0.85, 1.78, 0.6, [(head, {"bold": True, "size": 12})],
            align=PP_ALIGN.CENTER, space=0)
        box(s, x, y0 + 1.45, 1.78, 1.6, [(body, {"size": 10})], align=PP_ALIGN.CENTER,
            space=0)
    card(s, 0.4, 4.05, 9.2, 1.35, LIGHT)
    B = {"bullet": True, "indent": 0.18}
    box(s, 0.6, 4.18, 8.8, 1.4, [
        ("Nadzor Kupca: Voditelj projekta i nadzorni organi za građevinsku (LOT 1) "
         "te mašinsku i elektro fazu (LOT 2).", B),
        ("Viškovi do 15 % po stavci i 1 % ukupno odobrava nadzor; preko 10 % "
         "ukupne vrijednosti ide novi postupak.", B),
        ("Kolaudacija: EE napajanje 006-001; agregati klasa 4034 (8 %), "
         "ispravljači 3050 (10 %).", B),
    ], size=11, space=6)
    notes(s, "TD Tačka 3.3–3.4 (rokovi, nadzor, primopredaja) i Tačka 7.2 "
             "(viškovi i nepredviđeni radovi).")


def s_rizici(prs, L):
    s = new_slide(prs, L)
    title(s, "Rizici i mjere")
    rows = [["Rizik", "Mjera"],
            ["Pristup lokacijama (1076 m n.v., makadam), zimski uslovi",
             "obavezan obilazak; terenska vozila; radovi u proljeće/ljeto; uvođenje "
             "u posao po povoljnim uslovima"],
            ["Dozvole općine i zakup zemljišta",
             "klauzula o zamjenskoj lokaciji po jediničnim cijenama ili odustajanje"],
            ["Ispad agregata na lokaciji bez posade (servis jednom godišnje)",
             "pobuda AREP+ ili Stamford EBS (≥3 × In, 10 s); daljinski reset i "
             "start/stop preko NetEco"],
            ["Procjena LOT 2 u odnosu na tržište",
             "prije objave upit ovlaštenom distributeru za agregat sa traženom "
             "pobudom"],
            ["Usklađenost sa Huawei opremom",
             "spisak opreme Kupca u TD; zapisnik o preuzimanju sa serijskim "
             "brojevima"]]
    table(s, 0.4, 1.1, 9.2, rows, [3.7, 5.5], size=11, row_h=0.78, head_h=0.4)
    notes(s, "Referentni FG Wilson P18-6 standardno ima SHUNT pobudu; PMG nije "
             "dostupan u klasi 18–20 kVA (Leroy-Somer TAL 040).")


# --------------------------------------------------------------------------
def images(tmp):
    import pymupdf
    out = {}
    d = pymupdf.open(P3)
    pix = pymupdf.Pixmap(d, d[1].get_images()[0][0])
    out["sjednica"] = os.path.join(tmp, "sjednica.jpg")
    Image.frombytes("RGB", (pix.width, pix.height), pymupdf.Pixmap(
        pymupdf.csRGB, pix).samples).save(out["sjednica"], quality=88)
    pix = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.Pixmap(d, d[17].get_images()[0][0]))
    out["hamzici"] = os.path.join(tmp, "hamzici.jpg")
    Image.frombytes("RGB", (pix.width, pix.height), pix.samples).rotate(
        -90, expand=True).save(out["hamzici"], quality=88)
    out["m01"] = os.path.join(tmp, "m01.png")
    d[7].get_pixmap(dpi=150).save(out["m01"])
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        JOINT, "TD-OUTPUT", "5. Prezentacija planirane nabavke - hibridni sistemi "
                            "BS Sjednica i BS Hamzići.pptx")
    import tempfile
    tmp = tempfile.mkdtemp()
    img = images(tmp)
    prs, L = prep_template(src)
    edit_title_slide(prs.slides[0])
    s_opis(prs, L, img)
    s_stanje(prs, L, img)
    s_rjesenje(prs, L)
    s_bilans(prs, L)
    s_raspored(prs, L, img)
    s_lotovi(prs, L)
    s_oprema(prs, L)
    s_vrijednost(prs, L)
    s_elementi(prs, L)
    s_tok(prs, L)
    s_uslovi(prs, L)
    s_realizacija(prs, L)
    s_rizici(prs, L)
    move_last_to_end(prs)
    renumber(prs)
    prs.core_properties.title = "Autonomni hibridni sistemi napajanja BS Sjednica i BS Hamzići"
    prs.save(dst)
    print(f"snimljeno: {dst} ({len(prs.slides)} slajdova)")


if __name__ == "__main__":
    main()
