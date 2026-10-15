# Gold Council content pipeline

Everything that builds @the.goldcouncil posts, stories and reels.

- `templates/` – Matrix-theme artboards (.dc.html, 1080x1350 posts, 1080x1920 stories/reel covers). `launchkit/` holds the upgraded Launch Kit set.
- `render/render_list.py <dir> <out> <fontsource> <blobdir|-> W H names...` – renders artboards to PNG with Playwright.
- `render/stories.py` – "New on the grid" story frames from post images.
- `reel/` – motion reels: `reelN.html` scenes on `base.js`/`base.css`, `make_video.py` renders 30 fps MP4, `make_score.py cuesN.json` synthesises an original score + SFX, then mux with ffmpeg (`loudnorm=I=-14:TP=-1`).
- Fonts: `npm i @fontsource/noto-serif @fontsource/ibm-plex-sans @fontsource/jetbrains-mono`.
- Publishing: media files at the branch root are served from raw.githubusercontent.com and scheduled through Metricool (brand 7433302, Asia/Karachi).

Style rules: black #050507/#08080b, gold #d4af37/#f0cf6a, cream #f1eadc, Noto Serif display, IBM Plex Sans body, JetBrains Mono labels; currency rain, scanlines, gold corner brackets, REC dot. Every caption ends "Education only. Not financial advice." Every number carries its source. No Escape the Matrix countdown or premiere date until the owner sets one.
