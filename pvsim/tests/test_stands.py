"""stands.py must reproduce the figures already in the tender (07-proracuni B.5,
Rev <=6 07-calculations) before its 60° / 2x6 values mean anything."""
import pytest

from pvsim import config, stands

MODULE = {"L": 2278, "W": 1134, "kg": 32.0}


def test_rev8_3x4_at_45():
    r = stands.stand("3x4", 45, 1.20, MODULE, bottom_edge=0.5, strip_spacing=1.6)
    assert r["area_m2"] == pytest.approx(10.55, abs=0.01)
    assert r["Fh_kN"] == pytest.approx(13.4, abs=0.05)
    # Rev 8 rounds F_v to 13,4 before multiplying (20,2 - 2,1 = 18,1)
    assert r["uplift_uls_kN"] == pytest.approx(18.1, abs=0.1)
    assert r["M_kNm"] == pytest.approx(42.6, abs=0.1)
    assert r["couple_kN"] == pytest.approx(26.6, abs=0.1)
    assert r["top_edge_m"] == pytest.approx(3.736, abs=0.002)
    assert r["depth_m"] == pytest.approx(3.236, abs=0.002)


def test_rev6_2x6_at_45():
    r = stands.stand("2x6", 45, 1.20, MODULE, bottom_edge=0.5, strip_spacing=1.6)
    assert r["area_m2"] == pytest.approx(15.91, abs=0.01)
    assert r["M_kNm"] == pytest.approx(64.3, abs=0.1)
    assert r["uplift_uls_kN"] == pytest.approx(27.3, abs=0.1)


def test_60_degrees_geometry_and_moment_range():
    lo = stands.stand("3x4", 60, 1.20, MODULE, c_f=1.5)
    hi = stands.stand("3x4", 60, 1.20, MODULE, c_f=1.8)
    assert lo["top_edge_m"] == pytest.approx(4.46, abs=0.01)
    assert lo["depth_m"] == pytest.approx(2.288, abs=0.002)
    assert 60 < lo["M_kNm"] < hi["M_kNm"] < 75
    assert lo["snow_mu1"] == 0.0


def test_4x3L_landscape_at_45():
    """The adopted stand (11.09.2026): 4 stands of 3 modules in landscape."""
    r = stands.stand("4x3L", 45, 1.20, MODULE, bottom_edge=0.5, strip_spacing=1.6)
    assert (r["stands"], r["modules_per_stand"], r["strips"]) == (4, 3, 8)
    assert r["field_w_m"] == pytest.approx(2.278, abs=0.001)
    assert r["field_slope_m"] == pytest.approx(3.442, abs=0.001)
    assert r["depth_m"] == pytest.approx(2.434, abs=0.002)      # fits the 3,30 m band
    assert r["top_edge_m"] == pytest.approx(2.934, abs=0.002)
    assert r["M_kNm"] == pytest.approx(25.7, abs=0.1)
    assert r["strip_m3_required"] < r["strip_m3_adopted"] == stands.STRIP_4X3L_M3


def test_compare_covers_all_layouts_and_tilts():
    rows = stands.compare(config.load("sjednica"))
    combos = {(r["layout"], r["tilt"]) for r in rows}
    assert combos == {(lay, t) for lay in ("3x4", "2x6", "4x3L") for t in (45, 60)}
