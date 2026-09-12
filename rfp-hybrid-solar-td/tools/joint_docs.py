# -*- coding: utf-8 -*-
"""
The four Word documents of the joint tender (NZ, TD JN, Prijedlog Odluke,
Izjava), made from the Sjednica Rev 9 documents by OOXML edits.

Per the repo rule the .docx files are not regenerated: each is copied from the
Sjednica package and only its text is changed, through ooxml_edit.Part - which
concatenates the runs, edits the visible text and writes it back into the first
run of the span, so formatting survives. Two structural additions are done at
the XML level with the same care: a second row in TD JN Table 1 (Hamzići) and a
second "Postojeće stanje" block, both cloned from the Sjednica ones so they
carry the same styles.

Every replacement states how many times it must match; a template that has
drifted fails instead of half-editing.

Estimate (Investor, 12.09.2026): 100 000,00 KM bez PDV-a for both sites, LOT 1
30 000,00 KM and LOT 2 70 000,00 KM. The Sjednica documents carried three
different totals - 100 000 in the NZ and the Odluka point II, 50 000 (15 000 +
35 000) in the Odluka's plan paragraphs and one table total, and "pedesethiljada"
in words next to 100 000 - so every one is set to the Investor's figures here.
"""
import os
import re
import shutil
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import paths                                                        # noqa: E402

sys.path.insert(0, os.path.join(paths.SITES["sjednica"]["folder"], "tools"))
from ooxml_edit import Part                                         # noqa: E402

SRC = os.path.join(paths.SITES["sjednica"]["folder"], "TD-OUTPUT")
WORDS_100K = "(sto hiljada konvertibilnih maraka)"

TITLE_OLD = "SISTEM NAPAJANJA SJEDNICA, BILEĆA (LOT 1 i 2)"
TITLE_NEW = "SISTEM NAPAJANJA SJEDNICA, BILEĆA I HAMZIĆI, ČITLUK (LOT 1 i 2)"
LOT2_OLD = ("isporuka i instalacija agregatskog postrojenja 18 kVA za montažu u kontejner "
            "sa spremnikom goriva 500 l, ožičenje, testiranje i puštanje u rad")
LOT2_NEW = ("isporuka i instalacija dva agregatska postrojenja 18 kVA (po jedno na svakoj "
            "lokaciji) za montažu u postojeće kontejnere sa spremnikom goriva 500 l, "
            "ožičenje, testiranje i puštanje u rad")

ODLUKA_LIMITS_REV9 = (
    "Satna simulacija energetskog bilansa za 19 godina (pvlib, PVGIS-SARAH3, "
    "2005–2023) daje očekivani rad agregata od ≈250 h godišnje (u najlošijoj godini "
    "do ≈330 h), uz potrošnju goriva od ≈820 l godišnje; spremnik od 500 l "
    "dopunjava se u prosjeku dva puta godišnje. Vrijednosti važe uz "
    "parametriranje upravljačke jedinice za minimalan rad agregata, propisano "
    "Prilogom I TD. Agregat radi u režimu trajne (prime) snage prema ISO 8528-1, sa "
    "ulaznom snagom ispravljača ograničenom na 9,5 kW.")
# SW-facing fields at both sites (Investor 11.09.2026): the pvsim run at azimuth 225°
ODLUKA_LIMITS_JOINT = (
    "Satna simulacija energetskog bilansa za 19 godina (pvlib, PVGIS-SARAH3, "
    "2005–2023) daje očekivani rad agregata od ≈300 h godišnje na lokaciji Sjednica "
    "i ≈270 h na lokaciji Hamzići (u najlošijim godinama do ≈380 h, odnosno ≈350 h), "
    "uz potrošnju goriva od ≈990 l, odnosno ≈900 l godišnje; spremnik od 500 l "
    "dopunjava se u prosjeku dva do tri puta godišnje. Vrijednosti važe za FN polja "
    "okrenuta prema jugozapadu (azimut 225°, nagib 45°) i uz parametriranje "
    "upravljačke jedinice za minimalan rad agregata, propisano Prilogom I TD. "
    "Agregati rade u režimu trajne (prime) snage prema ISO 8528-1, sa ulaznom "
    "snagom ispravljača ograničenom na 9,5 kW.")

