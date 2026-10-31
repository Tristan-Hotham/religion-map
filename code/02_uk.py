"""UK censuses: harmonise religion in England and Wales (2021, 2011), Scotland (2022) and Northern Ireland (2021).

Harmonised groups (UKEYS): christian, none, muslim, hindu, sikh, jewish, buddhist, other, notstated.
- England and Wales 2021 (TS030): the ten published categories map one to one ('Not answered' = notstated).
- England and Wales 2011 (KS209EW): the same categories ('Religion not stated' = notstated). KS209EW on Nomis is
  crossed by a rural/urban dimension; the first block for each area is the total and is the one used.
  2011 districts are added up to the April 2023 local authorities (mergers listed in MERGE below).
- Scotland 2022 (UV205): christian = Church of Scotland + Roman Catholic + Other Christian; other = Pagan + Other religion.
- Northern Ireland 2021 (MS-B19): christian = Catholic + Presbyterian + Church of Ireland + Methodist + Other Christian;
  'Other religions' cannot be split by faith in this table, so muslim, hindu, sikh, jewish and buddhist are missing
  and all non-Christian religions are in other.
Shares are of all usual residents (all people), including those who did not answer.
"""
import csv
from collections import defaultdict
import openpyxl
from shapely.geometry import shape, mapping
from common import *

T10 = {"No religion": "none", "Christian": "christian", "Buddhist": "buddhist", "Hindu": "hindu", "Jewish": "jewish",
       "Muslim": "muslim", "Sikh": "sikh", "Other religion": "other", "Not answered": "notstated", "Religion not stated": "notstated"}


