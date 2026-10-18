"""Render a reel page frame by frame. Usage: make_video.py <page.html> <fontsource> <out.mp4|preview_dir> <dur> [preview times...]"""
import sys, pathlib, subprocess, shutil, tempfile
from playwright.sync_api import sync_playwright

src, fs, out, dur = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), pathlib.Path(sys.argv[3]), float(sys.argv[4])
preview = [float(x) for x in sys.argv[5:]]
fonts = "".join(f'<link rel="stylesheet" href="file://{fs}/{p}">' for p in [
    "noto-serif/700.css", "ibm-plex-sans/500.css", "ibm-plex-sans/700.css", "jetbrains-mono/700.css"])
page = src.with_name(src.stem + "_page.html")
page.write_text(src.read_text().replace("__FONTS__", fonts))
FPS = 30
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(f"file://{page}"); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(500)
    if preview:
        out.mkdir(parents=True, exist_ok=True)
        for t in preview:
            pg.evaluate(f"render({t})"); pg.screenshot(path=str(out / f"{src.stem}_{t:05.2f}.png"))
    else:
        fdir = pathlib.Path(tempfile.mkdtemp(dir=src.parent))
        for i in range(int(FPS * dur)):
            pg.evaluate(f"render({i / FPS})"); pg.screenshot(path=str(fdir / f"{i:04d}.jpg"), type="jpeg", quality=93)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(fdir / "%04d.jpg"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", str(out)], check=True)
        shutil.rmtree(fdir)
    b.close()
print("done", out)
