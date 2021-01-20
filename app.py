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
from utils import getSimplecastResponse, podIDs, episodeIDs, get_episode_data

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
        columns=[{'name': i, 'id': i} for i in pod_table.columns],
        
        data=pod_table.to_dict('records'),
        # filter_action="native",
        column_selectable='single',
        hidden_columns=['Podcast ID'],

        row_selectable='multi', # Allowing multiple podcast selections from table
        selected_columns=[],
        selected_rows=[],
        sort_action="native",
        # Styling DataTable; but make it ~spicy~

        style_cell={'textAlign': 'left', 'max-width': '50px'},
        style_data_conditional=[{
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'}
                                # },
                                # {'if': {'column_id': 'Total Downloads'},
                                # 'width' : '60px'},
                                # {'if': {'column_id': 'Total Listeners'},
                                # 'width' : '60px'},
                                # {'if': {'column_id': 'Average Downloads'},
                                # 'width' : '60px'}
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
    # Dropdown menu for user interaction
    # dcc.Dropdown(
    #     id='pod-title-dropdown',
    #     options=pod_id_list,
    #     searchable=True
    # )
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

    # Podcast table -- appears with episodes of a podcast when selected
    html.Div(id='episode-table-div',
        children=[
        dash_table.DataTable(
            id='episode-table',
            columns=[{'name': i, 'id': i} for i in episode_table_cols],
            column_selectable='single',
            data=[],
            hidden_columns=['id'],
            
            sort_action="native",
            style_cell={'textAlign': 'left'},
            style_data_conditional=[{
                                'if': {'row_index': 'odd'},
                                'backgroundColor': 'rgb(248, 248, 248)'
                                }],
            style_header={'font-weight':'bold'},
            style_table={
                    'height': 500,
                    'overflowY': 'auto'
                        }
            )


        ]),

    # Downloads per time period graph
    # html.Div([
    #     # Graph of downloads vs time
    #     html.Div([
    #     dcc.Graph(
    #     id='downloads-graph'
    #      ),
    #     # ]),

    #     # html.Div([
    #     # Slider to toggle interval
    #     dcc.Slider(
    #         id='interval-slider', 
    #         min=0, max=2, 
    #         marks={0: 'day', 1:'week', 2:'month'},
    #         value=1)
    #         ])
    # ])
    
    # Div for bottom 2 graphs -- side by side
    # html.Div([
    # # Distribution Platform Graph
    # html.Div([
    #         dcc.Graph(
    #         id='dist-platform-graph')
    #         ],  className='six columns'),
    # # Country Downlaods graph 
    # html.Div([

    #     dcc.Graph(
    #     id='country-downloads-graph')

    #     ],  className='six columns')
    # ]),

    # html.Div([
    # ########### EPISODE LEVEL VIEW ##############
    #     html.H2('Episode-Level Data'),

    # # Episode Dropdown
    #     dcc.Dropdown(
    #     id='episode-dropdown',
    #     # options=episodeIDs(),
    #     searchable=True
        
    # ),


    # ], id='episode-level'),

    # Episode Downlaod graph - same format as podcast donwload graph
    # html.Div([
    #     dcc.Graph(id='episode-download-graph'),

    #     dcc.Slider(
    #         id='ep-interval-slider', 
    #         min=0, max=2, 
    #         marks={0: 'day', 1:'week', 2:'month'},
    #         value=1)

    #     ])

    
])

# #################################################################################################

# Callbacks to update figure on screen based on user input
# For more info check: https://dash.plotly.com/basic-callbacks

# #############################
# Interval slider for network graph
@app.callback(
    Output(component_id='network-download-graph', component_property='figure'),
    Input(component_id='network-interval-slider', component_property='value')
)
def update_network_graph(interval):
    '''
    Function to update downloads figure based on inputted pod ID
    Pod ID parameter set by user selection on our dropdown menu
    '''
    # Getting data from Simplecast for selected podcast
    account_id = '3c7a8b2b-3c19-4d8d-8b92-b17852c3269c'
    print('Interval selcted:', interval)
    intervals = {0: 'day', 1:'week', 2:'month'}
    dat = getSimplecastResponse(f'/analytics/downloads?account={account_id}&interval={intervals[interval]}')
    df = pd.json_normalize(json.loads(dat), 'by_interval')
    # print(df)

    # Creating plotly
    f = px.line(df, x="interval", y="downloads_total")
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
    ]
)

    return f

# #############################
# Updating selected pod from dropdown menu
@app.callback(
    Output(component_id='dd-output-container', component_property='children'),
    Input(component_id='pod-title-dropdown', component_property='value')
)
def update_output_div(input_value):
    return f'Your selected podcast ID: {input_value}'

