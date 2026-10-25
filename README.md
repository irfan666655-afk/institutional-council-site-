# council-data

Data branch for the Institutional Council desk (simulated research). Pushing a change to `request.json`
starts the `council-data` workflow, which downloads hourly BID/ASK candles from Dukascopy and hourly/daily
bars from Yahoo Finance for every instrument, then commits them to `data/` with a `status.json` report.
Nothing here touches `main`.
