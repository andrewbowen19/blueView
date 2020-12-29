# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

# ########LOCAL IMPORT####
from getSimpleCast import getSimpleCast
from getSimplecastResponse import getSimplecastResponse
import json
from podIDs import podIDs
# ########################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Would be cool to add dropdown menu to select podcast (maps to id for API request) for interactivity!


# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
# #############################################################################
# sc = getSimpleCast()
test_id = '649a9132-4298-4d65-b650-8360b693520e'
# df = sc.getResponse(f'/analytics/downloads?podcast={test_id}', 'by_interval')
dat = getSimplecastResponse(f'/analytics/downloads?podcast={test_id}')#, 'by_interval')
df = pd.json_normalize(json.loads(dat), 'by_interval')
print(df)
# ############################################################################
# df = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })
# #############################################################################

fig = px.line(df, x="interval", y="downloads_total")#, color="City", barmode="group")

app.layout = html.Div(children=[
    html.H1(children=f'Downloads for podcast: {test_id}'),

    # Adding dropdown menu for user interaction
    
    dcc.Dropdown(
        id='demo-dropdown',
        options=podIDs(),
        # value='NYC'
    ),
    # html.Div(id='dd-output-container')
	

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
