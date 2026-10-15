"""Render Design-canvas .dc.html artboards to PNG at their exact size."""
import json, re, sys, pathlib
from playwright.sync_api import sync_playwright

proj = pathlib.Path(sys.argv[1])          # folder holding canvas.json + *.dc.html
out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
fs = pathlib.Path(sys.argv[3])            # node_modules/@fontsource
canvas = json.loads((proj / "canvas.json").read_text())

css = "".join(
    f'<link rel="stylesheet" href="file://{fs}/{p}">'
    for p in ["noto-serif/700.css", "noto-serif/700-italic.css",
              "ibm-plex-sans/500.css", "ibm-plex-sans/600.css", "ibm-plex-sans/700.css",
              "jetbrains-mono/500.css", "jetbrains-mono/700.css"])

with sync_playwright() as p:
    b = p.chromium.launch()
    for name in canvas["order"]:
        box = canvas["boards"][name]
        src = (proj / name).read_text()
        body = re.search(r"<x-dc>(.*)</x-dc>", src, re.S).group(1)
        body = re.sub(r"<link[^>]+fonts\.googleapis[^>]*>", "", body)
        body = body.replace("<helmet>", "").replace("</helmet>", "")
        html = f"<!doctype html><html><head><meta charset='utf-8'>{css}</head><body style='margin:0'>{body}</body></html>"
        tmp = out / (name + ".tmp.html"); tmp.write_text(html)
        pg = b.new_page(viewport={"width": box["w"], "height": box["h"]})
        pg.goto(f"file://{tmp}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(out / name.replace(".dc.html", ".png")))
        pg.close(); tmp.unlink()
        print("ok", name)
    b.close()