# #############################
# Getting pod stats
@app.callback(
    Output(component_id='pod-title-block', component_property='children'),
    Input(component_id='pod-title-dropdown', component_property='value')
)
def update_pod_stats(pod_title):
    # update pod name, # downloads, # episodes
    return f'Podcast Title: {pod_title} '#, " <# Downloads> ", ' <# Episodes> ']


# #############################
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
# @app.callback(
#     Output(component_id='dist-platform-graph', component_property='figure'),
#     Input(component_id='pod-title-dropdown', component_property='value')
# )
# def update_platform_graph(pod_id):
#     '''update distribution platform graph based on podcast selection'''
#     dat = getSimplecastResponse(f'/analytics/technology/applications?podcast={pod_id}')
#     dat2json = json.loads(dat)
#     df = pd.DataFrame(dat2json['collection'])
#     print(df)
#     print(df.columns)
#     fig = px.histogram(df, 
#                   x='name', y='downloads_total',
#                   labels={'name': 'Platform Name', 'downloads_total': 'Downloads'},
#                   range_x=[0,10],nbins=10,
#                   title='Downloads per Distribution platform')
#     return fig

# # ############################
# # Country Download Map
# @app.callback(
#     Output(component_id='country-downloads-graph', component_property='figure'),
#     Input(component_id='pod-title-dropdown', component_property='value')
# )
# def update_map(pod_id):
#     '''update map plot'''
#     dat = getSimplecastResponse(f'/analytics/location?podcast={pod_id}')
#     df = pd.DataFrame(json.loads(dat)['countries'])
#     fig = px.scatter_geo(df, locations="name", locationmode= 'country names',
#                      hover_name="name", size="downloads_total",
#                      projection="natural earth", title='Downloads Per Country')
#     return fig


# ############################
# Episode Level Dropdown
# @app.callback(
#     Output(component_id='episode-dropdown', component_property='options'),
#     Input(component_id='pod-title-dropdown', component_property='value')
# )
# def update_episode_dropdown(pod_id):
#     print('Podcast: Selected', pod_id)
#     episode_options = episodeIDs(pod_id)
#     print('Episode list (with tokens):', episode_options)
#     return episode_options

# ############################
# Episode Level Downloads graph
# Calback to update graph from dropdown menu
# @app.callback(
#     Output(component_id='episode-download-graph', component_property='figure'),
#     Input(component_id='pod-title-dropdown', component_property='value'),
#     Input(component_id='episode-dropdown', component_property='value'),
#     Input(component_id='ep-interval-slider', component_property='value')
# )
# def update_episode_graph(pod_id, episode_id, interval):
#     '''
#     Function to update downloads figure based on inputted pod ID and ep ID
#     Pod ID parameter set by user selection on our dropdown menu
#     '''
#     # Getting data from Simplecast for selected podcast/episode
#     intervals = {0: 'day', 1:'week', 2:'month'}
#     print('Episode Interval selcted:', intervals[interval])
#     print('Selected Episode ID:', episode_id)
#     print('Getting Episode Data from Simplecast...')

#     dat = getSimplecastResponse(f'/analytics/downloads?episode={episode_id}&interval={intervals[interval]}')
#     print(dat)
#     df = pd.json_normalize(json.loads(dat), 'by_interval')
#     print('Got Data!')
#     print('Episode Data pulled:', df)

#     # Creating plotly figure within our Dash app
#     fig = px.line(df, x="interval", y="downloads_total")
#     return fig

# ############################
# Updating podcast tile when selection is made
# @app.callback(
#     Output(component_is='podcast-title', component_property='children'),
#     Input(component_id='podcast-table', component_property='selected_rows')
#     )
# def update_pod_title():
#     '''Updating podcast title when selected by user'''


# ############################
# Having episode level table appear

@app.callback(
    [Output(component_id='episode-table', component_property='data'),
    Output(component_id='podcast-title', component_property='children')],
    Input(component_id='podcast-table', component_property='rows'), 
    Input(component_id='podcast-table', component_property='selected_rows')
    )
def update_episode_table(rows,selected_rows):
    # print('PODCAST INDEX SELECTED BY USER:',selected_rows)
    # Indexing Df - making copy of data
    selected_row = pod_table.loc[selected_rows]
    print('Selected Row:', selected_row)
    pod_id = selected_row['Podcast ID'].values[0]

    df = get_episode_data(pod_id)
    print(df.to_dict('records'))

    return df.to_dict('records'), selected_row['Podcast Title'] 






if __name__ == '__main__':
    app.run_server(
        debug=True
        )








