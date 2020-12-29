
'''
Python script to get HTTP responses from Simplecast API and returns dataframes usable for our Dash app
'''
import http.client
import pandas as pd
from pandas import json_normalize
import json



class getSimpleCast(object):
	'''
	object to get simplecast API responses
	Re-formats the JSON obejcts into pandas dataframes & csv files that are usable by plotly
	'''
	def __init__(self):
		self.auth = 'Bearer eyJhcGlfa2V5IjoiMmY4MThhMDg3NzEyOTYxZTk3NzcwNTM3NDJjMmJiNmUifQ=='
		self.payload = ''
		self.url = "api.simplecast.com"
		self.headers = {'authorization': self.auth}
		self.conn = http.client.HTTPSConnection(self.url)


	def getResponse(self, query_params, data_label):
		'''
		Method to establish connection to Simplecast API
		query_params - string for HTTP request params
		Check Simplecast docs for this
		'''
		conn = http.client.HTTPSConnection(self.url)
		conn.request("GET", query_params, self.payload, self.headers)
		res = conn.getresponse()
		data = res.read()

		# return data.decode('utf-8') #str

		# Using json_normalize to convert API response JSON object to pandas df
		# https://stackoverflow.com/questions/44802160/convert-json-api-response-to-pandas-dataframe#comment113544642_44802232
		df = json_normalize(json.loads(data.decode('utf-8')), data_label)

		# Returning json-style string as API response
		return df

	def downloadsByPod(self, pod_id):
		'''
		Method to get downloads by interval for each podcast
		'''
		params = f'/analytics/downloads?podcast={pod_id}'
		response = self.setupHTTP(params)
		response_json = json.loads(response)
		print('Response:', response, response_json)
		df = json_normalize(response_json, 'by_interval')

		return df

	def getNetworkData(self):
		'''
		Method to return data for all network podcasts
		'''
		return 'All the data!'




if __name__=='__main__':
	test_id = '649a9132-4298-4d65-b650-8360b693520e'
	gsc = getSimpleCast()

	sh = gsc.getResponse(f'/analytics/downloads?podcast={test_id}', 'by_interval')
	# gsc.downloadsByPod(f'/analytics/downloads?podcast={test_id}')
	print(sh)


