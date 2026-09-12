# -*- coding: utf-8 -*-
"""
Build the joint two-site tender package into rfp-hybrid-solar-td/TD-OUTPUT/.

    python rfp-hybrid-solar-td/tools/build_joint.py

Steps, each from the site folders' sources (never from hand-typed numbers):
  1. figures for Prilog I      site grafika + each site's review/pvsim/fig
  2. Prilog I                  review/prilog1.md -> pandoc -> .docx, checked
  3. proračuni                 each site's review/07-proracuni.md -> PDF with text
  4. drawings                  S-01..E-01 (Sjednica) and H-01..H-05 (Hamzići)
  5. NZ / TD JN / Odluka / Izjava   joint_docs.py (OOXML edits)
  6. Prilog II                 joint_boq.py, if present
  7. Prilog III                build_prilog3_joint.py, if present
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths                                                        # noqa: E402

SJ = paths.SITES["sjednica"]["folder"]
HZ = paths.SITES["hamzici"]["folder"]
sys.path.insert(0, os.path.join(SJ, "tools"))
import build_prilog1 as bp1                                         # noqa: E402

SOFFICE = os.environ.get("SOFFICE", r"C:\Program Files\LibreOffice\program\soffice.exe")
P1_DIR = os.path.join(paths.GRAFIKA, "prilog1")

FIGURES = {
    "agregat-bocni.png": os.path.join(SJ, "TD-OUTPUT", "grafika", "prilog1", "agregat-bocni.png"),
    "agregat-celni.png": os.path.join(SJ, "TD-OUTPUT", "grafika", "prilog1", "agregat-celni.png"),
    "spremnik-bocni.png": os.path.join(SJ, "TD-OUTPUT", "grafika", "prilog1", "spremnik-bocni.png"),
    "spremnik-odozgo.png": os.path.join(SJ, "TD-OUTPUT", "grafika", "prilog1", "spremnik-odozgo.png"),
    # rendered from the current sheet, like H-04 (the stored PNG predates the true orientation)
    "m01-raspored.png": os.path.join(SJ, "TD-OUTPUT", "grafika", "M-01.pdf"),
    "h04-raspored.png": os.path.join(HZ, "TD-OUTPUT", "grafika", "H-04.pdf"),
    "energetski-bilans-sjednica.png": os.path.join(SJ, "review", "pvsim", "fig", "f1_bilans_t45.png"),
    "energetski-bilans-hamzici.png": os.path.join(HZ, "review", "pvsim", "fig", "f1_bilans_t45.png"),
    "horizont-hamzici.png": os.path.join(HZ, "review", "pvsim", "fig", "f2_horizont.png"),
}

# Values that were wrong once and must not come back, and values that must be
# there. The Sjednica lists carry over (same system); the Hamzići ones are new.
FORBIDDEN = bp1.FORBIDDEN + [
    ("Čapljin", "Hamzići su u općini Čitluk"),
    ("AS 36 m", "stub na Hamzićima je 32 m"),
    ("Hamzići?", "zaostali upitnik iz nacrta"),
    ("1,94 m", "nadvišenje ograde na Hamzićima je 0,93 m: teren je 0,20 m ispod ploče"),
    ("ISTOČNI zid, južni kraj", "Stulz je u sredini JI zida (Naručilac 11.09.2026)"),
    ("duža osa istok–zapad", "agregat na Hamzićima stoji po osi SZ–JI"),
    # 11.09.2026: true orientation, SW fields, 4x3L stand at both sites
    ("azimut 180°", "polja su okrenuta prema jugozapadu, azimut 225°"),
    ("2 reda × 2", "nosač je 1 × 3 modula, položeno (4x3L)"),
    ("≈230 h/god", "Hamzići: ≈270 h/god sa poljem prema JZ"),
    ("≈750 l/god", "Hamzići: ≈900 l/god sa poljem prema JZ"),
    ("1,74 m", "nadvišenje ograde na Hamzićima je 0,93 m (4x3L)"),
]
# the Sjednica Rev 9 values this round supersedes, and what replaces them
SUPERSEDED_REQUIRED = {
    "42,6 kNm": "25,7 kNm", "26,6 kN": "16,1 kN", "1,485 m³": None, "8,91 m³": None,
    "+0,50 m / +3,74 m": None, "1,64 m": "0,83 m", "18,1 kN": None, "13,4 kN": None,
    "≈250 h/god": "≈300 h/god", "≈820 l/god": "≈990 l/god",
    "SJEVERNI zid, istočni kraj": None, "JUŽNI zid": None,
}
REQUIRED = [r for r in bp1.REQUIRED if r not in SUPERSEDED_REQUIRED] \
    + [v for v in SUPERSEDED_REQUIRED.values() if v] + [
    "493 m", "0,93 m", "h = 1,80 m", "3300 mm", "k.č. 109/1", "Stulz WDE80",
    "Alipašino Polje", "0,36 m²", "≈270 h/god", "≈900 l/god", "H-04", "12,3 kW",
    "izvlačni", "≤0,50 m", "3.6.9 Plan uzemljivača", "225°",
]
N_MEDIA = len(FIGURES)


def figures():
    os.makedirs(P1_DIR, exist_ok=True)
    for name, src in FIGURES.items():
        if not os.path.exists(src):
            raise SystemExit(f"missing figure source {src}")
        dst = os.path.join(P1_DIR, name)
        if src.lower().endswith(".pdf"):
            # A drawing sheet: the whole A3 page at 200 dpi, as m01-raspored.png is.
            import pymupdf
            with pymupdf.open(src) as doc:
                doc[0].get_pixmap(dpi=200).save(dst)
        else:
            shutil.copy(src, dst)
    print(f"  figures: {len(FIGURES)} -> {os.path.relpath(P1_DIR, paths.JOINT)}")


def prilog1():
    bp1.build(md=os.path.join(paths.JOINT, "review", "prilog1.md"), out=paths.PRILOG1,
              forbidden=FORBIDDEN, required=REQUIRED, n_media=N_MEDIA)
    evidence_table_widths(paths.PRILOG1)


def evidence_table_widths(path, shares=(0.07, 0.63, 0.10, 0.20)):
    """The evidence table (Br. | Dokaz | LOT | Oznaka) comes out of widen_tables
    with four equal columns, so the long 'Dokaz' texts wrap into nine lines. Give
    that one table its own widths; every other table keeps the shared layout."""
    import re
    import zipfile

    z = zipfile.ZipFile(path)
    items = {n: z.read(n) for n in z.namelist()}
    z.close()
    xml = items["word/document.xml"].decode("utf-8")
    done = 0

    def fix(m):
        nonlocal done
        tbl = m.group(0)
        first_cell = re.search(r"<w:tc>.*?</w:tc>", tbl, re.S)
        text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", first_cell.group(0))) \
            if first_cell else ""
        cols = re.findall(r'<w:gridCol w:w="(\d+)"\s*/>', tbl)
        if text.strip() != "Br." or len(cols) != len(shares):
            return tbl
        total = sum(int(c) for c in cols)
        new = [int(total * s) for s in shares]
        new[-1] += total - sum(new)
        done += 1
        return re.sub(r"<w:tblGrid>.*?</w:tblGrid>",
                      "<w:tblGrid>" + "".join(f'<w:gridCol w:w="{w}"/>' for w in new)
                      + "</w:tblGrid>", tbl, count=1, flags=re.S)

    xml = re.sub(r"<w:tbl>.*?</w:tbl>", fix, xml, flags=re.S)
    if done != 1:
        raise SystemExit(f"evidence table: expected 1, adjusted {done}")
    items["word/document.xml"] = xml.encode("utf-8")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as out:
        for name, data in items.items():
            out.writestr(name, data)


def calc_pdf(md, outs, required):
    """A calculations markdown -> PDF with a text layer (pandoc + LibreOffice)."""
    import fitz

    tmp = tempfile.mkdtemp(prefix="proracuni_")
    docx = os.path.join(tmp, "proracuni.docx")
    subprocess.run([bp1.pandoc(), md, "-o", docx, "--reference-doc", bp1.REF,
                    "--resource-path", os.path.dirname(md),
                    "--from", "markdown+pipe_tables+raw_attribute", "--columns", "999"],
                   check=True)
    bp1.widen_tables(docx)
    profile = "file:///" + os.path.join(tmp, "lo").replace("\\", "/")
    subprocess.run([SOFFICE, f"-env:UserInstallation={profile}", "--headless",
                    "--convert-to", "pdf", "--outdir", tmp, docx],
                   check=True, capture_output=True, timeout=600)
    pdf = os.path.join(tmp, "proracuni.pdf")
    d = fitz.open(pdf)
    text = "".join(p.get_text() for p in d).replace("\xa0", " ")
    pages = d.page_count
    d.close()
    missing = [r for r in required if r not in text]
    if missing:
        raise SystemExit(f"{os.path.basename(md)}: missing in the PDF: {missing}")
    for out in outs:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copy(pdf, out)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"  proračuni {os.path.basename(outs[0])}: {pages} str.")


def calculations():
    calc_pdf(os.path.join(SJ, "review", "07-proracuni.md"),
             [os.path.join(paths.TD, "proracuni_BS_Sjednica_Bileca.pdf")],
             ["A.6 Energetski bilans", "≈300 h/god", "25,7 kNm", "D.8 Trajni potrošači"])
    calc_pdf(os.path.join(HZ, "review", "07-proracuni.md"),
             [os.path.join(paths.TD, "proracuni_BS_Hamzici_Citluk.pdf"),
              os.path.join(HZ, "review", "07-proracuni_hamzici.pdf")],
             ["A.6 Energetski bilans", "≈270 h/god", "25,7 kNm", "Stulz WDE80", "D.9 Trajni potrošači"])


def drawings():
    for site, folder, pattern in (("sjednica", SJ, "[SME]-0*"), ("hamzici", HZ, "H-0*")):
        src = glob.glob(os.path.join(folder, "TD-OUTPUT", "grafika", pattern))
        dst = os.path.join(paths.GRAFIKA, site)
        os.makedirs(dst, exist_ok=True)
        for f in src:
            shutil.copy(f, dst)
        print(f"  drawings {site}: {len(src)} files")


def run(script):
    path = os.path.join(HERE, script)
    if not os.path.exists(path):
        print(f"  {script}: not present yet - skipped")
        return
    subprocess.run([sys.executable, path], check=True)


def main():
    os.makedirs(paths.TD, exist_ok=True)
    print("1. figures");        figures()
    print("2. Prilog I");       prilog1()
    print("3. proračuni");      calculations()
    print("4. drawings");       drawings()
    print("5. documents");      run("joint_docs.py")
    print("6. Prilog II");      run("joint_boq.py")
    print("7. Prilog III");     run("build_prilog3_joint.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
