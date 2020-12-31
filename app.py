'''
BlueView Main application script
'''

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
from utils import getSimplecastResponse, podIDs, episodeIDs

# from podIDs import podIDs
# ########################

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame -- reformatted from API JSON responses
# see https://plotly.com/python/px-arguments/ for more options
# #############################################################################

# Setting up app layout
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
    html.Div([
        # Graph of downloads vs time
        html.Div([
        dcc.Graph(
        id='downloads-graph'
         ),
        # ]),

        # html.Div([
        # Slider to toggle interval
        dcc.Slider(
            id='interval-slider', 
            min=0, max=2, 
            marks={0: 'day', 1:'week', 2:'month'},
            value=1)#,
            #tooltip={'placement':'right'},
            #vertical=True)
        ])
    ]),
    
    # Div for bottom 2 graphs -- side by side
    html.Div([
    # Distribution Platform Graph
    html.Div([
            dcc.Graph(
            id='dist-platform-graph')
            ],  className='six columns'),
    # Country Downlaods graph 
    html.Div([

        dcc.Graph(
        id='country-downloads-graph')

        ],  className='six columns')
    ]),

    html.Div([
    ### Episode Level ###
        html.H2('Episode-Level Data'),

    # Episode Dropdown
        dcc.Dropdown(
        id='episode-dropdown',
        # options=episodeIDs(),
        searchable=True
        
    ),


    ], id='episode-level'),

    # Episode Downlaod graph - same format as podcast donwload graph
    html.Div([
        dcc.Graph(id='episode-download-graph'),

        dcc.Slider(
            id='ep-interval-slider', 
            min=0, max=2, 
            marks={0: 'day', 1:'week', 2:'month'},
            value=1)

        ])

    
])

# #################################################################################################

# Callbacks to update figure on screen based on user input
# For more info check: https://dash.plotly.com/basic-callbacks

# #############################
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
    Input(component_id='pod-title-dropdown', component_property='value'),
    Input(component_id='interval-slider', component_property='value')
)
def update_graph(pod_id, interval):
    '''
    Function to update downloads figure based on inputted pod ID
    Pod ID parameter set by user selection on our dropdown menu
    '''
    # Getting data from Simplecast for selected podcast
    print('Interval selcted:', interval)
    intervals = {0: 'day', 1:'week', 2:'month'}
    dat = getSimplecastResponse(f'/analytics/downloads?podcast={pod_id}&interval={intervals[interval]}')
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
    '''update distribution platform graph based on podcast selection'''
    dat = getSimplecastResponse(f'/analytics/technology/applications?podcast={pod_id}')
    dat2json = json.loads(dat)
    df = pd.DataFrame(dat2json['collection'])
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
def update_map(pod_id):
    '''update map plot'''
    dat = getSimplecastResponse(f'/analytics/location?podcast={pod_id}')
    df = pd.DataFrame(json.loads(dat)['countries'])
    fig = px.scatter_geo(df, locations="name", locationmode= 'country names',
                     hover_name="name", size="downloads_total",
                     projection="natural earth", title='Downloads Per Country')
    return fig


# ############################
# Episode Level Dropdown
@app.callback(
    Output(component_id='episode-dropdown', component_property='options'),
    Input(component_id='pod-title-dropdown', component_property='value')
)
def update_episode_dropdown(pod_id):
    print('Podcast: Selected', pod_id)
    episode_options = episodeIDs(pod_id)
    print('Episode list (with tokens):', episode_options)
    return episode_options

# ############################
# Episode Level Downloads graph
# Calback to update graph from dropdown menu
@app.callback(
    Output(component_id='episode-download-graph', component_property='figure'),
    Input(component_id='pod-title-dropdown', component_property='value'),
    Input(component_id='episode-dropdown', component_property='value'),
    Input(component_id='ep-interval-slider', component_property='value')
)
def update_episode_graph(pod_id, episode_id, interval):
    '''
    Function to update downloads figure based on inputted pod ID and ep ID
    Pod ID parameter set by user selection on our dropdown menu
    '''
    # Getting data from Simplecast for selected podcast/episode
    intervals = {0: 'day', 1:'week', 2:'month'}
    print('Episode Interval selcted:', intervals[interval])
    print('Selected Episode ID:', episode_id)
    print('Getting Episode Data from Simplecast...')

    dat = getSimplecastResponse(f'/analytics/downloads?episode={episode_id}&interval={intervals[interval]}')
    print(dat)
    df = pd.json_normalize(json.loads(dat), 'by_interval')
    print('Got Data!')
    print('Episode Data pulled:', df)

    # Creating plotly figure within our Dash app
    fig = px.line(df, x="interval", y="downloads_total")
    return fig

if __name__ == '__main__':
    app.run_server(
        port=8050,
        host='0.0.0.0',
        debug=False
        )








