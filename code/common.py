"""Shared paths and helpers for the religion-map project.

Raw inputs (read in place, never modified), all retrieved in 2026:
- PEW: Pew Research Center, 'Religious Composition 2010-2020' dataset (June 2025, diversity statistics added 2026):
  percentages, rounded and unrounded counts, diversity statistics, by country and region, 2010 and 2020.
- REL: UK censuses.
  England and Wales 2021 (ONS via Nomis): ts030_msoa.csv, ts030_ltla23.csv, ts030_region_country.csv,
  ts031_ltla23.csv (detailed religion), rm118_country.csv (religion by age); 2011: ks209_lad2011.csv, ks209_country.csv.
  Scotland 2022 (NRS table UV205 via UK Data Service SuperWEB2): scot_uv205_ctry.csv, scot_uv205_ca2019.csv, scot_uv205_iz2011.csv.
  Northern Ireland 2021 (NISRA): ni_ms_b19_religion.xlsx, ni_ms_b23_religion_brought_up.xlsx, ni_ms_b22_religion_1861_2021.xlsx.
  OpenStreetMap places of worship: osm_places_of_worship_grid025.tsv (amenity=place_of_worship counted per 0.25 degree
  cell by religion and denomination tags, via QLever osm-planet).
- GEO: Natural Earth countries (1:50m) and populated places (1:10m); ONS/OS boundaries for MSOAs 2021 and local
  authority districts December 2023 (super generalised).
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAWD = "/home/claude/newdata/raw"
PEW = f"{RAWD}/pew/Religious Composition 2010-2020 dataset"
REL = f"{RAWD}/rel"
GEO = f"{RAWD}/geo"
DATA = os.path.join(ROOT, "data")
SHM = os.environ.get("RELTMP", "/dev/shm/religion")
WORK = os.path.join(SHM, "work")       # intermediates live in memory, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

DOI = "{{DOI}}"
SLUG = "religion-map"
PAGE = "https://maps.tristanhotham.com/religion-map/"
REPO = "https://github.com/Tristan-Hotham/religion-map"
BLOG = "https://blog.tristanhotham.com/2026/10/31/religion-map/"
RETRIEVED = "2026"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

# Harmonised religion groups. World (Pew): christian, muslim, none (religiously unaffiliated), hindu, buddhist, jewish, other.
# UK censuses add sikh and notstated; Sikhs are within 'other religions' in Pew.
REL_COL = {"christian": "#3B5BA9", "muslim": "#2E8B57", "none": "#5B4A8B", "hindu": "#E3672B", "buddhist": "#8E2A4A",
           "jewish": "#3F9FD6", "sikh": "#D4A21A", "other": "#B07AA1", "notstated": "#BDB6AA"}
WNAME = {"christian": "Christians", "muslim": "Muslims", "none": "Religiously unaffiliated", "hindu": "Hindus",
         "buddhist": "Buddhists", "jewish": "Jews", "other": "Other religions"}
UNAME = {"christian": "Christian", "none": "No religion", "muslim": "Muslim", "hindu": "Hindu", "sikh": "Sikh",
         "jewish": "Jewish", "buddhist": "Buddhist", "other": "Other religion", "notstated": "Not stated"}
WKEYS = ["christian", "muslim", "none", "hindu", "buddhist", "jewish", "other"]
UKEYS = ["christian", "none", "muslim", "hindu", "sikh", "jewish", "buddhist", "other", "notstated"]


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nodash(v):
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [nodash(x) for x in v]
    if isinstance(v, dict):
        return {k: nodash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = nodash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def r1(x):
    return round(float(x), 1)


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v
