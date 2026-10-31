"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
Placeholders left for the publisher: {{DOI}}, {{DOI_URL}}, https://blog.tristanhotham.com/2026/10/31/religion-map/."""
import re, zipfile
from common import *
import checks  # noqa: F401

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json")
RELD = os.path.join(ROOT, "release")
NAME = "Hotham_Faith_on_the_Map"


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    raise ValueError(f)


# numbers in blog alt text, checked against the data
w, u = R["world"], R["uk"]
rc = w["regions"]["christian"]
assert (rc["Sub-Saharan Africa"]["2010"], rc["Sub-Saharan Africa"]["2020"], rc["Europe"]["2010"], rc["Europe"]["2020"]) == (24.8, 30.7, 25.8, 22.3)
assert (rc["Latin America-Caribbean"]["2010"], rc["Latin America-Caribbean"]["2020"], rc["Asia-Pacific"]["2020"], rc["North America"]["2010"], rc["North America"]["2020"]) == (24.7, 24.1, 11.8, 12.4, 10.5)
A = {a["band"]: a for a in u["age"]["England and Wales"]}
assert 31 <= A["16-24"]["christian"] < 32 and 31 <= A["25-34"]["christian"] < 32 and round(A["75+"]["christian"]) == 77
assert round(A["25-34"]["none"]) == 51 and round(A["75+"]["none"]) == 14 and round(A["Under 16"]["muslim"]) == 11 and round(A["75+"]["muslim"]) == 1
h = u["ni_h"]
assert (round(h["prot1861"]), round(h["prot_peak"]), h["prot_peak_year"], round(h["prot2021"]), round(h["cath_min"]), round(h["cath2021"]), round(h["nons2021"])) == (58, 62, 1926, 30, 28, 42, 19)
CH = {c["n"]: c["b"][2] - c["a"][2] for c in SITE["c"].values()}
assert all(CH[n] > 10 for n in ("Australia", "United States", "Canada", "Chile", "Uruguay")) and 0 < CH["China"] < 5
assert all(CH[n] < -2 for n in ("Mozambique", "Ghana", "Ivory Coast"))
assert 1.6e6 <= R["osm"]["total"] < 1.65e6

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG|DOI_URL)([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
for img in used:
    assert os.path.exists(f"{RELD}/blog/{img}"), img
for fn in os.listdir(f"{RELD}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{RELD}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{RELD}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Faith on the map: religion around the world and across the UK",
        "slug": "religion-map",
        "excerpt": f"Christianity's centre has moved to sub-Saharan Africa, the unaffiliated are growing fast, and in Scotland {u['scot']['none']:.1f}% now say they have no religion. A map of religion in {w['n_countries']} countries, every UK neighbourhood and {R['osm']['total']:,} places of worship.",
        "seo_description": "An interactive map of religion around the world and across the UK, from Pew Research Center estimates, the UK censuses and OpenStreetMap.",
        "tags": ["religion", "census", "no religion", "Christianity", "Islam", "Northern Ireland", "maps", "data visualisation", "OpenStreetMap"],
        "header_alt": f"Title card reading 'Faith on the map' in black and blue on cream, beside a world map coloured by each country's largest religious group in 2020: Christians in blue, Muslims in green, the unaffiliated in violet, Hindus in orange and Buddhists in maroon. Text: the largest religious group in {w['n_countries']} countries and territories, and religion in every UK neighbourhood; Scotland {u['scot']['none']:.1f}% no religion."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{RELD}/blog/meta.json", indent=2)

# Zenodo
Z = f"{RELD}/zenodo"; os.makedirs(Z, exist_ok=True)


def link(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    os.link(src, dst)


link(f"{RELD}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/religion-map_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"religion-map/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        z.write(os.path.join(ROOT, fn), f"religion-map/{fn}")
tex = open(f"{RELD}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\emph{", "").replace("}", "").replace("\\&", "&")
zmeta = {"title": "Faith on the Map: Religion Around the World and Across the UK, from Pew Research Center Estimates, the UK Censuses and OpenStreetMap",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: https://maps.tristanhotham.com/religion-map/. Data and code: https://github.com/Tristan-Hotham/religion-map. Pew Research Center data are used with attribution; Pew Research Center is not responsible for the analyses or interpretations presented here.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["religion", "religious affiliation", "census", "no religion", "Christianity", "Islam", "Northern Ireland", "OpenStreetMap", "places of worship", "maps"],
         "license": "cc-by-4.0",
         "related_identifiers": [{"identifier": "https://github.com/Tristan-Hotham/religion-map", "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": "https://maps.tristanhotham.com/religion-map/", "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.pewresearch.org/religion/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.nomisweb.co.uk/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.scotlandscensus.gov.uk/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.nisra.gov.uk/statistics/census", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.openstreetmap.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": [f"{NAME}.pdf", "religion-map_data_and_code.zip"]}
jsave(zmeta, f"{Z}/metadata.json", indent=2)
import json as _json
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in s and "\u2013" not in s and "--" not in s
print("blog words", words, "; zenodo files", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