def nomis(fn, catcol):
    out = defaultdict(lambda: {"name": None, "total": None, **{k: 0 for k in UKEYS}})
    seen = set()
    with open(f"{REL}/{fn}", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            code, cat, v = r["GEOGRAPHY_CODE"], r[catcol].strip(), int(r["OBS_VALUE"])
            if (code, cat) in seen:          # KS209EW: later rural/urban blocks repeat the categories; keep the first (total)
                continue
            seen.add((code, cat))
            o = out[code]; o["name"] = r["GEOGRAPHY_NAME"]
            if cat.startswith("Total") or cat.startswith("All categories"):
                o["total"] = v
            elif cat in T10:
                o[T10[cat]] += v
    for c, o in out.items():
        assert abs(sum(o[k] for k in UKEYS) - o["total"]) <= 0, (fn, c, o)
    return dict(out)


ew21_la = nomis("ts030_ltla23.csv", "C2021_RELIGION_10_NAME")
ew21_msoa = nomis("ts030_msoa.csv", "C2021_RELIGION_10_NAME")
ew21_reg = nomis("ts030_region_country.csv", "C2021_RELIGION_10_NAME")
ew11_lad = nomis("ks209_lad2011.csv", "CELL_NAME")
ew11_ctry = nomis("ks209_country.csv", "CELL_NAME")
assert len(ew21_la) == 318 and len(ew21_msoa) == 7264 and len(ew11_lad) == 348, (len(ew21_la), len(ew21_msoa), len(ew11_lad))

# 2011 districts -> April 2023 local authorities (all changes 2011 to 2023 were mergers)
MERGE = {"E06000058": ["E06000028", "E06000029", "E07000048"],                       # Bournemouth, Christchurch and Poole
         "E06000059": ["E07000049", "E07000050", "E07000051", "E07000052", "E07000053"],  # Dorset
         "E06000060": ["E07000004", "E07000005", "E07000006", "E07000007"],          # Buckinghamshire
         "E06000061": ["E07000150", "E07000152", "E07000153", "E07000156"],          # North Northamptonshire
         "E06000062": ["E07000151", "E07000154", "E07000155"],                       # West Northamptonshire
         "E06000063": ["E07000026", "E07000028", "E07000029"],                       # Cumberland
         "E06000064": ["E07000027", "E07000030", "E07000031"],                       # Westmorland and Furness
         "E06000065": ["E07000163", "E07000164", "E07000165", "E07000166", "E07000167", "E07000168", "E07000169"],  # North Yorkshire
         "E06000066": ["E07000187", "E07000188", "E07000189", "E07000190", "E07000191"],  # Somerset
         "E07000244": ["E07000205", "E07000206"],                                    # East Suffolk
         "E07000245": ["E07000201", "E07000204"]}                                    # West Suffolk
old2new = {o: n for n, os_ in MERGE.items() for o in os_}
ew11_la = defaultdict(lambda: {"total": 0, **{k: 0 for k in UKEYS}})
for c, o in ew11_lad.items():
    n = old2new.get(c, c)
    assert n in ew21_la, (c, o["name"])
    for k in ["total"] + UKEYS:
        ew11_la[n][k] += o[k]
assert set(ew11_la) == set(ew21_la)
assert sum(o["total"] for o in ew11_la.values()) == ew11_ctry["K04000001"]["total"]


# ---- Scotland 2022 ----
SC = {"Church of Scotland": "cos", "Roman Catholic": "rc", "Other Christian": "ochr", "Buddhist": "buddhist", "Hindu": "hindu",
      "Jewish": "jewish", "Muslim": "muslim", "Sikh": "sikh", "Pagan": "pagan", "Other religion": "orel", "No religion": "none",
      "Religion not stated": "notstated"}


def superweb(fn, ordered=False):
    rows = []
    with open(f"{REL}/{fn}", encoding="utf-8") as f:
        for ln in f:
            if ln.startswith('"Individuals",'):
                rows.append(next(csv.reader([ln])))
    out = {} if not ordered else []
    cur = None
    for r in rows:
        name, cat, v = r[1], r[2], int(r[3])
        if cat == "All people":
            cur = {"name": name, "total": v}
            if ordered: out.append(cur)
            else: out[name] = cur
        else:
            cur[SC[cat]] = v
    for o in (out if ordered else out.values()):
        o["christian"] = o["cos"] + o["rc"] + o["ochr"]
        o["other"] = o["pagan"] + o["orel"]
    return out


sc_ctry = superweb("scot_uv205_ctry.csv")["Scotland"]
sc_ca = superweb("scot_uv205_ca2019.csv")
sc_iz = superweb("scot_uv205_iz2011.csv", ordered=True)
assert len(sc_ca) == 32 and len(sc_iz) == 1279, (len(sc_ca), len(sc_iz))

# ---- Northern Ireland 2021 ----


def xl(fn, sheet, header_first):
    ws = openpyxl.load_workbook(f"{REL}/{fn}", read_only=True, data_only=True)[sheet]
    rows = [list(r) for r in ws.iter_rows(values_only=True)]
    i = next(j for j, r in enumerate(rows) if r and r[0] == header_first)
    head = [str(h).split("\n")[0].strip() if h else h for h in rows[i]]
    out = []
    for r in rows[i + 1:]:
        if not r or r[0] is None or (isinstance(r[0], str) and r[0].startswith("MS-")):
            break
        out.append(dict(zip(head, r)))
    return out


b19 = xl("ni_ms_b19_religion.xlsx", "MS-B19", "Geography")
b23 = xl("ni_ms_b23_religion_brought_up.xlsx", "MS-B23", "Geography")
b22 = xl("ni_ms_b22_religion_1861_2021.xlsx", "MS-B22", "Census year")
assert len(b19) == 12 and len(b23) == 12, (len(b19), len(b23))
ni = {}
for r in b19:
    o = {"name": r["Geography"], "total": r["All usual residents"], "cath": r["Catholic"], "pres": r["Presbyterian Church in Ireland"],
         "coi": r["Church of Ireland"], "meth": r["Methodist Church in Ireland"], "ochr": r["Other Christian (including Christian related)"],
         "other": r["Other religions"], "none": r["No religion"], "notstated": r["Religion not stated"]}
    o["christian"] = o["cath"] + o["pres"] + o["coi"] + o["meth"] + o["ochr"]
    for k in ("muslim", "hindu", "sikh", "jewish", "buddhist"):
        o[k] = None
    ni[r["Geography code"]] = o
nib = {}
for r in b23:
    nib[r["Geography code"]] = {"total": r["All usual residents"], "cath": r["Catholic"], "prot": r["Protestant and Other Christian (including Christian related)"],
                                "other": r["Other religions"], "none": r["None"]}
hist = []
for r in b22:
    hist.append({"year": int(str(r["Census year"])[:4]), "total": r["All usual residents"], "cath": r["Catholic"], "pres": r["Presbyterian Church in Ireland"],
                 "coi": r["Church of Ireland"], "meth": r["Methodist Church in Ireland"], "other": r["Other religions"], "none_ns": r["None/Not Stated"]})
print("NI history years:", [h["year"] for h in hist])

# ---- local authority table, 361 areas (2023 boundaries) ----
LADG = jload(f"{GEO}/lad23_bsc.geojson")["features"]
lad_names = {f["properties"]["LAD23CD"]: f["properties"]["LAD23NM"] for f in LADG}
sc_code = {}
for c, n in lad_names.items():
    if c.startswith("S"):
        assert n in sc_ca, n
        sc_code[c] = n
nation = lambda c: {"E": "England", "W": "Wales", "S": "Scotland", "N": "Northern Ireland"}[c[0]]
LA = {}
for c, n in lad_names.items():
    if c[0] in "EW":
        o = ew21_la[c]; o11 = ew11_la[c]
        LA[c] = {"name": n, "nation": nation(c), "year": 2021, "total": o["total"], **{k: o[k] for k in UKEYS},
                 "y2011": {"total": o11["total"], **{k: o11[k] for k in UKEYS}}}
    elif c[0] == "S":
        o = sc_ca[sc_code[c]]
        LA[c] = {"name": n, "nation": "Scotland", "year": 2022, "total": o["total"], **{k: o[k] for k in UKEYS},
                 "detail": {"Church of Scotland": o["cos"], "Roman Catholic": o["rc"], "Other Christian": o["ochr"], "Pagan": o["pagan"], "Other religion": o["orel"]}}
    else:
        o = ni[c]; b = nib[c]
        LA[c] = {"name": n, "nation": "Northern Ireland", "year": 2021, "total": o["total"], **{k: o[k] for k in UKEYS},
                 "detail": {"Catholic": o["cath"], "Presbyterian Church in Ireland": o["pres"], "Church of Ireland": o["coi"], "Methodist Church in Ireland": o["meth"], "Other Christian": o["ochr"]},
                 "brought_up": b}
assert len(LA) == 361

# local authority of each MSOA (MSOA names are '<LA name> 001')
# (MSOA names carry 2021 district names, so the 2023 local authority is found by point in polygon)
from shapely.strtree import STRtree
LADF = [f for f in jload(f"{GEO}/lad23_bgc.geojson")["features"] if f["properties"]["LAD23CD"][0] in "EW"]
LGS = [shape(f["geometry"]) for f in LADF]; LTR = STRtree(LGS)
MSGEO = {f["properties"]["MSOA21CD"]: shape(f["geometry"]) for f in jload(f"{GEO}/msoa21_bsc.geojson")["features"]}
la_by_name = {v["name"]: c for c, v in LA.items() if c[0] in "EW"}
MS = {}
for c, o in ew21_msoa.items():
    la = la_by_name.get(o["name"].rsplit(" ", 1)[0])
    if not la:
        pt = MSGEO[c].representative_point()
        hit = [i for i in LTR.query(pt) if LGS[i].contains(pt)] or [int(LTR.nearest(pt))]
        la = LADF[hit[0]]["properties"]["LAD23CD"]
    MS[c] = {"name": o["name"], "la": la, "total": o["total"], **{k: o[k] for k in UKEYS}}
# check: MSOA totals add up to local authority totals
agg = defaultdict(int)
for o in MS.values():
    agg[o["la"]] += o["total"]
bad = [c for c in agg if abs(agg[c] - LA[c]["total"]) > 50]
print("local authorities whose MSOAs do not add up:", len(bad), bad[:5])

# ---- TS031 detailed answers (England and Wales) ----
det = defaultdict(int)
with open(f"{REL}/ts031_ltla23.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        det[r["C2021_RELIGION_58_NAME"].strip()] += int(r["OBS_VALUE"])

# ---- age (RM118, England and Wales). The extract has blank age labels; the eight bands are identified by their
# population totals, which match the ONS age structure for 2021: 0 to 2, 3 to 15, 16 to 24, 25 to 34, 35 to 49,
# 50 to 64, 65 to 74, 75 and over. The first two are combined as 'under 16'. ----
AGEB = ["u16a", "u16b", "16-24", "25-34", "35-49", "50-64", "65-74", "75+"]
age = defaultdict(lambda: defaultdict(dict))
with open(f"{REL}/rm118_country.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))
idx = defaultdict(int)
for r in rows:
    g, cat = r["GEOGRAPHY_NAME"], r["C2021_RELIGION_10_NAME"]
    i = idx[(g, cat)]; idx[(g, cat)] += 1
    band = "all" if i == 0 else AGEB[i - 1]
    key = "total" if cat == "Total" else T10[cat]
    age[g][band][key] = int(r["OBS_VALUE"])
for g in age:
    for k in ["total"] + UKEYS:
        age[g]["Under 16"][k] = age[g]["u16a"][k] + age[g]["u16b"][k]
    del age[g]["u16a"], age[g]["u16b"]
    assert sum(age[g][b]["total"] for b in age[g] if b != "all") == age[g]["all"]["total"]
assert abs(age["England and Wales"]["all"]["total"] - ew21_reg["K04000001"]["total"]) < 10

# ---- write ----
U = {"ew21_reg": ew21_reg, "ew11_ctry": ew11_ctry, "scot": sc_ctry, "ni": ni, "ni_b": nib, "ni_hist": hist, "LA": LA, "MS": MS,
     "det": dict(det), "age": {g: dict(v) for g, v in age.items()},
     "sc_iz": [{"name": o["name"], "total": o["total"], **{k: o.get(k) for k in UKEYS}} for o in sc_iz]}
jsave(U, f"{WORK}/uk.json")

with open(f"{DATA}/uk_local_authorities.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["code", "name", "nation", "census_year", "all_residents"] + UKEYS + [f"pct_{k}" for k in UKEYS] +
               ["all_residents_2011"] + [f"{k}_2011" for k in UKEYS])
    for c in sorted(LA):
        o = LA[c]; t = o["total"]; y = o.get("y2011")
        w.writerow([c, o["name"], o["nation"], o["year"], t] + [o[k] for k in UKEYS] +
                   [None if o[k] is None else round(100 * o[k] / t, 2) for k in UKEYS] +
                   ([y["total"]] + [y[k] for k in UKEYS] if y else [None] * 10))
with open(f"{DATA}/ew_msoa_2021.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["msoa21cd", "msoa21nm", "la_code", "all_residents"] + UKEYS + [f"pct_{k}" for k in UKEYS])
    for c in sorted(MS):
        o = MS[c]; t = o["total"]
        w.writerow([c, o["name"], o["la"], t] + [o[k] for k in UKEYS] + [round(100 * o[k] / t, 2) for k in UKEYS])
with open(f"{DATA}/ni_religion_1861_2021.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["year", "all_residents", "catholic", "presbyterian", "church_of_ireland", "methodist", "other_religions", "none_or_not_stated"])
    for h in hist:
        w.writerow([h["year"], h["total"], h["cath"], h["pres"], h["coi"], h["meth"], h["other"], h["none_ns"]])


# ---- page geometry: local authorities and MSOAs, rounded ----
def rnd(o, d):
    if isinstance(o, (list, tuple)):
        if o and isinstance(o[0], (int, float)):
            return [round(o[0], d), round(o[1], d)]
        return [rnd(x, d) for x in o]
    return o


def geo(feats, codek, tol, d):
    out = []
    for f in feats:
        g = shape(f["geometry"])
        if tol:
            g = g.simplify(tol, preserve_topology=True)
        gm = mapping(g)
        out.append({"type": "Feature", "properties": {"c": f["properties"][codek]}, "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"], d)}})
    return {"type": "FeatureCollection", "features": out}


jsave(geo(LADG, "LAD23CD", 0.002, 3), f"{DATA}/uk_la.json")
MSG = jload(f"{GEO}/msoa21_bsc.geojson")["features"]
assert {f["properties"]["MSOA21CD"] for f in MSG} == set(MS)
jsave(geo(MSG, "MSOA21CD", 0.0006, 4), f"{DATA}/uk_msoa.json")
for fn in ("uk_la.json", "uk_msoa.json"):
    print(fn, os.path.getsize(f"{DATA}/{fn}") // 1024, "KB")
