"""World: Pew Research Center religious composition 2010 and 2020 joined to Natural Earth countries.

Outputs
- data/world.json: simplified Natural Earth 1:50m country outlines (property iso = Natural Earth ADM0_A3).
- data/world_religion.csv: one row per Pew country and year with shares, rounded counts and diversity statistics.
- work/pew.json: the same, keyed by Pew country code, plus regional and world rows.
- data/cities.json: place names for the map (Natural Earth populated places, public domain).
"""
import csv
from shapely.geometry import shape, mapping
from common import *

COLS = {"Christians": "christian", "Muslims": "muslim", "Religiously_unaffiliated": "none", "Buddhists": "buddhist",
        "Hindus": "hindu", "Jews": "jewish", "Other_religions": "other"}


def read(fn):
    with open(f"{PEW}/{fn}", encoding="utf-8-sig") as f:
        return [r for r in csv.DictReader(f)]


num = lambda s: float(str(s).replace(",", "")) if str(s).strip() not in ("", "<10,000") else None
P = {}
for r in read("Religious Composition 2010-2020 (percentages).csv"):
    k = (r["Countrycode"], r["Year"])
    P[k] = {"region": r["Region"], "name": r["Country"], "year": int(r["Year"]), "level": int(r["Level"]), "code": int(r["Countrycode"]),
            "pop": float(r["Population"]), "pct": {COLS[c]: float(r[c]) for c in COLS}}
for r in read("Religious Composition 2010-2020 (rounded counts).csv"):
    k = (r["Countrycode"], r["Year"])
    P[k]["cnt"] = {COLS[c]: (r[c].strip() if r[c].strip().startswith("<") else num(r[c])) for c in COLS}
    P[k]["pop_r"] = num(r["Population"])
for r in read("Religious Composition 2010-2020 (unrounded counts).csv"):
    k = (r["Countrycode"], r["Year"])
    P[k]["raw"] = {COLS[c]: num(r[c]) for c in COLS}
for r in read("Religious Composition 2010-2020 (diversity statistics).csv"):
    k = (r["Countrycode"], r["Year"])
    P[k]["rdi"] = float(r["RDI_score"]) if r["RDI_score"] else None
    P[k]["rdi_level"] = r["Diveristy_level"]
    P[k]["rdi_rank"] = int(r["Diversity_rank"]) if r["Diversity_rank"] else None
assert len(P) == 416, len(P)
countries = sorted({k[0] for k, v in P.items() if v["level"] == 1})
print(len(countries), "Pew countries and territories")
assert len(countries) == 201

# ---- Natural Earth: map Pew codes (UN M49) to ADM0_A3 ----
NE = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")["features"]
n3 = {}
for f in NE:
    p = f["properties"]
    c = p["ISO_N3_EH"] if p["ISO_N3_EH"] not in ("-99", None) else p["ISO_N3"]
    if c not in ("-99", None):
        n3.setdefault(int(c), []).append(p["ADM0_A3"])
MANUAL = {412: ["KOS"], 830: ["JEY", "GGY"], 706: ["SOM", "SOL"], 36: ["AUS"], 578: ["NOR"], 250: ["FRA"]}
ISO = {}   # pew code -> [ADM0_A3]
for c in countries:
    ci = int(c)
    isos = MANUAL.get(ci) or n3.get(ci)
    if not isos:
        print("no outline:", P[(c, "2020")]["name"])
        continue
    ISO[c] = isos
# Somaliland is drawn with Somalia's values (Pew estimates Somalia as a whole); Northern Cyprus is left without data.

feats = []
for f in NE:
    p = f["properties"]
    if p["ADM0_A3"] in ("ATA",):
        continue
    g = shape(f["geometry"]).simplify(0.06, preserve_topology=True)
    if g.is_empty:
        continue
    gm = mapping(g)

    def rnd(o):
        if isinstance(o, (list, tuple)):
            if o and isinstance(o[0], (int, float)):
                return [round(o[0], 2), round(o[1], 2)]
            return [rnd(x) for x in o]
        return o
    feats.append({"type": "Feature", "properties": {"iso": p["ADM0_A3"], "name": p["NAME"]},
                  "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/world.json")
print("world.json", os.path.getsize(f"{DATA}/world.json") // 1024, "KB,", len(feats), "outlines")

# centroids for labels (largest polygon)
cpos = {}
for f in NE:
    p = f["properties"]
    g = shape(f["geometry"])
    big = max(g.geoms, key=lambda x: x.area) if g.geom_type == "MultiPolygon" else g
    pt = big.representative_point()
    cpos[p["ADM0_A3"]] = [round(pt.x, 2), round(pt.y, 2), int(p["POP_EST"] or 0)]

out = {"rows": {f"{k[0]}|{k[1]}": v for k, v in P.items()}, "iso": ISO, "cpos": cpos}
jsave(out, f"{WORK}/pew.json")

with open(f"{DATA}/world_religion.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["pew_code", "iso3_ne", "level", "region", "country", "year", "population"] + [f"pct_{k}" for k in WKEYS] +
               [f"count_{k}_rounded" for k in WKEYS] + ["largest_group", "rdi_score", "rdi_level", "rdi_rank"])
    for (c, y), v in sorted(P.items(), key=lambda kv: (kv[1]["level"] != 3, kv[1]["level"] != 2, kv[1]["name"], kv[1]["year"])):
        lg = max(WKEYS, key=lambda k: v["pct"][k])
        w.writerow([c, "|".join(ISO.get(c, [])), {1: "country", 2: "region", 3: "world"}[v["level"]], v["region"], v["name"], y, v["pop_r"]] +
                   [round(v["pct"][k], 2) for k in WKEYS] + [v["cnt"][k] for k in WKEYS] + [lg, None if v["rdi"] is None else round(v["rdi"], 2), v["rdi_level"], v["rdi_rank"]])

# ---- place names: Natural Earth populated places ----
pp = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]
cities = []
for f in pp:
    p = f["properties"]
    pop = p["pop_max"] or 0
    uk = p["adm0_a3"] == "GBR"
    if pop >= 150000 or (uk and pop >= 20000) or p["adm0cap"]:
        cities.append({"name": p["name"], "lat": round(p["latitude"], 3), "lon": round(p["longitude"], 3), "pop": int(pop), "cap": int(p["adm0cap"] or 0)})
cities.sort(key=lambda c: -c["pop"])
jsave(cities, f"{DATA}/cities.json")
print(len(cities), "place names")
