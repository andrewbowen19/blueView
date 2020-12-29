'''
Python script as a function to grab simplecast API data
'''
import http.client
import pandas as pd
from pandas import json_normalize
import json


def getSimplecastResponse(query_params):
	'''
	Method to establish connection to Simplecast API
	query_params - string for HTTP request params
	Check Simplecast docs for this
	'''
	auth = 'Bearer eyJhcGlfa2V5IjoiMmY4MThhMDg3NzEyOTYxZTk3NzcwNTM3NDJjMmJiNmUifQ=='
	payload = ''
	url = "api.simplecast.com"
	headers = {'authorization': auth}
	conn = http.client.HTTPSConnection(url)
	conn.request("GET", query_params, payload, headers)
	res = conn.getresponse()
	data = res.read()

	return data.decode('utf-8') #str

def podIDs():
	'''Get up-to-date pod IDs and titles from Simpelcast API'''
	pod_name_info = []
	dat = getSimplecastResponse('/podcasts?limit=1000')
	# print(json.loads(dat)['collection'])

	# Writing API title-id responses to list
	for item in json.loads(dat)['collection']:
		# print(item)
		pod_name_info.append({'label': item['title'], 'value': item['id']})

	# print('Podcast Titles & IDs: ', pod_name_info)
	# print('# of podcasts returned:', len(pod_name_info))

	return pod_name_info

if __name__=='__main__':
	test_id = '649a9132-4298-4d65-b650-8360b693520e'
	usa_id = str(6252001)
	# g = getSimplecastResponse('/podcasts?limit=1000')
	g = getSimplecastResponse(f'/analytics/location?podcast={test_id}')#state={usa_id}')
	print(g)
