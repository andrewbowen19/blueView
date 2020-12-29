# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
import json

# ########LOCAL IMPORTS####
# from getSimpleCast import getSimpleCast
from utils import getSimplecastResponse, podIDs

# from podIDs import podIDs
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

    # Downloads per time period graph
    dcc.Graph(
        id='downloads-graph'
    ),
    html.Div(id='separator'),
    # Distribution Platform Graph
    dcc.Graph(
        id='dist-platform-graph'
    ),

    dcc.Graph(
        id='country-downloads-graph'
        
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

# Calback to update graph from dropdown menu
@app.callback(
	Output(component_id='downloads-graph', component_property='figure'),
	Input(component_id='pod-title-dropdown', component_property='value')
)
def update_graph(pod_id):
	'''
	Function to update downloads figure based on inputted pod ID
	Pod ID parameter set by user selection on our dropdown menux
	'''
	# Getting data from Simplecast for selected podcast
	dat = getSimplecastResponse(f'/analytics/downloads?podcast={pod_id}')
	df = pd.json_normalize(json.loads(dat), 'by_interval')
	print(df)

	# Creating plotly
	fig = px.line(df, x="interval", y="downloads_total")
	return fig

# #############################
# Distribution platform graph
@app.callback(
    Output(component_id='dist-platform-graph', component_property='figure'),
    Input(component_id='pod-title-dropdown', component_property='value')
)
def update_platform_graph(pod_id):
    dat = getSimplecastResponse(f'/analytics/technology/applications?podcast={pod_id}')
    # print(json.loads(dat))
    df = pd.DataFrame(json.loads(dat)['collection'])
    print(df)
    print(df.columns)
    fig = px.histogram(df, 
                  x='name', y='downloads_total',
                  labels={'name': 'Platform Name', 'downloads_total': 'Downloads'},
                  range_x=[0,10],nbins=10,
                  title='Downloads per Distribution platform')
    return fig

# ############################
# Country Download Map
@app.callback(
    Output(component_id='country-downloads-graph', component_property='figure'),
    Input(component_id='pod-title-dropdown', component_property='value')
)
def update_graph(pod_id):
    dat = getSimplecastResponse(f'/analytics/location?podcast={pod_id}')
    df = pd.DataFrame(json.loads(dat)['countries'])
    fig = px.scatter_geo(df, locations="name", locationmode= 'country names',
                     hover_name="name", size="downloads_total",
                     projection="natural earth")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)








