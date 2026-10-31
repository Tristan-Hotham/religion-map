# Faith on the map: religion around the world and across the UK

An interactive map and data study of religious affiliation: the religious make-up of 201 countries and territories in 2010 and 2020 (Pew Research Center estimates), the censuses of the four UK nations harmonised down to 7,264 neighbourhoods in England and Wales, a Northern Ireland series from 1861 to 2021, and 1,624,818 places of worship mapped in OpenStreetMap.

Interactive page: https://maps.tristanhotham.com/religion-map/
Paper: https://doi.org/10.5281/zenodo.23842991
Blog post: https://blog.tristanhotham.com/2026/10/31/religion-map/

## Headline results

- World, 2010 to 2020: the population grew by 12.3%; Muslims by 20.7% (347 million), the religiously unaffiliated by 16.5%, Christians by 5.7%; Buddhists fell by 5.4%. The Christian share of the world fell from 30.6% to 28.8%.
- Sub-Saharan Africa's share of the world's Christians rose from 24.8% to 30.7%, overtaking Europe (25.8% to 22.3%).
- The unaffiliated share rose in 103 countries, most in Australia (+17.5 points); by 2020 Uruguay and New Zealand had more unaffiliated people than Christians.
- England and Wales: Christian 59.3% (2011) to 46.2% (2021); no religion 25.1% to 37.2%. Wales 46.5% no religion, Scotland 51.1% (a majority), Northern Ireland 79.7% Christian. No religion is the most common answer in 75 of 361 UK local authorities.
- Age: 76.7% of people aged 75 and over in England and Wales are Christian; 50.6% of 25 to 34 year olds have no religion.
- Northern Ireland: Catholics have outnumbered the Presbyterian, Church of Ireland and Methodist churches combined since 2001 (42.3% against 30.5% in 2021).
- OpenStreetMap: 77.5 mapped places of worship per 100,000 people in North America, 7.1 in sub-Saharan Africa: a map of mapping as much as of worship.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; `data/uk_la.json`, `data/uk_msoa.json` and `data/osm_cells.json` are loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/world_religion.csv` | Pew estimates by country, region and world, 2010 and 2020: shares, rounded counts, largest group, diversity index. |
| `data/uk_local_authorities.csv` | 361 UK local authorities (2023 boundaries): harmonised religion counts and shares, with 2011 counts for England and Wales. |
| `data/ew_msoa_2021.csv` | 7,264 MSOAs in England and Wales, 2021: counts and shares (0.9 MB). |
| `data/ni_religion_1861_2021.csv` | Northern Ireland by religion at every census, 1861 to 2021. |
| `data/osm_places_of_worship_by_country.csv` | OpenStreetMap places of worship by country, religion and Christian denomination family (ODbL). |
| `data/osm_cells.json` | Places of worship per quarter degree square by religion, with the main tagged Christian denomination (ODbL; 2.5 MB). |
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

Needs Python 3 with pandas, shapely, pyproj, openpyxl, matplotlib, fontTools and Pillow; xelatex and pdftotext; node with Playwright and Leaflet 1.9.4 for `qa.js`. Raw inputs, retrieved in 2026, are read in place from the paths in `code/common.py` (Pew dataset folder, UK census CSV and XLSX files, the OpenStreetMap count file, Natural Earth and ONS boundaries). Intermediate files go to `/dev/shm/religion/work` (set `RELTMP` to change).

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

Hotham, T. (2026) Faith on the map: religion around the world and across the UK, from Pew Research Center estimates, the UK censuses and OpenStreetMap. Zenodo. https://doi.org/10.5281/zenodo.23842991

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
