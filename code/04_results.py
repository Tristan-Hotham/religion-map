"""results.json (every number quoted anywhere) and the page data (site.json, MSOA properties)."""
from collections import Counter, defaultdict
from common import *

PJ = jload(f"{WORK}/pew.json"); U = jload(f"{WORK}/uk.json"); O = jload(f"{WORK}/osm.json")
ROWS = PJ["rows"]
C = defaultdict(dict)
for v in ROWS.values():
    if v["level"] == 1:
        C[str(v["code"])][v["year"]] = v
W = {y: ROWS[f"900|{y}"] for y in (2010, 2020)}
REGS = ["Asia-Pacific", "Europe", "Latin America-Caribbean", "Middle East-North Africa", "North America", "Sub-Saharan Africa"]
RG = {(v["region"], v["year"]): v for v in ROWS.values() if v["level"] == 2}
largest = lambda v: max(WKEYS, key=lambda k: v["pct"][k])
R = {"meta": {"retrieved": RETRIEVED, "page": PAGE, "repo": REPO, "doi": DOI, "blog": BLOG}}

# ---------------- world ----------------
w = {"n_countries": len(C), "pop2010": W[2010]["pop_r"], "pop2020": W[2020]["pop_r"],
     "pop_growth_pct": r1(100 * (W[2020]["pop_r"] / W[2010]["pop_r"] - 1)), "groups": {}}
for k in WKEYS:
    a, b = W[2010]["cnt"][k], W[2020]["cnt"][k]
    w["groups"][k] = {"pct2010": r1(W[2010]["pct"][k]), "pct2020": r1(W[2020]["pct"][k]), "cnt2010": a, "cnt2020": b,
                      "bn2020": round(b / 1e9, 2), "m2020": round(b / 1e6), "growth_pct": r1(100 * (b / a - 1)), "change_m": round((b - a) / 1e6)}
for y in (2010, 2020):
    cs = [d[y] for d in C.values()]
    w[f"largest{y}"] = dict(Counter(largest(v) for v in cs))
    w[f"majority{y}"] = dict(Counter(largest(v) for v in cs if v["pct"][largest(v)] > 50))
w["changed"] = [{"name": d[2020]["name"], "from": largest(d[2010]), "to": largest(d[2020]), "none": r1(d[2020]["pct"]["none"]),
                 "christian": r1(d[2020]["pct"]["christian"])} for d in C.values() if largest(d[2010]) != largest(d[2020])]
w["regions"] = {}
for k in WKEYS:
    w["regions"][k] = {reg: {str(y): r1(100 * RG[(reg, y)]["cnt"][k] / W[y]["cnt"][k]) for y in (2010, 2020)} for reg in REGS}
w["region_share"] = {reg: {str(y): {k: r1(RG[(reg, y)]["pct"][k]) for k in WKEYS} for y in (2010, 2020)} for reg in REGS}
w["region_pop"] = {reg: RG[(reg, 2020)]["pop_r"] for reg in REGS}
w["top_change"] = {}
for k in WKEYS:
    s = sorted(C.values(), key=lambda d: d[2020]["pct"][k] - d[2010]["pct"][k])
    f = lambda d: {"name": d[2020]["name"], "pp": r1(d[2020]["pct"][k] - d[2010]["pct"][k]), "pct2010": r1(d[2010]["pct"][k]), "pct2020": r1(d[2020]["pct"][k])}
    w["top_change"][k] = {"fall": [f(d) for d in s[:6]], "rise": [f(d) for d in s[::-1][:6]]}
