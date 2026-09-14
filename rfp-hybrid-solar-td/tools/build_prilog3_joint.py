# -*- coding: utf-8 -*-
"""
Prilog III of the joint tender: one annex, two site blocks.

    cover (joint)
    A. BS Sjednica  - photo page with the block headline, site data, S-01..E-01,
                      the seven K2 sheets, INFO-02
    B. BS Hamzići   - photos with the block headline, site data, H-01..H-05,
                      sheets of the certified 2017 project (as reference), INFO-02

The A4 pages and both INFO-02 pages carry the BH Telecom memorandum as their
header (Investor, 11.09.2026); the A3 drawings keep their own title block.
There are no separator pages: each block opens with its headline on the photo
page.  The Sjednica site data and INFO-02 are set by the functions of the
Sjednica tools/build_prilog3.py, its drawings come from its grafika folder and
only the K2 sheets and the photo are lifted from its annex, so the two cannot
drift apart.  The Hamzići pages are built here from
hamzici-hybrid-solar/cad/design.json, its review/pvsim/ and its drawings.
"""
import hashlib
import json
import os
import sys

import fitz

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths                                                        # noqa: E402

SJ = paths.SITES["sjednica"]["folder"]
HZ = paths.SITES["hamzici"]["folder"]
sys.path.insert(0, os.path.join(SJ, "tools"))
# build_prilog3 imports its own site's paths module, but the joint one already
# sits in sys.modules under the same name: swap it out while bp3 loads.
_joint_paths = sys.modules.pop("paths")
import build_prilog3 as bp3                                         # noqa: E402
sys.modules["paths"] = _joint_paths

SJ_ANNEX = bp3.OUT            # Sjednica Prilog III (16 pages): photo and K2 sheets
SJ_SHEETS = ["S-01", "S-02", "S-03", "M-01", "E-01"]
HZ_PROJECT = os.path.join(HZ, "GP BS HAMZIĆI_Čitluk K2 i AS 36 m")
_AG = os.path.join(HZ_PROJECT, "4 - ARHITEKTONSKO GRADJEVINSKI DIO", "6 Graficki dio")
CERTIFIED = [
    (os.path.join(_AG, "461 Graficki dio TEMELJ i OGRADA", "01_Situacija 1_200.dwg"),
     "Situacija 1:200"),
    (os.path.join(_AG, "461 Graficki dio TEMELJ i OGRADA", "04_Ograda.dwg"), "Ograda"),
    (os.path.join(_AG, "462 Graficki dio ANTENSKI STUB 32 m", "01_Dispozicija S32 m.dwg"),
     "Dispozicija antenskog stuba S32"),
    (os.path.join(_AG, "463 Graficki dio OBJEKAT", "01 Osnova.dwg"), "Kontejner K2 — osnova"),
    (os.path.join(_AG, "463 Graficki dio OBJEKAT", "04 Fasade.dwg"), "Kontejner K2 — fasade"),
    (os.path.join(HZ_PROJECT, "5_ELEKTRO INSTALACIJE", "Graficki dio",
                  "3.6.9  Plan uzemljivača objekta.dwg"), "Plan uzemljivača objekta"),
]
PHOTOS = [("20260908_121209_sunce.jpg", "Antenski stub i kontejner; pogled prema jugu-jugoistoku"),
          ("20260908_121141_sunce.jpg", "Kontejner sa klima-uređajem Stulz WDE80 (demontira se)")]
H_SHEETS = ["H-01", "H-02", "H-03", "H-04", "H-05"]
PVSIM_BAR_PX = 46             # caption strip `pvsim photo` adds (pvsim/photo.py, bar)
ORANGE, GREY, INK = (0.96, 0.51, 0.12), (0.35, 0.35, 0.35), (0.04, 0.04, 0.04)
POINTS = ("sjever", "sjeveroistok", "istok", "jugoistok", "jug", "jugozapad", "zapad",
          "sjeverozapad")


def r10(v):
    return int(v / 10 + 0.5) * 10


def num(v, nd=0):
    return f"{v:,.{nd}f}".replace(",", " ").replace(".", ",")