HAMZICI_OBJECT = [
    "Objekat Hamzići, Čitluk (493 mnv) je građevinska cjelina sa prisutnim strukturama:",
    "temelj: AB temeljna ploča dim. 5,40 x 5,40 m, na kojoj stoje antenski stub i kontejner",
    "antenski sistem: rešetkasti stub visine h = 32 m, sa platformom na +3,0 m iznad krova kontejnera",
    "objekat: kontejner K2 vanjskih dimenzija 3,00 x 2,30 m, prazan (bez GRO i instalacija), sa "
    "kompaktnim zidnim klima-uređajem Stulz WDE80 na jugoistočnom zidu, koji se demontira i "
    "odvozi u "
    "skladište BH Telecom-a (Alipašino Polje, Sarajevo)",
    "vanjski ormari za TK opremu: Huawei ICC360-HA1-C1 (PowerCube 1000) sa ispravljačima, LFP "
    "baterijama i kontrolerom (zasebna nabavka Naručioca)",
    "okolina: metalna ograda visine 1,80 m oko temelja 5,40 x 5,40 m, sa kapijom na "
    "sjeverozapadnoj strani;",
    "zakupljena površina 150 m² (12,00 x 12,50 m), k.č. 109/1 K.O. Hamzići",
    "Lokacija nije priključena na EES (priključak projektovan 2017. godine nije izveden) i DEA "
    "predstavlja rezervni izvor napajanja u okviru hibridnog sistema.",
]

ODLUKA_HAMZICI = (
    "Objekat Hamzići (Čitluk) nalazi se na nadmorskoj visini od 493 m, na koordinatama "
    "43.2880° N, 17.6248° E, na parceli k.č. 109/1 K.O. Hamzići (zakup 150 m²). Na lokaciji "
    "su AB temeljna ploča 5,40 × 5,40 m, rešetkasti antenski stub visine 32 m, metalna "
    "ograda visine 1,80 m i kontejner K2 bez opreme, sa zidnim klima-uređajem Stulz koji se "
    "demontira. Priključak na elektrodistributivnu mrežu, projektovan 2017. godine, nije "
    "izveden, pa se i ova lokacija napaja autonomnim hibridnim sistemom, istim kao na "
    "lokaciji Sjednica.")


# --------------------------------------------------------------------------
def load(path):
    z = zipfile.ZipFile(path)
    items = {n: z.read(n) for n in z.namelist()}
    z.close()
    return items


def save(path, items):
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for name, data in items.items():
            out.writestr(name, data)
    os.replace(tmp, path)


def replace(part, find, repl, expect, regex=False):
    """Replace exactly `expect` matches of the visible text (None = at least one)."""
    pat = find if regex else re.escape(find)
    n = len(re.findall(pat, part.text))
    if (expect is None and n == 0) or (expect is not None and n != expect):
        raise SystemExit(f"EDIT FAILED: {find[:70]!r}: expected {expect}, found {n}")
    part.replace(find, repl, n, regex)
    return n


PARA = re.compile(r"<w:p[ >].*?</w:p>", re.S)
RUN = re.compile(r"<w:r[ >].*?</w:r>", re.S)


def clone_paragraph(p_xml, text):
    """Same paragraph properties and first-run formatting, new text."""
    runs = RUN.findall(p_xml)
    first = next(r for r in runs if "<w:t" in r)
    rpr = re.search(r"<w:rPr>.*?</w:rPr>", first, re.S)
    esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    new_run = ("<w:r>" + (rpr.group(0) if rpr else "") +
               f'<w:t xml:space="preserve">{esc}</w:t></w:r>')
    head = p_xml[:p_xml.index(runs[0])]
    return head + new_run + "</w:p>"


def para_text(p_xml):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p_xml))


def insert_after_paragraph(xml, anchor_text, new_paras):
    paras = [(m.start(), m.end(), m.group(0)) for m in PARA.finditer(xml)]
    hits = [p for p in paras if para_text(p[2]).strip() == anchor_text]
    if len(hits) != 1:
        raise SystemExit(f"anchor {anchor_text[:60]!r}: found {len(hits)}")
    end = hits[0][1]
    return xml[:end] + "".join(new_paras) + xml[end:]


def paragraph_by_text(xml, text):
    hits = [m.group(0) for m in PARA.finditer(xml) if para_text(m.group(0)).strip() == text]
    if len(hits) != 1:
        raise SystemExit(f"paragraph {text[:60]!r}: found {len(hits)}")
    return hits[0]


