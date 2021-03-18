'''
Python script as a function to grab simplecast API data
'''
import http.client
import pandas as pd
from pandas import json_normalize
import json
import numpy as np
import os


def getSimplecastResponse(query_params):
    '''
    Method to establish connection to Simplecast API
    query_params - string for HTTP request params
    Check Simplecast docs for this
    '''
    # Figure out how to set this as an env variable
    auth = 'Bearer eyJhcGlfa2V5IjoiMmY4MThhMDg3NzEyOTYxZTk3NzcwNTM3NDJjMmJiNmUifQ=='
    payload = ''
    url = "api.simplecast.com"
    headers = {'authorization': auth}
    conn = http.client.HTTPSConnection(url)
    conn.request("GET", query_params, payload, headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()

    return data.decode('utf-8') #str

def podIDs():
    '''Get up-to-date pod IDs and titles from Simpelcast API'''
    pod_name_info = []
    dat = getSimplecastResponse('/podcasts?limit=1000')
    # print(json.loads(dat)['collection'])

    # Writing API title-id responses to list
    for item in json.loads(dat)['collection']:
        pod_name_info.append({'label': item['title'], 'value': item['id']})

    # print('Podcast Titles & IDs: ', pod_name_info)
    # print('# of podcasts returned:', len(pod_name_info))

    return pod_name_info

def episodeIDs(pod_id):
    '''
    Function to get updated episode ids for a given podcast
    '''
    dat = getSimplecastResponse(f'/podcasts/{pod_id}/episodes?limit=1000')
    # print(json.loads(dat)['collection'])
    episode_id_titles = []
    for ep in json.loads(dat)['collection']:
        # print(ep['id'])
        pub_date = ep['published_at']
        label = ep['title'] + '\t' + f'(Published: {pub_date})'
        episode_id_titles.append({'label': f'{label}', 'value': ep['id']})

    return episode_id_titles

def formatNetworkQueryString():
    '''
    Function to format network query string based on # of podcasts in network
    Should scale as # of pods increases
    Should return list of strings so we can loop through it in the network data call
    '''

    pod_ids = ['&podcast='+x['value'] for x in podIDs()] # we need to get better at using llist comprehensions
    l = []
    for i in range(0, len(pod_ids), 100):
        l.append(pod_ids[i:i + 100])
    # print(len(l[0]))
    pl = []
    for ll in l:
        pod_ids_str = str(ll)[1:-1].replace(' ','')
        pod_ids_str = pod_ids_str.replace("'", '')
        pod_ids_str = pod_ids_str.replace(",", '')[1::]#removes first unecessary '&' symbol from str
        # print(pod_ids_str)
        pl.append(pod_ids_str)
    # print(pl)
    return pl

# Need a func to get network level data from Simplecast -- called on entry
def networkLevel():
    '''
    Function to get network level data from Simplecast
    Will be displayed on login to web app
    '''
    # TODO:

    # WRITE THIS SO IT DOESNT TAKE FOREVER TO RUN ON SIGN-IN
    # WOULD LIKE ONE API CALL MAX WITH ALL PODCASTS PULLED
    # EVEN BETTER, DOES SIMPLECAST HAVE A NETWORK LEVEL PULL?
    # dat = getSimplecastResponse('/analytics/?limit=1000')
    # print(json.loads(dat)['collection'])
    # Formatting API Call query string
    downloads_by_pod = []
    query_str_list = formatNetworkQueryString()
    pod_ids = ['&podcast='+x['value'] for x in podIDs()]
    # for s in query_str_list:
    for p in pod_ids:
        # ... (Call api with each string and append returned val)

        print('QUERY STRING:')
        print(f'/analytics/downloads?{p}')

        pod_data = json.loads(getSimplecastResponse(f'/analytics/downloads?{p}'))['total']
    # pod_data.append(json.loads(getSimplecastResponse(f'/analytics?podcast={pod_ids_str}')))
        print('##########################')
        print('##########################')
        print(pod_data)
    # network_data = pd.DataFrame(pod_data)
    # network_data = getSimplecastResponse(f'/analytics?podcast={pod_ids}')
    # return network_data
        downloads_by_pod.append(pod_data)
    print('FINAL API RESPONSE:')
    print(downloads_by_pod)

def get_episode_data(pod_id):
    '''
    Function to get episode data (donwloads, listeners)
    And return it for  an individual podcast
    
    returns: pandas df object with individual episode data
    df.columns = ['title', 'published_at', 'number', 'id', 'downloads', 'listeners']

    '''
    print('Pod ID selected by user:', pod_id)
    pod_dat = json.loads(getSimplecastResponse(f'/analytics/episodes?podcast={pod_id}&limit=1000')) # Getting downloads
    list_dat = json.loads(getSimplecastResponse(f'/analytics/episodes/listeners?podcast={pod_id}&limit=1000')) # getting listeners

    # listeners and downloads dfs
    downloads_df = pd.DataFrame(pod_dat['collection'])
    listeners_df = pd.DataFrame(list_dat['collection'])

    # print(downloads_df, listeners_df)
    # Joining listeners and downloads 
    df = pd.concat([downloads_df.reset_index(drop=True), listeners_df.reset_index(drop=True)], axis=1,copy=False)
    df = df.loc[:,~df.columns.duplicated()] # Dropping duplicate cols

    # print('Joined DF:', df, '\n', df.columns)
    table_cols = ['title', 'published_at', 'id', 'downloads', 'listeners']
    table = df[table_cols]
    table['downloads'] = [x.get('total', 0) for x in table['downloads']]
    table['listeners'] = [x.get('total', 0) for x in table['listeners']]

    # Changing pub date format for readability
    table['published_at'] = pd.to_datetime(table['published_at'], utc=True).dt.date 

    # print('Episode data table: \n', table)
    return table    

def group_listener_data(listener_data, interval):
    '''
    Function to group listener data for whole network (from csv) by day, week or month
    Interval - should be interval selected by user on slider (int) {0:'Day', 1:'Week', 2: 'Month'}
    '''
    print('Using listener data for network graph...')
    # Sub in listener_data with global read in in real app
    df = listener_data# = pd.read_csv(os.path.join('.', 'db', 'network-listeners-by-date.csv'))
    y_data_label = 'total'
    # Converting to selected interval
    print('')
    # Day interval
    if interval==0:
        df = df
        # print('Listener data grouped by day:\n', df)

    # Week grouping (default)
    elif interval == 1:
        df['interval'] = pd.to_datetime(df['interval'], utc=True)
        df = df.resample('W',on='interval').sum()
        # print('Listener Data Grouped by week:\n', df)

    # Month
    elif interval ==2:
        df['interval'] = pd.to_datetime(df['interval'], utc=True)
        # https://stackoverflow.com/questions/53700107/pandas-time-series-resample-binning-seems-off
        df = df.resample('BM', on='interval').sum()

        # print('Listener Data Grouped by month:\n', df)
    df['interval'] = df.index
    print('Listeners Data (grouped):\n', df, df.columns)

    return df

def get_podcast_downloads_by_interval(pod_id):
    '''
    Get the downlaods by interval for a given pod
    Returnd a dataframe with downlaods by interval
    '''

    dat = json.loads(getSimplecastResponse(f'/analytics/downloads?podcast={pod_id}'))
    interval_data = dat['by_interval']

    df = pd.DataFrame(interval_data)

    # print(df)
    return df


# Can test included functions if needed
if __name__=='__main__':
    # Test podcast ID
    test_id = '93cc0b3a-49ea-455f-affd-ac01fdafd761'
    usa_id = str(6252001)
    interval='month'
    episode_id = 'e51b5998-749f-4ca7-9f39-b17cda147746'

    # Simplecast Account ID
    account_id = '3c7a8b2b-3c19-4d8d-8b92-b17852c3269c'

    listener_data = pd.read_csv(os.path.join('.', 'db', 'network-listeners-by-date.csv'))



    