def azimuth(az):
    """225 -> 'azimut 225° (jugozapad)'."""
    return f"azimut {az:g}° ({POINTS[round(az / 45) % 8]})"


def fonts(page):
    return bp3.arial(page)


def line(page, font, txt, y, size, colour=INK, x0=50, x1=None, align=1):
    x1 = page.rect.width - 50 if x1 is None else x1
    if page.insert_textbox(fitz.Rect(x0, y, x1, y + size * 3.4), txt, fontname=font,
                           fontsize=size, color=colour, align=align) < 0:
        raise SystemExit(f"Prilog III: {txt[:50]!r} nije stalo")


def headline(page, y, letter, site, place):
    """Block headline, in place of the separator pages (Investor, 11.09.2026)."""
    reg, bold = fonts(page)
    line(page, bold, f"{letter}.  BS {site.upper()} ({place.upper()})", y, 16, align=0)
    page.draw_line(fitz.Point(50, y + 28), fitz.Point(page.rect.width - 50, y + 28),
                   color=ORANGE, width=1.6)
    return y + 38


# --------------------------------------------------------------------------
def cover(doc):
    page = doc.new_page(width=595, height=842)
    bp3.memo_header(page)
    reg, bold = fonts(page)
    page.draw_line(fitz.Point(50, 168), fitz.Point(545, 168), color=ORANGE, width=1.6)
    line(page, bold, "TENDERSKA DOKUMENTACIJA ZA NABAVKU", 210, 14)
    line(page, bold, "INFRASTRUKTURA I INSTALACIJA OPREME ZA AUTONOMNI HIBRIDNI SISTEM "
                     "NAPAJANJA SJEDNICA, BILEĆA I HAMZIĆI, ČITLUK (LOT 1 i 2)", 250, 13)
    line(page, reg, "PROVOĐENJEM NABAVKE PUTEM PREGOVARAČKOG POSTUPKA NABAVKE SA OBJAVOM "
                    "OBAVJEŠTENJA", 330, 10, GREY)
    page.draw_rect(fitz.Rect(90, 400, 505, 500), color=ORANGE, width=1.2)
    line(page, bold, "PRILOG III", 418, 20)
    line(page, reg, "SITUACIJE, DISPOZICIJA OPREME I GRAFIČKI PRILOZI (NACRTI)", 452, 11)
    line(page, bold, "Lokacije", 545, 10)
    line(page, reg, "A.  BS Sjednica, Bileća — 42,9448° N · 18,3236° E · 1076 m n.v.", 563, 10)
    line(page, reg, "B.  BS Hamzići, Čitluk — 43,2880° N · 17,6248° E · 493 m n.v.", 581, 10)
    line(page, bold, "Sarajevo, septembar 2026. godine", 700, 11)


def photo_page_sj(doc, sj):
    """The Sjednica photo, with its INFO-01 title strip, lifted from the Sjednica
    annex and scaled to about 85 % under the block headline."""
    pno = bp3.LAYOUT["photo"]
    src = sj[pno]
    rects = [r for im in src.get_images(full=True) for r in src.get_image_rects(im[0])]
    if not rects:
        raise SystemExit("Sjednica annex: no photo on its photo page")
    photo = max(rects, key=lambda r: r.get_area())
    clip = fitz.Rect(0, photo.y0 - 4, src.rect.width, src.rect.height - 8)
    page = doc.new_page(width=595, height=842)
    y = headline(page, bp3.memo_header(page) + 4, "A", "Sjednica", "Bileća") + 6
    w = 0.85 * 595
    h = w * clip.height / clip.width
    if y + h > 842 - 24:
        h = 842 - 24 - y
        w = h * clip.width / clip.height
    x0 = (595 - w) / 2
    page.show_pdf_page(fitz.Rect(x0, y, x0 + w, y + h), sj, pno, clip=clip)