w["top_share"] = {k: [{"name": d[2020]["name"], "pct": r1(d[2020]["pct"][k])} for d in sorted(C.values(), key=lambda d: -d[2020]["pct"][k])[:8]] for k in WKEYS}
w["top_count"] = {k: [{"name": d[2020]["name"], "m": round(d[2020]["raw"][k] / 1e6, 1)} for d in sorted(C.values(), key=lambda d: -(d[2020]["raw"][k] or 0))[:6]] for k in WKEYS}
rdi = sorted([d[2020] for d in C.values() if d[2020]["rdi_rank"]], key=lambda v: v["rdi_rank"])
w["rdi_top"] = [{"name": v["name"], "rdi": round(v["rdi"], 1), "rank": v["rdi_rank"], "level": v["rdi_level"]} for v in rdi[:10]]
w["rdi_bottom_n"] = sum(1 for v in rdi if v["rdi"] is not None and v["rdi"] < 1)
w["rdi_levels"] = dict(Counter(d[2020]["rdi_level"] for d in C.values()))
w["rdi_world"] = round(W[2020]["rdi"], 1)
w["rdi_regions"] = {reg: round(RG[(reg, 2020)]["rdi"], 1) for reg in REGS}
uk = C["826"]
w["uk"] = {f"{k}{y}": r1(uk[y]["pct"][k]) for k in ("christian", "none", "muslim") for y in (2010, 2020)}
w["christ_down_n"] = sum(1 for d in C.values() if d[2020]["pct"]["christian"] < d[2010]["pct"]["christian"] - .05)
w["none_up_n"] = sum(1 for d in C.values() if d[2020]["pct"]["none"] > d[2010]["pct"]["none"] + .05)
chn = C["156"][2020]
w["china_none_pct"] = r1(chn["pct"]["none"]); w["china_none_m"] = round(chn["raw"]["none"] / 1e6)
w["china_share_of_none"] = r1(100 * chn["raw"]["none"] / W[2020]["raw"]["none"])
w["ssa_christ_m2020"] = round(RG[("Sub-Saharan Africa", 2020)]["cnt"]["christian"] / 1e6)
w["eur_christ_m2020"] = round(RG[("Europe", 2020)]["cnt"]["christian"] / 1e6)
w["ssa_christ_m2010"] = round(RG[("Sub-Saharan Africa", 2010)]["cnt"]["christian"] / 1e6)
w["eur_christ_m2010"] = round(RG[("Europe", 2010)]["cnt"]["christian"] / 1e6)
R["world"] = w

# ---------------- UK ----------------
sh = lambda o: {k: (None if o.get(k) is None else r1(100 * o[k] / o["total"])) for k in UKEYS}
ew, eng, wal = U["ew21_reg"]["K04000001"], U["ew21_reg"]["E92000001"], U["ew21_reg"]["W92000004"]
ew11, eng11, wal11 = U["ew11_ctry"]["K04000001"], U["ew11_ctry"]["E92000001"], U["ew11_ctry"]["W92000004"]
sc, ni, nb = U["scot"], U["ni"]["N92000002"], U["ni_b"]["N92000002"]
u = {"ew2021": sh(ew), "ew2011": sh(ew11), "eng2021": sh(eng), "eng2011": sh(eng11), "wal2021": sh(wal), "wal2011": sh(wal11),
     "scot": sh(sc), "ni": sh(ni), "ew_total2021": ew["total"], "ew_christian_m": round(ew["christian"] / 1e6, 1), "ew_none_m": round(ew["none"] / 1e6, 1),
     "ew_muslim_m": round(ew["muslim"] / 1e6, 1), "ew11_christian_m": round(ew11["christian"] / 1e6, 1), "ew11_none_m": round(ew11["none"] / 1e6, 1)}
u["ew_change"] = {k: r1(u["ew2021"][k] - u["ew2011"][k]) for k in UKEYS}
u["scot_detail"] = {k: r1(100 * sc[k] / sc["total"]) for k in ("cos", "rc", "ochr", "pagan")}
u["ni_detail"] = {k: r1(100 * ni[k] / ni["total"]) for k in ("cath", "pres", "coi", "meth", "ochr")}
u["ni_prot_all"] = r1(100 * (ni["pres"] + ni["coi"] + ni["meth"] + ni["ochr"]) / ni["total"])
u["ni_brought_up"] = {k: r1(100 * nb[k] / nb["total"]) for k in ("cath", "prot", "other", "none")}
tot = ew["total"] + sc["total"] + ni["total"]
u["uk3"] = {"total": tot, "christian": r1(100 * (ew["christian"] + sc["christian"] + ni["christian"]) / tot),
            "none": r1(100 * (ew["none"] + sc["none"] + ni["none"]) / tot), "christian_m": round((ew["christian"] + sc["christian"] + ni["christian"]) / 1e6, 1),
            "none_m": round((ew["none"] + sc["none"] + ni["none"]) / 1e6, 1)}
LA = U["LA"]
lg = lambda o: max([k for k in UKEYS if o.get(k) is not None and k != "notstated"], key=lambda k: o[k])
la = {"n": len(LA), "largest": dict(Counter(lg(o) for o in LA.values())),
      "none_largest_by_nation": dict(Counter(o["nation"] for o in LA.values() if lg(o) == "none")),
      "n_by_nation": dict(Counter(o["nation"] for o in LA.values())),
      "muslim_largest": sorted(o["name"] for o in LA.values() if lg(o) == "muslim"),
      "ew_n": sum(1 for o in LA.values() if "y2011" in o),
      "ew_none_largest_2011": sum(1 for o in LA.values() if "y2011" in o and lg(o["y2011"]) == "none"),
      "ew_none_largest_2021": sum(1 for o in LA.values() if "y2011" in o and lg(o) == "none"),
      "ew_christian_fell": sum(1 for o in LA.values() if "y2011" in o and o["christian"] / o["total"] < o["y2011"]["christian"] / o["y2011"]["total"]),
      "ew_none_rose": sum(1 for o in LA.values() if "y2011" in o and o["none"] / o["total"] > o["y2011"]["none"] / o["y2011"]["total"]),
      "top": {}}
