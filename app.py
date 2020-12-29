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
# ########################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
# #############################################################################
sc = getSimpleCast()
test_id = '649a9132-4298-4d65-b650-8360b693520e'
df = sc.downloadsByPod(f'/analytics/downloads?podcast={test_id}')


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