def photo_page_hz(doc):
    """A4 LANDSCAPE, the two site photos side by side (Investor, 14.09.2026).
    Portrait stacked them at 290 pt high and left most of the page empty."""
    W, H = 842, 595
    page = doc.new_page(width=W, height=H)
    y = headline(page, bp3.memo_header(page) + 4, "B", "Hamzići", "Čitluk")
    reg, bold = fonts(page)
    line(page, reg, "Fotografije postojećeg stanja lokacije, 08.09.2026.", y, 9.5, GREY,
         align=0)
    y += 20
    gap, margin = 24, 50
    w = (W - 2 * margin - gap) / len(PHOTOS)
    avail = H - y - 28                       # room left for the image and its caption
    for i, (name, caption) in enumerate(PHOTOS):
        path = os.path.join(HZ, "review", "pvsim", "photo", name)
        pix = fitz.Pixmap(path)
        # These were shot in portrait and stored turned on their side, so the mast
        # lay across the page. ROTATE=270 (i.e. 90° clockwise) stands it up. The
        # 46 px caption strip `pvsim photo` adds along the bottom is cropped off -
        # turned with the image it would run vertically up the side; the view is
        # named in the caption below instead.
        clip = fitz.IRect(0, 0, pix.width, pix.height - PVSIM_BAR_PX)
        cropped = fitz.Pixmap(pix.colorspace, clip, pix.alpha)
        cropped.copy(pix, clip)
        pix = cropped
        iw, ih = w, w * pix.width / pix.height      # portrait once turned
        if ih > avail - 16:
            ih = avail - 16
            iw = ih * pix.height / pix.width
        x0 = margin + i * (w + gap) + (w - iw) / 2
        page.insert_image(fitz.Rect(x0, y, x0 + iw, y + ih), pixmap=pix, rotate=270)
        line(page, reg, caption, y + ih + 5, 8.5, GREY,
             x0=margin + i * (w + gap), x1=margin + i * (w + gap) + w, align=0)
    if y + avail > H - 12:
        raise SystemExit("Hamzići photo page: the photos do not fit")


def table_page(doc, title, rows):
    """A titled two-column data page under the memorandum, rows sized to their
    text (the same layout as the Sjednica site-data page)."""
    page = doc.new_page(width=595, height=842)
    y0 = bp3.memo_header(page)
    reg, bold = fonts(page)
    page.insert_textbox(fitz.Rect(50, y0 + 12, 545, y0 + 42), title, fontname=bold, fontsize=14)
    page.draw_line(fitz.Point(50, y0 + 44), fitz.Point(545, y0 + 44), color=ORANGE, width=1.6)
    x0, x1, x2, size = 50, 195, 545, 8.5
    scratch = fitz.open()
    probe = scratch.new_page(width=595, height=842)
    preg, _ = fonts(probe)

    def height_for(txt):
        for h in range(24, 108, 11):
            if probe.insert_textbox(fitz.Rect(x1 + 7, 6, x2 - 4, h), txt, fontname=preg,
                                    fontsize=size) >= 0:
                return h
        raise SystemExit(f"{title}: red ne stane — {txt[:60]!r}")

    y = y0 + 65
    for label, value in rows:
        h = height_for(value)
        page.draw_rect(fitz.Rect(x0, y, x2, y + h), color=(0.75, 0.75, 0.75), width=0.6)
        page.draw_line(fitz.Point(x1, y), fitz.Point(x1, y + h), color=(0.75, 0.75, 0.75),
                       width=0.6)
        for rect, txt, font in ((fitz.Rect(x0 + 7, y + 6, x1 - 4, y + h), label, bold),
                                (fitz.Rect(x1 + 7, y + 6, x2 - 4, y + h), value, reg)):
            if page.insert_textbox(rect, txt, fontname=font, fontsize=size) < 0:
                raise SystemExit(f"{title}: {txt[:50]!r} nije stalo")
        y += h
    scratch.close()
    if y > 842 - 30:
        raise SystemExit(f"{title}: the table runs off the page")


