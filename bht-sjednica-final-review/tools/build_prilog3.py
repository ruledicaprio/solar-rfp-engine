# -*- coding: utf-8 -*-
"""
Assemble Prilog III from parts, instead of splicing into an inherited PDF.

Rev 3 restructure (Investor, 2026-08-11):

  - the eight K3 container drawings (G-01..G-08) are replaced by the K2 set from
    the certified project of THIS object - the site is a K2, so the K3 sheets
    described a different container;
  - the nine K3 electrical drawings (E-01..E-09) all go, replaced by the single
    K2 single-line diagram of the GRO. The PMO drawings go with them: the PMO no
    longer has a supply, and our own E-01 sheet shows the new GRO;
  - INFO-03 (RFI block diagram), INFO-04 (names PowerCube, which the package no
    longer specifies) and the closing REFERENTNA DOKUMENTACIJA page are dropped;
  - INFO-01 (site photo) moves directly behind the cover;
  - the cover is rebuilt in the style of the TD cover page.

The K2 drawings are vendor DWGs: they are converted to DXF with the ODA File
Converter, cropped to their own sheet frame (several carry stray content beside
the frame) and plotted to A3.
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import tempfile

import ezdxf
import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from paths import GRAFIKA as DWG, LOGO_SVG, PRILOG3 as OUT          # noqa: E402

SITE = os.path.join(BASE, "SITE-PROJECT-SJEDNICA-Bileca-K2-S38-m")
ODA = os.environ.get(
    "ODA_CONVERTER_PATH", r"C:\Program Files\ODA\ODAFileConverter\ODAFileConverter.exe"
)

ARCH = os.path.join(SITE, "2 - ARHITEKTONSKO GRADJEVINSKI DIO", "6 Graficki dio")
ELEC = os.path.join(SITE, "3_ELEKTRO INSTALACIJE", "Graficki dio")

# K2 source drawing -> (caption, crop). Cropping is opt-in per sheet, not
# guessed: only the GRO single-line parks content away from its frame, and a
# heuristic applied to all of them threw away real content on the plans.
K2_SHEETS = [
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "01 Osnova.dwg"),
        "Kontejner K2 — osnova",
        False,
    ),
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "02 Presjek 1_1.dwg"),
        "Kontejner K2 — presjek 1-1",
        False,
    ),
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "03 Presjek 2_2.dwg"),
        "Kontejner K2 — presjek 2-2",
        False,
    ),
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "04 Fasade.dwg"),
        "Kontejner K2 — fasade",
        False,
    ),
    (
        os.path.join(ARCH, "463 Graficki dio OBJEKAT", "05 Detalji.dwg"),
        "Kontejner K2 — detalji",
        False,
    ),
    (
        os.path.join(ARCH, "461 Graficki dio TEMELJ i OGRADA", "03 Osnova temelja.dwg"),
        "Osnova temelja",
        False,
    ),
    (os.path.join(ELEC, "3.5.2 Jednopolna sema GRO.dwg"), "Jednopolna šema GRO", True),
]

# Pages lifted out of the previous annex, matched by drawing number. Only the
# site photo is still inherited; INFO-02 is rebuilt from the pvsim run
# (info_pv_page) since Rev 9.
KEEP_FROM_OLD = {"INFO-01": "site photo"}

# Page layout of this annex since Rev 8: cover, photo, site data, S-01..E-01,
# the seven K2 sheets, INFO-02. --k2-from-existing reuses the photo and K2
# pages from it, so the annex can be rebuilt without the 232 MB site project.
LAYOUT = {"pages": 16, "photo": 1, "k2": range(8, 15)}


# --------------------------------------------------------------------------
def to_dxf(dwg_paths):
    """Convert the vendor DWGs in one ODA batch; returns {source: dxf path}."""
    tmp = tempfile.mkdtemp(prefix="prilog3_")
    src, dst = os.path.join(tmp, "in"), os.path.join(tmp, "out")
    os.makedirs(src)
    names = {}
    for i, p in enumerate(dwg_paths):
        # flat, ASCII names: the converter is unhappy with some source names
        stem = f"k2_{i:02d}"
        shutil.copy(p, os.path.join(src, stem + ".dwg"))
        names[p] = os.path.join(dst, stem + ".dxf")
    r = subprocess.run(
        [ODA, src, dst, "ACAD2018", "DXF", "0", "1"],
        capture_output=True,
        text=True,
        timeout=1800,
    )
    made = glob.glob(os.path.join(dst, "*.dxf"))
    if not made:
        raise SystemExit(f"ODA produced nothing.\n{r.stdout}\n{r.stderr}")
    return names, tmp


def _bbox(e):
    """Bounding box via ezdxf's own extents, so block INSERTs and hatches are
    measured too - a hand-rolled version skipped them, and the stray table on
    the GRO sheet is a block, so it survived every crop."""
    from ezdxf import bbox

    try:
        b = bbox.extents([e], fast=True)
    except Exception:  # noqa: BLE001
        return None
    if not b.has_data:
        return None
    return b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y


def find_frame(msp, extents=None):
    """Largest axis-aligned closed rectangle - the sheet frame on these drawings.

    A candidate that spans essentially the whole file is skipped: some of these
    drawings carry an outer border around the sheet *and* whatever is parked
    beside it, so cropping to that would crop nothing. The sheet frame is then
    the next-largest rectangle.
    """
    cands = []
    for e in msp.query("LWPOLYLINE"):
        pts = [(p[0], p[1]) for p in e.get_points()]
        if len(pts) not in (4, 5):
            continue
        xs = sorted({round(p[0], 1) for p in pts})
        ys = sorted({round(p[1], 1) for p in pts})
        if len(xs) != 2 or len(ys) != 2:
            continue  # not axis-aligned
        cands.append(((xs[1] - xs[0]) * (ys[1] - ys[0]), (xs[0], ys[0], xs[1], ys[1])))
    if not cands:
        return None
    cands.sort(key=lambda c: -c[0])
    if extents:
        ex0, ey0, ex1, ey1 = extents
        whole = (ex1 - ex0) * (ey1 - ey0)
        for area, box in cands:
            if area < 0.9 * whole:
                return box
    return cands[0][1]


def main_cluster(centres, span):
    """Keep the densest run of coordinates, split at the largest wide gap.

    Not every drawing draws its frame as a polyline, so frame detection alone is
    not enough. What these sheets do have in common is that the stray content
    sits well away from the drawing, leaving a gap far wider than anything
    inside it - so split on the widest gap and keep the busier side.
    """
    if len(centres) < 8:
        return None
    xs = sorted(centres)
    gaps = [(xs[i + 1] - xs[i], i) for i in range(len(xs) - 1)]
    width, i = max(gaps)
    if width < 0.18 * span:
        return None
    left, right = xs[: i + 1], xs[i + 1 :]
    keep = left if len(left) >= len(right) else right
    return min(keep), max(keep)


def crop_to_frame(doc):
    """Delete anything wholly outside the sheet frame.

    Several of these drawings park a stray table or an old revision beside the
    frame; plotted with fit-to-page that padding would shrink the drawing into a
    corner of the sheet.
    """
    msp = doc.modelspace()
    boxes = [(e, _bbox(e)) for e in msp]
    boxes = [(e, b) for e, b in boxes if b is not None]
    if not boxes:
        return 0

    allx = [b[0] for _, b in boxes] + [b[2] for _, b in boxes]
    ally = [b[1] for _, b in boxes] + [b[3] for _, b in boxes]
    extents = (min(allx), min(ally), max(allx), max(ally))
    fr = find_frame(msp, extents)
    if fr is None:
        span_x, span_y = max(allx) - min(allx), max(ally) - min(ally)
        cx = main_cluster([(b[0] + b[2]) / 2 for _, b in boxes], span_x)
        cy = main_cluster([(b[1] + b[3]) / 2 for _, b in boxes], span_y)
        if cx is None and cy is None:
            return 0
        x0, x1 = cx if cx else (min(allx), max(allx))
        y0, y1 = cy if cy else (min(ally), max(ally))
        fr = (x0, y0, x1, y1)

    x0, y0, x1, y1 = fr
    pad = 0.03 * max(x1 - x0, y1 - y0)
    dropped = 0
    for e, b in boxes:
        if b[2] < x0 - pad or b[0] > x1 + pad or b[3] < y0 - pad or b[1] > y1 + pad:
            msp.delete_entity(e)
            dropped += 1
    return dropped


def plot_a3(dxf_path, out_pdf, crop=False):
    from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf
    from ezdxf.addons.drawing.config import BackgroundPolicy, Configuration

    doc = ezdxf.readfile(dxf_path)
    dropped = crop_to_frame(doc) if crop else 0
    msp = doc.modelspace()
    backend = pymupdf.PyMuPdfBackend()
    cfg = Configuration(
        background_policy=BackgroundPolicy.WHITE, lineweight_scaling=0.7
    )
    Frontend(RenderContext(doc), backend, config=cfg).draw_layout(msp)
    page = layout.Page(420, 297, layout.Units.mm, margins=layout.Margins.all(0))
    data = backend.get_pdf_bytes(page, settings=layout.Settings(fit_page=True, scale=1))
    with open(out_pdf, "wb") as fh:
        fh.write(data)
    return dropped


# --------------------------------------------------------------------------
MEMO = ("Dioničko društvo BH Telecom Sarajevo",
        "Franca Lehara 7, 71000 Sarajevo, BiH",
        "Izvršna direkcija za tehnologiju i razvoj servisa",
        "tel: +387 33 256 500; fax: +387 33 256 505")
MEMO_WEB = "www.bhtelecom.ba"


def arial(page):
    """Embed the system Arial on a page: the base-14 PDF fonts have no
    š/ć/č/ž/đ. Returns (regular, bold) font names."""
    have = set()
    for tag, fname in (("bht", "arial.ttf"), ("bhtb", "arialbd.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fname)
        if os.path.exists(p):
            page.insert_font(fontname=tag, fontfile=p)
            have.add(tag)
    return ("bht" if "bht" in have else "helv"), ("bhtb" if "bhtb" in have else "hebo")


def memo_header(page, x0=50, x1=None, top=30):
    """The BH Telecom memorandum as the page header (Investor, 11.09.2026): the
    bh mark on the left with the web address under it, the company block on the
    right, a grey rule below. A4 and INFO pages only - the A3 drawings keep
    their own title block. Returns the y below it, where the content starts."""
    x1 = x1 or page.rect.width - 50
    reg, bold = arial(page)
    logo = fitz.open("pdf", fitz.open(LOGO_SVG).convert_to_pdf())
    h = 34
    w = h * logo[0].rect.width / logo[0].rect.height
    page.show_pdf_page(fitz.Rect(x0, top, x0 + w, top + h), logo, 0)
    page.insert_text(fitz.Point(x0, top + h + 11), MEMO_WEB, fontname=reg, fontsize=7,
                     color=(0.35, 0.35, 0.35))
    y = top + 4
    for i, txt in enumerate(MEMO):
        if page.insert_textbox(fitz.Rect(x1 - 320, y, x1, y + 13), txt,
                               fontname=bold if i == 0 else reg, fontsize=8 if i == 0 else 7,
                               color=(0.04, 0.04, 0.04) if i == 0 else (0.35, 0.35, 0.35),
                               align=2) < 0:
            raise SystemExit(f"memorandum: {txt!r} nije stalo")
        y += 10.5
    bar = top + h + 18
    page.draw_line(fitz.Point(x0, bar), fitz.Point(x1, bar), color=(0.6, 0.6, 0.6), width=0.6)
    return bar + 8


def cover_page(doc):
    """Cover in the style of the TD title page, adapted for Prilog III."""
    page = doc.new_page(width=595, height=842)  # A4 portrait
    # The memorandum carries the mark (cad/bht-logo.svg, the file the drawing
    # title blocks trace, placed as vector) and the company lines.
    memo_header(page)

    # The base-14 PDF fonts have no š/ć/č/ž/đ, so Bosnian text comes out with
    # question marks. Embed the system Arial instead.
    fonts = {}
    for tag, fname in (("bht", "arial.ttf"), ("bhtb", "arialbd.ttf")):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", fname)
        if os.path.exists(p):
            page.insert_font(fontname=tag, fontfile=p)
            fonts[tag] = True

    def line(txt, y, size, bold=False, colour=(0, 0, 0), align=1):
        if bold:
            font = "bhtb" if "bhtb" in fonts else "hebo"
        else:
            font = "bht" if "bht" in fonts else "helv"
        page.insert_textbox(
            fitz.Rect(50, y, 545, y + size * 3.4),
            txt,
            fontname=font,
            fontsize=size,
            color=colour,
            align=align,
        )

    page.draw_line(
        fitz.Point(50, 168), fitz.Point(545, 168), color=(0.96, 0.51, 0.12), width=1.6
    )

    line("TENDERSKA DOKUMENTACIJA ZA NABAVKU", 210, 14, bold=True)
    line(
        "INFRASTRUKTURA I INSTALACIJA OPREME ZA AUTONOMNI HIBRIDNI "
        "SISTEM NAPAJANJA SJEDNICA, BILEĆA (LOT 1 i 2)",
        250,
        13,
        bold=True,
    )
    line(
        "PROVOĐENJEM NABAVKE PUTEM PREGOVARAČKOG POSTUPKA NABAVKE "
        "SA OBJAVOM OBAVJEŠTENJA",
        330,
        10,
        colour=(0.35, 0.35, 0.35),
    )

    page.draw_rect(fitz.Rect(90, 400, 505, 500), color=(0.96, 0.51, 0.12), width=1.2)
    line("PRILOG III", 418, 20, bold=True)
    line("SITUACIJA, DISPOZICIJA OPREME I GRAFIČKI PRILOZI (NACRTI)", 452, 11)

    line("Lokacija:  BS Sjednica, Bileća, BiH", 560, 10)
    line("Koordinate:  42,9448° N · 18,3236° E · 1076 m n.v.", 578, 10)
    line("Sarajevo, august 2026. godine", 700, 11, bold=True)
    return page


def page_text(page):
    """Text with the PDF's non-breaking spaces and soft hyphens normalised.

    This annex sets words with NBSP between them, so a plain substring search
    for "OPŠTI PODACI O LOKACIJI" finds nothing.
    """
    return page.get_text().replace("\xa0", " ").replace("­", "-").replace("‑", "-")


def portrait_page(out, src, pno, margin=40):
    """Put the site photo on an A4 portrait sheet, so the front matter (cover,
    photo, site data) reads as one portrait set before the A3 drawings.

    The source is A3 landscape with a portrait photograph in the middle and the
    title block bottom right. Fitting the whole sheet would leave the photo tiny,
    so the photo and the title block are placed separately.
    """
    sp = src[pno]
    page = out.new_page(width=595, height=842)
    photo = None
    for im in sp.get_images(full=True):
        for r in sp.get_image_rects(im[0]):
            if photo is None or r.get_area() > photo.get_area():
                photo = r
    if photo is None:                                   # no image - fit the sheet
        w = 595 - 2 * margin
        h = w * sp.rect.height / sp.rect.width
        page.show_pdf_page(fitz.Rect(margin, (842 - h) / 2, margin + w,
                                     (842 - h) / 2 + h), src, pno)
        return page

    w = 595 - 2 * margin
    h = w * photo.height / photo.width
    if h > 660:                                         # keep room for the strip
        h = 660
        w = h * photo.width / photo.height
    x0 = (595 - w) / 2
    page.show_pdf_page(fitz.Rect(x0, margin + 22, x0 + w, margin + 22 + h),
                       src, pno, clip=photo)
    # title-block strip from the bottom right of the source sheet
    strip = fitz.Rect(sp.rect.width * 0.58, sp.rect.height * 0.90,
                      sp.rect.width - 18, sp.rect.height - 8)
    sh = w * strip.height / strip.width
    top = margin + 22 + h + 16
    page.show_pdf_page(fitz.Rect(x0, top, x0 + w, top + sh), src, pno, clip=strip)
    return page


def site_data_page(doc):
    """Set the site-data page from data instead of inheriting it.

    It used to be lifted verbatim out of the previous annex, which meant it went
    on saying 22 kVA / 17,6 kW, "FG Wilson P22-6" and "ograda visine 1,90 m" long
    after all three were superseded - and `check_consistency` cannot see it,
    because Prilog III carries no text layer once assembled, so a stale figure
    here shipped unnoticed.

    Spot-redacting the inherited page was tried and reverted: its values share
    text objects with the labels beside them, so a redaction rect takes the
    neighbour with it and the reprint collides with the next column. The same
    flaw truncated "Bileća" to "Bile" when the entity was stripped. Rebuilding
    the page is both simpler and self-maintaining - every figure below comes
    from cad/design.json.
    """
    import json

    d = json.load(open(os.path.join(BASE, "cad", "design.json"), encoding="utf-8"))
    g, a, m, tk, sup = d["genset"], d["array"], d["module"], d["tank"], d["support"]
    if "energy" not in d:
        raise SystemExit("design.json has no energy block - run tools/sync_energy.py")
    e = d["energy"]
    fence = 2.10                       # certified 04 Ograda.dwg (Rev 6)

    page = doc.new_page(width=595, height=842)
    y0 = memo_header(page)
    reg, bold = arial(page)

    page.insert_textbox(fitz.Rect(50, y0 + 12, 545, y0 + 42), "1.  OPŠTI PODACI O LOKACIJI",
                        fontname=bold, fontsize=14)
    page.draw_line(fitz.Point(50, y0 + 44), fitz.Point(545, y0 + 44),
                   color=(0.96, 0.51, 0.12), width=1.6)

    rows = [
        ("Investitor", "BH Telecom d.d. Sarajevo, Franca Lehara 7, 71000 Sarajevo"),
        ("Objekat", "Bazna stanica SJEDNICA"),
        ("Općina", "Bileća"),
        ("Koordinate", "42,9448° N,  18,3236° E"),
        ("Nadmorska visina", "1076 m"),
        ("Zakupljena površina", "≈150 m² (dio k.č. 1/1, k.o. Granica 2)"),
        ("Betonski temelj", f"5,40 × 5,40 m, sa metalnom ogradom visine "
                            f"{fence:.2f} m".replace(".", ",")),
        ("Antenski stub", "Rešetkasta izvedba, visina 38 m; baza 4,20 m (dno) / "
                          "1,20 m (vrh)"),
        ("Priključak na EES", "NE — lokacija nije priključena na "
                              "elektroenergetsku mrežu"),
        ("TK oprema", "Huawei RRU (3 kom) + BBU/MPLS, −48 VDC"),
        ("Snaga potrošača", "1.180 W nazivno / 1.330 W maksimalno (sa hlađenjem)"),
        ("Sistem napajanja", "Hibridni: FN moduli (primarni) + LFP baterije + "
                             "DEA (rezervni)"),
        ("FN konfiguracija", f"{a['modules_total']} × "
                             f"{m['model'].split('/')[0].replace('Huawei', '').strip()} "
                             f"({a['kWp']:.2f} kWp) na {a['count']} nosača po "
                             f"{sup['modules_each']} modula (položeno), nagib "
                             f"{a['tilt_deg']}°, azimut {a['azimuth_deg']}° (JZ)"
                             .replace(".", ",")),
        ("DEA", f"{g['kVA']:g} kVA / {g['kW']} kW, skid u kontejneru; ulaz ispravljača "
                f"≤{d['control']['rect_cap_ac_kw']} kW".replace(".", ",")),
        ("Spremnik goriva", f"Dvoplašni, {tk['litres']} l, sa nivo sondom i "
                            f"detekcijom curenja"),
        ("Orijentacija", "vrata JI, hladnjak DEA SZ, FN polje JZ; ormari ICC i MTS SI "
                         "(Google Maps, Naručilac 11.09.2026)"),
        ("Očekivani rad agregata", f"{r10(e['genset_h_mean'])}~{r10(e['genset_h_p90'])} "
                                   f"h/god"),
    ]

    x0, x1, x2 = 50, 195, 545
    SIZE = 8.5

    # `insert_textbox` draws NOTHING when the text does not fit and merely
    # returns a negative number - that is how the "Kontejner" row came out blank
    # on the first build of this page. So the row height is measured before the
    # frame is drawn, on a scratch page carrying the same font, and a row that
    # still will not fit stops the build instead of shipping empty.
    scratch = fitz.open()
    probe = scratch.new_page(width=595, height=842)
    arial_ttf = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts",
                             "arial.ttf")
    pfont = "p" if os.path.exists(arial_ttf) else "helv"
    if pfont == "p":
        probe.insert_font(fontname="p", fontfile=arial_ttf)

    def height_for(txt):
        for h in range(24, 108, 11):
            if probe.insert_textbox(fitz.Rect(x1 + 7, 6, x2 - 4, h),
                                    txt, fontname=pfont, fontsize=SIZE) >= 0:
                return h
        raise SystemExit(f"stranica opštih podataka: red ne stane — {txt[:60]!r}")

    y = y0 + 65
    for label, value in rows:
        h = height_for(value)
        page.draw_rect(fitz.Rect(x0, y, x2, y + h), color=(0.75, 0.75, 0.75),
                       width=0.6)
        page.draw_line(fitz.Point(x1, y), fitz.Point(x1, y + h),
                       color=(0.75, 0.75, 0.75), width=0.6)
        for rect, txt, font in (
                (fitz.Rect(x0 + 7, y + 6, x1 - 4, y + h), label, bold),
                (fitz.Rect(x1 + 7, y + 6, x2 - 4, y + h), value, reg)):
            if page.insert_textbox(rect, txt, fontname=font,
                                   fontsize=SIZE) < 0:
                raise SystemExit(
                    f"stranica opštih podataka: {txt[:50]!r} nije stalo")
        y += h
    scratch.close()
    return page


def r10(v):
    """Round half up to the nearest 10 - the '≈' figures in the prose."""
    return int(v / 10 + 0.5) * 10


def num(v, nd=0):
    return f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")


def info_pv_page(doc):
    """INFO-02, rebuilt from the pvsim run: production and energy balance.

    The page it replaces was a clear-sky irradiance map from the old simulation,
    stamped NISU MJERODAVNE since Rev 1 because the report behind it was out by
    an order of magnitude. Here the figures come from review/pvsim/ (written by
    `python -m pvsim report`) and the numbers from kpis.json, set as text so
    check_consistency can read the page.
    """
    import hashlib
    import json

    kp = os.path.join(BASE, "review", "pvsim", "kpis.json")
    raw = open(kp, "rb").read()
    d = json.loads(raw.decode("utf-8"))
    design = json.load(open(os.path.join(BASE, "cad", "design.json"), encoding="utf-8"))
    t = f"{design['array']['tilt_deg']:g}"
    k, v = d["tilts"][t]["kpis"], d["validation"][t]
    c = d["inputs"]["control"]
    fig = os.path.join(BASE, "review", "pvsim", "fig")

    page = doc.new_page(width=1190.55, height=841.89)          # A3 landscape
    # the memorandum takes the top; everything below moves down by dy
    dy = memo_header(page, 40, 1150) - 40
    reg, bold = arial(page)
    orange, grey, ink = (0.96, 0.51, 0.12), (0.35, 0.35, 0.35), (0.04, 0.04, 0.04)

    page.insert_text(fitz.Point(40, dy + 68), "FN simulacija — proizvodnja i energetski "
                     "bilans (informativno)", fontname=bold, fontsize=17, color=ink)
    page.draw_line(fitz.Point(40, dy + 78), fitz.Point(1150, dy + 78), color=orange,
                   width=1.6)

    page.insert_image(fitz.Rect(40, dy + 92, 585, dy + 392),
                      filename=os.path.join(fig, f"f1_bilans_t{t}.png"))
    page.insert_image(fitz.Rect(605, dy + 92, 1150, dy + 432),
                      filename=os.path.join(fig, f"f4_dea_godine_t{t}.png"))

    da = design["array"]
    rows = [
        ("Polje", f"12 × iPV585-M2A = 7,02 kWp na {da['count']} nosača, nagib {t}°, "
                  f"azimut {da['azimuth_deg']}° (jugozapad)"),
        ("FN na DC sabirnici (−48 V)", f"{num(k['pv_bus_kwh'])} kWh/god · "
                                       f"{num(k['specific_yield_bus'])} kWh/kWp"),
        ("Potrošnja", f"{num(k['load_kwh'])} kWh/god (1180 W + hlađenje ormara i "
                      f"pomoćna potrošnja)"),
        ("Decembar", f"FN {num(k['dec_pv_kwh'])} kWh prema potrošnji "
                     f"{num(k['dec_load_kwh'])} kWh"),
        ("Solarni udio u potrošnji", f"{num(100 * k['solar_fraction'], 1)} %"),
        ("Rad DEA", f"prosjek {num(k['genset_h_mean'])} h/god · 9 od 10 godina "
                    f"≤{num(k['genset_h_p90'])} h · najviše {num(k['genset_h_max'])} h"),
        ("Gorivo", f"prosjek {num(k['fuel_l_mean'])} l/god · dopuna spremnika 500 l "
                   f"{num(k['refills_mean'], 1)} puta godišnje"),
        ("Nepokrivena potrošnja", f"{num(k['unmet_kwh_total'])} kWh u "
                                  f"{k['n_years']} godina"),
        ("Provjera prema PVGIS-u", f"PVcalc {num(v['pvcalc_E_y'])} kWh/god, pvsim sa "
                                   f"istim gubicima {num(v['pvsim_E_y'])} kWh/god; "
                                   f"najveće mjesečno odstupanje "
                                   f"{num(100 * v['worst_month_dev'], 1)} %"),
    ]
    x0, x1, x2, y = 40, 250, 800, dy + 452
    for label, value in rows:
        page.draw_rect(fitz.Rect(x0, y, x2, y + 24), color=(0.75, 0.75, 0.75), width=0.6)
        page.draw_line(fitz.Point(x1, y), fitz.Point(x1, y + 24),
                       color=(0.75, 0.75, 0.75), width=0.6)
        for rect, txt, font in ((fitz.Rect(x0 + 6, y + 6, x1 - 4, y + 24), label, bold),
                                (fitz.Rect(x1 + 6, y + 6, x2 - 4, y + 24), value, reg)):
            if page.insert_textbox(rect, txt, fontname=font, fontsize=9) < 0:
                raise SystemExit(f"INFO-02: {txt[:50]!r} nije stalo")
        y += 24

    note = (f"Satna simulacija energetskog bilansa na −48 V DC sabirnici za "
            f"{k['years'][0]}–{k['years'][1]} (pvlib + PVGIS-SARAH3), uz "
            f"parametriranje SMU iz Priloga I, Tačka 4.6: start pri DOD "
            f"{num(100 * c['dod_start'])} %, zaustavljanje pri SoC "
            f"{num(100 * c['soc_stop'])} %, ograničenje ispravljača 9,5 kW. "
            f"Metoda, gubici, osjetljivost i pretpostavke: Proračuni, dio A.6. "
            f"Vrijednosti su informativne i ne mijenjaju zahtjeve Priloga I. "
            f"Izvor: review/pvsim/kpis.json (sha256 "
            f"{hashlib.sha256(raw).hexdigest()[:12]}, pvsim commit {d['git_commit']}).")
    page.insert_textbox(fitz.Rect(820, dy + 452, 1150, dy + 690), note, fontname=reg,
                        fontsize=8.5, color=grey)
    page.draw_rect(fitz.Rect(1030, 760, 1150, 800), color=ink, width=0.8)
    page.insert_textbox(fitz.Rect(1030, 770, 1150, 800), "INFO-02", fontname=bold,
                        fontsize=14, align=1)
    return page


def strip_entity(page):
    """Drop the entity from the municipality row - the Investor wants the
    opština named on its own."""
    hits = []
    for word in ("Republika", "Srpska"):
        hits += page.search_for(word)
    if not hits:
        return 0
    r = hits[0]
    for h in hits[1:]:
        r |= h
    # reach left far enough to take the separator in "Bileća / Republika Srpska"
    page.add_redact_annot(fitz.Rect(r.x0 - 14, r.y0 - 2, r.x1 + 3, r.y1 + 2),
                          fill=(1, 1, 1))
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    return len(hits)


def old_pages_by_code(src):
    """Map drawing number (INFO-01 ...) to page index in the previous annex."""
    found = {}
    for i in range(src.page_count):
        t = page_text(src[i])
        for code in KEEP_FROM_OLD:
            if code in t:
                found.setdefault(code, i)
    return found


def main(argv=None):
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--k2-from-existing", action="store_true",
                    help="reuse the photo and the seven K2 sheets of the current "
                         "annex instead of re-plotting them from the site project")
    args = ap.parse_args(argv)

    if not os.path.exists(OUT):
        raise SystemExit(f"previous annex missing: {OUT}")
    src = fitz.open(OUT)

    tmp = None
    if args.k2_from_existing:
        if src.page_count != LAYOUT["pages"]:
            raise SystemExit(f"--k2-from-existing expects the {LAYOUT['pages']}-page "
                             f"layout, the current annex has {src.page_count}")
        for i in LAYOUT["k2"]:
            if abs(src[i].rect.width * 25.4 / 72 - 420) > 2:
                raise SystemExit(f"page {i + 1} of the current annex is not an A3 "
                                 f"K2 sheet")
        k2 = [(src, i) for i in LAYOUT["k2"]]
        print(f"  K2 sheets: {len(k2)} reused from the current annex")
    else:
        names, tmp = to_dxf([p for p, _, _ in K2_SHEETS])
        k2 = []
        for source, caption, crop in K2_SHEETS:
            pdf = os.path.join(tmp, os.path.basename(names[source])[:-4] + ".pdf")
            dropped = plot_a3(names[source], pdf, crop=crop)
            k2.append((fitz.open(pdf), 0))
            note = f"cropped {dropped} stray entities" if crop else "full sheet"
            print(f"  plotted {caption:34s} ({note})")

    out = fitz.open()
    cover_page(out)
    photo = src[LAYOUT["photo"]]
    if photo.rect.width < photo.rect.height:            # already the A4 photo page
        out.insert_pdf(src, from_page=LAYOUT["photo"], to_page=LAYOUT["photo"])
    else:                                               # a pre-Rev 3 annex
        codes = old_pages_by_code(src)
        if "INFO-01" not in codes:
            raise SystemExit("cannot find INFO-01 in the previous annex")
        portrait_page(out, src, codes["INFO-01"])
    site_data_page(out)
    print("  site-data page: set from cad/design.json (no longer inherited)")
    for n in ("S-01", "S-02", "S-03", "M-01", "E-01"):
        p = os.path.join(DWG, n + ".pdf")
        if not os.path.exists(p):
            raise SystemExit(f"missing plot {p} - run cad/export.py first")
        out.insert_pdf(fitz.open(p))
    for pdf, i in k2:
        out.insert_pdf(pdf, from_page=i, to_page=i)
    info_pv_page(out)
    print("  INFO-02: rebuilt from review/pvsim (kpis.json + figures)")

    out.set_metadata(
        {
            "title": "Prilog III — Situacija, dispozicija opreme i grafički prilozi",
            "author": "BH Telecom d.d. Sarajevo",
            "subject": "BS Sjednica (Bileća) — autonomni hibridni sistem napajanja",
            "creator": "______________, dipl. ing. ___",
        }
    )
    out.subset_fonts()
    before = os.path.getsize(OUT)
    src.close()
    out.save(
        OUT,
        garbage=4,
        deflate=True,
        deflate_images=True,
        deflate_fonts=True,
        clean=True,
    )
    n = out.page_count
    out.close()
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    print(
        f"\nPrilog III: {n} pages, {before / 1e6:.1f} MB -> "
        f"{os.path.getsize(OUT) / 1e6:.2f} MB"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
