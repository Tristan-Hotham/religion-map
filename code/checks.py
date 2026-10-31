"""Facts stated in words (not as tokens) in the page, paper, blog, collage and Reddit post, checked against the data.
Imported by every build script, so a rerun on changed data fails loudly instead of printing a false sentence."""
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
O = jload(f"{WORK}/osm.json")
w, u, o = R["world"], R["uk"], R["osm"]
G = w["groups"]
C2020 = {c["n"]: dict(zip(SITE["wk"], c["b"])) for c in SITE["c"].values()}
largest = lambda n: max(SITE["wk"], key=lambda k: C2020[n][k])

# world
assert max(G, key=lambda k: G[k]["growth_pct"]) == "muslim"
assert [k for k in G if G[k]["growth_pct"] < 0] == ["buddhist"]
assert G["muslim"]["growth_pct"] > w["pop_growth_pct"] > G["christian"]["growth_pct"]
assert G["christian"]["pct2020"] < G["christian"]["pct2010"] and G["none"]["pct2020"] > G["none"]["pct2010"]
for n in ("China", "Japan", "Czech Republic", "Netherlands", "Uruguay", "New Zealand"):
    assert largest(n) == "none", n
assert {c["name"] for c in w["changed"]} == {"Uruguay", "New Zealand"} and all(c["to"] == "none" for c in w["changed"])
for n in ("Sri Lanka", "Mongolia"):
    assert largest(n) == "buddhist", n
assert sorted(n for n in C2020 if largest(n) == "hindu") == ["India", "Mauritius", "Nepal"]
assert [n for n in C2020 if largest(n) == "jewish"] == ["Israel"] and [n for n in C2020 if largest(n) == "other"] == ["Taiwan"]
assert w["largest2020"]["jewish"] == 1 and w["largest2020"]["other"] == 1
rc = w["regions"]["christian"]
assert rc["Europe"]["2010"] > rc["Sub-Saharan Africa"]["2010"] and rc["Sub-Saharan Africa"]["2020"] > rc["Europe"]["2020"]
assert max(rc, key=lambda r: rc[r]["2020"]) == "Sub-Saharan Africa"
assert [d["name"] for d in w["top_change"]["none"]["rise"][:4]] == ["Australia", "Chile", "Uruguay", "United States"]
assert [d["name"] for d in w["top_change"]["buddhist"]["fall"][:3]] == ["South Korea", "Japan", "Vietnam"]
sg = C2020["Singapore"]
assert all(sg[k] >= 5 for k in ("buddhist", "christian", "muslim", "hindu", "other", "none")) and w["rdi_top"][0]["name"] == "Singapore"
assert w["china_share_of_none"] > 60
assert w["uk"]["christian2020"] > w["uk"]["none2020"]

# OpenStreetMap
assert [x["name"] for x in o["top_muslim"][:2]] == ["Indonesia", "Turkey"]
assert [x["name"] for x in o["top_hindu"][:2]] == ["India", "Nepal"]
assert [x["name"] for x in o["top_buddhist"][1:3]] == ["Myanmar", "Thailand"] and o["top_shinto"][0]["name"] == "Japan"
rd = o["region_den"]
assert rd["Europe"][0]["k"] == "catholic" and rd["Latin America-Caribbean"][0]["k"] == "catholic"
assert [x["k"] for x in rd["Latin America-Caribbean"][1:3]] == ["pentecostal", "evangelical"]
assert [x["k"] for x in rd["North America"][:3]] == ["baptist", "catholic", "methodist"]
assert [x["k"] for x in rd["Sub-Saharan Africa"][:3]] == ["orthodox", "catholic", "pentecostal"]
assert O["by_country"]["ETH"]["d"]["orthodox"] / O["by_region"]["Sub-Saharan Africa"]["d"]["orthodox"] > .9
reg = o["region"]
assert min(reg, key=lambda r: reg[r]["per100k"]) == "Sub-Saharan Africa" and max(reg, key=lambda r: reg[r]["per100k"]) == "North America"

# UK
e = u["ew2021"]
assert e["christian"] > e["none"] > 0 and e["christian"] < 50 and u["ew2011"]["christian"] > 50
assert u["wal2021"]["none"] > u["wal2021"]["christian"] and u["scot"]["none"] > 50
assert u["ni"]["christian"] == max(x["christian"] for x in (u["ew2021"], u["scot"], u["ni"], u["wal2021"], u["eng2021"]))
mins = sorted(["muslim", "hindu", "sikh", "jewish", "buddhist", "other"], key=lambda k: -e[k])
assert mins[:3] == ["muslim", "hindu", "sikh"]
la = u["la"]
assert la["ew_christian_fell"] == la["ew_n"]
assert la["ew_none_largest_2011"] == 0
assert [x["name"] for x in la["change"]["christian"]["fall"][:5]] == ["South Tyneside", "Rotherham", "County Durham", "Hartlepool", "Wakefield"]
assert [x["name"] for x in la["change"]["christian"]["rise"][:3]] == ["Camden", "Brent", "Harrow"]
T = u["msoa"]["top"]
las = lambda k, n: [x["la"] for x in T[k][:n]]
assert set(las("none", 4)) == {"Brighton and Hove"}
assert set(las("christian", 3)) == {"Liverpool", "Knowsley"}
assert set(las("muslim", 5)) == {"Birmingham", "Blackburn with Darwen", "Bradford"}
assert set(las("hindu", 5)) == {"Leicester", "Brent"}
assert set(las("sikh", 5)) == {"Ealing", "Wolverhampton", "Birmingham"}
assert set(las("jewish", 5)) == {"Salford", "Barnet", "Hackney", "Bury", "Haringey"}
assert set(las("buddhist", 3)) == {"Rushmoor"} and la["top"]["buddhist"][0]["name"] == "Rushmoor"
A = {a["band"]: a for a in u["age"]["England and Wales"]}
assert A["35-49"]["christian"] - A["35-49"]["none"] < 1 and A["25-34"]["none"] > A["25-34"]["christian"] and A["50-64"]["christian"] > A["50-64"]["none"]
assert max(A, key=lambda b: A[b]["muslim"]) == "Under 16"
assert u["age_bands"][6] == "75+" and u["age_bands"][2] == "25-34" and u["age_bands"][0] == "Under 16"
h = u["ni_h"]
assert h["cross_year"] == 2001 and all(x["cath"] > x["prot3"] for x in u["ni_hist"] if x["year"] >= 2001)
assert h["cath_min_year"] == 1981 and u["ni_brought_up"]["cath"] > u["ni_brought_up"]["prot"]
assert h["n_censuses"] == 16
assert u["scot_detail"]["cos"] > u["scot_detail"]["rc"]
assert [d["name"] for d in w["top_change"]["none"]["fall"][:3]] == ["Mozambique", "Ivory Coast", "Ghana"]
assert .19 < la["largest"]["none"] / la["n"] < .22
assert max(w["rdi_regions"], key=w["rdi_regions"].get) == "Asia-Pacific" and min(w["rdi_regions"], key=w["rdi_regions"].get) == "Middle East-North Africa"
assert o["gbr"]["den"][0]["k"] == "anglican" and la["muslim_largest"] == ["Redbridge", "Tower Hamlets"]
print("word facts ok")
