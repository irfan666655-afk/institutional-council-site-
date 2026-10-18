"""Render the series story cards (morning teaser + evening 'live now') to PNG. Usage: make_stories3.py <fontsource> <outdir>"""
import sys, json, pathlib, urllib.parse
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
fs, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
fonts = "".join(f'<link rel="stylesheet" href="file://{fs}/{p}">' for p in
                ["noto-serif/700.css", "ibm-plex-sans/500.css", "ibm-plex-sans/700.css", "jetbrains-mono/700.css"])
page = here / "story3_page.html"
page.write_text((here / "story3.html").read_text().replace("__FONTS__", fonts))
G = '<span class="g">{}</span>'
CARDS = {
  "s3-p1-am": dict(part=1, kicker="NEW SERIES · 5 PARTS", big="THE MACHINE", q="1947 mein 1 dollar " + G.format("Rs 3.31") + " ka tha. Aaj?", e="Part 1 drops tonight.", pill="AAJ SHAAM 6 BAJE"),
  "s3-p1-pm": dict(part=1, kicker="PART 1/5 · LIVE", big="THE MACHINE", q="Part 1 grid par hai. " + G.format("Jawab dekh kar") + " hairan ho jaoge.", e="Watch, then guess Part 2 in the replies.", pill="REEL DEKHO ↓"),
  "s3-p2-am": dict(part=2, kicker="PART 2/5 · TONIGHT", big="EK SAAL", q="Sirf ek saal mein rupee ko " + G.format("kya hua?"), e="Reply with your guess before 6 PM.", pill="AAJ SHAAM 6 BAJE"),
  "s3-p2-pm": dict(part=2, kicker="PART 2/5 · LIVE", big="1971 → 1972", q="Part 2 grid par hai. " + G.format("Ek saal, ek jhatka."), e="Missed Part 1? It's right below it.", pill="REEL DEKHO ↓"),
  "s3-p3-am": dict(part=3, kicker="PART 3/5 · TONIGHT", big="CLASSIFIED", q="Central banks " + G.format("chupke se") + " kya khareed rahe hain?", e="One word. Reply with your guess.", pill="AAJ SHAAM 6 BAJE"),
  "s3-p3-pm": dict(part=3, kicker="PART 3/5 · LIVE", big="DECRYPTED", q="Jawab grid par hai. " + G.format("Teen saal lagatar."), e="Part 4 is about Pakistan.", pill="REEL DEKHO ↓"),
  "s3-p4-am": dict(part=4, kicker="PART 4/5 · TONIGHT", big="SBP VAULT", q="State Bank ke paas " + G.format("kitna sona") + " hai? Guess karo.", e="Reply with a number in tonnes.", pill="AAJ SHAAM 6 BAJE"),
  "s3-p4-pm": dict(part=4, kicker="PART 4/5 · LIVE", big="LAKH TOLA", q="Pakistan ka sona " + G.format("tola") + " mein. Grid par dekho.", e="Tomorrow: the final part.", pill="REEL DEKHO ↓"),
  "s3-p5-am": dict(part=5, kicker="PART 5/5 · FINAL · TONIGHT", big="WHO FIRST?", q="Naya paisa " + G.format("pehle kis ko") + " milta hai?", e="The last piece of the machine.", pill="AAJ SHAAM 6 BAJE"),
  "s3-p5-pm": dict(part=5, kicker="FILE CLOSED · 5/5", big="THE MACHINE", q="Poori series grid par. " + G.format("Part 1 se dekho."), e="Save all five. Send them to one person.", pill="REEL DEKHO ↓"),
}
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    for name, c in CARDS.items():
        pg.goto(f"file://{page}?n={name}#" + urllib.parse.quote(json.dumps(c))); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.screenshot(path=str(out / f"{name}.png"))
    b.close()
print("stories:", len(CARDS))
