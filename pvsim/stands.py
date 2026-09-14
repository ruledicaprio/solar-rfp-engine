"""Wind actions on the PV stands and the foundation strips they need.

The method of 07-proracuni B.5/B.6: net force coefficient per BAS EN 1991-1-4
§7.3 (c_f = 1,5 at 45°), ULS partial factors gamma_Q = 1,5 and
gamma_G,fav = 0,9, overturning about the ground from the centroid of the field,
and a full-depth strip whose own weight must hold the uplift couple. Here it is
parameterised so the stand layouts (3 stands of 2x2 modules, "3x4"; 2 stands
of 2x3, "2x6"; 4 stands of 1x3 landscape, "4x3L") and both tilts (45° / 60°)
can be compared per site. "4x3L" is the adopted stand at both sites (user
decision 11.09.2026): separate small plates instead of one sail, and 2,43 m
deep at 45°, so it fits the 3,30 m band at Hamzići.

EN 1991-1-4 gives canopy coefficients only up to 30° pitch. Above 45° the plate
behaves more like a free-standing sign, so 60° is reported for c_f = 1,5 AND 1,8,
a range rather than a figure. The bidder's certified calculation governs.

Reproduces the Rev 8 Sjednica values (3x4 at 45°: 13,4 kN horizontal, 18,1 kN
ULS uplift, 42,6 kNm, 26,6 kN per strip) and the Rev <=6 2x6 overturning moment
(64,3 kNm) - see tests/test_stands.py.
"""
from __future__ import annotations

import math

MODULE_GAP_W = 0.037    # between module columns, m (2305 = 2 x 1134 + 37)
MODULE_GAP_L = 0.020    # between module rows, m    (4576 = 2 x 2278 + 20)
GAMMA_Q, GAMMA_G_FAV = 1.5, 0.9
CONCRETE_KN_M3 = 24.0
REV8_STRIP_M3 = 1.485   # 450/550 x 900 x 3300 mm, 07-proracuni B.6

STRIP_4X3L_M3 = 1.170   # 500 x 900 x 2600 mm constant section, 07-proracuni B.6 (4x3L)

# "landscape" puts the module's long side across the stand, so the slope is
# rows x module W instead of rows x module L.
LAYOUTS = {
    "3x4": {"stands": 3, "cols": 2, "rows": 2, "orient": "portrait", "frame_kg": 110.0,
            "strip_m3": REV8_STRIP_M3,
            "_frame": "design.json support.weight_kg (estimate, fabricator confirms)"},
    "2x6": {"stands": 2, "cols": 3, "rows": 2, "orient": "portrait", "frame_kg": 159.0,
            "strip_m3": REV8_STRIP_M3,
            "_frame": "Rev <=6 2x6 design: 0,9 G = 3,1 kN -> 351 kg per stand less 6 modules"},
    "4x3L": {"stands": 4, "cols": 1, "rows": 3, "orient": "landscape", "frame_kg": 0.0,
             "strip_m3": STRIP_4X3L_M3,
             "_frame": "the frame's own weight is NEGLECTED in the uplift proof (favourable "
                       "action, so omitting it is the safe side). The former 95 kg estimate was "
                       "withdrawn on the reviewer's comment (Adis Colpa, 27.08.2026, proracun "
                       "B.3) that it is implausibly small; the real mass follows from the "
                       "fabricator's certified calculation and is not tendered as a figure."},
}


def snow_mu1(tilt):
    """EN 1991-1-3 §5.3.2 monopitch shape coefficient."""
    if tilt <= 30:
        return 0.8
    if tilt >= 60:
        return 0.0
    return 0.8 * (60.0 - tilt) / 30.0


def stand(layout, tilt, qp, module, bottom_edge=0.5, strip_spacing=1.6, c_f=1.5):
    lay = LAYOUTS[layout]
    L, W = module["L"] / 1000.0, module["W"] / 1000.0
    if lay["orient"] == "landscape":
        L, W = W, L
    width = lay["cols"] * W + (lay["cols"] - 1) * MODULE_GAP_W
    slope = lay["rows"] * L + (lay["rows"] - 1) * MODULE_GAP_L
    area = width * slope
    a = math.radians(tilt)

    f = c_f * qp * area
    fh, fv = f * math.sin(a), f * math.cos(a)
    n_mod = lay["cols"] * lay["rows"]
    g = (n_mod * module["kg"] + lay["frame_kg"]) * 9.81 / 1000.0
    uplift = GAMMA_Q * fv - GAMMA_G_FAV * g
    centroid = bottom_edge + slope / 2.0 * math.sin(a)
    m = GAMMA_Q * fh * centroid
    couple = m / strip_spacing
    strip_req = couple / GAMMA_G_FAV / CONCRETE_KN_M3
    return {
        "layout": layout, "tilt": tilt, "c_f": c_f, "stands": lay["stands"],
        "modules_per_stand": n_mod, "field_w_m": width, "field_slope_m": slope,
        "area_m2": area, "F_kN": f, "Fh_kN": fh, "Fv_kN": fv, "G_kN": g,
        "uplift_uls_kN": uplift, "centroid_m": centroid, "M_kNm": m,
        "couple_kN": couple, "strip_m3_required": strip_req,
        "strip_m3_adopted": max(strip_req, lay["strip_m3"]),
        "strips": 2 * lay["stands"],
        "concrete_m3_total": 2 * lay["stands"] * max(strip_req, lay["strip_m3"]),
        "top_edge_m": bottom_edge + slope * math.sin(a),
        "depth_m": slope * math.cos(a), "snow_mu1": snow_mu1(tilt),
    }


def compare(site, gap_between_stands=0.4):
    """All four layout x tilt combinations for a site; 60° at both c_f bounds."""
    st = site["stands"]
    module = site["design"]["module"]
    rows = []
    for layout in LAYOUTS:
        for tilt in site["array"].get("tilts", [site["array"]["tilt_deg"]]):
            for c_f in ((1.5,) if tilt <= 45 else (1.5, 1.8)):
                r = stand(layout, tilt, st["qp_kNm2"], module, st["bottom_edge_m"],
                          st["strip_spacing_m"], c_f)
                n = r["stands"]
                r["array_w_m"] = n * r["field_w_m"] + (n - 1) * gap_between_stands
                r["fits_width"] = r["array_w_m"] <= st["plot_max_width_m"]
                r["fits_depth"] = r["depth_m"] <= st["plot_max_depth_m"]
                rows.append(r)
    return rows