# --------------------------------------------------------------------------
def nz(path):
    items = load(path)
    p = Part(items["word/document.xml"].decode("utf-8"))
    replace(p, TITLE_OLD, TITLE_NEW, 1)
    replace(p, "Predmet nabavke je podijeljen na 2 LOT-a:",
            "Predmet nabavke za obje lokacije je podijeljen na 2 LOT-a:", 1)
    replace(p, "montaža nosača za fotonaponske panele 3 kpl,",
            "montaža nosača za fotonaponske panele 8 kpl (4 kpl po lokaciji),", 1)
    replace(p, LOT2_OLD + " hibridnog sistema.",
            LOT2_NEW + " hibridnih sistema, te demontaža postojećeg klima-uređaja na "
            "lokaciji Hamzići.", 1)
    replace(p, "Prilog III TD: Situacija Sjednica, Bileća.",
            "Prilog III TD: Situacije Sjednica, Bileća i Hamzići, Čitluk.", 1)
    replace(p, "Prilog II TD: Obrazac za cijenu ponude i",
            "Prilog II TD: Obrazac za cijenu ponude (zaseban za svaki LOT) i", 1)
    # estimate (Investor, 12.09.2026): 100 000 KM bez PDV-a, LOT 1 30 000 / LOT 2 70 000 -
    # the amounts of the Sjednica NZ; only the amount in words was wrong
    replace(p, "100.000,00 KM (pedesethiljada konvertibilnih maraka)", f"100.000,00 KM {WORDS_100K}", 1)
    replace(p, "LOT 1 — 30.000,00 KM", "LOT 1 — 30.000,00 KM", 1)
    replace(p, "LOT 2 — 70.000,00 KM", "LOT 2 — 70.000,00 KM", 1)
    replace(p, "Mjesto realizacije je objekat BH Telecoma Sjednica, Bileća (42.9448° N, "
               "18.3236° E, nadmorska visina 1076 m).",
            "Mjesta realizacije su objekti BH Telecoma Sjednica, Bileća (42.9448° N, 18.3236° E, "
            "nadmorska visina 1076 m) i Hamzići, Čitluk (43.2880° N, 17.6248° E, nadmorska "
            "visina 493 m).", 1)
    replace(p, "Projektnim zadatkom za hibridno napajanje BS Sjednica.",
            "Projektnim zadatkom za hibridno napajanje BS Sjednica, koji se primjenjuje i na "
            "BS Hamzići.", 1)
    replace(p, "Autonomni hibridni sistem napajanja - BS Sjednica (Bileća)",
            "Autonomni hibridni sistemi napajanja - BS Sjednica (Bileća) i BS Hamzići (Čitluk)", 1)
    items["word/document.xml"] = p.xml.encode("utf-8")
    save(path, items)


