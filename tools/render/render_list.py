"""Render named .dc.html artboards to PNG. Usage: render_list.py <proj dir> <out dir> <fontsource dir> <blob dir|-> W H name [name...]"""
import re, sys, pathlib
from playwright.sync_api import sync_playwright

proj, out, fs = map(pathlib.Path, sys.argv[1:4]); blobs = sys.argv[4]
W, H = int(sys.argv[5]), int(sys.argv[6]); names = sys.argv[7:]
out.mkdir(parents=True, exist_ok=True)
css = "".join(f'<link rel="stylesheet" href="file://{fs}/{p}">' for p in [
    "noto-serif/700.css", "noto-serif/700-italic.css", "ibm-plex-sans/500.css", "ibm-plex-sans/600.css",
    "ibm-plex-sans/700.css", "jetbrains-mono/500.css", "jetbrains-mono/700.css"])
with sync_playwright() as p:
    b = p.chromium.launch()
    for name in names:
        src = (proj / f"{name}.dc.html").read_text()
        body = re.search(r"<x-dc>(.*)</x-dc>", src, re.S).group(1)
        body = re.sub(r"<link[^>]+fonts\.googleapis[^>]*>", "", body).replace("<helmet>", "").replace("</helmet>", "")
        if blobs != "-":
            body = re.sub(r"/_blob/([0-9a-f]{32})", lambda m: f"file://{blobs}/{m.group(1)}.png", body)
        tmp = out / f"{name}.tmp.html"
        tmp.write_text(f"<!doctype html><html><head><meta charset='utf-8'>{css}</head><body style='margin:0'>{body}</body></html>")
        pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto(f"file://{tmp}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(out / f"{name}.png")); pg.close(); tmp.unlink()
        print("ok", name)
    b.close()
