"""House style for static figures: fonts (a static Fraunces Black instance cut from the variable font, Source Serif 4,
IBM Plex Mono), colours, and Natural Earth outlines in the Equal Earth projection."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
import numpy as np
from pyproj import Transformer
from common import *

FONTS = "/home/claude/ref/fonts"
FD = os.path.join(SHM, "fonts")
os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    vf = TTFont(f"{FONTS}/FrauncesVar.ttf")
    loc = {a.axisTag: a.defaultValue for a in vf["fvar"].axes}
    loc.update({"wght": 900, "opsz": 144})
    loc = {k: v for k, v in loc.items() if k in ("wght", "opsz", "SOFT", "WONK")}
    if "SOFT" in loc: loc["SOFT"] = 0
    if "WONK" in loc: loc["WONK"] = 0
    instancer.instantiateVariableFont(vf, loc).save(f"{FD}/Fraunces-Black.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Regular.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Medium.ttf")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 11, "axes.edgecolor": "#676373", "axes.labelcolor": "#1F1D2B",
                     "xtick.color": "#676373", "ytick.color": "#676373", "svg.fonttype": "none"})
BG, FG, MUT, LAND, RULE = "#F7F4EE", "#1F1D2B", "#676373", "#E7E1D4", "#E0DACE"
DECR = "#9A6A44"
tr = Transformer.from_crs(4326, 8857, always_xy=True)
W = jload(f"{DATA}/world.json")
SITE = jload(f"{DATA}/site.json")


def rings(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        yield np.array(poly[0])


SHAPES = []
for f in W["features"]:
    ps = []
    for ring in rings(f["geometry"]):
        x, y = tr.transform(np.clip(ring[:, 0], -179.9, 179.9), ring[:, 1])
        ps.append(np.column_stack([x, y]))
    SHAPES.append((f["properties"]["iso"], ps))
WORLD_EXT = (-12.5e6, 15.6e6, -6.2e6, 8.4e6)


def world(ax, colour_of, lw=.35, extent=WORLD_EXT, ec="#FFFFFF", land=LAND):
    for iso, ps in SHAPES:
        c = colour_of(iso)
        for p in ps:
            ax.add_patch(MPoly(p, closed=True, fc=c or land, ec=ec, lw=lw))
    ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3]); ax.set_aspect("equal"); ax.axis("off")


def mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(A, B))


def pew(iso):
    c = SITE["iso2pew"].get(iso)
    return SITE["c"].get(c) if c else None


def largest(c, year="b"):
    i = int(np.argmax(c[year]))
    return SITE["wk"][i], c[year][i]


def largest_col(k, v):
    return mix("#EFE9DD", REL_COL[k], .95 if v >= 50 else .55)


WBINS = [1, 5, 10, 25, 50, 75, 90]


def seq(v, k, bins=WBINS):
    if v is None:
        return None
    i = -1
    for j, b in enumerate(bins):
        if v >= b:
            i = j
    return mix("#EFE9DD", REL_COL[k], .12 + .82 * (i + 1) / len(bins))


CB = [-15, -10, -5, -2, -0.5, 0.5, 2, 5, 10, 15]


def div(v, k):
    if v is None:
        return None
    i = sum(1 for b in CB if v >= b)
    if i == 5:
        return "#E4DED2"
    t = abs(i - 5) / 5
    return mix("#EFE9DD", REL_COL[k] if i > 5 else DECR, .25 + .72 * t)


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
