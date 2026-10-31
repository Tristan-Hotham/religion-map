"""README.md and LICENSE, numbers from data/results.json."""
from common import *
import checks  # noqa: F401

R = jload(f"{DATA}/results.json")
w, u, o = R["world"], R["uk"], R["osm"]
G = w["groups"]
size = lambda f: f"{os.path.getsize(os.path.join(DATA, f)) / 1e6:.1f} MB"
readme = f"""# Faith on the map: religion around the world and across the UK

An interactive map and data study of religious affiliation: the religious make-up of {w['n_countries']} countries and territories in 2010 and 2020 (Pew Research Center estimates), the censuses of the four UK nations harmonised down to {u['msoa']['n']:,} neighbourhoods in England and Wales, a Northern Ireland series from 1861 to 2021, and {o['total']:,} places of worship mapped in OpenStreetMap.

Interactive page: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}

## Headline results

- World, 2010 to 2020: the population grew by {w['pop_growth_pct']:.1f}%; Muslims by {G['muslim']['growth_pct']:.1f}% ({G['muslim']['change_m']:,} million), the religiously unaffiliated by {G['none']['growth_pct']:.1f}%, Christians by {G['christian']['growth_pct']:.1f}%; Buddhists fell by {abs(G['buddhist']['growth_pct']):.1f}%. The Christian share of the world fell from {G['christian']['pct2010']:.1f}% to {G['christian']['pct2020']:.1f}%.
- Sub-Saharan Africa's share of the world's Christians rose from {w['regions']['christian']['Sub-Saharan Africa']['2010']:.1f}% to {w['regions']['christian']['Sub-Saharan Africa']['2020']:.1f}%, overtaking Europe ({w['regions']['christian']['Europe']['2010']:.1f}% to {w['regions']['christian']['Europe']['2020']:.1f}%).
- The unaffiliated share rose in {w['none_up_n']} countries, most in {w['top_change']['none']['rise'][0]['name']} (+{w['top_change']['none']['rise'][0]['pp']:.1f} points); by 2020 Uruguay and New Zealand had more unaffiliated people than Christians.
- England and Wales: Christian {u['ew2011']['christian']:.1f}% (2011) to {u['ew2021']['christian']:.1f}% (2021); no religion {u['ew2011']['none']:.1f}% to {u['ew2021']['none']:.1f}%. Wales {u['wal2021']['none']:.1f}% no religion, Scotland {u['scot']['none']:.1f}% (a majority), Northern Ireland {u['ni']['christian']:.1f}% Christian. No religion is the most common answer in {u['la']['largest']['none']} of {u['la']['n']} UK local authorities.
- Age: {u['age']['England and Wales'][6]['christian']:.1f}% of people aged 75 and over in England and Wales are Christian; {u['age']['England and Wales'][2]['none']:.1f}% of 25 to 34 year olds have no religion.
- Northern Ireland: Catholics have outnumbered the Presbyterian, Church of Ireland and Methodist churches combined since {u['ni_h']['cross_year']} ({u['ni_h']['cath2021']:.1f}% against {u['ni_h']['prot2021']:.1f}% in 2021).
- OpenStreetMap: {o['region']['North America']['per100k']:.1f} mapped places of worship per 100,000 people in North America, {o['region']['Sub-Saharan Africa']['per100k']:.1f} in sub-Saharan Africa: a map of mapping as much as of worship.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; `data/uk_la.json`, `data/uk_msoa.json` and `data/osm_cells.json` are loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/world_religion.csv` | Pew estimates by country, region and world, 2010 and 2020: shares, rounded counts, largest group, diversity index. |
| `data/uk_local_authorities.csv` | {u['la']['n']} UK local authorities (2023 boundaries): harmonised religion counts and shares, with 2011 counts for England and Wales. |
| `data/ew_msoa_2021.csv` | {u['msoa']['n']:,} MSOAs in England and Wales, 2021: counts and shares ({size('ew_msoa_2021.csv')}). |
| `data/ni_religion_1861_2021.csv` | Northern Ireland by religion at every census, 1861 to 2021. |
| `data/osm_places_of_worship_by_country.csv` | OpenStreetMap places of worship by country, religion and Christian denomination family (ODbL). |
| `data/osm_cells.json` | Places of worship per quarter degree square by religion, with the main tagged Christian denomination (ODbL; {size('osm_cells.json')}). |
| `data/results.json` | Every number used in the page, paper, blog, collage and post. |
| `data/site.json`, `data/world.json`, `data/cities.json`, `data/uk_la.json`, `data/uk_msoa.json` | Page data and outlines. |
| `code/` | Scripts, run in order (below), page, paper and blog templates, `checks.py` (asserts for every fact stated in words) and `qa.js` (browser checks). |
| `release/` | Paper PDF and LaTeX source with figures, blog post, figures and meta, Zenodo files and metadata. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- World: Pew's published percentages and rounded counts for seven groups, joined to Natural Earth outlines by UN country code. Largest group = highest share; majority = over 50%.
- UK: census answers grouped as no religion, Christian, Muslim, Hindu, Sikh, Jewish, Buddhist, other religion and not stated, as shares of all usual residents. Scotland's Church of Scotland, Roman Catholic and other Christian are added together; Pagan is in other religion. Northern Ireland's tables do not separate non-Christian faiths. 2011 districts are added up to the councils of 2023. The question is voluntary and worded differently in each nation.
- Age: RM118 age bands were unlabelled in the download and were identified from their population totals.
- Places of worship: amenity=place_of_worship counted per quarter degree square by religion and denomination tags; denominations grouped into families; squares assigned to countries by their centre.
- Caveats: affiliation is not belief or practice; Pew's figures are estimates; question wording differs; OpenStreetMap coverage is very uneven. The study describes and does not rank or judge any religion or none.

## How to rerun

Needs Python 3 with pandas, shapely, pyproj, openpyxl, matplotlib, fontTools and Pillow; xelatex and pdftotext; node with Playwright and Leaflet 1.9.4 for `qa.js`. Raw inputs, retrieved on {R['meta']['retrieved']}, are read in place from the paths in `code/common.py` (Pew dataset folder, UK census CSV and XLSX files, the OpenStreetMap count file, Natural Earth and ONS boundaries). Intermediate files go to `/dev/shm/religion/work` (set `RELTMP` to change).

```
python3 code/01_world.py        # Pew estimates, world outlines, place names
python3 code/02_uk.py           # UK censuses harmonised, UK outlines
python3 code/03_osm.py          # OpenStreetMap places of worship
python3 code/04_results.py      # results.json and page data
python3 code/05_build_site.py   # index.html
python3 code/06_figures.py      # header, blog and paper figures
python3 code/07_paper.py        # paper PDF
python3 code/08_readme.py       # README and LICENSE
python3 code/09_release.py      # blog post, Zenodo files
python3 reddit/collage.py       # collage
node code/qa.js                 # screenshots and console check
```

## Sources and licences

- Pew Research Center (2025), 'How the Global Religious Landscape Changed From 2010 to 2020', dataset 'Religious Composition 2010-2020' with diversity statistics (2026). Used with attribution; Pew Research Center bears no responsibility for the analyses or interpretations of the data presented here. `data/world_religion.csv` repackages Pew's published figures with this attribution; the original dataset is available from Pew Research Center.
- Office for National Statistics, Census 2021 and 2011, via Nomis. Open Government Licence v3.0.
- National Records of Scotland, Scotland's Census 2022, table UV205, via the UK Data Service. Open Government Licence v3.0.
- Northern Ireland Statistics and Research Agency, Census 2021, tables MS-B19, MS-B22, MS-B23. Open Government Licence v3.0.
- OpenStreetMap contributors (https://www.openstreetmap.org/copyright), via QLever. ODbL 1.0.
- ONS boundaries (MSOA 2021, local authority districts December 2023), Open Government Licence v3.0, contains OS data © Crown copyright and database right; Natural Earth (public domain).
- Base map tiles on the page: © Esri.

## Citation

Hotham, T. (2026) Faith on the map: religion around the world and across the UK, from Pew Research Center estimates, the UK censuses and OpenStreetMap. Zenodo. https://doi.org/{DOI}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in readme.replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, the figures and the derived data files in data/ are
released under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), with
these exceptions and conditions:
- data/osm_cells.json and data/osm_places_of_worship_by_country.csv are derived
  from OpenStreetMap and are made available under the Open Database Licence 1.0
  (c) OpenStreetMap contributors.
- UK census data (ONS, NRS, NISRA) contain public sector information licensed
  under the Open Government Licence v3.0; boundaries contain OS data (c) Crown
  copyright and database right.
- Figures derived from Pew Research Center's 'Religious Composition 2010-2020'
  dataset are reused with attribution to Pew Research Center, which bears no
  responsibility for the analyses or interpretations presented here.
- Natural Earth data are in the public domain.
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
print("README", len(readme.split()), "words")
