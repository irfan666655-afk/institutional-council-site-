# Escape the Matrix: vertical episode pipeline

The 24-minute film (16:9, from the Claude artifact's HLS stream) is cut into 12 vertical episodes and short clips.

1. Rebuild film.mp4: concatenate hls/init.mp4 + hls/seg000..144.mp4, then `ffmpeg -i film_frag.mp4 -c copy film.mp4`.
2. Subtitles: `cues_fixed.json` already holds every on-screen subtitle with start/end seconds (OCR of the film, cleaned).
3. Frames: `make_frames.py <fontsource> frames` (episodes) and `make_clip_frames.py <fontsource> .` (clips.json).
4. Render: `render_ep.py . <n>` for episodes, `render_clip.py . specs/<name>.json` for clips (one seeked input per segment).

Layout 1080x1920: header with Roman Urdu hook and 12-segment progress (y 300-680), film window 1080x457 at y 700 (crop 1920x812 at y 128),
captions IBM Plex Sans 48-50 px from y 1195 with numbers in gold, progress bar at y 1159, end card in the last 3 s. Loudness -14 LUFS.
Fonts for libass: convert the @fontsource woff2 files to TTF into ~/.fonts (fonttools) and run fc-cache.
