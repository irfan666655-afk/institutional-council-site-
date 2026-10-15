"""Make 9:16 'new on the grid' story frames from post images, plus a reply-based poll story."""
import pathlib, sys
from playwright.sync_api import sync_playwright

S = pathlib.Path("/tmp/claude-0/-home-claude/ee3cde47-b1ef-53af-8c44-9324be7079bc/scratchpad")
FS = S / "fontpkg/node_modules/@fontsource"
SRC = S / "GoldCouncil_Posts"
OUT = S / "stories"; OUT.mkdir(exist_ok=True)
fonts = "".join(f'<link rel="stylesheet" href="file://{FS}/{p}">' for p in [
    "noto-serif/700.css", "ibm-plex-sans/600.css", "ibm-plex-sans/700.css", "jetbrains-mono/700.css"])
RAIN = "".join(
    f'<div style="position:absolute;top:{-200 + (i * 137) % 400}px;left:{20 + i * 80}px;width:22px;word-break:break-all;'
    f'font:700 32px/1.1 \'JetBrains Mono\',monospace;color:{"rgba(95,211,196,.12)" if i % 3 == 1 else "rgba(212,175,55,.16)"}">'
    + ("7$1₨09%2€4¥8₿3$6₨1905$7₨2$9₨4$1₨" * 3)[i % 7:] + "</div>" for i in range(13))
HUD = """
<div style="position:absolute;inset:0;background:radial-gradient(ellipse 80% 45% at 50% 50%,rgba(5,5,7,.96) 0%,rgba(5,5,7,.7) 60%,rgba(5,5,7,.3) 100%)"></div>
<div style="position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(240,207,106,.035) 0 2px,transparent 2px 6px)"></div>
<div style="position:absolute;left:40px;top:200px;width:70px;height:70px;border-top:5px solid #d4af37;border-left:5px solid #d4af37"></div>
<div style="position:absolute;right:40px;top:200px;width:70px;height:70px;border-top:5px solid #d4af37;border-right:5px solid #d4af37"></div>
<div style="position:absolute;left:40px;bottom:200px;width:70px;height:70px;border-bottom:5px solid #d4af37;border-left:5px solid #d4af37"></div>
<div style="position:absolute;right:40px;bottom:200px;width:70px;height:70px;border-bottom:5px solid #d4af37;border-right:5px solid #d4af37"></div>"""

def page(inner):
    return (f"<!doctype html><html><head><meta charset='utf-8'>{fonts}</head><body style='margin:0'>"
            f"<div style=\"width:1080px;height:1920px;position:relative;overflow:hidden;background:#050507;font-family:'IBM Plex Sans',sans-serif;color:#f1eadc\">"
            f"{RAIN}{HUD}{inner}</div></body></html>")

def grid_story(img, label):
    return page(f"""
<div style="position:absolute;left:0;right:0;top:250px;display:flex;justify-content:center;align-items:center;gap:14px;font:700 28px 'JetBrains Mono',monospace;letter-spacing:.24em;color:#d4af37">
<span style="width:16px;height:16px;border-radius:50%;background:#e05a4f"></span>NEW ON THE GRID</div>
<div style="position:absolute;left:0;right:0;top:310px;text-align:center;font:700 24px 'JetBrains Mono',monospace;letter-spacing:.2em;color:#a39d90">{label}</div>
<img src="file://{img}" style="position:absolute;left:90px;top:400px;width:900px;height:1125px;object-fit:cover;border:3px solid #d4af37;border-radius:14px;box-shadow:0 30px 80px rgba(0,0,0,.6)">
<div style="position:absolute;left:0;right:0;top:1580px;text-align:center;font:700 40px 'Noto Serif',serif;color:#f1eadc">Tap our profile to read it</div>
<div style="position:absolute;left:0;right:0;top:1650px;text-align:center;font:700 30px 'JetBrains Mono',monospace;color:#d4af37">@the.goldcouncil</div>""")

poll = page("""
<div style="position:absolute;left:0;right:0;top:300px;display:flex;justify-content:center;align-items:center;gap:14px;font:700 28px 'JetBrains Mono',monospace;letter-spacing:.24em;color:#d4af37">
<span style="width:16px;height:16px;border-radius:50%;background:#e05a4f"></span>ONE QUESTION</div>
<h1 style="position:absolute;left:90px;right:90px;top:460px;margin:0;text-align:center;font:700 112px/1.05 'Noto Serif',serif;letter-spacing:-.02em;color:#f1eadc">Do you know what <span style="color:#f0cf6a;text-shadow:-4px 0 rgba(95,211,196,.5),4px 0 rgba(224,90,79,.5)">1971</span> did to your money?</h1>
<div style="position:absolute;left:140px;right:140px;top:1180px;display:flex;gap:30px">
<div style="flex:1;padding:34px 0;border:3px solid #d4af37;border-radius:20px;text-align:center;font:700 40px 'JetBrains Mono',monospace;color:#f0cf6a">YES</div>
<div style="flex:1;padding:34px 0;border:3px solid #8f8a7e;border-radius:20px;text-align:center;font:700 40px 'JetBrains Mono',monospace;color:#cfc7b6">NO IDEA</div></div>
<div style="position:absolute;left:0;right:0;top:1360px;text-align:center;font:600 36px 'IBM Plex Sans',sans-serif;color:#cfc7b6">Reply to this story with one word.</div>
<div style="position:absolute;left:0;right:0;top:1650px;text-align:center;font:700 30px 'JetBrains Mono',monospace;color:#d4af37">#EscapeTheMatrix</div>""")

jobs = [("st-01.png", grid_story(SRC / "01-image.png", "SOMETHING IS SHRINKING")),
        ("st-03.png", grid_story(SRC / "03-image.png", "THE ARITHMETIC")),
        ("st-04.png", grid_story(SRC / "04-slide1.png", "SWIPE · 4 SLIDES")),
        ("st-06.png", grid_story(SRC / "06-image.png", "MYTH VS RECORD")),
        ("st-07.png", grid_story(SRC / "07-slide1.png", "SWIPE · 5 SLIDES")),
        ("st-08.png", grid_story(SRC / "08-slide1.png", "SWIPE · 4 SLIDES")),
        ("st-09.png", grid_story(SRC / "09-image.png", "NO ONE KNOWS THE HOUR")),
        ("st-poll.png", poll)]
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    for name, html in jobs:
        f = OUT / (name + ".html"); f.write_text(html)
        pg.goto(f"file://{f}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(250)
        pg.screenshot(path=str(OUT / name)); f.unlink(); print("ok", name)
    b.close()