for k in UKEYS:
    s = sorted([o for o in LA.values() if o.get(k) is not None], key=lambda o: -o[k] / o["total"])
    la["top"][k] = [{"name": o["name"], "nation": o["nation"], "pct": r1(100 * o[k] / o["total"])} for o in s[:5]]
ewl = [o for o in LA.values() if "y2011" in o]
dd = lambda o, k: 100 * o[k] / o["total"] - 100 * o["y2011"][k] / o["y2011"]["total"]
la["change"] = {k: {"fall": [{"name": o["name"], "pp": r1(dd(o, k))} for o in sorted(ewl, key=lambda o: dd(o, k))[:5]],
                    "rise": [{"name": o["name"], "pp": r1(dd(o, k))} for o in sorted(ewl, key=lambda o: -dd(o, k))[:5]]} for k in UKEYS}
u["la"] = la
MS = U["MS"]
ms = {"n": len(MS), "none_largest": sum(1 for o in MS.values() if lg(o) == "none"), "christian_majority": sum(1 for o in MS.values() if o["christian"] / o["total"] > .5),
      "none_majority": sum(1 for o in MS.values() if o["none"] / o["total"] > .5), "largest": dict(Counter(lg(o) for o in MS.values())), "top": {}}
LAN = {c: o["name"] for c, o in LA.items()}
for k in UKEYS:
    s = sorted(MS.values(), key=lambda o: -o[k] / o["total"])
    ms["top"][k] = [{"name": o["name"], "la": LAN[o["la"]], "pct": r1(100 * o[k] / o["total"])} for o in s[:5]]
u["msoa"] = ms
iz = U["sc_iz"]
u["scot_iz"] = {"n": len(iz), "none_majority": sum(1 for o in iz if o["none"] / o["total"] > .5)}
ag = U["age"]["England and Wales"]
BANDS = ["Under 16", "16-24", "25-34", "35-49", "50-64", "65-74", "75+"]
u["age"] = {g: [{"band": b, **{k: r1(100 * U["age"][g][b][k] / U["age"][g][b]["total"]) for k in UKEYS}} for b in BANDS] for g in ("England and Wales", "England", "Wales")}
u["age_bands"] = BANDS
det = U["det"]
u["det"] = {k.split(": ", 1)[1]: v for k, v in det.items() if ": " in k}
u["det_top_other"] = [{"name": k.split(": ", 1)[1], "n": v} for k, v in sorted(det.items(), key=lambda kv: -kv[1]) if k.startswith("Other religion:") and "Other religions" not in k][:12]
H = U["ni_hist"]
hist = [{"year": h["year"], "cath": r1(100 * h["cath"] / h["total"]), "prot3": r1(100 * (h["pres"] + h["coi"] + h["meth"]) / h["total"]),
         "pres": r1(100 * h["pres"] / h["total"]), "coi": r1(100 * h["coi"] / h["total"]), "meth": r1(100 * h["meth"] / h["total"]),
         "other": r1(100 * h["other"] / h["total"]), "none_ns": r1(100 * h["none_ns"] / h["total"]), "total": h["total"]} for h in H]
u["ni_hist"] = hist
mn = min(hist, key=lambda h: h["cath"]); pk = max(hist, key=lambda h: h["prot3"])
cross = next(h["year"] for h in hist if h["cath"] > h["prot3"])
u["ni_h"] = {"cath1861": hist[0]["cath"], "prot1861": hist[0]["prot3"], "cath_min": mn["cath"], "cath_min_year": mn["year"],
             "prot_peak": pk["prot3"], "prot_peak_year": pk["year"], "cath2021": hist[-1]["cath"], "prot2021": hist[-1]["prot3"],
             "cross_year": cross, "nons1961": next(h["none_ns"] for h in hist if h["year"] == 1961), "nons2021": hist[-1]["none_ns"],
             "n_censuses": len(hist)}
R["uk"] = u

