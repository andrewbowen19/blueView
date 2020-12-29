'''
Code for a plotly histogram applet

User can select podcasts from dropdown menu and view histogram of distribution platform data

Plotly express histogram docs: https://plotly.github.io/plotly.py-docs/generated/plotly.express.histogram.html
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
    html.H1(children='Podcast Downloads by Platform'),

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



##### CALBACKS HERE #####
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
    dat = getSimplecastResponse(f'/analytics/technology/applications?podcast={pod_id}')#, 'by_interval')
    # print(json.loads(dat))
    df = pd.DataFrame(json.loads(dat)['collection'])#pd.json_normalize(json.loads(dat)['countries'])#, 'countries')
    print(df)
    print(df.columns)
    fig = px.histogram(df, 
                  x='name', y='downloads_total', labels={'name': 'Platform Name', 'downloads_total': 'Downloads'})#,
                  # hover_name=['name', 'rank',
                         # "downloads_total"])
    return fig


###########################





###########################
if __name__ == '__main__':
    app.run_server(debug=True)



