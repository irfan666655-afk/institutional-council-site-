"""Escape the Matrix launch stories. Usage: make_stories4.py <fontsource> <outdir> <episodes.json>"""
import sys, json, pathlib, urllib.parse
from playwright.sync_api import sync_playwright
here = pathlib.Path(__file__).parent
fs, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
EPS = json.load(open(sys.argv[3]))
fonts = "".join(f'<link rel="stylesheet" href="file://{fs}/{p}">' for p in ["noto-serif/700.css","ibm-plex-sans/500.css","ibm-plex-sans/700.css","jetbrains-mono/700.css"])
page = here / "story4_page.html"; page.write_text((here / "story4.html").read_text().replace("__FONTS__", fonts))
G = '<span class="g">{}</span>'
C = {
 "etm-cd-trailer": dict(part=0, kicker="ESCAPE THE MATRIX · OFFICIAL TRAILER", big="TRAILER", q="Trailer grid par hai. Premiere: " + G.format("Itwar, 7 PM"), e="Turn on post notifications.", pill="REEL DEKHO ↓"),
 "etm-cd-2din": dict(part=0, kicker="ESCAPE THE MATRIX · PREMIERE", big="2 DIN", q="Ek tola. Ek trunk. " + G.format("5,000 saal") + " ki kahani.", e="Premiere: Sunday 1 November, 7 PM PKT", pill="ITWAR · SHAAM 7 BAJE"),
 "etm-cd-kal": dict(part=0, kicker="ESCAPE THE MATRIX · PREMIERE", big="KAL", q="Kal shaam 7 baje: " + G.format("Episode 1") + ".", e="12 episodes. One every evening.", pill="NOTIFICATIONS ON KAREIN"),
 "etm-cd-aaj": dict(part=1, kicker="ESCAPE THE MATRIX · PREMIERE", big="AAJ", q="Aaj shaam 7 baje " + G.format("Escape the Matrix") + " shuru.", e="Episode 1: The Trunk.", pill="AAJ SHAAM 7 BAJE"),
}
for e in EPS:
    C[f"etm-live-{e['ep']:02d}"] = dict(part=e["ep"], kicker=f"EP {e['ep']:02d}/12 · LIVE NOW", big=e["title"].upper() if len(e["title"]) < 12 else f"EP {e['ep']:02d}",
        q=e["hook"].replace("class='g'", 'class="g"'), e="Missed one? Every episode is on the grid.", pill="REEL DEKHO ↓", qs=62)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    for name, c in C.items():
        pg.goto(f"file://{page}?n={name}#" + urllib.parse.quote(json.dumps(c))); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(out / f"{name}.png"))
    b.close()
print("stories", len(C))
