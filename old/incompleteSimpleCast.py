'''
Python script as a function to grab simplecast API data
'''
import http.client
import pandas as pd
from pandas import json_normalize
import json


def getSimplecastResponse(self, query_params, data_label):
	'''
	Method to establish connection to Simplecast API
	query_params - string for HTTP request params
	Check Simplecast docs for this
	'''
	conn = http.client.HTTPSConnection(self.url)
	conn.request("GET", query_params, self.payload, self.headers)
	res = conn.getresponse()
	data = res.read()

	return data.decode('utf-8') #str



if __name__=='__main__':

