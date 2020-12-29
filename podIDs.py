'''
Script to get updated list of podcast ids
Should return list of dictionaries with {<podcast title> : <pod ID>} as keys, vals
'''

import http.client
import pandas as pd
from pandas import json_normalize
import json

from getSimplecastResponse import getSimplecastResponse

def podIDs():
	'''Get up-to-date pod IDs and titles from Simpelcast API'''
	pod_name_info = []
	dat = getSimplecastResponse('/podcasts')

	for item in json.loads(dat)['collection']:
		print(item.keys())
		pod_name_info.append({'label': item['title'], 'value': item['id']})

	# print(pod_name_info, len(pod_name_info))
	print(json.loads(dat))

	return pod_name_info


if __name__ == "__main__":
	podIDs()