def tdjn(path):
    items = load(path)
    xml = items["word/document.xml"].decode("utf-8")

    # Table 1: a second location row, cloned from the Sjednica row
    tbl = re.search(r"<w:tbl>.*?</w:tbl>", xml, re.S)
    rows = re.findall(r"<w:tr[ >].*?</w:tr>", tbl.group(0), re.S)
    if len(rows) != 2 or "SJEDNICA" not in para_text(rows[1]):
        raise SystemExit("TD JN Table 1 is not the expected 2-row location table")
    new_row = rows[1]
    for old, new in (("1.", "2."), ("RS", "FBiH"), ("BILEĆA", "ČITLUK"),
                     ("SJEDNICA", "HAMZIĆI"), ("42.944810, 18.323640", "43.288012, 17.624794")):
        new_row, n = re.subn(r"(<w:t[^>]*>)" + re.escape(old) + r"(</w:t>)",
                             r"\g<1>" + new.replace("\\", r"\\") + r"\g<2>", new_row, count=1)
        if n != 1:
            raise SystemExit(f"Table 1: cell {old!r} is split across runs")
    table = tbl.group(0).replace(rows[1], rows[1] + new_row, 1)
    xml = xml[:tbl.start()] + table + xml[tbl.end():]

    # a second "Postojeće stanje" block for Hamzići, cloned from the Sjednica one
    sj = [paragraph_by_text(xml, t) for t in (
        "Objekat Sjednica, Bileća (1076 mnv) je građevinska cjelina sa prisutnim strukturama:",
        "temelj: AB temeljna ploča dim. 5,40 x 5,40 m",
        "antenski sistem: rešetkasti stub visine h = 38 m",
        "objekat: kontejner vanjskih dimenzija 3,00 x 2,30 m")]
    sj_rest = [m.group(0) for m in PARA.finditer(xml)
               if para_text(m.group(0)).startswith(("vanjski ormari za TK opremu",
                                                   "okolina: metalna ograda",
                                                   "dostupna površina parcele",
                                                   "Lokacija nije priključena na EES"))]
    if len(sj_rest) != 4:
        raise SystemExit(f"Postojeće stanje block: expected 4 more paragraphs, found {len(sj_rest)}")
    templates = sj + sj_rest
    clones = [clone_paragraph(t, s) for t, s in zip(templates, HAMZICI_OBJECT)]
    xml = insert_after_paragraph(
        xml, "Lokacija nije priključena na EES i DEA predstavlja rezervni izvor napajanja u "
             "okviru hibridnog sistema.", clones)

    p = Part(xml)
    replace(p, TITLE_OLD, TITLE_NEW, 1)
    replace(p, "na lokalitetu Sjednica, Bileća", "na lokalitetima Sjednica, Bileća i Hamzići, "
            "Čitluk", 1)
    replace(p, "Tabela 1 Geografski položaj objekta sa koordinatama",
            "Tabela 1 Geografski položaj objekata sa koordinatama", 1)
    replace(p, "Objekat ima otežan putni pristup", "Oba objekta imaju otežan putni pristup", 1)
    # the Sjednica template pencilled Hamzići in as a possible substitute site;
    # in the joint tender it is one of the two sites
    replace(p, "zamjensku lokaciju sličnih karakteristika (Hamzići?), ili",
            "zamjensku lokaciju sličnih karakteristika, ili", 1)
    replace(p, "biće realizovan jednodnevni obilazak lokacije za sve prijavljene ponuđače",
            "biće realizovan obilazak obje lokacije (po jedan dan za svaku) za sve prijavljene "
            "ponuđače", 1)
    # warranty clauses named the LOTs the wrong way round (LOT 1 = PV stands)
    replace(p, "isporučeni agregat i pratecu opremu (za LOT 1), nosače PV panela i prateću "
               "opremu (za LOT 2)",
            "nosače PV panela i prateću opremu (za LOT 1), isporučeni agregat i prateću opremu "
            "(za LOT 2)", 2)
    # Prilog II: one price form per LOT (Investor, 12.09.2026) - the award is per LOT
    replace(p, "PRILOG II: Obrazac za cijenu ponude (LOT 1 i LOT 2)",
            "PRILOG II: Obrazac za cijenu ponude, zaseban za LOT 1 i za LOT 2", 1)
    replace(p, "izražena u KM bez PDV-a. (za jedan ili oba LOT-a)",
            "izražena u KM bez PDV-a. (za jedan ili oba LOT-a; za svaki LOT kojem ponuda "
            "pristupa popunjava se, potpisuje i ovjerava zaseban obrazac)", 1)
    items["word/document.xml"] = p.xml.encode("utf-8")
    save(path, items)


