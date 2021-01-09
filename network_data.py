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


def network_data():
	'''
	Function to get network-level data (# pods, Total # downloads, Total # Episodes)
	Should be scheduled run (i.e. runs once per day/hour)
	Want this to update a db/file for our app to pull from
	'''
	pod_ids = [x['value'] for x in podIDs()]
	# Getting download and episode totals for each pod in network
	episodes = []
	downloads = []

	downloads_by_interval = []


	for p in pod_ids:
		print(f'Getting data for podcast: {p}')

		# Download data grab
		download_dat = json.loads(getSimplecastResponse(f'/analytics/downloads?podcast={p}'))
		# print(type(download_dat['by_interval']),download_dat['by_interval'])

		downloads_by_interval.append(pd.DataFrame(download_dat['by_interval']))
		pod_downloads = download_dat['total']
		print(f'Total # of downloads: {pod_downloads}')

		# Episode data grab
		episode_data = json.loads(getSimplecastResponse(f'/podcasts/{p}/episodes'))
		n_episodes = episode_data['count']
		print(f'Number of episodes: {n_episodes}')
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

	# Writing to a csv for both network stats and 

	network_downloads_grouped.to_csv('network-downloads.csv', index=False)
	network_stats.to_csv('network-stats.csv', index=False)



# Look into scheduling this script
if __name__ == '__main__':
	network_data()