def hamzici_data(doc):
    """Technical data only (Investor, 11.09.2026): no container row, no note."""
    d = json.load(open(os.path.join(HZ, "cad", "design.json"), encoding="utf-8"))
    e, g, a, sup, ctl = d["energy"], d["genset"], d["array"], d["support"], d["control"]
    rows = [
        ("Investitor", "BH Telecom d.d. Sarajevo, Franca Lehara 7, 71000 Sarajevo"),
        ("Objekat", "Bazna stanica HAMZIĆI"),
        ("Općina", "Čitluk"),
        ("Koordinate", "43,2880° N,  17,6248° E"),
        ("Nadmorska visina", "493 m"),
        ("Zakupljena površina", "150 m² (12,00 × 12,50 m), k.č. 109/1 K.O. Hamzići (novi premjer)"),
        ("Betonski temelj", "5,40 × 5,40 m, sa metalnom ogradom visine 1,80 m; kapija 1,30 m "
                            "na SZ strani"),
        ("Antenski stub", "Rešetkasta izvedba, visina 32 m; baza 3,70 × 3,70 m; platforma na "
                          "+3,0 m iznad krova kontejnera"),
        ("Klima-uređaj", "Stulz WDE80, 8 kW, u sredini JI zida; demontaža i odvoz u "
                         "skladište Alipašino Polje (LOT 2)"),
        ("Oprema Kupca", "FN moduli, PVDB, iSSU, baterije, ICC360-HA1-C1 — nabavka "
                         "Naručioca; preuzimanje u skladištu Azići, Bojnička bb, Sarajevo, "
                         "prevoz i istovar u LOT 2 (Prilog I, Tačka 4.9)"),
        ("Priključak na EES", "Nema; priključak projektovan 2017. nije izveden"),
        ("Snaga potrošača", "1.180 W nazivno / 1.330 W maksimalno"),
        ("Sistem napajanja", "Hibridni: FN moduli + LFP baterije + DEA (rezervni)"),
        ("FN konfiguracija", f"{a['modules_total']} × iPV585-M2A ({num(a['kWp'], 2)} kWp) na "
                             f"{a['count']} nosača po {sup['modules_each']} modula (položeno), "
                             f"nagib {a['tilt_deg']}°, azimut {a['azimuth_deg']}° (JZ)"),
        ("DEA", f"{g['kVA']:g} kVA / {num(g['kW'], 1)} kW, skid u kontejneru; ulaz "
                f"ispravljača ≤{num(ctl['rect_cap_ac_kw'], 1)} kW"),
        ("Spremnik goriva", "Dvoplašni, 500 l, sa nivo sondom i detekcijom curenja"),
        ("Orijentacija", "Vrata i kapija SZ, hladnjak DEA JI, FN polje JZ; ormari ICC360 i "
                         "MTS na JZ strani, iza FN polja"),
        ("Očekivani rad agregata", f"{r10(e['genset_h_mean'])}~{r10(e['genset_h_p90'])} h/god"),
    ]
    table_page(doc, "1.  OPŠTI PODACI O LOKACIJI — BS HAMZIĆI", rows)


def tree_note(base, t):
    """The tree study of `python -m pvsim photo`, if the site has one."""
    zj = os.path.join(base, "review", "pvsim", "photo", "zasjenjenje.json")
    if not os.path.exists(zj):
        return ""
    res = json.load(open(zj, encoding="utf-8"))["results"][t]
    h0 = res["bez prepreke (DEM)"]["genset_h_mean"]
    dh = [v["genset_h_mean"] - h0 for k, v in res.items() if k.startswith("stablo")]
    return (f"Bez zasjenjenja stablom JJI–JI; sa stablom rad DEA raste za "
            f"{min(dh):.0f}–{max(dh):.0f} h/god. ")