# ---------------- OpenStreetMap ----------------
DEN = dict(jload(f"{DATA}/osm_cells.json")["den"])
o = {"total": O["total"], "n_cells": O["n_cells"], "by_rel": O["by_rel"], "by_den": O["by_den"], "christian_den_tagged": sum(v for k, v in O["by_den"].items() if k != "untagged")}
o["christian_den_tagged_pct"] = r1(100 * o["christian_den_tagged"] / O["by_rel"]["christian"])
o["untagged_rel_pct"] = r1(100 * O["by_rel"]["untagged"] / O["total"])
o["region_den"] = {}
o["region"] = {}
for reg in REGS:
    v = O["by_region"][reg]; t = sum(n for k, n in v["d"].items() if k != "untagged")
    o["region_den"][reg] = [{"k": k, "name": DEN[k], "n": n, "pct": r1(100 * n / t)} for k, n in sorted(v["d"].items(), key=lambda kv: -kv[1]) if k != "untagged"][:6]
    allp = sum(v["r"].values())
    o["region"][reg] = {"n": allp, "per100k": r1(1e5 * allp / RG[(reg, 2020)]["pop_r"]), "christian": v["r"].get("christian", 0), "muslim": v["r"].get("muslim", 0),
                        "christian_per100k": r1(1e5 * v["r"].get("christian", 0) / RG[(reg, 2020)]["cnt"]["christian"]),
                        "muslim_per100k": r1(1e5 * v["r"].get("muslim", 0) / RG[(reg, 2020)]["cnt"]["muslim"])}
NEN = {f["properties"]["iso"]: f["properties"]["name"] for f in jload(f"{DATA}/world.json")["features"]}
bc = sorted([(iso, sum(v["r"].values())) for iso, v in O["by_country"].items() if iso], key=lambda x: -x[1])
o["top_countries"] = [{"iso": i, "name": NEN.get(i, i), "n": n} for i, n in bc[:10]]
for rel in ("muslim", "buddhist", "hindu", "shinto", "jewish", "sikh"):
    s = sorted([(iso, v["r"].get(rel, 0)) for iso, v in O["by_country"].items() if iso], key=lambda x: -x[1])
    o[f"top_{rel}"] = [{"iso": i, "name": NEN.get(i, i), "n": n, "pct": r1(100 * n / O["by_rel"][rel])} for i, n in s[:5]]
gb = O["by_country"]["GBR"]
o["gbr"] = {"n": sum(gb["r"].values()), "christian": gb["r"].get("christian", 0), "muslim": gb["r"].get("muslim", 0),
            "den": [{"k": k, "name": DEN[k], "n": n} for k, n in sorted(gb["d"].items(), key=lambda kv: -kv[1]) if k != "untagged"][:6]}
R["osm"] = o
jsave(R, f"{DATA}/results.json", indent=1)

# ---------------- page data ----------------
iso2pew = {}
for c, isos in PJ["iso"].items():
    for i in isos:
        iso2pew[i] = c
site = {"wk": WKEYS, "uk": UKEYS, "wname": WNAME, "uname": UNAME, "col": REL_COL, "iso2pew": iso2pew, "cpos": PJ["cpos"], "c": {}, "la": {},
        "regs": REGS, "osmc": {}}
for c, d in C.items():
    a, b = d[2010], d[2020]
    site["c"][c] = {"n": b["name"], "r": b["region"], "p": [round(a["pop"]), round(b["pop"])],
                    "a": [round(a["pct"][k], 2) for k in WKEYS], "b": [round(b["pct"][k], 2) for k in WKEYS],
                    "k": [b["cnt"][k] for k in WKEYS], "d": [None if b["rdi"] is None else round(b["rdi"], 2), b["rdi_level"], b["rdi_rank"]]}
for code, v in LA.items():
    e = {"n": v["name"], "t": v["nation"][0], "y": v["year"], "T": v["total"], "v": [v[k] for k in UKEYS]}
    if "y2011" in v:
        e["o"] = [v["y2011"]["total"]] + [v["y2011"][k] for k in UKEYS]
    if "detail" in v:
        e["x"] = v["detail"]
    if "brought_up" in v:
        e["bu"] = v["brought_up"]
    site["la"][code] = e
RD = list(DEN)
for iso, v in O["by_country"].items():
    if iso:
        site["osmc"][iso] = {"r": v["r"], "d": {k: n for k, n in v["d"].items()}}
site["den"] = jload(f"{DATA}/osm_cells.json")["den"]
site["osmReg"] = {reg: O["by_region"][reg]["d"] for reg in REGS}
jsave(site, f"{DATA}/site.json")
# MSOA properties merged into the page geometry
g = jload(f"{DATA}/uk_msoa.json")
for f in g["features"]:
    m = MS[f["properties"]["c"]]
    f["properties"] = {"c": f["properties"]["c"], "n": m["name"], "l": m["la"], "T": m["total"], "v": [m[k] for k in UKEYS]}
jsave(g, f"{DATA}/uk_msoa.json")
print("results.json", os.path.getsize(f"{DATA}/results.json") // 1024, "KB; site.json", os.path.getsize(f"{DATA}/site.json") // 1024, "KB; uk_msoa.json", os.path.getsize(f"{DATA}/uk_msoa.json") // 1024, "KB")
print(R["world"]["regions"]["christian"]); print(R["osm"]["region"]); print(R["uk"]["la"]["largest"], R["uk"]["la"]["muslim_largest"], R["uk"]["ni_h"], R["uk"]["uk3"])
