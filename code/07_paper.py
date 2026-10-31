"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/Hotham_Faith_on_the_Map.pdf and .tex (figures f_*.png alongside)."""
import re, subprocess
from common import *
import checks  # noqa: F401

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Faith_on_the_Map"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def fmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "absf1": return f"{abs(float(v)):.1f}"
    return tex(str(v))


w, u, o = R["world"], R["uk"], R["osm"]
TS = ("\\begin{table}[tbp]\\centering\\small\\caption{Sources, what was used and licences.}\\label{tab:sources}"
      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{3.4cm}>{\\raggedright\\arraybackslash}p{7.2cm}>{\\raggedright\\arraybackslash}p{3.6cm}}\\toprule Source & Used & Licence\\\\\\midrule\n"
      f"Pew Research Center & Religious composition of {w['n_countries']} countries and territories, 2010 and 2020; diversity index & Reuse with attribution\\\\\n"
      f"ONS census 2021 and 2011 & Religion for {u['msoa']['n']:,} MSOAs and {u['la']['ew_n']} councils (TS030, TS031, RM118, KS209EW) & Open Government Licence v3.0\\\\\n"
      f"NRS census 2022 & Religion for Scotland, 32 council areas and {u['scot_iz']['n']:,} intermediate zones (UV205) & Open Government Licence v3.0\\\\\n"
      f"NISRA census 2021 & Religion, religion brought up in and religion 1861 to 2021 (MS-B19, MS-B23, MS-B22) & Open Government Licence v3.0\\\\\n"
      f"OpenStreetMap & {o['total']:,} places of worship counted in {o['n_cells']:,} quarter degree squares & ODbL 1.0\\\\\n"
      "Natural Earth; ONS boundaries & Country, MSOA and council outlines & Public domain; OGL v3.0\\\\\n"
      "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
N = [("England", u["eng2021"]), ("Wales", u["wal2021"]), ("Scotland", u["scot"]), ("N. Ireland", u["ni"]), ("E and W 2011", u["ew2011"])]
for k in UKEYS:
    rows += f"{UNAME[k]} & " + " & ".join("n/a" if s[k] is None else f"{s[k]:.1f}" for _, s in N) + "\\\\\n"
TU = ("\\begin{table}[tbp]\\centering\\small\\caption{Religion in the UK nations, per cent of usual residents. England and Wales 2021, Scotland 2022, Northern Ireland 2021 (n/a: within other religion), and England and Wales 2011.}\\label{tab:uk}"
      "\\begin{tabular}{lrrrrr}\\toprule & England & Wales & Scotland & N. Ireland & E and W 2011\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = re.sub(r"\{\{(?!TABLE_|DOI)([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3) or "raw"), t)
t = t.replace("{{TABLE_SOURCES}}", TS).replace("{{TABLE_UK}}", TU)
assert "--" not in t and "—" not in t and "–" not in t
assert set(re.findall(r"\{\{[^}]*\}\}", t)) <= {"{{DOI}}"}, re.findall(r"\{\{[^}]*\}\}", t)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("—") + txt.count("–") + txt.count("--"))
