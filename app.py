# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.express as px
import pandas as pd

# ########LOCAL IMPORT####
# from getSimpleCast import getSimpleCast
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
# test_id = '649a9132-4298-4d65-b650-8360b693520e'
# # df = sc.getResponse(f'/analytics/downloads?podcast={test_id}', 'by_interval')
# dat = getSimplecastResponse(f'/analytics/downloads?podcast={test_id}')#, 'by_interval')
# df = pd.json_normalize(json.loads(dat), 'by_interval')
# print(df)
# ############################################################################
# df = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })
# #############################################################################
# dat = getSimplecastResponse(f'/analytics/downloads?podcast={pod_id}')#, 'by_interval')
# df = pd.json_normalize(json.loads(dat), 'by_interval')
# fig = px.line(df, x="interval", y="downloads_total")#, color="City", barmode="group")

app.layout = html.Div(children=[
    html.H1(children=f'Downloads for podcasts by date'),

    # Adding dropdown menu for user interaction
    
    dcc.Dropdown(
        id='pod-title-dropdown',
        options=podIDs(),
        # value= '',
        searchable=True
        
    ),
    html.Div(id='dd-output-container'),
	

    # html.Div(children="Your"),

    dcc.Graph(
        id='downloads-graph'#,
        # figure=fig
    )
])

# Callbacks to update figure on screen based on user input
# For more info check: https://dash.plotly.com/basic-callbacks

# Using a callback to grab API data
# @app.callback(
# 	Output(component_id='dd-output-container', component_property='value'),
# 	Input(component_id='pod-title-dropdown', component_property='value')
# )
# def get_pod_df(pod_id):
# 	dat = getSimplecastResponse(f'/analytics/downloads?podcast={pod_id}')#, 'by_interval')
# 	df = pd.json_normalize(json.loads(dat), 'by_interval')
# 	return df

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
	'''
	dat = getSimplecastResponse(f'/analytics/downloads?podcast={pod_id}')#, 'by_interval')
	df = pd.json_normalize(json.loads(dat), 'by_interval')
	print(df)

	fig = px.line(df, x="interval", y="downloads_total")
	return fig

if __name__ == '__main__':
    app.run_server(debug=True)