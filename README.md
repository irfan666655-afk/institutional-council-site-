# institutional-council-site

Public client-facing site for the [Institutional Council](https://github.com/irfan666655-afk/institutional-council)
XAU/USD trading engine — landing page, live verdict snapshot, market windows,
the "Beat the Council" simulator, and an authenticated read-only client desk.

Extracted from `institutional-council/src/site.html` so the trading engine
repo holds only the engine; this repo holds only the public site. It has no
backend of its own — it's a single static page that calls the trading-os API
directly from the browser.

## Deploy

Static hosting only (Vercel, Netlify, GitHub Pages, etc.) — no build step,
no server. Point your host at `index.html`.

## Required configuration before going live

1. **API base URL** — set the `council-api-base` meta tag in `index.html` to
   the deployed trading-os origin:

   ```html
   <meta name="council-api-base" content="https://YOUR-APP.up.railway.app">
   ```

   Leaving it empty falls back to same-origin requests, which only works if
   this site happens to be served from the same host as the API.

2. **CORS** — add this site's deployed origin to trading-os's `CORS_ORIGINS`
   environment variable (see `institutional-council/DEPLOYMENT.md`), or
   cross-origin requests from the client desk (login, metrics) will be
   rejected by the browser.

## What's real vs. simulated

The hero/verdict sections show a dated snapshot baked into the page at
extraction time (`SNAP_AS_OF` in the script). The client desk section, once
signed in, pulls live data from the trading-os API. Everything on this site
describes a paper-trading account — no real capital is deployed.
