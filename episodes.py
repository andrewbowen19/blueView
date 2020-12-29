'''
Getting episode level data
'''

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
import json

from utils import getSimplecastResponse, podIDs

# ########################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame -- reformatted from API JSON responses
# see https://plotly.com/python/px-arguments/ for more options
# #############################################################################


app.layout = html.Div(children=[
    html.H1(children='Podcast Downloads by Date'),

    # Dropdown menu for user interaction
    dcc.Dropdown(
        id='pod-title-dropdown',
        options=podIDs(),
        searchable=True
        
    ),
    # Outputs selected podcast ID to user: not sure if we need this later on
    html.Div(id='dd-output-container'),

    # Figure widget
    dcc.Graph(
        id='episode-graph'
    )
])

# Callbacks to update figure on screen based on user input
# For more info check: https://dash.plotly.com/basic-callbacks

# Updating selected pod from dropdown menu
@app.callback(
    Output(component_id='dd-output-container', component_property='children'),
    Input(component_id='pod-title-dropdown', component_property='value')
)
def update_output_div(input_value):
    return f'Your selected podcast ID: {input_value}'

@app.callback(
	Output(component_id='episode-graph', component_property='figure'),
	Input(component_id='pod-title-dropdown', component_property='value')
)
# Will need to chain more callbacks on for second dropdown for episode selection  once podcast has ben chosen

# ########################
if __name__ == '__main__':
    app.run_server(debug=True)

