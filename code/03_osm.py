"""OpenStreetMap places of worship (amenity=place_of_worship), counted per 0.25 degree cell by religion and
denomination tags (QLever osm-planet, retrieved in 2026). Cell y = floor(lat * 4), x = floor(lon * 4).

Religion tags are grouped (RGRP); Christian denomination tags into families (DEN). Each cell is assigned to the Natural
Earth country containing its centre (nearest country within 0.5 degrees for coastal cells), and so to a Pew region.

Outputs
- data/osm_cells.json: page layer, one row per cell [y, x, total, by religion group..., top Christian family index].
- data/osm_places_of_worship_by_country.csv: counts by country, religion group and Christian family.
- work/osm.json: totals for results.json.
"""
import csv
from collections import defaultdict, Counter
from shapely.geometry import shape, Point
from shapely.strtree import STRtree
from common import *

RG = ["christian", "muslim", "buddhist", "hindu", "shinto", "jewish", "sikh", "taoist", "other", "untagged"]
UNTAG = {"", "none", "no", "unknown", "yes"}


def rgroup(t):
    t = t.strip().lower()
    if t in UNTAG:
        return "untagged"
    return t if t in RG else "other"


DEN = [("catholic", "Catholic"), ("orthodox", "Orthodox and Oriental"), ("anglican", "Anglican and Episcopal"), ("lutheran", "Lutheran"),
       ("reformed", "Reformed and Presbyterian"), ("baptist", "Baptist"), ("methodist", "Methodist"), ("pentecostal", "Pentecostal"),
       ("evangelical", "Evangelical"), ("adventist", "Adventist"), ("lds", "Latter-day Saints"), ("jw", "Jehovah's Witnesses"),
       ("protestant", "Protestant (unspecified)"), ("otherchr", "Other Christian"), ("untagged", "No denomination tagged")]
DK = [d[0] for d in DEN]


def dgroup(t):
    t = t.strip().lower().replace("-", "_").replace(" ", "_")
    if t in ("", "none", "unknown", "yes", "christian", "christianity"):
        return "untagged"
    if "catholic" in t or t in ("catolica", "maronite", "syro_malabar", "syro_malankara", "chaldean", "melkite", "old_catholic") or t.startswith("roman"):
        return "catholic" if t != "old_catholic" else "otherchr"
    if "orthodox" in t or t in ("armenian_apostolic", "coptic", "old_believers", "assyrian", "church_of_the_east", "ethiopian_tewahedo", "armenian"):
        return "orthodox"
    if t in ("anglican", "episcopal", "church_of_england", "church_of_ireland", "church_in_wales", "scottish_episcopal", "episcopalian", "anglican_church"):
        return "anglican"
    if "lutheran" in t:
        return "lutheran"
    if "reformed" in t or "presbyterian" in t or t in ("church_of_scotland", "congregational", "calvinist", "free_church_of_scotland", "huguenot", "hervormd", "gereformeerd", "united_church_of_christ", "pkn"):
        return "reformed"
    if "baptist" in t:
        return "baptist"
    if "methodist" in t or t in ("wesleyan", "free_methodist"):
        return "methodist"
    if "pentecostal" in t or t in ("assemblies_of_god", "foursquare", "church_of_god", "apostolic", "church_of_god_in_christ", "elim", "redeemed_christian_church_of_god", "christian_congregation_in_brazil", "congregacao_crista_no_brasil", "universal_church_of_the_kingdom_of_god", "deeper_life_bible_church", "charismatic"):
        return "pentecostal"
    if t in ("evangelical", "evangelica", "evangelicalism", "evangelical_free", "evangelical_covenant", "nondenominational", "non_denominational", "evangelical_christian", "free_evangelical"):
        return "evangelical"
    if "adventist" in t:
        return "adventist"
    if t in ("mormon", "latter_day_saints", "lds", "the_church_of_jesus_christ_of_latter_day_saints"):
        return "lds"
    if t in ("jehovahs_witness", "jehovah's_witness", "jehovahs_witnesses"):
        return "jw"
    if t in ("protestant", "protestantism"):
        return "protestant"
    return "otherchr"


