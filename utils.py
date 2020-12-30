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
		# print(item)
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

if __name__=='__main__':
	test_id = '93cc0b3a-49ea-455f-affd-ac01fdafd761'
	usa_id = str(6252001)
	interval='month'
	episode_id = 'e51b5998-749f-4ca7-9f39-b17cda147746'

	g = getSimplecastResponse(f'/analytics/downloads?episode={episode_id}&interval={interval}')
	print(g)
	# # print(podIDs())
	# e = episodeIDs(test_id)
	# print(e)
