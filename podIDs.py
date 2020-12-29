'''
Script to get updated list of podcast ids
Should return list of dictionaries with {<podcast title> : <pod ID>} as keys, vals
Used in our app script to produce label, val list for user dropdown menu
'''

import http.client
import pandas as pd
from pandas import json_normalize
import json

from getSimplecastResponse import getSimplecastResponse

def podIDs():
	'''Get up-to-date pod IDs and titles from Simpelcast API'''
	pod_name_info = []
	dat = getSimplecastResponse('/podcasts?limit=1000')
	print(dat)
	# print(json.loads(dat)['collection'])

	# Writing API title-id responses to list
	for item in json.loads(dat)['collection']:
		# print(item)
		pod_name_info.append({'label': item['title'], 'value': item['id']})

	# print('Podcast Titles & IDs: ', pod_name_info)
	# print('# of podcasts returned:', len(pod_name_info))

	return pod_name_info


if __name__ == "__main__":
	podIDs()