def info_pv(doc, base, t):
    """INFO-02 for Hamzići, from its review/pvsim (the Sjednica block's comes from
    bp3.info_pv_page)."""
    kp = os.path.join(base, "review", "pvsim", "kpis.json")
    raw = open(kp, "rb").read()
    d = json.loads(raw.decode("utf-8"))
    k, v, c = d["tilts"][t]["kpis"], d["validation"][t], d["inputs"]["control"]
    da = json.load(open(os.path.join(base, "cad", "design.json"), encoding="utf-8"))["array"]
    fig = os.path.join(base, "review", "pvsim", "fig")
    page = doc.new_page(width=1190.55, height=841.89)
    dy = bp3.memo_header(page, 40, 1150) - 40
    reg, bold = fonts(page)
    page.insert_text(fitz.Point(40, dy + 68), "FN simulacija — proizvodnja i energetski bilans "
                     "(informativno)", fontname=bold, fontsize=17, color=INK)
    page.draw_line(fitz.Point(40, dy + 78), fitz.Point(1150, dy + 78), color=ORANGE, width=1.6)
    page.insert_image(fitz.Rect(40, dy + 92, 585, dy + 392),
                      filename=os.path.join(fig, f"f1_bilans_t{t}.png"))
    page.insert_image(fitz.Rect(605, dy + 92, 1150, dy + 432),
                      filename=os.path.join(fig, f"f4_dea_godine_t{t}.png"))
    rows = [
        ("Polje", f"12 × iPV585-M2A = 7,02 kWp na {da['count']} nosača, nagib {t}°, "
                  f"{azimuth(da['azimuth_deg'])}"),
        ("FN na DC sabirnici (−48 V)", f"{num(k['pv_bus_kwh'])} kWh/god · "
                                       f"{num(k['specific_yield_bus'])} kWh/kWp"),
        ("Potrošnja", f"{num(k['load_kwh'])} kWh/god (1180 W + hlađenje ormara i pomoćna "
                      f"potrošnja)"),
        ("Decembar", f"FN {num(k['dec_pv_kwh'])} kWh prema potrošnji {num(k['dec_load_kwh'])} kWh"),
        ("Solarni udio u potrošnji", f"{num(100 * k['solar_fraction'], 1)} %"),
        ("Rad DEA", f"prosjek {num(k['genset_h_mean'])} h/god · 9 od 10 godina "
                    f"≤{num(k['genset_h_p90'])} h · najviše {num(k['genset_h_max'])} h"),
        ("Gorivo", f"prosjek {num(k['fuel_l_mean'])} l/god · dopuna spremnika 500 l "
                   f"{num(k['refills_mean'], 1)} puta godišnje"),
        ("Nepokrivena potrošnja", f"{num(k['unmet_kwh_total'])} kWh u {k['n_years']} godina"),
        ("Provjera prema PVGIS-u", f"PVcalc {num(v['pvcalc_E_y'])} kWh/god, pvsim sa istim "
                                   f"gubicima {num(v['pvsim_E_y'])} kWh/god; najveće mjesečno "
                                   f"odstupanje {num(100 * v['worst_month_dev'], 1)} %"),
    ]
    x0, x1, x2, y = 40, 250, 800, dy + 452
    for label, value in rows:
        page.draw_rect(fitz.Rect(x0, y, x2, y + 24), color=(0.75, 0.75, 0.75), width=0.6)
        page.draw_line(fitz.Point(x1, y), fitz.Point(x1, y + 24), color=(0.75, 0.75, 0.75),
                       width=0.6)
        for rect, txt, font in ((fitz.Rect(x0 + 6, y + 6, x1 - 4, y + 24), label, bold),
                                (fitz.Rect(x1 + 6, y + 6, x2 - 4, y + 24), value, reg)):
            if page.insert_textbox(rect, txt, fontname=font, fontsize=9) < 0:
                raise SystemExit(f"INFO-02: {txt[:50]!r} nije stalo")
        y += 24
    note = (f"Satna simulacija energetskog bilansa na −48 V DC sabirnici za "
            f"{k['years'][0]}–{k['years'][1]} (pvlib + PVGIS-SARAH3), uz parametriranje SMU iz "
            f"Priloga I, Tačka 4.6: start pri DOD {num(100 * c['dod_start'])} %, zaustavljanje "
            f"pri SoC {num(100 * c['soc_stop'])} %, ograničenje ispravljača 9,5 kW. "
            f"{tree_note(base, t)}Metoda, gubici, osjetljivost i pretpostavke: proračuni "
            f"lokacije, dio A.6. Vrijednosti su informativne. Izvor: review/pvsim/kpis.json "
            f"(sha256 {hashlib.sha256(raw).hexdigest()[:12]}, pvsim commit {d['git_commit']}).")
    page.insert_textbox(fitz.Rect(820, dy + 452, 1150, dy + 700), note, fontname=reg,
                        fontsize=8.5, color=GREY)
    page.draw_rect(fitz.Rect(1030, 760, 1150, 800), color=INK, width=0.8)
    page.insert_textbox(fitz.Rect(1030, 770, 1150, 800), "INFO-02", fontname=bold,
                        fontsize=14, align=1)


