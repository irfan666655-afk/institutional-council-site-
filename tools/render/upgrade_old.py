"""Apply the upgraded Matrix layer + content fixes to Launch Kit artboards, in place."""
import pathlib, sys, re

proj = pathlib.Path(sys.argv[1])
OVERLAY = (
    '<div aria-hidden="true" style="position: absolute; inset: 0; background: repeating-linear-gradient(0deg, rgba(240,207,106,0.03) 0 2px, transparent 2px 6px)"></div>\n'
    '<div aria-hidden="true" style="position: absolute; left: 30px; top: 30px; width: 46px; height: 46px; border-top: 4px solid #d4af37; border-left: 4px solid #d4af37"></div>\n'
    '<div aria-hidden="true" style="position: absolute; right: 30px; top: 30px; width: 46px; height: 46px; border-top: 4px solid #d4af37; border-right: 4px solid #d4af37"></div>\n'
    '<div aria-hidden="true" style="position: absolute; left: 30px; bottom: 30px; width: 46px; height: 46px; border-bottom: 4px solid #d4af37; border-left: 4px solid #d4af37"></div>\n'
    '<div aria-hidden="true" style="position: absolute; right: 30px; bottom: 30px; width: 46px; height: 46px; border-bottom: 4px solid #d4af37; border-right: 4px solid #d4af37"></div>\n'
)
MARK = "<!-- hud-layer -->"
files = ["P1-Shrinking", "P2-Arithmetic", "P3-Myth", "P4-Hour"] + \
        [f"C1-Who-{i}" for i in range(1, 5)] + [f"C2-Why-{i}" for i in range(1, 5)]
fixes = {
    "@thegoldcouncil": "@the.goldcouncil",
    ">01 / 06<": ">01 / 04<", ">02 / 06<": ">02 / 04<", ">03 / 06<": ">03 / 04<", ">04 / 06<": ">04 / 04<",
    "435,720": "437,500",
    "×10,112": "×10,174",
    "SBP; Grand Atlas II (computed)": "SBP; tola rate 12 Oct 2026; Grand Atlas II",
}
for name in files:
    p = proj / f"{name}.dc.html"
    s = p.read_text()
    for a, b in fixes.items():
        s = s.replace(a, b)
    if name == "C2-Why-3":
        s = s.replace(">Today</span>", ">Oct 2026</span>")
    if MARK not in s:
        k = s.rfind("</div>\n</x-dc>")
        assert k > 0, name
        s = s[:k] + MARK + "\n" + OVERLAY + s[k:]
    p.write_text(s)
    print("upgraded", name)
