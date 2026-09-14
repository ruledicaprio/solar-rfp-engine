# -*- coding: utf-8 -*-
"""Build the measured-load report ("Koliko radi agregat uz stvarnu potrošnju?").

The report runs the TD's pvsim dispatch for BS Sjednica and BS Hamzići with
measured telecom loads instead of the tender's 1180 W. Everything site-specific
lives in report/local/, which is gitignored - this repo is public and the
measurements come from other BH Telecom sites:

    local/template.html   the report page; its data placeholder is /*__DATA__*/null
    local/measured.json   {"hod_w": {"0": W, ... "23": W}, "mean_w": W,
                           "level_w": W, "mpls_w": W}
                          hod_w/mean_w: the measured daily shape; level_w: the
                          measured mean level; mpls_w: the transport device added
                          in the upper scenario

Writes local/out/report_data.json and local/out/neteco-report.html. Publishing
the page is a separate, manual step.

The load model deliberately differs from pvsim's (the TD keeps pvsim's):
shelter cooling is a free-cooling floor all hours from October to March, and
from April to September the floor below T0 rising linearly to MAX at T1 on the
hourly ERA5 air temperature.

Other differences from the TD run:
  * tank: one refill a year, to 500 l on 1 September; an extra refill is counted
    when the level reaches 20 % before the next September;
  * weeks: the Nov-Feb week with most genset hours and the coldest week of the
    median year, for the regime chart.

    python rfp-hybrid-solar-td/report/build_report.py        (from the repo root)
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LOCAL = os.path.join(HERE, "local")
OUTDIR = os.path.join(LOCAL, "out")
sys.path.insert(0, ROOT)
from pvsim import config, model, pv, pvgis                          # noqa: E402
from pvsim import dispatch as D                                     # noqa: E402

TZ = "Europe/Sarajevo"
SITES = (("sjednica", "bht-sjednica-final-review"), ("hamzici", "hamzici-hybrid-solar"))
COOL = {"fc_w": 25.0, "max_w": 150.0, "t0": 18.0, "t1": 35.0}   # shelter cooling model
DOD_SENS = (0.70, 0.80, 0.85, 0.90)                             # SMU02C "DOD to Start"
FC_SENS = (0.0, 50.0)                                           # free-cooling floor, W
CUR = {"b": None}                                               # hourly telecom load, W


def cool_w(temp_air):
    T = np.asarray(temp_air, dtype=float)
    month = temp_air.index.tz_convert(TZ).month.to_numpy()
    ramp = np.clip((T - COOL["t0"]) / (COOL["t1"] - COOL["t0"]), 0.0, 1.0)
    fc = COOL["fc_w"]
    return np.where((month >= 4) & (month <= 9), fc + (COOL["max_w"] - fc) * ramp, fc)


def load_kw(temp_air, s):
    """pvsim's load with the seasonal cooling; CUR["b"] replaces the constant base_w."""
    x = (s["load"]["base_w"] + s["load"]["aux_w"] + cool_w(temp_air)) / 1000.0
    if CUR["b"] is None:
        return x
    hrs = temp_air.index.tz_convert(TZ).hour
    return x + (np.array([CUR["b"][h] for h in hrs]) - s["load"]["base_w"]) / 1000.0


def runs(h):
    f = h["gen_frac"].to_numpy(); out = []; cur = 0.0
    for v in f:
        if v > 0:
            cur += v
        elif cur > 0:
            out.append(cur); cur = 0.0
    if cur > 0:
        out.append(cur)
    return np.array(out)


def tank_trace(fuel_local, cap=500.0, at=100.0):
    """One refill to `cap` on 1 September; extra refills when the level reaches `at`."""
    level = cap; days = []; extra = []
    for i, (_, f) in enumerate(fuel_local.resample("D").sum().items()):
        level -= f
        if level <= at:
            extra.append(i); level = cap
        days.append(round(level, 1))
    return days, extra


def brief(k):
    return {"h": round(k["genset_h_mean"]), "h_p90": round(k["genset_h_p90"]), "l": round(k["fuel_l_mean"]),
            "starts": round(k["starts_mean"], 1), "curt": round(k["curtailed_kwh"]),
            "l_per_kwh_dc": round(k["fuel_l_mean"] / k["gen_dc_kwh"], 3) if k["gen_dc_kwh"] else None,
            "gap_days": round(k["longest_genset_free_days"], 1)}


