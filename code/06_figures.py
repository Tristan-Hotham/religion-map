"""Static figures: header.png (1200 x 630), blog figures (release/blog/b_*.png) and paper figures (release/paper/f_*.png).
Maps are drawn from Natural Earth and ONS outlines, no web tiles."""
from collections import Counter
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.collections import PatchCollection
from shapely.geometry import shape
from figstyle import *
import checks  # noqa: F401

R = jload(f"{DATA}/results.json")
OSM = jload(f"{DATA}/osm_cells.json")
U = jload(f"{WORK}/uk.json")
REL = os.path.join(ROOT, "release"); os.makedirs(f"{REL}/blog", exist_ok=True); os.makedirs(f"{REL}/paper", exist_ok=True)
WK, UKK = SITE["wk"], SITE["uk"]
OCOL = {"christian": REL_COL["christian"], "muslim": REL_COL["muslim"], "buddhist": REL_COL["buddhist"], "hindu": REL_COL["hindu"],
        "shinto": "#C0392B", "jewish": REL_COL["jewish"], "sikh": REL_COL["sikh"], "taoist": "#5D7A3A", "other": "#B07AA1"}
ONAME = {"christian": "Christian", "muslim": "Muslim", "buddhist": "Buddhist", "hindu": "Hindu", "shinto": "Shinto", "jewish": "Jewish", "sikh": "Sikh", "taoist": "Taoist", "other": "Other"}


def legend(fig, items, y, ncol=4, x=.03, fs=9.4, marker=False):
    h = [Line2D([], [], marker="s" if not marker else "o", ls="", ms=8, mfc=c, mec="none", label=l) for l, c in items]
    fig.legend(handles=h, loc="upper left", bbox_to_anchor=(x, y), ncol=ncol, frameon=False, fontsize=fs, handletextpad=.4,
               columnspacing=1.3, labelspacing=.5)


def both(name):
    return [f"{REL}/blog/b_{name}.png", f"{REL}/paper/f_{name}.png"]


# ---------- OpenStreetMap cells: dominant religion per cell, projected ----------
RG = OSM["rg"]
cells = np.array([r[:2] + [r[2]] for r in OSM["rows"]], dtype=float)
dom = []
for r in OSM["rows"]:
    v = r[3:3 + len(RG)]
    best = max((n, g) for n, g in zip(v, RG) if g != "untagged") if any(n for n, g in zip(v, RG) if g != "untagged") else (0, "untagged")
    dom.append(best[1])
cx, cy = tr.transform((cells[:, 1] + .5) / 4, (cells[:, 0] + .5) / 4)


def osm_scatter(ax, s=.7, alpha=.75):
    order = ["christian", "muslim", "hindu", "buddhist", "shinto", "taoist", "jewish", "sikh", "other"]
    dn = np.array(dom)
    for g in order:
        m = dn == g
        if m.any():
            ax.scatter(cx[m], cy[m], s=s * np.clip(np.log10(cells[m, 2] + 1), .4, 3), c=OCOL[g], lw=0, alpha=alpha, zorder=3, rasterized=True)


# ---------- header (1200 x 630) ----------
fig = plt.figure(figsize=(6, 3.15), facecolor=BG)
ax = fig.add_axes([.34, .04, .68, .92])
world(ax, lambda iso: (largest_col(*largest(pew(iso))) if pew(iso) else None), lw=.2, extent=(-12.0e6, 15.6e6, -5.6e6, 8.3e6), ec=BG)
fig.text(.04, .86, "Faith on", fontproperties=DISP, fontsize=23, color=FG, va="top")
fig.text(.04, .72, "the map", fontproperties=DISP, fontsize=23, color=REL_COL["christian"], va="top")
w, u = R["world"], R["uk"]
fig.text(.04, .54, f"The largest religious group in\n{w['n_countries']} countries and territories, and\nreligion in every UK neighbourhood.\nScotland: {u['scot']['none']:.1f}% no religion.",
         fontproperties=SERP, fontsize=8.2, color=FG, va="top", linespacing=1.45)
