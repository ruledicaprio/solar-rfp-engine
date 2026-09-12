# -*- coding: utf-8 -*-
"""Where the joint two-site TD package lives, and where it takes its parts from.

The joint package is assembled from the two site folders, which stay the
source of truth for their own drawings, calculations and energy figures:

    bht-sjednica-final-review/   BS Sjednica (Bileća)  - Rev 9
    hamzici-hybrid-solar/        BS Hamzići (Čitluk)

TD_OUT redirects every output to another folder (reproduction checks).
"""
import os

JOINT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(JOINT)
TD = os.environ.get("TD_OUT") or os.path.join(JOINT, "TD-OUTPUT")
GRAFIKA = os.path.join(TD, "grafika")

SITES = {
    "sjednica": {"folder": os.path.join(ROOT, "bht-sjednica-final-review"),
                 "name": "Sjednica", "place": "Bileća", "altitude_m": 1076},
    "hamzici": {"folder": os.path.join(ROOT, "hamzici-hybrid-solar"),
                "name": "Hamzići", "place": "Čitluk", "altitude_m": 493},
}

NZ = os.path.join(TD, "1. NZ hibridni sistem napajanja BS Sjednica i BS Hamzići.docx")
TDJN = os.path.join(TD, "2. TD JN Hibridni sistem napajanja BS Sjednica i BS Hamzići.docx")
ODLUKA = os.path.join(TD, "2.1 Prijedlog Odluke Hibridni sistem napajanja BS Sjednica i BS Hamzići.docx")
PRILOG1 = os.path.join(TD, "3. Prilog I TD - Specifikacija zahtjeva.docx")
# one price form per LOT: a bidder fills in and signs only the LOT it bids for
PRILOG2_LOT = {lot: os.path.join(TD, f"3.1 PRILOG II TD - Obrazac za cijenu ponude {lot} - "
                                     f"Sjednica i Hamzici.xlsx") for lot in ("LOT 1", "LOT 2")}
PRILOG3 = os.path.join(TD, "3.2 Prilog III TD - Situacije.pdf")
IZJAVA = os.path.join(TD, "4. Izjava o stanju zaliha BS Sjednica i BS Hamzići.docx")
