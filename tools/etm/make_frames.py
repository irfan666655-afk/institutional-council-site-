"""Render per-episode frame PNGs and end-card overlays. Usage: make_frames.py <fontsource> <outdir>"""
import sys, json, pathlib, urllib.parse
from playwright.sync_api import sync_playwright
here = pathlib.Path(__file__).parent
fs, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
fonts = "".join(f'<link rel="stylesheet" href="file://{fs}/{p}">' for p in
                ["noto-serif/700.css", "ibm-plex-sans/500.css", "ibm-plex-sans/700.css", "jetbrains-mono/700.css"])
page = here / "frame_page.html"; page.write_text((here / "frame.html").read_text().replace("__FONTS__", fonts))
EPS = json.load(open(here / "episodes.json")); N = len(EPS)
WY, WH, CY, CH = 700, 457, 1170, 320
jobs = []
for e in EPS:
    jobs.append((f"frame_{e['ep']:02d}.png", dict(kind="frame", ep=e["ep"], of=N, part=e["part"], hook=e["hook"], wy=WY, wh=WH), False))
    if e["ep"] < N:
        nx = EPS[e["ep"]]
        card = dict(kind="end", y=CY, h=CH, k=f"AGLA EPISODE · EP {nx['ep']:02d}/{N}", t=nx["title"], p="KAL SHAAM 7 BAJE · FOLLOW KAREIN")
    else:
        card = dict(kind="end", y=CY, h=CH, k="FILE CLOSED · 12/12", t="Poori film ek saath: <span class='g'>link in bio</span>", p="SAVE KAREIN · SHARE KAREIN")
    jobs.append((f"end_{e['ep']:02d}.png", card, True))
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    for name, cfg, transparent in jobs:
        pg.goto(f"file://{page}?n={name}#" + urllib.parse.quote(json.dumps(cfg)))
        pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(250)
        pg.locator("#st").screenshot(path=str(out / name), omit_background=transparent)
    b.close()
print("frames", len(jobs))