cells = defaultdict(lambda: {"r": Counter(), "d": Counter()})
tags_rel, tags_den = Counter(), Counter()
with open(f"{REL}/osm_places_of_worship_grid025.tsv", encoding="utf-8") as f:
    next(f)
    for ln in f:
        y, x, rel, den, n = ln.rstrip("\n").split("\t")
        n = int(n); key = (int(float(y)), int(float(x)))
        rel = rel.strip('"'); den = den.strip('"')
        g = rgroup(rel); cells[key]["r"][g] += n; tags_rel[rel] += n
        if g == "christian":
            cells[key]["d"][dgroup(den)] += n; tags_den[den] += n
TOT = sum(sum(c["r"].values()) for c in cells.values())
print(len(cells), "cells,", TOT, "places")

# countries
NE = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")["features"]
G = [shape(f["geometry"]) for f in NE]; I = [f["properties"]["ADM0_A3"] for f in NE]; T = STRtree(G)


def country(lon, lat):
    p = Point(lon, lat)
    for i in T.query(p):
        if G[i].contains(p):
            return I[i]
    i = int(T.nearest(p))
    return I[i] if G[i].distance(p) <= .5 else None


PEWJ = jload(f"{WORK}/pew.json")
iso2pew = {iso: c for c, isos in PEWJ["iso"].items() for iso in isos}
pew_region = {c: PEWJ["rows"][f"{c}|2020"]["region"] for c in PEWJ["iso"]}
byc = defaultdict(lambda: {"r": Counter(), "d": Counter()})
rows = []
for (y, x), c in cells.items():
    iso = country((x + .5) / 4, (y + .5) / 4)
    c["iso"] = iso
    byc[iso]["r"].update(c["r"]); byc[iso]["d"].update(c["d"])
    tot = sum(c["r"].values())
    dd = [(n, k) for k, n in c["d"].items() if k != "untagged"]
    top = DK.index(max(dd)[1]) if dd else -1
    rows.append([y, x, tot] + [c["r"].get(g, 0) for g in RG] + [top])
rows.sort()
jsave({"rg": RG, "den": DEN, "rows": rows}, f"{DATA}/osm_cells.json")
print("osm_cells.json", os.path.getsize(f"{DATA}/osm_cells.json") // 1024, "KB")

# by region (Pew regions) and by country
byr = defaultdict(lambda: {"r": Counter(), "d": Counter()})
for iso, v in byc.items():
    reg = pew_region.get(iso2pew.get(iso), "Not assigned")
    byr[reg]["r"].update(v["r"]); byr[reg]["d"].update(v["d"])
CN = {f["properties"]["ADM0_A3"]: f["properties"]["NAME"] for f in NE}
with open(f"{DATA}/osm_places_of_worship_by_country.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["iso3_ne", "country", "pew_region", "all"] + [f"rel_{g}" for g in RG] + [f"christian_{d}" for d in DK])
    for iso in sorted(byc, key=lambda i: -sum(byc[i]["r"].values())):
        v = byc[iso]
        w.writerow([iso or "", CN.get(iso, "Sea or unassigned"), pew_region.get(iso2pew.get(iso), ""), sum(v["r"].values())] +
                   [v["r"].get(g, 0) for g in RG] + [v["d"].get(d, 0) for d in DK])
out = {"total": TOT, "n_cells": len(cells), "by_rel": {g: sum(c["r"].get(g, 0) for c in cells.values()) for g in RG},
       "by_den": {d: sum(c["d"].get(d, 0) for c in cells.values()) for d in DK},
       "by_country": {iso or "": {"r": dict(v["r"]), "d": dict(v["d"])} for iso, v in byc.items()},
       "by_region": {k: {"r": dict(v["r"]), "d": dict(v["d"])} for k, v in byr.items()},
       "top_rel_tags": tags_rel.most_common(40), "top_den_tags": tags_den.most_common(80)}
jsave(out, f"{WORK}/osm.json")
print(out["by_rel"]); print(out["by_den"])
for k, v in byr.items():
    t = sum(n for d, n in v["d"].items() if d != "untagged")
    print(k, sum(v["r"].values()), [(d, round(100 * n / t)) for d, n in sorted(v["d"].items(), key=lambda kv: -kv[1]) if d != "untagged"][:6])
