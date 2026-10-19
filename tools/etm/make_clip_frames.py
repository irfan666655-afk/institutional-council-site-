"""Render frames/end cards for clips.json and write per-clip spec files. Usage: make_clip_frames.py <fontsource> <doc dir>"""
import sys, json, pathlib, urllib.parse
from playwright.sync_api import sync_playwright
fs, D = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
fonts = "".join(f'<link rel="stylesheet" href="file://{fs}/{p}">' for p in
                ["noto-serif/700.css", "ibm-plex-sans/500.css", "ibm-plex-sans/700.css", "jetbrains-mono/700.css"])
page = D / "frame_page.html"; page.write_text((D / "frame.html").read_text().replace("__FONTS__", fonts))
clips = json.load(open(D / "clips.json")); (D / "specs").mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    for c in clips:
        jobs = [(f"cframe_{c['name']}.png", dict(kind="frame", ep=0, of=12, part=c["part"], hook=c["hook"], wy=700, wh=457, tag=c.get("tag","CLIP"), foot=c.get("foot")), False),
                (f"cend_{c['name']}.png", dict(kind="end", y=1170, h=320, **c["end"]), True)]
        for name, cfg, tr in jobs:
            pg.goto(f"file://{page}?n={name}#" + urllib.parse.quote(json.dumps(cfg))); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(250)
            pg.locator("#st").screenshot(path=str(D / "frames" / name), omit_background=tr)
        json.dump({"name": c["name"], "segments": c["segments"], "tail": c["tail"],
                   "frame": f"frames/cframe_{c['name']}.png", "end": f"frames/cend_{c['name']}.png"}, open(D / "specs" / f"{c['name']}.json", "w"))
    b.close()
print("ok", len(clips))