def scenario(s, p, temp):
    k, years, monthly, h = model.dispatch(s, p, temp)
    loc = h.tz_convert(TZ)
    mm = monthly.groupby(level="month").mean()
    r = runs(h)
    wins = sorted((loc[f"{y}-09-01":f"{y + 1}-08-31"]["fuel_l"].sum(), y) for y in range(2005, 2023)
                  if len(loc[f"{y}-09-01":f"{y + 1}-08-31"]) > 8700)
    fmed, ymed = wins[len(wins) // 2]
    days, extra = tank_trace(loc[f"{ymed}-09-01":f"{ymed + 1}-08-31"]["fuel_l"])
    so = {"h": round(k["genset_h_mean"]), "h_p90": round(k["genset_h_p90"]), "h_max": round(k["genset_h_max"]),
          "l": round(k["fuel_l_mean"]), "starts": round(k["starts_mean"], 1),
          "mean_run_h": round(float(r.mean()), 2), "run_hist": np.histogram(r, bins=[0, 1, 2, 3, 4, 6, 99])[0].tolist(),
          "runs_total": int(len(r)), "n_years": len(years),
          "gap_days": round(k["longest_genset_free_days"], 1), "wet_h": round(k["wet_stack_h_mean"], 1),
          "l_per_h": round(k["fuel_l_mean"] / k["genset_h_mean"], 2) if k["genset_h_mean"] else None,
          "gen_kwh_dc": round(k["gen_dc_kwh"]), "load_kwh": round(k["load_kwh"]), "curt": round(k["curtailed_kwh"]),
          "mh": [round(float(mm.loc[m, "genset_h"]), 1) for m in range(1, 13)],
          "ml": [round(float(mm.loc[m, "fuel_l"]), 1) for m in range(1, 13)],
          "m_pv_used": [round(float(mm.loc[m, "pv_used_kwh"])) for m in range(1, 13)],
          "m_gen": [round(float(mm.loc[m, "gen_dc_kwh"])) for m in range(1, 13)],
          "m_load": [round(float(mm.loc[m, "load_kwh"])) for m in range(1, 13)],
          "tank": {"year": ymed, "fuel": round(fmed), "days": days, "refills": extra, "end": days[-1]}}
    return so, loc


def week(H, hl, tl, t0):
    t1 = t0 + pd.Timedelta(days=7)
    wk = {}
    for name in ("low", "tender"):
        hh = H[name]
        w = hh[(hh.index >= t0) & (hh.index < t1)]
        wk[name] = {"soc": [round(v * 100, 1) for v in w["soc"]], "gen": [round(v, 2) for v in w["gen_dc"]],
                    "starts": int(w["start"].sum()), "gen_h": round(float(w["gen_frac"].sum()), 1)}
    w = hl[(hl.index >= t0) & (hl.index < t1)]
    tw = tl[(tl.index >= t0) & (tl.index < t1)]
    return {"start": str(w.index[0])[:16], "pv": [round(v, 2) for v in w["pv_used"]],
            "load": [round(v, 3) for v in w["load"]], "low": wk["low"], "tender": wk["tender"],
            "t_mean": round(float(tw.mean()), 1), "t_min": round(float(tw.min()), 1)}


def main():
    with open(os.path.join(LOCAL, "measured.json"), encoding="utf-8") as f:
        meas = json.load(f)
    hod = {int(h): w for h, w in meas["hod_w"].items()}
    shape = {h: meas["level_w"] * hod[h] / meas["mean_w"] for h in range(24)}
    scen = {"tender": None, "low": shape, "high": {h: shape[h] + meas["mpls_w"] for h in range(24)}}
    D.load_kw = load_kw

    pvs = {}
    for sid, _ in SITES:
        s = config.with_tilt(config.load(sid), 45)
        az = s["array"]["azimuth_deg"]
        df, _ = pvgis.hourly(s, 45, az, offline=True)
        pvs[sid] = (s, pv.dc_chain(df, s, 45, az)[0]["p_bus"] / 1000.0, df["temp_air"])

    out = {"sites": {}, "cool": dict(COOL), "cool_sens": {}, "start_sens": {}}
    hourly = {}
    for sid, (s, p, temp) in pvs.items():
        c = cool_w(temp)
        month = temp.index.tz_convert(TZ).month.to_numpy()
        site_out = {"m_cool": [round(float(c[month == m].mean()), 1) for m in range(1, 13)],
                    "cool_mean_w": round(float(c.mean()), 1)}
        for name, base in scen.items():
            CUR["b"] = base
            site_out[name], hourly[sid, name] = scenario(s, p, temp)
            so = site_out[name]
            print(f"{sid:9s} {name:6s} {so['h']:4d} h (P90 {so['h_p90']}) {so['l']:5d} l "
                  f"starts {so['starts']:5.1f} | tank {so['tank']['year']}: "
                  f"+{len(so['tank']['refills'])} refills, end {so['tank']['end']} l")
        out["sites"][sid] = site_out

    # the regime chart's two weeks (Sjednica, the low scenario's median year)
    s, p, temp = pvs["sjednica"]
    y0 = out["sites"]["sjednica"]["low"]["tank"]["year"]
    tl = temp.tz_convert(TZ)
    hl = hourly["sjednica", "low"]
    win = hl[f"{y0}-11-01":f"{y0 + 1}-02-28"]
    best = max(range(0, len(win) - 168, 24), key=lambda i: win["gen_frac"].iloc[i:i + 168].sum())
    roll = tl[f"{y0}-09-01":f"{y0 + 1}-08-31"].resample("D").mean().rolling(7).mean()
    H = {n: hourly["sjednica", n] for n in ("low", "tender")}
    out["sites"]["sjednica"]["weeks"] = {
        "heavy": week(H, hl, tl, win.index[best]),
        "cold": week(H, hl, tl, roll.idxmin() - pd.Timedelta(days=6))}

    for fc in FC_SENS:
        COOL["fc_w"] = fc
        for name in ("low", "tender"):
            CUR["b"] = scen[name]
            out["cool_sens"][f"{int(fc)}_{name}"] = brief(model.dispatch(s, p, temp)[0])
    COOL["fc_w"] = 25.0
    for name in ("low", "tender"):
        CUR["b"] = scen[name]
        for dod in DOD_SENS:
            out["start_sens"][f"{name}_{int(dod * 100)}"] = brief(
                model.dispatch(s, p, temp, {"control.dod_start": dod})[0])

    out["gen"], out["vent"] = {}, {}
    for sid, folder in SITES:
        g = config.load(sid)["genset"]
        out["gen"][sid] = {"fuel_l_h": g["fuel_l_h"], "prime_kw": g["prime_kw"], "rect_cap_ac_kw": g["rect_cap_ac_kw"]}
        with open(os.path.join(ROOT, folder, "cad", "design.json"), encoding="utf-8") as f:
            v = json.load(f).get("ventilation", {})
        out["vent"][sid] = {k: v.get(k) for k in (
            "radiator_m3h", "radiator_m3h_site_derated", "combustion_air_m3h", "heat_to_water_kW",
            "heat_radiated_to_room_kW", "intake_mm", "discharge_mm", "max_external_restriction_Pa",
            "room_fan_m3h", "room_min_m3h", "exhaust_flow_m3h", "exhaust_T_C", "exhaust_DN",
            "exhaust_velocity_ms", "exhaust_back_pressure_kPa", "max_back_pressure_kPa")}

    os.makedirs(OUTDIR, exist_ok=True)
    with open(os.path.join(OUTDIR, "report_data.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)
    with open(os.path.join(LOCAL, "template.html"), encoding="utf-8") as f:
        tpl = f.read()
    blob = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    if tpl.count("/*__DATA__*/null") != 1 or "</script" in blob:
        sys.exit("template placeholder missing, or the data would close the script tag")
    page = os.path.join(OUTDIR, "neteco-report.html")
    with open(page, "w", encoding="utf-8") as f:
        f.write(tpl.replace("/*__DATA__*/null", blob))
    print(f"written {page}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
