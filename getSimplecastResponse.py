'''
Python script as a function to grab simplecast API data
'''
import http.client
import pandas as pd
from pandas import json_normalize
import json



def getSimplecastResponse(query_params):#, data_label):
	'''
	Method to establish connection to Simplecast API
	query_params - string for HTTP request params
	Check Simplecast docs for this
	'''
	auth = 'Bearer eyJhcGlfa2V5IjoiMmY4MThhMDg3NzEyOTYxZTk3NzcwNTM3NDJjMmJiNmUifQ=='
	payload = ''
	url = "api.simplecast.com"
	headers = {'authorization': auth}
	conn = http.client.HTTPSConnection(url, timeout=60)
	conn.request("GET", query_params, payload, headers)
	res = conn.getresponse()
	data = res.read()

	return data.decode('utf-8') #str



if __name__=='__main__':
	test_id = '649a9132-4298-4d65-b650-8360b693520e'
	g = getSimplecastResponse(f'/analytics/downloads?podcast={test_id}', 'by_interval')
	print(g)
