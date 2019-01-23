import logging
import os

from flask import Flask, request
from google.cloud import storage

from asx import getdata as asxscrape
from yahoo import getdata as yahooscrape

import datetime

app = Flask(__name__)

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']

from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from contextlib import closing
from requests import get


def Output(input):
# should output to file on google cloud storage??
	print(input)

def simple_get(url):
	"""
	Attempts to get the content at url by making an HTTP GET request.
	If the content-type of response is some kind of HTML/XML, return the
	text content, otherwise return None.
	"""
	try:
		with closing(get(url, stream=True)) as resp:
			if is_good_response(resp):
				return resp.content
			else:
				return None

	except RequestException as e:
		log_error('Error during requests to {0} : {1}'.format(url, str(e)))
		return None

def is_good_response(resp):
	"""
	Returns True if the response seems to be HTML, False otherwise.
	"""
	content_type = resp.headers['Content-Type'].lower()
	return (resp.status_code == 200 and content_type is not None and content_type.find('html') > -1)

import sys
def log_error(e):
	"""
	It is always a good idea to log errors.
	This function just prints them, but you can
	make it do anything.
	"""
	# print(e)

	input_code = "xjo"
	input_url = "https://www.asx.com.au/asx/markets/optionPrices.do?by=underlyingCode&underlyingCode=" + input_code + "&expiryDate=&optionType=B"

	raw_html = simple_get(input_url)
	html = BeautifulSoup(raw_html, 'html.parser')

	OptionPriceOutput = ""

	for i, li in enumerate(html.select('tr')):

		ParseText = li.text
		ParseText = ParseText.replace('\n\t\t\t\t',"")
		ParseText = ParseText.replace('\n',"",1)
		ParseText = ParseText.replace(',',"")
		ParseText = ParseText.replace('\n',",")

		if "Code," not in ParseText:
			if "Options," not in ParseText:
				# global OptionPriceOutput
				OptionPriceOutput += ParseText + '\n'

	return OptionPriceOutput



ASX_CODES = ['xjo']

@app.route('/asx')
def asx():

	# Create a Cloud Storage client.
	gcs = storage.Client()

	# Get the bucket that the file will be uploaded to.
	bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

	# Create a new blob and upload the file's content.
	for t in ASX_CODES:
		blob = bucket.blob('asx_{}.csv'.format(t))

		# data = log_error('abc')
		data = asxscrape(t,'','B')
		# data = str(datetime.datetime.now())
		old_data = b''

		try:
			old_data = blob.download_as_string()
		except:
			pass
		if not old_data:
			old_data = '{},{},{},{},{},{},{},{},{},{},{}\n'.format('Retr_date',
																   'Contract_name', 'EDate', 'PC', 'Strike', 'Bid', 'Ask', 'Last', 'Volume', 'Openinterest', 'MarginPrice'
																   ).encode('utf-8')
		# return "==>" + str(type(old_data)).replace('<','')
		# print(type(old_data))
		# print(type(data))
		consolidated = old_data + b"\n" + data.encode('utf-8')
		# print(type(consolidated))
		# data = 'hello testststst'
		blob.upload_from_string(consolidated)

		# The public URL can be used to directly access the uploaded file via HTTP.
		# 	return 'You can access content at https://storage.cloud.google.com/{}/{}'.format(CLOUD_STORAGE_BUCKET, 'abc.txt')

	return 'Done'

YAHOO_TICKERS = ['AAPL', 'GOOG']



@app.route('/yho')
def yho():

	# Create a Cloud Storage client.
	gcs = storage.Client()

	# Get the bucket that the file will be uploaded to.
	bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

	# Create a new blob and upload the file's content.
	for t in YAHOO_TICKERS:
		blob = bucket.blob('yahoo_{}.csv'.format(t))

		# data = log_error('abc')
		data = yahooscrape(t)
		# data = str(datetime.datetime.now())
		old_data = b''

		try:
			old_data = blob.download_as_string()
		except:

			pass
		if not old_data:
			old_data = '{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n'.format('Retr_date', 'EDate',
																   'Contract_name', 'Last_tradedate', 'Strike', 'Lastprice', 'Bid', 'Ask', 'Change',
																			'Perchange', 'Volume', 'Openinterest', 'Implied_volatility', 'PC'
																   ).encode('utf-8')
		# return "==>" + str(type(old_data)).replace('<','')
		# print(type(old_data))
		# print(type(data))
		consolidated = old_data + b"\n" + data.encode('utf-8')
		# print(type(consolidated))
		# data = 'hello testststst'
		blob.upload_from_string(consolidated)

		# The public URL can be used to directly access the uploaded file via HTTP.
		# 	return 'You can access content at https://storage.cloud.google.com/{}/{}'.format(CLOUD_STORAGE_BUCKET, 'abc.txt')

	return 'Done'

@app.errorhandler(500)
def server_error(e):
	logging.exception('An error occurred during a request.')
	return """
	An internal error occurred: <pre>{}</pre>
	See logs for full stacktrace.
	""".format(e, 500)


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_storage_app]