def odluka(path):
    items = load(path)
    xml = items["word/document.xml"].decode("utf-8")
    anchor = next(para_text(m.group(0)).strip() for m in PARA.finditer(xml)
                  if para_text(m.group(0)).startswith("Objekat Sjednica (Bileća) je 2014."))
    xml = insert_after_paragraph(xml, anchor,
                                 [clone_paragraph(paragraph_by_text(xml, anchor), ODLUKA_HAMZICI)])
    # financial-plan tables: the first table's total reads 50.000 under its 100.000 row.
    # Done per <w:t>, because the flat text glues neighbouring cells into "100.000100.000"
    xml, n_cells = re.subn(r"(<w:t(?:\s[^>]*)?>)50\.000(</w:t>)", r"\g<1>100.000\g<2>", xml)
    if n_cells != 2:
        raise SystemExit(f"Odluka: expected the two 50.000 table-total cells, found {n_cells}")
    p = Part(xml)
    replace(p, "napajanja Sjednica, Bileća (LOT 1 i 2)",
            "napajanja Sjednica, Bileća i Hamzići, Čitluk (LOT 1 i 2)", 3)
    replace(p, "na baznoj stanici Sjednica (Bileća)",
            "na baznim stanicama Sjednica (Bileća) i Hamzići (Čitluk)", 4)
    replace(p, "NA BAZNOJ STANICI SJEDNICA (BILEĆA)",
            "NA BAZNIM STANICAMA SJEDNICA (BILEĆA) I HAMZIĆI (ČITLUK)", 2)
    replace(p, "(ground mount support) - 3 kpl,", "(ground mount support) - 8 kpl (4 kpl po "
            "lokaciji),", 2)
    replace(p, LOT2_OLD + " hibridnog sistema.",
            LOT2_NEW + " hibridnih sistema, te demontaža postojećeg klima-uređaja na "
            "lokaciji Hamzići.", 1)
    replace(p, LOT2_OLD + " čitavog hibridnog sistema.",
            LOT2_NEW + " čitavih hibridnih sistema, te demontaža postojećeg klima-uređaja na "
            "lokaciji Hamzići.", 1)
    # estimate (Investor, 12.09.2026): 100 000 KM bez PDV-a, LOT 1 30 000 / LOT 2 70 000
    replace(p, "(pedesethiljada konvertibilnih maraka)", WORDS_100K, 3)
    replace(p, "ukupno 50.000,00 KM", "ukupno 100.000,00 KM", 2)
    replace(p, "LOT 1 — 15.000,00 KM i LOT 2 — 35.000,00 KM",
            "LOT 1 — 30.000,00 KM i LOT 2 — 70.000,00 KM", 2)
    replace(p, "od čega se iznos od 30.000,00 KM odnosi na LOT 1a iznos od 70.000,00 KM na "
               "LOT 2 —", "od čega se iznos od 30.000,00 KM odnosi na LOT 1, a iznos od "
               "70.000,00 KM na LOT 2. ", 1)
    # Aneks 2: the approved two-site wording
    replace(p, ODLUKA_LIMITS_REV9, ODLUKA_LIMITS_JOINT, 1)
    replace(p, "smješten u postojeći kontejner. DEA napaja ispravljače.",
            "smješten u postojeći kontejner na svakoj lokaciji. DEA napaja ispravljače.", 1)
    # 4x3L and SW at both sites (Investor 11.09.2026)
    replace(p, "LOT 1 : metalna konstrukcija sa 3 (tri) nosača za fotonaponske panele",
            "LOT 1 : metalne konstrukcije sa po 4 (četiri) odvojena nosača za fotonaponske "
            "panele na svakoj lokaciji", 1)
    replace(p, "orijentacije jug (azimut 180°)", "orijentacije jugozapad (azimut 225°)", 1)
    replace(p, "LOT 2: agregatsko postrojenje sa automatskim",
            "LOT 2: dva agregatska postrojenja (po jedno na svakoj lokaciji) sa automatskim", 1)
    replace(p, "postojeći kontejner na lokaciji, dvoplašnim spremnikom",
            "postojeće kontejnere na lokacijama, dvoplašnim spremnicima", 1)
    replace(p, "sa ožičenjem sistema do potpune funcionalnosti i puštanjem u rad.",
            "sa ožičenjem sistema do potpune funcionalnosti i puštanjem u rad, te demontažom "
            "postojećeg klima-uređaja na lokaciji Hamzići.", 1)
    replace(p, "objekat Sjednica, Bileća ne može biti pušten u rad, obzirom da lokacija nije "
               "priključena",
            "objekti Sjednica, Bileća i Hamzići, Čitluk ne mogu biti pušteni u rad, obzirom da "
            "lokacije nisu priključene", 1)
    replace(p, "Nabavka autonomnog hibridnog sistema napajanja za BS Sjednica nije",
            "Nabavka autonomnih hibridnih sistema napajanja za BS Sjednica i BS Hamzići nije", 1)
    replace(p, "Nabavka i instalacija hibridnog sistema napajanja - BS Sjednica",
            "Nabavka i instalacija hibridnih sistema napajanja - BS Sjednica i BS Hamzići", 1)
    items["word/document.xml"] = p.xml.encode("utf-8")
    save(path, items)


def izjava(path):
    items = load(path)
    p = Part(items["word/document.xml"].decode("utf-8"))
    replace(p, "na baznoj stanici Sjednica (Bileća)",
            "na baznim stanicama Sjednica (Bileća) i Hamzići (Čitluk)", 2)
    items["word/document.xml"] = p.xml.encode("utf-8")
    save(path, items)


JOBS = [
    ("1. NZ hibridni sistem napajanja BS Sjednica.docx", paths.NZ, nz),
    ("2. TD JN Hibridni sistem napajanja BS Sjednica.docx", paths.TDJN, tdjn),
    ("2.1 Prijedlog Odluke Hibridni sistem napajanja BS Sjednica.docx", paths.ODLUKA, odluka),
    ("4. Izjava o stanju zaliha BS Sjednica.docx", paths.IZJAVA, izjava),
]


def main():
    os.makedirs(paths.TD, exist_ok=True)
    for src, dst, fn in JOBS:
        shutil.copy(os.path.join(SRC, src), dst)
        fn(dst)
        print(f"  {os.path.basename(dst)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
