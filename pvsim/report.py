"""python -m pvsim report --site <id>

Every tilt, the sensitivity cases, the figures and kpis.json, written into the
site's review/pvsim/. These are the files the TD's 07-proracuni and Prilog I /
III take their energy figures from - nothing is typed in by hand.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess

from pvsim import __version__, config, figures, model, pvgis, validate

HERE = os.path.dirname(os.path.abspath(__file__))

# SMU settings and assumptions the result depends on. The first row is the
# base case: the settings Prilog I §4.6 requires since Rev 9 (stop SoC 60 %,
# charge at the BMS maximum, taken as 0,5 C). The second row is what an SMU
# left at its usual settings would do.
SENSITIVITY = [
    ("Osnovni slučaj (TD Rev 9): start DOD 85 %, stop SoC 60 %, punjenje 0,5 C", {}),
    ("SMU bez parametriranja: stop SoC 90 %, punjenje 0,25 C",
     {"control.soc_stop": 0.9, "battery.charge_c_rate": 0.25}),
    ("Stop SoC 90 %", {"control.soc_stop": 0.9}),
    ("Stop SoC 100 % (punjenje do vrha)", {"control.soc_stop": 1.0}),
    ("Stop SoC 40 %", {"control.soc_stop": 0.4}),
    ("Punjenje 0,25 C", {"battery.charge_c_rate": 0.25}),
    ("Punjenje 0,15 C", {"battery.charge_c_rate": 0.15}),
    ("Start pri DOD 70 %", {"control.dod_start": 0.7}),
    ("Baterija 28,8 kWh (6 × 100 Ah, stara ponuda Huawei)",
     {"battery.kwh_per_module": 4.8}),
    ("Potrošnja 1180 W stalno (bez hlađenja i pomoćne)",
     {"load.aux_w": 0, "load.cooling_w_max": 0}),
    ("Potrošnja 1330 W stalno", {"load.base_w": 1330, "load.aux_w": 0,
                                 "load.cooling_w_max": 0}),
]
MONTHS = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt",
          "nov", "dec"]


def _git(*args):
    return subprocess.run(["git", *args], cwd=config.ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def _git_commit():
    """HEAD, marked "-dirty" when pvsim's code or site files differ from it:
    then the hash alone does not reproduce the numbers in kpis.json."""
    try:
        head = _git("rev-parse", "--short", "HEAD")
        dirty = _git("status", "--porcelain", "--", "pvsim")
    except (OSError, subprocess.CalledProcessError):
        return None
    return head + "-dirty" if dirty else head


def _n(v, nd=0):
    return figures.num(v, nd) if v is not None else "—"


def _sens_row(label, k):
    return {"case": label, "genset_h_mean": k["genset_h_mean"],
            "genset_h_p90": k["genset_h_p90"], "genset_h_max": k["genset_h_max"],
            "fuel_l_mean": k["fuel_l_mean"], "fuel_l_p90": k["fuel_l_p90"],
            "fuel_l_max": k["fuel_l_max"], "refills_mean": k["refills_mean"],
            "tank_years_mean": k["tank_years_mean"], "starts_mean": k["starts_mean"],
            "gen_dc_kwh": k["gen_dc_kwh"], "curtailed_kwh": k["curtailed_kwh"],
            "wet_stack_h_mean": k["wet_stack_h_mean"]}


def run(site, offline=False):
    out_dir = os.path.join(config.ROOT, site["review_dir"])
    fig_dir = os.path.join(out_dir, "fig")
    os.makedirs(fig_dir, exist_ok=True)
    name = f"{site['name']} ({site['place']})"
    tank_l = site["design"]["tank"]["litres"]
    lim = site["limits"]

    tilts, sens, valid, files = {}, {}, {}, []
    for tilt in site["array"]["tilts"]:
        t = f"{tilt:g}"
        pv_kw, temp, chain, fit, n_years = model.pv_series(site, tilt, offline)
        s = config.with_tilt(site, tilt)
        rows = []
        for label, over in SENSITIVITY:
            k, years, monthly, h = model.dispatch(s, pv_kw, temp, over)
            rows.append(_sens_row(label, k))
            if not over:
                base = (k, years, monthly, h)
        k, years, monthly, h = base
        k.update({"site": site["id"], "tilt": tilt, "issu_fit": fit,
                  "specific_yield_bus": k["pv_bus_kwh"] / site["array"]["kWp"]})
        wf = model.pv.loss_waterfall(chain, n_years)
        mm = monthly.groupby(level="month").mean()
        tilts[t] = {"kpis": k, "waterfall": wf,
                    "monthly_mean": {c: [float(mm.loc[m, c]) for m in range(1, 13)]
                                     for c in mm.columns},
                    "years": years.reset_index(names="year").to_dict(orient="records")}
        sens[t] = rows
        valid[t] = validate.metrics(site, tilt, offline)
        years.to_csv(os.path.join(out_dir, f"years_t{t}.csv"))
        monthly.to_csv(os.path.join(out_dir, f"monthly_t{t}.csv"))

        files += [
            figures.f1_monthly(monthly, f"{name}, nagib {t}° — mjesečni energetski bilans",
                               os.path.join(fig_dir, f"f1_bilans_t{t}.png")),
            figures.f3_heatmap(h, f"{name}, nagib {t}° — rad agregata po danima",
                               os.path.join(fig_dir, f"f3_dea_dani_t{t}.png")),
            figures.f4_years(years, lim, tank_l,
                             f"{name}, nagib {t}° — agregat po godinama",
                             os.path.join(fig_dir, f"f4_dea_godine_t{t}.png")),
            figures.f5_waterfall(wf, f"{name}, nagib {t}° — gubici FN lanca",
                                 os.path.join(fig_dir, f"f5_gubici_t{t}.png")),
        ]

    uh, markers = None, ()
    if site.get("obstacles"):
        from pvsim import photo
        uh, markers = photo.horizon_for_figure(site, site["array"]["tilt_deg"])
    files.append(figures.f2_horizon(site, pvgis.horizon(site, offline),
                                    os.path.join(fig_dir, "f2_horizont.png"),
                                    user_horizon=uh, markers=markers))
    files.append(figures.f6_tilts({float(t): v["kpis"] for t, v in tilts.items()},
                                  name, lim, os.path.join(fig_dir, "f6_nagibi.png")))

    manifest = json.load(open(os.path.join(HERE, "sites", site["id"], "pvgis_ref",
                                           "manifest.json"), encoding="utf-8"))
    doc = {
        "site": site["id"], "name": site["name"], "place": site["place"],
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "pvsim_version": __version__, "git_commit": _git_commit(),
        "inputs": {k: site[k] for k in ("lat", "lon", "altitude_m", "pvgis", "array",
                                        "pv", "load", "battery", "control", "genset",
                                        "tank", "limits")},
        "design": site["design"], "pvgis_manifest": manifest,
        "validation": valid, "tilts": tilts, "sensitivity": sens,
    }
    with open(os.path.join(out_dir, "kpis.json"), "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, ensure_ascii=False, default=str)
    md = os.path.join(out_dir, "energetski-bilans.md")
    with open(md, "w", encoding="utf-8") as fh:
        fh.write(markdown(doc))
    print(f"{site['id']}: kpis.json, energetski-bilans.md, {len(files)} slika -> {out_dir}")
    return 0


# --------------------------------------------------------------------------
_POINTS = ("sjever", "sjeveroistok", "istok", "jugoistok", "jug", "jugozapad", "zapad",
           "sjeverozapad")


def _azimuth(az):
    """225 -> 'azimut 225° (jugozapad)'."""
    return f"azimut {az:g}° ({_POINTS[round(az / 45) % 8]})"


def markdown(doc):
    s = doc["inputs"]
    tilts = list(doc["tilts"])
    K = {t: doc["tilts"][t]["kpis"] for t in tilts}
    lim = s["limits"]
    L = []
    w = L.append
    w(f"# Energetski bilans — {doc['name']} ({doc['place']})\n")
    w(f"*Simulacija pvlib + PVGIS-SARAH3, satno {K[tilts[0]]['years'][0]}–"
      f"{K[tilts[0]]['years'][1]}. Generisano {doc['generated_utc'][:10]}, pvsim "
      f"{doc['pvsim_version']}, commit {doc['git_commit']}. Ulazi i pretpostavke: "
      f"`pvsim/sites/{doc['site']}.json`; brojevi: `kpis.json` u ovom folderu. "
      f"Ne uređivati ručno — `python -m pvsim report --site {doc['site']}`.*\n")

    w("## Metoda\n")
    w(f"- **Ozračenje:** PVGIS v5.3 `seriescalc`, SARAH3 + ERA5 (temperatura, vjetar), "
      f"satno za {K[tilts[0]]['n_years']} godina; horizont iz PVGIS DEM-a; polje "
      f"{_azimuth(s['array']['azimuth_deg'])}, nagib {' i '.join(t + '°' for t in tilts)}.")
    w("- **FN lanac:** refleksija Martin-Ruiz (a_r 0,16), temperatura modula Faiman "
      "(26,9 / 6,2), model modula Huld c-Si (PVGIS), mjesečno zaprljanje i snijeg, "
      "neusklađenost i LID, DC kablovi 0,78 % pri Imp, optimizatori 99,0 %, iSSU "
      "S4875G2 po krivulji proizvođača (Vin 330 V), ograničenje 4 kW po modulu.")
    b, c, g = s["battery"], s["control"], s["genset"]
    cap = b["modules"] * b["kwh_per_module"]
    w(f"- **Bilans na −48 V DC sabirnici:** satno, sve godine neprekidno. Baterija "
      f"{b.get('label', str(b['modules']) + ' modula')} = {_n(cap, 1)} kWh, "
      f"η punjenja/pražnjenja "
      f"{_n(100 * b['eta_charge'], 1)} %, punjenje do {_n(b['charge_c_rate'], 2)} C. "
      f"DEA preko ispravljača ograničenih na {_n(g['rect_cap_ac_kw'], 1)} kW AC "
      f"(η {_n(100 * g['eta_rect'])} %): start pri DOD {_n(100 * c['dod_start'])} %, "
      f"stop pri SoC {_n(100 * c['soc_stop'])} %, najkraći rad {_n(c['min_run_h'], 1)} h. "
      f"Gorivo po tehničkom listu P18-6 (prime).")
    ld = s["load"]
    w(f"- **Potrošnja:** {ld['base_w']} W TK + {ld.get('aux_w', 0)} W pomoćna "
      f"(SMU, BMS, ventilatori) + hlađenje ormara do {ld['cooling_w_max']} W "
      f"(linearno {ld['cooling_t0_c']}→{ld['cooling_t1_c']} °C).")
    w("- Parametri bez podatka proizvođača (efikasnost i punjenje baterije, stop SoC, "
      "zaprljanje, snijeg, hlađenje) su pretpostavke, označene u ulaznom fajlu; "
      "njihov uticaj je u tabeli osjetljivosti.\n")

    w("## Validacija prema PVGIS-u\n")
    w("| Nagib | PVcalc, kWh/god | pvsim s PVGIS gubicima 14 %, kWh/god | "
      "najveće mjesečno odstupanje | satna korelacija s PVGIS P |")
    w("|---|---|---|---|---|")
    for t in tilts:
        v = doc["validation"][t]
        w(f"| {t}° | {_n(v['pvcalc_E_y'])} | {_n(v['pvsim_E_y'])} | "
          f"{_n(100 * v['worst_month_dev'], 1)} % | {_n(v['hourly_r'], 4)} |")
    w("")

    w("## Gubici FN lanca (prosjek godine)\n")
    w("| Stavka | " + " | ".join(f"{t}°, kWh" for t in tilts) + " | " +
      " | ".join(f"{t}°, gubitak" for t in tilts) + " |")
    w("|---|" + "---|" * (2 * len(tilts)))
    wfs = {t: doc["tilts"][t]["waterfall"] for t in tilts}
    for i, r in enumerate(wfs[tilts[0]]):
        cells = [_n(wfs[t][i]["kwh"]) for t in tilts]
        loss = ["" if wfs[t][i]["loss_pct"] is None else
                f"−{_n(wfs[t][i]['loss_pct'], 2)} %" for t in tilts]
        w(f"| {r['label']} | " + " | ".join(cells) + " | " + " | ".join(loss) + " |")
    w("")

    for t in tilts:
        mm = doc["tilts"][t]["monthly_mean"]
        w(f"## Mjesečni bilans, nagib {t}° (prosjek godina)\n")
        w("| Mjesec | FN na sabirnici, kWh | Potrošnja, kWh | DEA (DC), kWh | "
          "DEA, h | Gorivo, l |")
        w("|---|---|---|---|---|---|")
        for m in range(12):
            w(f"| {MONTHS[m]} | {_n(mm['pv_kwh'][m])} | {_n(mm['load_kwh'][m])} | "
              f"{_n(mm['gen_dc_kwh'][m])} | {_n(mm['genset_h'][m], 1)} | "
              f"{_n(mm['fuel_l'][m])} |")
        w("")

    w("## Ključni pokazatelji\n")
    w("| Pokazatelj | " + " | ".join(f"{t}°" for t in tilts) +
      " | RFI / Odluka do Rev 9 |")
    w("|---|" + "---|" * len(tilts) + "---|")
    rows = [
        ("FN na DC sabirnici, kWh/god", lambda k: _n(k["pv_bus_kwh"]), ""),
        ("Specifični prinos na sabirnici, kWh/kWp", lambda k: _n(k["specific_yield_bus"]), ""),
        ("FN iskorišteno / odbačeno (baterija puna), kWh/god",
         lambda k: f"{_n(k['pv_used_kwh'])} / {_n(k['curtailed_kwh'])}", ""),
        ("Potrošnja, kWh/god", lambda k: _n(k["load_kwh"]), ""),
        ("Solarni udio u potrošnji", lambda k: f"{_n(100 * k['solar_fraction'], 1)} %", ""),
        ("Decembar: FN / potrošnja, kWh",
         lambda k: f"{_n(k['dec_pv_kwh'])} / {_n(k['dec_load_kwh'])}", ""),
        ("DEA rad, h/god — prosjek / P90 / najgora god.",
         lambda k: f"{_n(k['genset_h_mean'])} / {_n(k['genset_h_p90'])} / "
                   f"{_n(k['genset_h_max'])}", f"≤{lim['genset_h_max']} h/god"),
        ("DEA startova, /god — prosjek / najviše",
         lambda k: f"{_n(k['starts_mean'])} / {k['starts_max']}", ""),
        ("Gorivo, l/god — prosjek / P90 / najgora god.",
         lambda k: f"{_n(k['fuel_l_mean'])} / {_n(k['fuel_l_p90'])} / "
                   f"{_n(k['fuel_l_max'])}", ""),
        (f"Spremnik {doc['design']['tank']['litres']} l traje, god — prosjek / najgora",
         lambda k: f"{_n(k['tank_years_mean'], 2)} / {_n(k['tank_years_worst'], 2)}",
         f"≥{_n(lim['tank_years_min'], 0)} god"),
        ("Dopuna goriva, /god — prosjek / najviše",
         lambda k: f"{_n(k['refills_mean'], 1)} / {k['refills_max']}", ""),
        ("Najduže razdoblje bez rada DEA, dana",
         lambda k: _n(k["longest_genset_free_days"]), ""),
        ("Ekvivalentnih ciklusa baterije, /god", lambda k: _n(k["cycles_mean"]), ""),
        ("Rad DEA ispod 30 % opterećenja, h/god", lambda k: _n(k["wet_stack_h_mean"], 1), ""),
        ("Nepokrivena potrošnja, kWh", lambda k: _n(k["unmet_kwh_total"], 1), "0"),
    ]
    for label, f, limit in rows:
        w(f"| {label} | " + " | ".join(f(K[t]) for t in tilts) + f" | {limit} |")
    ok = lambda b: "ispunjeno" if b else "**NIJE ispunjeno**"   # noqa: E731
    w(f"| ≤{lim['genset_h_max']} h/god (P90 / najgora god.) | " + " | ".join(
        f"{ok(K[t]['pass_genset_h'])} / {ok(K[t]['pass_genset_h_worst'])}"
        for t in tilts) + " | |")
    w(f"| ≥{_n(lim['tank_years_min'], 0)} god na spremnik (prosjek / najgora god.) | "
      + " | ".join(f"{ok(K[t]['pass_tank_year'])} / {ok(K[t]['pass_tank_year_worst'])}"
                   for t in tilts) + " | |")
    w("")

    for t in tilts:
        w(f"## Osjetljivost, nagib {t}°\n")
        w("| Slučaj | DEA h/god prosjek | P90 | najgora | Gorivo l/god prosjek | "
          "najgora | Spremnik traje, god | Startova/god |")
        w("|---|---|---|---|---|---|---|---|")
        for r in doc["sensitivity"][t]:
            w(f"| {r['case']} | {_n(r['genset_h_mean'])} | {_n(r['genset_h_p90'])} | "
              f"{_n(r['genset_h_max'])} | {_n(r['fuel_l_mean'])} | {_n(r['fuel_l_max'])} | "
              f"{_n(r['tank_years_mean'], 2)} | {_n(r['starts_mean'])} |")
        w("")

    w("## Zaključak (izveden iz brojeva iznad)\n")
    for t in tilts:
        rows = doc["sensitivity"][t]
        best_h = min(rows, key=lambda r: r["genset_h_p90"])
        best_f = min(rows, key=lambda r: r["fuel_l_mean"])
        w(f"- **{t}°:** DEA {_n(K[t]['genset_h_mean'])} h/god u prosjeku "
          f"(P90 {_n(K[t]['genset_h_p90'])}), gorivo {_n(K[t]['fuel_l_mean'])} l/god. "
          f"Najpovoljniji slučaj osjetljivosti za sate ({best_h['case']}) daje P90 "
          f"{_n(best_h['genset_h_p90'])} h/god; za gorivo ({best_f['case']}) "
          f"{_n(best_f['fuel_l_mean'])} l/god, tj. spremnik "
          f"{doc['design']['tank']['litres']} l traje {_n(best_f['tank_years_mean'], 2)} god.")
    w("")
    return "\n".join(L) + "\n"
