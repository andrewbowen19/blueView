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
import dash_table
import plotly.express as px
import os
import pandas as pd
import json

# ########LOCAL IMPORTS####
from utils import *#getSimplecastResponse, podIDs, episodeIDs, get_episode_data, group_listener_data, 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server # server needed for heroku deploy

# Network data from db
network_stats = pd.read_csv(os.path.join('.', 'db', 'network-stats.csv'))
network_downloads = pd.read_csv(os.path.join('.', 'db', 'network-downloads.csv'))
pod_table = pd.read_csv(os.path.join('.', 'db', 'podcast-table.csv'))
print('PODCAST TABLE:', pod_table)

num_pods = "{:,}".format(network_stats['Number of Podcasts'].values[0])
n_episodes = "{:,}".format(network_stats['Total Episodes'].values[0])
n_downloads = "{:,}".format(network_stats['Total Downloads'].values[0])
episode_table_cols = ['title', 'published_at', 'id', 'downloads', 'listeners']

pod_id_list = podIDs()
# assume you have a "long-form" data frame -- reformatted from API JSON responses
# see https://plotly.com/python/px-arguments/ for more options
# #############################################################################

# Setting up app layout
app.layout = html.Div(children=[

    html.Div([
        html.H1(children='Blue Wire Network Data', style={'color':'#0000ff', 'text-align':'center'}),
    ]),
    # Network Stats
    html.Div(children=[

        # Number of podcasts
        html.H2(id='number-podcasts', 
            children=f'{num_pods} Podcasts',
            className='four columns',
            style={'text-align':'center'}),
        # Number of downloads -- BW network
        html.H2(id='network-total-downloads', 
            children=f'{n_downloads} Downloads',
            className='four columns',
            style={'text-align':'center'}),
        # Number of episodes -- BW network
        html.H2(id='network-number-epidoses', 
            children=f'{n_episodes} Episodes',
            className='four columns',
            style={'text-align':'center'}),

        # dcc.Graph(id='network-download-graph',
        # figure=f)
    ]),
    html.Div([
        html.H3(children='Network Chart', style={'color':'#ffffff','text-align':'left'}),
    ]),
    # Network level downloads graph
    html.Div([
        dcc.Graph(id='network-download-graph',
        figure=px.line(network_downloads, x='interval', y='downloads_total', title='Network Data').update_xaxes(
    rangeslider_visible=True,
    tickformatstops = [
        dict(dtickrange=[None, 1000], value="%H:%M:%S.%L ms"),
        dict(dtickrange=[1000, 60000], value="%H:%M:%S s"),
        dict(dtickrange=[60000, 3600000], value="%H:%M m"),
        dict(dtickrange=[3600000, 86400000], value="%H:%M h"),
        dict(dtickrange=[86400000, 604800000], value="%e. %b d"),
        dict(dtickrange=[604800000, "M1"], value="%e. %b w"),
        dict(dtickrange=["M1", "M12"], value="%b '%y M"),
        dict(dtickrange=["M12", None], value="%Y Y")
    ]
)),#px.line(network_downloads, x='interval', y='downloads_total', title='Network Data')),
        dcc.Slider(
            id='network-interval-slider', 
            min=0, max=2, 
            marks={0: 'day', 1:'week', 2:'month'},
            value=1)

        ]),

    ###########Podcast Table code Here ###############
    # https://dash.plotly.com/datatable/callbacks
    # https://dash.plotly.com/datatable/reference
    html.H3('Blue Wire Podcasts'),
    html.Div([
        dash_table.DataTable(
        id='podcast-table',
        columns=[{'name': i, 'id': i, "selectable": True} for i in pod_table.columns],
        data=pod_table.to_dict('records'),
        # filter_action="native",
        column_selectable='single',
        hidden_columns=['Podcast ID'],
        row_selectable='single', # Allowing multiple podcast selections from table
        selected_columns=['Total Downloads'],
        selected_rows=[],
        sort_action="native",
        sort_mode="multi",
        # Styling DataTable; but make it ~spicy~

        style_cell={'textAlign': 'left', 'max-width': '50px'},
        style_data_conditional=[{
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'}
                                ],
        style_header={'font-weight':'bold'},
        style_table={
                    'height': 500,
                    'overflowY': 'auto',
                    'width': '75%',
                    'marginLeft': 'auto', 'marginRight': 'auto'


        })
            
    ]),

    
    ##############PODCAST LEVEL VIEW##################
    html.Div([
    html.H1(id='podcast-title',children='Podcast'),
    ]),

    # Outputs selected podcast ID to user: not sure if we need this later on
    html.Div(id='dd-output-container'),

    # Div for # of episodes/downloads -- produced when podcast is selected
    html.Div(id='pod-stats-div',children=[
        # Title block
        html.Div(id='pod-title-block', 
            className='three columns'),
        # # Episodes block
        html.Div(id='pod-episode-number', 
            className='three columns'),
        #Downloads block
        html.Div(id='pod-downloads-number', 
            className='three columns')
        ]),

    # Podcast table & graph -- appears with episodes of a podcast when selected
    html.Div(id='episode-table-div', className='row',
        children=[

        html.Div(id='episode-table-half', className='six colummns',
        children=[
        dash_table.DataTable(
            id='episode-table',
            columns=[{'name': i, 'id': i} for i in episode_table_cols],
            column_selectable='single',
            data=[],
            hidden_columns=['id'],
            row_selectable='single',
            selected_columns=[],
            selected_rows=[],
            sort_action="native",
            sort_mode='multi',
            style_cell={'textAlign': 'left'},
            style_data_conditional=[{
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                                }],
            style_header={'font-weight':'bold'},
            style_table={
                    'height': 500,
                    'overflowY': 'auto'}#,#
                    # 'width': '50%'}#,
                    # 'marginLeft': 0, 'marginRight': 'auto'}
            
        )
        ]),

        # Podcast table graph --scatter
        html.Div(id='podcast-graph-div', className='six colummns',
                children=[
                dcc.Graph(id='podcast-graph', figure={'layout':{'width':'50%'}})  
        ])

    ])
])

# #################################################################################################

# Callbacks to update figure on screen based on user input
# For more info check: https://dash.plotly.com/basic-callbacks

# #############################
# Highlighting col of podcast table when single col selected
@app.callback(
    Output('podcast-table', 'style_data_conditional'),
    Input('podcast-table', 'selected_columns')
    )
def update_styles(selected_columns):
    return [{
        'if': { 'column_id': i },
        'background_color': '#D2F3FF'
    } for i in selected_columns]

# #############################
# Interval slider for network graph
@app.callback(
    Output(component_id='network-download-graph', component_property='figure'),
    Input(component_id='network-interval-slider', component_property='value'),
    Input(component_id='podcast-table', component_property='selected_columns')
)
def update_network_graph(interval, selected_columns):
    '''
    Function to update downloads figure based on inputted pod ID
    Pod ID parameter set by user selection on our dropdown menu
    '''
    # Getting data from Simplecast for selected podcast

    account_id = '3c7a8b2b-3c19-4d8d-8b92-b17852c3269c'
    print('New Column Type Selected!')
    print('Interval selcted:', interval)
    print('Col selected:', selected_columns)
    intervals = {0: 'day', 1:'week', 2:'month'}
    # table_cols = {'Total Downloads': '/analytics/downloads', 'Total Listeners':  }
    # Getting downloads
    # y_data_label = 'downloads_total'
    if 'Total Downloads' in selected_columns:
        print('Using download data for network graph...')
        dat = getSimplecastResponse(f'/analytics/downloads?account={account_id}&interval={intervals[interval]}')
        df = pd.json_normalize(json.loads(dat), 'by_interval')
        y_data_label = 'downloads_total'

    # Getting time-series listener data
    elif 'Total Listeners' in selected_columns:
        print('Using listener data for network graph...')
        listeners_network = pd.read_csv(os.path.join('.', 'db', 'network-listeners-by-date.csv'))
        # df = listeners_network
        y_data_label = 'total'
        df = group_listener_data(listeners_network, interval)


    # Creating plotly - maybe add multi columns to graph if desired
    f = px.line(df, x="interval", y=y_data_label)

    f.update_xaxes(
    rangeslider_visible=True,
    tickformatstops = [
        dict(dtickrange=[None, 1000], value="%H:%M:%S.%L ms"),
        dict(dtickrange=[1000, 60000], value="%H:%M:%S s"),
        dict(dtickrange=[60000, 3600000], value="%H:%M m"),
        dict(dtickrange=[3600000, 86400000], value="%H:%M h"),
        dict(dtickrange=[86400000, 604800000], value="%e. %b d"),
        dict(dtickrange=[604800000, "M1"], value="%e. %b w"),
        dict(dtickrange=["M1", "M12"], value="%b '%y M"),
        dict(dtickrange=["M12", None], value="%Y Y")
        ])

    return f


# ############################
# Having episode level table appear
@app.callback(
    [Output(component_id='episode-table', component_property='data'),
    Output(component_id='podcast-title', component_property='children'),
    Output(component_id='podcast-graph', component_property='figure')],
    Input(component_id='podcast-table', component_property='selected_rows')

    )
def update_episode_table(selected_rows):
    # Updating the episode table & podcast graph below the main podcast table upon selection
    # Indexing Df - making copy of data
    selected_row = pod_table.loc[selected_rows]
    print('Selected Row & col:', selected_row)#, selected_columns)
    pod_id = selected_row['Podcast ID'].values[0]
    pod_title = selected_row['Podcast Title'].values[0]
    print(pod_title)

    df = get_episode_data(pod_id)
    print('Episode data for pod selected:', df)

    # Getting interval download data for selected pod
    dat = get_podcast_downloads_by_interval(pod_id)

    # Creating downlaods graph for podcast selected
    f = px.line(dat, x='interval', y='downloads_total', title=pod_title)


    return df.to_dict('records'), pod_title , f


# ############################
# Episode selection graph tie-in
# @app.callback(
#     Output('podcast-graph', 'figure'),
#     Input('episode-table', 'selected_rows')
# )
# def update_episode_graph(selected_rows):
#     print(f'Episode selected row:{selected_row}')


# ############################


# Run the app
if __name__ == '__main__':
    app.run_server(
        debug=True
        )