for i, k in enumerate(WK):
    xx, yy = .045 + (i % 2) * .135, .225 - (i // 2) * .045
    fig.add_artist(Line2D([xx], [yy], marker="s", ms=4.2, mfc=REL_COL[k], mec="none", ls="", transform=fig.transFigure))
    fig.text(xx + .012, yy, WNAME[k].replace("Religiously unaffiliated", "Unaffiliated"), fontsize=5.2, color=FG, va="center")
fig.text(.04, .035, "maps.tristanhotham.com/religion-map", fontsize=5.6, color=MUT)
save(fig, os.path.join(ROOT, "header.png"))

# ---------- largest group by country, 2020 ----------
cnt = Counter(largest(c)[0] for c in SITE["c"].values())
for out in both("largest_map"):
    fig = plt.figure(figsize=(7.6, 4.9), facecolor=BG)
    ax = fig.add_axes([0, .17, 1, .83]); world(ax, lambda iso: (largest_col(*largest(pew(iso))) if pew(iso) else None))
    legend(fig, [(f"{WNAME[k]} ({cnt[k]})", largest_col(k, 60)) for k in WK], .165, ncol=4, fs=8.6)
    fig.text(.03, .035, "Darker: a majority of the population. Lighter: the largest group, but under half. Pew Research Center estimates, 2020.", fontsize=7.2, color=MUT)
    save(fig, out)

# ---------- change in the unaffiliated share ----------
for out in both("none_change_map"):
    fig = plt.figure(figsize=(7.6, 4.9), facecolor=BG)
    ax = fig.add_axes([0, .17, 1, .83])
    ch = lambda iso: (div(pew(iso)["b"][2] - pew(iso)["a"][2], "none") if pew(iso) else None)
    world(ax, ch)
    labs = ["under -5", "-5 to -2", "-2 to -0.5", "about the same", "0.5 to 2", "2 to 5", "5 to 10", "10 to 15", "over 15"]
    vals = [-7, -3, -1, 0, 1, 3, 7, 12, 17]
    legend(fig, [(l, div(v, "none")) for l, v in zip(labs, vals)], .165, ncol=5, fs=8.6)
    fig.text(.03, .035, "Change in the unaffiliated share, 2010 to 2020, percentage points. Pew Research Center estimates.", fontsize=7.2, color=MUT)
    save(fig, out)

# ---------- global composition 2010 and 2020 ----------
G = w["groups"]
for out in both("global"):
    fig = plt.figure(figsize=(7.6, 3.9), facecolor=BG); ax = fig.add_axes([.31, .08, .63, .88], facecolor=BG)
    ys = np.arange(len(WK))[::-1]
    for y, k in zip(ys, WK):
        ax.barh(y + .18, G[k]["pct2010"], height=.3, color=REL_COL[k], alpha=.35)
        ax.barh(y - .14, G[k]["pct2020"], height=.38, color=REL_COL[k])
        ax.text(G[k]["pct2020"] + .5, y - .14, (f"{G[k]['pct2020']:.1f}%  ({G[k]['bn2020']:.2f} bn)" if G[k]['bn2020'] >= .1 else f"{G[k]['pct2020']:.1f}%  ({G[k]['m2020']} m)"), va="center", fontsize=9)
    ax.set_yticks(ys); ax.set_yticklabels([WNAME[k] for k in WK], fontsize=10); ax.set_xlim(0, 40)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(left=False); ax.set_xticks([0, 10, 20, 30]); ax.set_xticklabels(["0%", "10%", "20%", "30%"])
    ax.text(30, ys[0] + .55, "pale 2010, solid 2020", fontsize=8, color=MUT)
    save(fig, out)

# ---------- where the world's Christians live ----------
rc = w["regions"]["christian"]
RN = {"Sub-Saharan Africa": "Sub-Saharan Africa", "Europe": "Europe", "Latin America-Caribbean": "Latin America and Caribbean", "Asia-Pacific": "Asia-Pacific", "North America": "North America", "Middle East-North Africa": "Middle East and North Africa"}
regs = sorted(rc, key=lambda r: -rc[r]["2020"])
for out in both("christ_regions"):
    fig = plt.figure(figsize=(7.6, 3.6), facecolor=BG); ax = fig.add_axes([.37, .1, .56, .86], facecolor=BG)
    ys = np.arange(len(regs))[::-1]
    for y, r in zip(ys, regs):
        ax.barh(y + .18, rc[r]["2010"], height=.3, color=REL_COL["christian"], alpha=.35)
        ax.barh(y - .14, rc[r]["2020"], height=.38, color=REL_COL["christian"])
        ax.text(max(rc[r]["2020"], rc[r]["2010"]) + .5, y, f"{rc[r]['2010']:.1f}% to {rc[r]['2020']:.1f}%", va="center", fontsize=9)
    ax.set_yticks(ys); ax.set_yticklabels([RN[r] for r in regs], fontsize=10); ax.set_xlim(0, 42)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(left=False); ax.set_xticks([0, 10, 20, 30]); ax.set_xticklabels(["0%", "10%", "20%", "30%"])
    ax.set_xlabel("share of the world's Christians (pale 2010, solid 2020)", fontsize=8.5, color=MUT)
    save(fig, out)

# ---------- places of worship ----------
by = R["osm"]["by_rel"]
for out in both("osm_map"):
    fig = plt.figure(figsize=(7.6, 4.8), facecolor=BG)
    ax = fig.add_axes([0, .15, 1, .85]); world(ax, lambda iso: "#E9E3D6", lw=.2, ec=BG)
    osm_scatter(ax)
    legend(fig, [(f"{ONAME[g]} ({by[g]:,})", OCOL[g]) for g in ["christian", "muslim", "buddhist", "hindu", "shinto", "taoist", "jewish", "sikh"]], .145, ncol=4, fs=8.4, marker=True)
    fig.text(.03, .015, "Each dot is a quarter degree square, coloured by its most common tagged religion,\nsized by the number of places. OpenStreetMap contributors (ODbL).", fontsize=7, color=MUT)
    save(fig, out)

DK = ["catholic", "orthodox", "anglican", "lutheran", "reformed", "baptist", "methodist", "pentecostal", "evangelical", "protestant", "otherchr"]
DN = dict(OSM["den"])
DC = {"catholic": "#C0392B", "orthodox": "#D4A21A", "anglican": "#3B5BA9", "lutheran": "#2E8B9A", "reformed": "#6E6A86", "baptist": "#2E8B57", "methodist": "#B07AA1",
      "pentecostal": "#E3672B", "evangelical": "#8E2A4A", "protestant": "#9E9E9E", "otherchr": "#CFC8BA"}
OB = jload(f"{WORK}/osm.json")["by_region"]
dregs = ["Europe", "North America", "Latin America-Caribbean", "Sub-Saharan Africa", "Asia-Pacific", "Middle East-North Africa"]
for out in both("denominations"):
    fig = plt.figure(figsize=(7.6, 4.2), facecolor=BG); ax = fig.add_axes([.37, .3, .6, .66], facecolor=BG)
    ys = np.arange(len(dregs))[::-1]
    for y, r in zip(ys, dregs):
        d = OB[r]["d"]; t = sum(d.get(k, 0) for k in DK); x = 0
        for k in DK:
            v = 100 * d.get(k, 0) / t
            ax.barh(y, v, left=x, color=DC[k], height=.7, edgecolor=BG, lw=.5)
            if v > 7: ax.text(x + v / 2, y, f"{v:.0f}%", ha="center", va="center", fontsize=8, color="#fff")
            x += v
    ax.set_yticks(ys); ax.set_yticklabels([RN[r] for r in dregs], fontsize=9.5); ax.set_xlim(0, 100)
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.tick_params(left=False); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    legend(fig, [(DN[k], DC[k]) for k in DK], .2, ncol=3, fs=8)
    save(fig, out)

# ---------- UK: no religion by neighbourhood (E&W MSOAs) and council (Scotland, NI) ----------
MS = jload(f"{DATA}/uk_msoa.json")["features"]; LAJ = jload(f"{DATA}/uk_la.json")["features"]
k0 = np.cos(np.radians(54.5))
UB = [10, 20, 30, 40, 50, 60]
ucol = lambda v: seq(v, "none", UB)


def polys(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for p in cs:
        a = np.array(p[0]); yield np.column_stack([a[:, 0] * k0, a[:, 1]])


def ukmap(ax, key, shares=True):
    pat, col = [], []
    for f in MS:
        p = f["properties"]; v = 100 * p["v"][UKK.index(key)] / p["T"]
        for q in polys(f["geometry"]): pat.append(MPoly(q, closed=True)); col.append(ucol(v))
    for f in LAJ:
        c = f["properties"]["c"]
        if c[0] in "SN":
            d = SITE["la"][c]; v = 100 * d["v"][UKK.index(key)] / d["T"]
            for q in polys(f["geometry"]): pat.append(MPoly(q, closed=True)); col.append(ucol(v))
    ax.add_collection(PatchCollection(pat, facecolors=col, edgecolors="none", lw=0))
    lines = [MPoly(q, closed=True) for f in LAJ for q in polys(f["geometry"])]
    ax.add_collection(PatchCollection(lines, facecolors="none", edgecolors="#ffffff", lw=.25))
    ax.set_xlim(-8.3 * k0, 1.9 * k0); ax.set_ylim(49.85, 60.9); ax.set_aspect("equal"); ax.axis("off")


for out in both("uk_none_map"):
    fig = plt.figure(figsize=(7.6, 8.6), facecolor=BG)
    ax = fig.add_axes([.02, .02, .7, .96]); ukmap(ax, "none")
    items = [(f"under {UB[0]}%", ucol(5))] + [(f"{a} to {b}%" if b else f"{a}% and over", ucol(a)) for a, b in zip(UB, UB[1:] + [None])]
    fig.legend(handles=[Patch(fc=c, ec="none", label=l) for l, c in items], loc="upper left", bbox_to_anchor=(.66, .62), frameon=False, fontsize=9.5)
    fig.text(.66, .9, "No religion,\nUK censuses\n2021 and 2022", fontproperties=DISP, fontsize=22, color=FG, va="top", linespacing=1.1)
    fig.text(.66, .32, f"England and Wales: {u['ew2021']['none']:.1f}%\nWales: {u['wal2021']['none']:.1f}%\nScotland: {u['scot']['none']:.1f}%\nNorthern Ireland: {u['ni']['none']:.1f}%", fontsize=9.5, color=FG, va="top", linespacing=1.6)
    fig.text(.66, .16, "England and Wales by\nneighbourhood (MSOA), 2021;\nScotland (2022) and Northern\nIreland (2021) by council.", fontsize=8, color=MUT, va="top", linespacing=1.4)
    save(fig, out)

# ---------- UK nations stacked ----------
NAT = [("England", u["eng2021"]), ("Wales", u["wal2021"]), ("Scotland", u["scot"]), ("Northern Ireland", u["ni"])]
for out in both("uk_nations"):
    fig = plt.figure(figsize=(7.6, 3.4), facecolor=BG); ax = fig.add_axes([.2, .34, .77, .62], facecolor=BG)
    ys = np.arange(len(NAT))[::-1]
    for y, (n, s) in zip(ys, NAT):
        x = 0
        for k in UKK:
            v = s[k] or 0
            ax.barh(y, v, left=x, color=REL_COL[k], height=.7, edgecolor=BG, lw=.5)
            if v > 6: ax.text(x + v / 2, y, f"{v:.0f}%", ha="center", va="center", fontsize=8.5, color="#fff")
            x += v
    ax.set_yticks(ys); ax.set_yticklabels([n for n, _ in NAT], fontsize=10); ax.set_xlim(0, 100)
    for s_ in ("top", "right", "left"): ax.spines[s_].set_visible(False)
    ax.tick_params(left=False); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
    legend(fig, [(UNAME[k], REL_COL[k]) for k in UKK], .2, ncol=5, fs=8.4)
    save(fig, out)

# ---------- age ----------
A = u["age"]["England and Wales"]; bl = [a["band"].replace("-", " to ").replace("75+", "75+") for a in A]
for out in both("age"):
    fig = plt.figure(figsize=(7.6, 4.0), facecolor=BG); ax = fig.add_axes([.09, .14, .72, .82], facecolor=BG)
    for k in ("christian", "none", "muslim"):
        v = [a[k] for a in A]; ax.plot(range(len(A)), v, color=REL_COL[k], lw=2.6, marker="o", ms=5)
        ax.text(len(A) - .8, v[-1], UNAME[k], color=REL_COL[k], va="center", fontsize=10, fontweight="medium")
    ax.set_xticks(range(len(A))); ax.set_xticklabels(bl, fontsize=9); ax.set_ylim(0, 85); ax.set_xlim(-.3, len(A) - .7)
    ax.set_yticks([0, 20, 40, 60, 80]); ax.set_yticklabels(["0%", "20%", "40%", "60%", "80%"]); ax.grid(axis="y", color=RULE, lw=.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.set_xlabel("age, England and Wales, census 2021", fontsize=9, color=MUT)
    save(fig, out)

# ---------- Northern Ireland 1861 to 2021 ----------
H = u["ni_hist"]; yrs = [h["year"] for h in H]
NIS = [("Catholic", "#9C5B2E", "cath"), ("Presbyterian, Church\nof Ireland, Methodist", "#3C7A89", "prot3"), ("Other", "#B5A26A", "other"), ("None or not stated", REL_COL["none"], "none_ns")]
for out in both("ni_history"):
    fig = plt.figure(figsize=(7.6, 4.2), facecolor=BG); ax = fig.add_axes([.08, .1, .6, .86], facecolor=BG)
    for n, c, k in NIS:
        v = [h[k] for h in H]; ax.plot(yrs, v, color=c, lw=2.6, marker="o", ms=4)
        ax.text(2026, v[-1] + (2.2 if k == "prot3" else -1.6 if k == "none_ns" else 0), n, color=c, va="center", fontsize=9, fontweight="medium")
    ax.set_ylim(0, 70); ax.set_xlim(1855, 2024); ax.set_yticks([0, 20, 40, 60]); ax.set_yticklabels(["0%", "20%", "40%", "60%"])
    ax.grid(axis="y", color=RULE, lw=.8); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.annotate("1981: campaign of\nnon-cooperation", xy=(1981, 18.5), xytext=(1935, 26), fontsize=8, color=MUT, arrowprops=dict(arrowstyle="-", color=MUT, lw=.7))
    save(fig, out)

# ---------- mapping density (paper) ----------
reg = R["osm"]["region"]; rr = sorted(reg, key=lambda r: reg[r]["per100k"])
fig = plt.figure(figsize=(7.6, 3.2), facecolor=BG); ax = fig.add_axes([.37, .14, .56, .82], facecolor=BG)
ax.barh(range(len(rr)), [reg[r]["per100k"] for r in rr], color="#5B5670", height=.65)
for i, r in enumerate(rr): ax.text(reg[r]["per100k"] + 1, i, f"{reg[r]['per100k']:.1f}", va="center", fontsize=9)
ax.set_yticks(range(len(rr))); ax.set_yticklabels([RN[r] for r in rr], fontsize=9.5)
for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
ax.tick_params(left=False); ax.set_xlabel("places of worship in OpenStreetMap per 100,000 people (2020)", fontsize=8.5, color=MUT)
save(fig, f"{REL}/paper/f_osm_density.png")
print("figures done")
