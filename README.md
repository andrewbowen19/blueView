# BlueView

[BlueView](https://blu-view.herokuapp.com) is a podcast data visualization web app hosted by [Heroku](https://dashboard.heroku.com/apps).

This applet will eventually replace our Power BI analytics dashboard

This app is created using Plotly and Dash.
[Plotly Dash docs](https://dash.plotly.com)

## Dev Notes
For development, the application can be viewed by running `python app.py` form the command line and visiting the local host port provided.


## **TODO:**

- [X] Add dropdown, app layout functions to utils
- [X] Figure out simplecast individual state API call for geo bubble chart
- [X] Research hosting platforms compatible with plotly (AWS might be feasible here)
- [] Look into JSON parsing error ('countries', 'collection', etc.) when converting to pandas df
- [] Add network-level dtaa to db for faster pulls on login than API call
- [] Add podcast table to our login view; docs [here](https://dash.plotly.com/datatable/callbacks)


