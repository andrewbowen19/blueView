this repo is a sandbox for us to build a dash visualization app based on Simplecast response data

Eventually want this to replace our Power BI dashboard as a visualization tool

[Plotly Dash docs](https://dash.plotly.com)

Info on plotly callbacks (used in our downloads_total app) can be found [here](https://dash.plotly.com/basic-callbacks).

To use the podcasts-downloads dashboard, run `python app.py` from the command line and visit the HTTP port from the local server

To get a histogram of podcast downloads by distribution  platform (Apple, Spotify, etc.) run `python platform_hist.py` from the command line and navigate to listed local server (http://127.0.0.1:8050/)

##**TODO:**

- [] Add dropdown, app layout functions to utils
- [] Figure out simplecast individual state API call for geo bubble chart
- [] Research hosting platforms compatible with plotly (AWS might be feasible here)



