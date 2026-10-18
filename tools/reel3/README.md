# Reel engine v3 (The Gold Council)

Beat-synced motion reels with an original synthesized score. Nothing is sampled.

## Build one reel

```bash
npm i @fontsource/noto-serif @fontsource/ibm-plex-sans @fontsource/jetbrains-mono
export FONTSOURCE=$PWD/node_modules/@fontsource
./build_v3.sh ep1 12        # reads v3_ep1.html + cues_v3_ep1.json, writes out/v3_ep1.mp4
```

Preview frames before a full render:
`python3 make_video.py $PWD/v3_ep1.html $FONTSOURCE $PWD/prev 12 0 3.6 5.0 8.6 11.2`

## Pieces

| File | What it does |
|---|---|
| `base3.js` / `base3.css` | Chrome (currency rain, HUD, corners, grain, vignette), camera push-in per scene, pump on every beat inside `PULSE`, shake + gold flash on `HITS` and cuts, `.sweep` gold light sweep, `pop()` kinetic landing, `words()` word-by-word reveal, `SERIES` progress bar |
| `make_beat.py` | Original score from a cue sheet: D-minor progression (Dm Bb Gm A), trap groove, saturated 808 (audible on phone speakers), plucks, sidechained pad, risers, impacts with sub drops, stutters, tape stop, counter ticks, typing, chime |
| `make_video.py` | Renders a page frame by frame at 30 fps and encodes H.264 |
| `build_v3.sh` | Video + score + loudness normalisation to -14 LUFS, muxed AAC |
| `story3.html` / `make_stories3.py` | Series story cards (morning teaser + evening "live now") |

## Timing grid

BPM 100: one beat = 0.6 s, one bar = 2.4 s. Put every scene cut on a bar line (2.4, 4.8, 7.2, 9.6) and every pop on a beat.
Standard 12 s series layout:

| Bar | Seconds | Section | Job |
|---|---|---|---|
| 1 | 0–2.4 | intro | Hook fully visible on frame 0 (number + Roman Urdu question) |
| 2 | 2.4–4.8 | intro + riser | Build: counter, chart drawing, decrypting |
| 3–4 | 4.8–9.6 | drop | Payoff on the drop (HIT at 4.8), second fact at 7.2 |
| 5 | 9.6–12 | break + tape stop | Cliffhanger: next part, "kal shaam 6 baje", follow |

## Rules

- Frame 0 shows the whole hook. No typing-in, no fade from black. No flash on frame 0.
- Main line in Roman Urdu, smaller English line under it.
- Content between y 640 and 1400. Mono numbers: keep `chars × 0.6 × font-size` under 880 px and add `white-space:nowrap`.
- Every number has a source line on screen or in the caption.
- Check preview frames for overflow, orphan words and overlaps before the full render.
