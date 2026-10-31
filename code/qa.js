// QA: open index.html at 1280 px and 390 px, record console errors, take screenshots of key states into qa/.
// Usage: node code/qa.js   (serves the repo root on a local port; web tiles and fonts are blocked offline and ignored;
// Leaflet is served from a local npm copy of the same version)
const { chromium } = require("playwright");
const http = require("http"), fs = require("fs"), path = require("path");
const PORT = +(process.env.QAPORT || 8791);
const ROOT = path.resolve(__dirname, ".."), OUT = path.join(ROOT, "qa");
const TYPES = { ".html": "text/html", ".json": "application/json", ".png": "image/png", ".js": "text/javascript" };
const srv = http.createServer((q, s) => { let p = decodeURIComponent(q.url.split("?")[0]); if (p.endsWith("/")) p += "index.html"; const f = path.join(ROOT, p);
  fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, { "Content-Type": TYPES[path.extname(f)] || "application/octet-stream" }); s.end(d); }); });
const SCEN = [
  ["world_largest", async pg => {}],
  ["world_none_change", async pg => { await pg.click('#relTabs .btn[data-r="none"]'); await pg.click('#measRow .btn[data-m="change"]'); }],
  ["world_popup", async pg => { await pg.evaluate(() => pickCountry("826", true)); }],
  ["world_rdi", async pg => { await pg.click('#relTabs .btn[data-r="rdi"]'); }],
  ["uk_none_msoa", async pg => { await pg.click('#viewRow .btn[data-v="uk"]'); await pg.waitForTimeout(1500); await pg.click('#relTabs .btn[data-r="none"]'); }],
  ["uk_largest", async pg => { await pg.click('#viewRow .btn[data-v="uk"]'); await pg.waitForTimeout(1500); }],
  ["uk_christian_change", async pg => { await pg.click('#viewRow .btn[data-v="uk"]'); await pg.waitForTimeout(1500); await pg.click('#relTabs .btn[data-r="christian"]'); await pg.click('#measRow .btn[data-m="change"]'); }],
  ["uk_london_muslim", async pg => { await pg.click('#viewRow .btn[data-v="uk"]'); await pg.waitForTimeout(1500); await pg.click('#relTabs .btn[data-r="muslim"]'); await pg.evaluate(() => map.fitBounds([[51.28, -0.52], [51.7, 0.33]])); }],
  ["uk_search_leicester", async pg => { await pg.fill("#q", "Leices"); await pg.waitForTimeout(500); await pg.screenshot({ path: `${OUT}/${pg._tag}_search_list.png` }); await pg.keyboard.press("Enter"); }],
  ["uk_ni_popup", async pg => { await pg.evaluate(() => pickLA("N09000003", true)); }],
  ["osm_den_usa", async pg => { await pg.evaluate(() => { LY.osm = true; LY.osmRel = "den"; syncLayers(); applyLayers(); }); await pg.waitForTimeout(1500); await pg.evaluate(() => map.fitBounds([[24, -125], [50, -66]])); }],
  ["osm_all_world", async pg => { await pg.evaluate(() => { LY.osm = true; LY.osmRel = "all"; LY.fill = false; syncLayers(); applyLayers(); }); }],
  ["layers_panel", async pg => { await pg.click(".lyrBtn"); }],
];
(async () => {
  await new Promise(r => srv.listen(PORT, r));
  const b = await chromium.launch();
  const errs = [];
  for (const [w, h, tag] of [[1280, 900, "desk"], [390, 844, "phone"]]) {
    const open = async () => {
      const pg = await b.newPage({ viewport: { width: w, height: h } }); pg._tag = tag;
      pg.on("console", m => { if (m.type() === "error" && !/Failed to load resource|ERR_|net::/.test(m.text())) errs.push(`${tag}: ${m.text()}`); });
      pg.on("pageerror", e => errs.push(`${tag} pageerror: ${e.message}`));
      await pg.route(/arcgisonline|googleapis|gstatic/, r => r.abort());
      await pg.route(/leaflet.min.js/, r => r.fulfill({ path: require.resolve("leaflet/dist/leaflet.js") }));
      await pg.route(/leaflet.min.css/, r => r.fulfill({ path: require.resolve("leaflet/dist/leaflet.css") }));
      await pg.addInitScript(() => { try { localStorage.clear(); } catch (e) {} });
      await pg.goto(`http://localhost:${PORT}/index.html`, { waitUntil: "networkidle" });
      await pg.waitForTimeout(600); return pg;
    };
    let pg = await open();
    const ov = await pg.evaluate(() => document.documentElement.scrollWidth - innerWidth);
    if (ov > 0) errs.push(`${tag}: horizontal overflow ${ov}px`);
    if (!(await pg.$(".mfs-btn"))) errs.push(`${tag}: no full-screen button`);
    await pg.screenshot({ path: `${OUT}/${tag}_top.png` });
    for (const id of ["globChart", "regChart", "noneChart", "rdiChart", "denChart", "densChart", "nationChart", "ewChart", "ageChart", "niChart", "cards"]) {
      const e = await pg.$("#" + id); await e.scrollIntoViewIfNeeded(); await pg.waitForTimeout(150); await e.screenshot({ path: `${OUT}/${tag}_chart_${id}.png` });
    }
    await pg.click("#theme"); await pg.waitForTimeout(500); await pg.evaluate(() => window.scrollTo(0, 0)); await pg.screenshot({ path: `${OUT}/${tag}_dark_top.png` });
    await (await pg.$("#atlas")).screenshot({ path: `${OUT}/${tag}_dark_map.png` });
    await pg.close();
    for (const [name, fn] of SCEN) {
      pg = await open();
      try { await (await pg.$("#atlas")).scrollIntoViewIfNeeded(); await fn(pg); await pg.waitForTimeout(1800); await (await pg.$("#atlas")).screenshot({ path: `${OUT}/${tag}_${name}.png` }); }
      catch (e) { errs.push(`${tag} ${name}: ${e.message.split("\n")[0]}`); }
      await pg.close();
    }
  }
  await b.close(); srv.close();
  console.log(errs.length ? errs.join("\n") : "no console errors");
})();
