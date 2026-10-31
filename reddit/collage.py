"""r/dataisbeautiful collage for religion-map: 2400 x 3000 px, light background. Numbers from data/results.json."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
import checks  # noqa: F401
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.collections import PatchCollection

R = jload(f"{DATA}/results.json")
w, u = R["world"], R["uk"]
BGC = "#F6F3EC"
fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BGC)
fig.text(.045, .968, "Faith on the map", fontproperties=DISP, fontsize=60, color=FG, va="top")
fig.text(.045, .9, f"The largest religious group in each of {w['n_countries']} countries and territories in 2020 (Pew Research Center estimates),\nwith a decade of change and the UK's latest censuses below.",
         fontproperties=SERP, fontsize=16, color=FG, va="top", linespacing=1.4)

# hero map
ax = fig.add_axes([0, .515, 1, .33])
world(ax, lambda iso: (largest_col(*largest(pew(iso))) if pew(iso) else None), lw=.4, extent=(-12.3e6, 15.6e6, -5.9e6, 7.4e6), ec=BGC)


def note(lon, lat, tx, ty, text):
    x0, y0 = tr.transform(lon, lat); x1, y1 = tr.transform(tx, ty)
    ax.annotate(text, xy=(x0, y0), xytext=(x1, y1), fontsize=10.5, color=FG, ha="left", va="center", family=MONO,
                arrowprops=dict(arrowstyle="-", color=FG, lw=.7, shrinkA=2, shrinkB=1), zorder=6)
    ax.plot([x0], [y0], "o", ms=3, color=FG, zorder=7)


note(-56, -32.8, -35, -38, "Uruguay: unaffiliated\nbecame the largest group")
note(172, -41.5, 120, -52, "New Zealand: the same")
cx_, cy_ = tr.transform(48, -32)
ax.text(cx_, cy_, f"China (violet) is\nhome to {w['china_share_of_none']:.0f}% of\nthe world's\nunaffiliated people", fontsize=10.5, color=FG, family=MONO, va="center", zorder=6)
cnt = {k: w["largest2020"].get(k, 0) for k in WK} if (WK := SITE["wk"]) else {}
LEGP = SERP.copy(); LEGP.set_size(13.5)
h = [Patch(fc=largest_col(k, 60), ec="none", label=f"{WNAME[k]} {cnt[k]}") for k in WK]
fig.legend(handles=h, loc="upper left", bbox_to_anchor=(.04, .512), ncol=4, frameon=False, prop=LEGP, handlelength=1.1, columnspacing=1.5, labelspacing=.5)
fig.text(.045, .452, "Number of countries and territories where each group is largest. Darker: a majority; lighter: largest but under half.", family=MONO, fontsize=10, color=MUT)

# big numbers
G = w["groups"]; rc = w["regions"]["christian"]
nums = [(f"{rc['Sub-Saharan Africa']['2020']:.1f}%", REL_COL["christian"], f"of the world's Christians\nlive in sub-Saharan Africa,\nup from {rc['Sub-Saharan Africa']['2010']:.1f}% in 2010;\nEurope {rc['Europe']['2020']:.1f}%"),
        (f"+{G['muslim']['growth_pct']:.1f}%", REL_COL["muslim"], f"growth in the number of\nMuslims, 2010 to 2020;\nworld population\n+{w['pop_growth_pct']:.1f}%"),
        (f"{u['scot']['none']:.1f}%", REL_COL["none"], f"of people in Scotland\nsaid no religion (2022);\nEngland and Wales\n{u['ew2021']['none']:.1f}%"),
        (f"{u['ew2021']['christian']:.1f}%", "#9A6A44", f"Christian in England and\nWales in 2021, down\nfrom {u['ew2011']['christian']:.1f}% in 2011")]
for i, (big, col, small) in enumerate(nums):
    x = .045 + i * .235
    fig.text(x, .432, big, fontproperties=DISP, fontsize=44, color=col, va="top")
    fig.text(x, .382, small, family=MONO, fontsize=11.5, color=FG, va="top", linespacing=1.45)

# panel 1: UK no religion
MS = jload(f"{DATA}/uk_msoa.json")["features"]; LAJ = jload(f"{DATA}/uk_la.json")["features"]
k0 = np.cos(np.radians(54.5)); UB = [10, 20, 30, 40, 50, 60]; UK = SITE["uk"]
ucol = lambda v: seq(v, "none", UB)


def polys(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for p in cs:
        a = np.array(p[0]); yield np.column_stack([a[:, 0] * k0, a[:, 1]])


a1 = fig.add_axes([.02, .07, .27, .19])
pat, col = [], []
for f in MS:
    p = f["properties"]; v = 100 * p["v"][UK.index("none")] / p["T"]
    for q in polys(f["geometry"]): pat.append(MPoly(q, closed=True)); col.append(ucol(v))
for f in LAJ:
    c = f["properties"]["c"]
    if c[0] in "SN":
        d = SITE["la"][c]; v = 100 * d["v"][UK.index("none")] / d["T"]
        for q in polys(f["geometry"]): pat.append(MPoly(q, closed=True)); col.append(ucol(v))
a1.add_collection(PatchCollection(pat, facecolors=col, edgecolors="none", lw=0))
a1.set_xlim(-8.3 * k0, 1.9 * k0); a1.set_ylim(49.85, 59.5); a1.set_aspect("equal"); a1.axis("off")
fig.text(.03, .265, "No religion, UK censuses", family=MONO, fontsize=12.5, color=FG, weight="medium")
for i, (lab, v) in enumerate([("under 10%", 5), ("10 to 30%", 20), ("30 to 50%", 40), ("50% and over", 55)]):

    fig.add_artist(Rectangle((.252, .182 - i * .022 - .006), .012, .012 * .8, fc=ucol(v), ec="none", transform=fig.transFigure))
    fig.text(.27, .182 - i * .022, lab, family=MONO, fontsize=9.5, color=FG, va="center")

# panel 2: age
A = u["age"]["England and Wales"]
a2 = fig.add_axes([.40, .09, .26, .155], facecolor=BGC)
for k in ("christian", "none", "muslim"):
    v = [x[k] for x in A]; a2.plot(range(len(A)), v, color=REL_COL[k], lw=2.4, marker="o", ms=4)
a2.text(6, A[6]["christian"] + 5, "Christian", color=REL_COL["christian"], ha="right", fontsize=10.5, family=MONO)
a2.text(2, A[2]["none"] + 5, "No religion", color=REL_COL["none"], ha="center", fontsize=10.5, family=MONO)
a2.text(0, A[0]["muslim"] + 5, "Muslim", color=REL_COL["muslim"], ha="left", fontsize=10.5, family=MONO)
a2.set_xticks(range(len(A))); a2.set_xticklabels(["<16", "16", "25", "35", "50", "65", "75+"], fontsize=9)
a2.set_ylim(0, 90); a2.set_yticks([0, 40, 80]); a2.set_yticklabels(["0%", "40%", "80%"], fontsize=9)
for s in ("top", "right"): a2.spines[s].set_visible(False)
fig.text(.385, .265, "By age, England and Wales 2021", family=MONO, fontsize=12.5, color=FG, weight="medium")

# panel 3: Christians by region
regs = sorted(rc, key=lambda r: -rc[r]["2020"])
RN = {"Sub-Saharan Africa": "Sub-Saharan Afr.", "Europe": "Europe", "Latin America-Caribbean": "Latin America", "Asia-Pacific": "Asia-Pacific", "North America": "North America", "Middle East-North Africa": "Mid. East, N. Afr."}
a3 = fig.add_axes([.84, .09, .13, .14], facecolor=BGC)
ys = np.arange(len(regs))[::-1]
for y, r in zip(ys, regs):
    a3.barh(y + .18, rc[r]["2010"], height=.3, color=REL_COL["christian"], alpha=.35)
    a3.barh(y - .14, rc[r]["2020"], height=.38, color=REL_COL["christian"])
a3.set_yticks(ys); a3.set_yticklabels([RN[r] for r in regs], fontsize=9.5); a3.set_xlim(0, 35)
a3.set_xticks([0, 15, 30]); a3.set_xticklabels(["0%", "15%", "30%"], fontsize=9)
for s in ("top", "right", "left"): a3.spines[s].set_visible(False)
a3.tick_params(left=False)
fig.text(.69, .265, "Share of the world's Christians", family=MONO, fontsize=12.5, color=FG, weight="medium")
fig.text(.69, .249, "pale 2010, solid 2020", family=MONO, fontsize=9.5, color=MUT)

fig.text(.045, .014, "Sources: Pew Research Center, Religious Composition 2010-2020 (Pew is not responsible for this analysis); censuses of England and Wales\n"
         "2011 and 2021 (ONS), Scotland 2022 (NRS), Northern Ireland 2021 (NISRA), Open Government Licence; Natural Earth; ONS boundaries.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib  ·  maps.tristanhotham.com/religion-map", family=MONO, fontsize=9.5, color=MUT, linespacing=1.5, va="bottom")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faith_on_the_map.png")
fig.savefig(out, facecolor=BGC, dpi=200)
print("ok", out)