def certified_sheets(doc):
    names, tmp = bp3.to_dxf([p for p, _ in CERTIFIED])
    for src, caption in CERTIFIED:
        pdf = os.path.join(tmp, os.path.basename(names[src])[:-4] + ".pdf")
        bp3.plot_a3(names[src], pdf, crop=False)
        sheet = fitz.open(pdf)
        page = sheet[0]
        reg, bold = fonts(page)
        box = fitz.Rect(page.rect.width - 470, 12, page.rect.width - 14, 52)
        page.draw_rect(box, color=ORANGE, fill=(1, 1, 1), width=1.0)
        page.insert_textbox(fitz.Rect(box.x0 + 6, box.y0 + 4, box.x1 - 6, box.y1),
                            f"{caption} — preuzeto iz ovjerenog projekta GP-BS-10472-291 (2017), "
                            f"samo kao podloga. Crtež iz 2017. zakrenut je ≈180° prema stanju na "
                            f"terenu; vrata i kapija gledaju na SZ (vidi H-01).",
                            fontname=reg, fontsize=7.5, color=INK)
        doc.insert_pdf(sheet)
        print(f"  certified: {caption}")
    return tmp


def main():
    if not os.path.exists(SJ_ANNEX):
        raise SystemExit(f"Sjednica annex missing: {SJ_ANNEX}")
    missing = [s for s in H_SHEETS
               if not os.path.exists(os.path.join(HZ, "TD-OUTPUT", "grafika", s + ".pdf"))]
    missing += [s for s in SJ_SHEETS if not os.path.exists(os.path.join(bp3.DWG, s + ".pdf"))]
    if missing:
        raise SystemExit(f"drawings missing: {missing} - run the site drawing builds")
    sj = fitz.open(SJ_ANNEX)
    if sj.page_count != bp3.LAYOUT["pages"]:
        raise SystemExit(f"Sjednica annex: {sj.page_count} pages, expected {bp3.LAYOUT['pages']}")
    for i in bp3.LAYOUT["k2"]:
        if abs(sj[i].rect.width * 25.4 / 72 - 420) > 2:
            raise SystemExit(f"Sjednica annex page {i + 1} is not an A3 K2 sheet")
    out = fitz.open()
    cover(out)
    photo_page_sj(out, sj)
    bp3.site_data_page(out)
    for s in SJ_SHEETS:
        out.insert_pdf(fitz.open(os.path.join(bp3.DWG, s + ".pdf")))
    for i in bp3.LAYOUT["k2"]:
        out.insert_pdf(sj, from_page=i, to_page=i)
    bp3.info_pv_page(out)
    photo_page_hz(out)
    hamzici_data(out)
    for s in H_SHEETS:
        out.insert_pdf(fitz.open(os.path.join(HZ, "TD-OUTPUT", "grafika", s + ".pdf")))
    tmp = certified_sheets(out)
    info_pv(out, HZ, "45")
    out.set_metadata({"title": "Prilog III — Situacije, dispozicija opreme i grafički prilozi",
                      "author": "BH Telecom d.d. Sarajevo",
                      "subject": "BS Sjednica (Bileća) i BS Hamzići (Čitluk) — autonomni "
                                 "hibridni sistemi napajanja"})
    out.subset_fonts()
    out.save(paths.PRILOG3, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True,
             clean=True)
    n = out.page_count
    out.close()
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Prilog III (joint): {n} pages, {os.path.getsize(paths.PRILOG3) / 1e6:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
