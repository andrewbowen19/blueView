'''
Script to get network data for login view of bluView
This script should be scheduled to run once per day to update network stats for log-in view of bluView
'''

import os
import numpy as np
import pandas as pd
import json
# from pandas import json_normalize
import http.client
import datetime
from utils import getSimplecastResponse, podIDs

# Blue Wire Account ID
account_id = '3c7a8b2b-3c19-4d8d-8b92-b17852c3269c'
test_id = '93cc0b3a-49ea-455f-affd-ac01fdafd761'
pod_ids = [x['value'] for x in podIDs()]
def network_data():
	'''
	Function to get network-level data (# pods, Total # downloads, Total # Episodes)
	Should be scheduled run (i.e. runs once per day/hour)
	Want this to update a db/file for our app to pull from
	'''
	# pod_ids = [x['value'] for x in podIDs()]
	# Getting download and episode totals for each pod in network
	episodes = []
	downloads = []

	downloads_by_interval = []


	for p in pod_ids:
		print(f'Getting data for podcast: {p}')

		# Download data grab
		download_dat = json.loads(getSimplecastResponse(f'/analytics/downloads?podcast={p}'))
		print(type(download_dat['by_interval']),download_dat)

		downloads_by_interval.append(pd.DataFrame(download_dat['by_interval']))
		pod_downloads = download_dat['total']
		print(f'Total # of downloads: {pod_downloads}')

		# Episode data grab
		episode_data = json.loads(getSimplecastResponse(f'/podcasts/{p}/episodes'))
		n_episodes = episode_data['count']
		print(f'Number of episodes: {n_episodes}')
		
		
		# listener data for each pod
		# listener_dat = json.loads(getSimplecastResponse(f'/analytics/episodes/listeners?podcast={p}'))
		# unique_listeners = listener_dat['total']
		# print('LISTENERS:',listener_dat.keys())



		print('#########################')
		# Writing data to list, then a file
		downloads.append(pod_downloads)
		episodes.append(n_episodes)

	# Getting Network totals
	downloads_total = np.sum(downloads)
	episodes_total = np.sum(episodes)

	# Setting up a DF with network stats

	network_stats = pd.DataFrame.from_dict({'Number of Podcasts': [len(pod_ids)],
								  'Total Downloads': [downloads_total],
								  'Total Episodes':[episodes_total]})

	print('#########################')
	print('NETWORK TOTALS')
	print(f'Total Downloads: {downloads_total}')
	print(f'Total Episodes: {episodes_total}', '\n')


	# Getting network downlaods table -- want to sum downlaods based on common interval vals
	network_downloads = pd.concat(downloads_by_interval)
	network_downloads_grouped = network_downloads.groupby('interval', as_index=False)['downloads_total'].sum()
	print('NETWORK DOWNLOADS BY DAY:')
	print(network_downloads_grouped, network_downloads_grouped.columns, type(network_downloads_grouped))

	# Writing to a csv for both network stats and downloads
	network_downloads_grouped.to_csv(os.path.join('.', 'db', 'network-downloads.csv'), index=False)
	network_stats.to_csv(os.path.join('.', 'db', 'network-stats.csv'), index=False)

def network_pull():
	'''
	Function to get netweork data with one pull from our BW simplecast account
	From Lem's email
	add '/current_user' to query string
	'''
	# Figure out how to set this as an env variable
	
	res = getSimplecastResponse(f'/analytics/podcasts?account={account_id}&limit=1000')
	res_dict = json.loads(res)
	# print(res_dict['collection'])
	# print(res_dict.keys(), len(res_dict['collection']))

	df = pd.DataFrame(res_dict['collection'])
	print(df)

	return df

def get_network_downloads():
	'''
	Function to grab network download data
	Returns df with columns ['interval', 'downloads_total', 'downloads_percent'] & total downloads for network
	'''

	response = getSimplecastResponse(f'/analytics/downloads?account={account_id}') # &limit=1000

	total_downloads = json.loads(response)['total']
	df = pd.DataFrame(json.loads(response)['by_interval'])
	print(type(total_downloads))


	df.to_csv(os.path.join('.', 'db', 'network-downloads.csv'), index=False)
	return df, total_downloads


def get_listeners():
	'''
	Getting unique listener data for each pod
	'''
	listener_dfs = []
	for p in pod_ids:


		listener_dat = json.loads(getSimplecastResponse(f'/analytics/listeners?podcast={p}'))
		print(listener_dat['by_interval'])
		listener_dfs.append(pd.DataFrame(listener_dat['by_interval']))


	listeners = pd.concat(listener_dfs)
	
	listener_path = os.path.join('.', 'db', 'network-listeners-by-date.csv')
	listeners = listeners.groupby('interval', as_index=False)['total'].sum()
	print('Listeners by date:\n', listeners)
	listeners.to_csv(listener_path, index=False)
	return listeners


def network_pod_table():
	'''
	We're sitting down and writng this table

	Should output table (can be csv for now) with following cols:
	['Pod Title', '# Downloads', '# Listeners', '#Avg Downloads']
	'''
	pod_ids = [x['value'] for x in podIDs()]

	print('Getting Network Table Data')
	podcasts = []
	for p in pod_ids:
		 # Dictionary to hold 4 values: Title, # Downloads, # Listeners, Avg Downloads
		pod_data = {}

		# Getting Pod Title; this should be simpler
		title = json.loads(getSimplecastResponse(f'/podcasts/{p}'))['title']
		pod_data['Podcast Title'] = title

		# Getting total downloads for pod
		downloads = json.loads(getSimplecastResponse(f'/analytics/downloads?podcast={p}'))['total']
		pod_data['Total Downloads'] = downloads

		# Getting listener data
		listeners = json.loads(getSimplecastResponse(f'/analytics/episodes/listeners?podcast={p}'))['total']
		pod_data['Total Listeners'] = listeners

		# Getting Avg Download data
		avg_downloads = json.loads(getSimplecastResponse(f'/analytics/episodes/average_downloads?podcast={p}'))['total']
		pod_data['Average Downloads'] = avg_downloads

		# Setting up pod ID to be included
		pod_data['Podcast ID'] = p

		print('Pod Data:', pod_data)
		podcasts.append(pod_data)


		print('######################')


	df = pd.DataFrame(podcasts)
	print('Final Dataframe:\n', df)
	csv_path = os.path.join('.', 'db', 'podcast-table.csv')
	df.to_csv(csv_path, index=False)
	return df

# Look into scheduling this script
# May want to add it to utils script
if __name__ == '__main__':
	network_data()
	get_network_downloads()
	get_listeners()
	network_pod_table()



