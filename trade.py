#!/usr/bin/python
import matplotlib.pyplot as plt
import pandas as pd
import urllib2
import datetime

#for google spredsheet download
import requests

def test_run():
	df = pd.read_csv("3.csv")
	#df = pd.read_csv('data/aapl_ohlc.csv', header=0, index_col='Date', parse_dates=True)
	#print df
	#df['close'].plot()
	#date = df['date']
	#print (datetime.datetime.fromtimestamp(
        #int(date)).strftime('%Y-%m-%d %H:%M:%S'))
	#print date[1:-1]
	#print date
	#plt.show()
	long = df['long']
	print long

def test_run2():
	response = requests.get('https://docs.google.com/spreadsheet/ccc?key=1RtKztdvSfTi1uhOzidZX9JGjyjOVf4PfrH6e-lEAJ_Y&output=csv')
	assert response.status_code == 200, 'Wrong status code'
	print response.content
	file = open("3.csv","w")
	file.write(response.content)
	#file.write("date,close,high,low,open\n")
	#file.write(html.split('\n',7)[-1])
	file.close()
	
def test_run3():
	df = pd.read_csv("3.csv")
	long = df['long']
	if long.str() == "Long":
            print long
	
if __name__=="__main__":
	#test_run2()
	response = urllib2.urlopen('https://finance.google.com/finance/getprices?q=KWALITY&f=c,h,l,o,d&i=240500')
	html = response.read()
	#print html.split('\n',7)[-1]
	file = open("2.csv","w")
	#file.write(html)
	#file.write("date,close,high,low,open\n")
	file.write(html.split('\n',7)[-1])
	file.close()
	test_run3()
	print "exit2"
