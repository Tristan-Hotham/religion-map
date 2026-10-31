"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; facts stated in words are checked by the asserts in checks.py. Page data (site.json, world.json,
place names) are embedded; data/uk_la.json, data/uk_msoa.json and data/osm_cells.json are loaded by the page.
The full-screen map snippet (code/fullscreen_snippet.html) is pasted before </body>."""
import json, re
from common import *
import checks  # noqa: F401  (runs the word-fact asserts)

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")


def fmt(v, f):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "absf1": return f"{abs(float(v)):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    if f == "bn": return f"{float(v) / 1e9:.2f}"
    raise ValueError(f)


TOKEN = re.compile(r"\{\{(?!DOI|BLOG_URL)([^}|]+)(\|(\w+))?\}\}")


def fill(tpl):
    return TOKEN.sub(lambda m: fmt(get(R, m.group(1)), m.group(3)), tpl)


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = fill(tpl)
    left = re.findall(r"\{\{[^}]*\}\}", html)
    assert set(left) <= {"{{DOI}}", "https://blog.tristanhotham.com/2026/10/31/religion-map/"}, left
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{"name": x["name"], "lat": x["lat"], "lon": x["lon"], "pop": x["pop"]} for x in jload(f"{DATA}/cities.json")]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
