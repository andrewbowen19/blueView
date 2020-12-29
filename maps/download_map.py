'''
Script for a download map based on user-selected podcast
Plotly bubble map infor can be foudn here: https://plotly.com/python/bubble-maps/
'''

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
import json


from utils import podIDs, getSimplecastResponse

# print(podIDs())

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Podcast Downloads by Country'),

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
        id='downloads-by-country-graph'
        
    )
])

# ### CALLBACKS GO HERE ###
# #############################
# Updating pod ID div based on user selection
@app.callback(
    Output(component_id='dd-output-container', component_property='children'),
    Input(component_id='pod-title-dropdown', component_property='value')
)
def update_output_div(input_value):
    return f'Your selected podcast ID: {input_value}'

# Updating graph from dropdown selection (pod ID)
@app.callback(
	Output(component_id='downloads-by-country-graph', component_property='figure'),
	Input(component_id='pod-title-dropdown', component_property='value')
)
def update_graph(pod_id):
	dat = getSimplecastResponse(f'/analytics/location?podcast={pod_id}')#, 'by_interval')
	print(json.loads(dat))
	df = pd.DataFrame(json.loads(dat)['countries'])#pd.json_normalize(json.loads(dat)['countries'])#, 'countries')
	print(df['name'])
	print(df.columns)
	fig = px.scatter_geo(df, locations="name", locationmode= 'country names',
                     hover_name="name", size="downloads_total",
                     projection="natural earth")
	return fig

# #############################

if __name__ == '__main__':
    app.run_server(debug=True)
