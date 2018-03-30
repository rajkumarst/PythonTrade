#!/usr/bin/python 
"""
Retrieve intraday stock data from Google Finance.
"""
import matplotlib.pyplot as plt

from indicators import ema,money_flow_index,typical_price,rsi,macd,money_flow_index2,bollinger_bands
#from indicators import *
import csv
import datetime
import re

import pandas as pd
import requests

def get_google_finance_intraday(ticker, period=60, days=1):
    """
    Retrieve intraday stock data from Google Finance.

    Parameters
    ----------
    ticker : str
        Company ticker symbol.
    period : int
        Interval between stock values in seconds.
    days : int
        Number of days of data to retrieve.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the opening price, high price, low price,
        closing price, and volume. The index contains the times associated with
        the retrieved price values.
    """

    uri = 'http://www.google.com/finance/getprices' \
          '?i={period}&p={days}d&f=d,o,h,l,c,v&df=cpct&q={ticker}'.format(ticker=ticker,
                                                                          period=period,
                                                                          days=days)
    print uri
    page = requests.get(uri)
    reader = csv.reader(page.content.splitlines())
    #columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    columns = [ 'CLOSE', 'HIGH','LOW','OPEN','VOLUME']
    rows = []
    times = []
    for row in reader:
        if re.match('^[a\d]', row[0]):
            if row[0].startswith('a'):
                start = datetime.datetime.fromtimestamp(int(row[0][1:]))
                times.append(start)
            else:
                times.append(start+datetime.timedelta(seconds=period*int(row[0])))
            rows.append(map(float, row[1:]))
    if len(rows):
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'),
                            columns=columns)
    else:
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'))

def add_row_count(data):
	count=0
	data['row_index'] = 0

	for index,row in data.iterrows():	
			data.set_value(index, 'row_index', count)
			count +=1


ticker = "HCLTECH"
#15 mins
data =  get_google_finance_intraday(ticker, period=900, days=100)
#30 mins
#data =  get_google_finance_intraday(ticker, period=1800, days=100)
#60 mins
#data =  get_google_finance_intraday(ticker, period=3600, days=100)
#daily chart
#data =  get_google_finance_intraday(ticker, period=86400, days=100)

#data =  get_google_finance_intraday("HCLTECH", 600)
#data.reset_index(drop=False)
#new_index = ['CLOSE','OPEN']
#data.reindex(new_index)
#print data
#exit(0)
#print ema(data)
ema(data, 5, 'CLOSE')
ema(data, 10, 'CLOSE')
#ema2 = ema(data, 5, 'CLOSE')
print " ---------------------"
add_row_count(data)
#print data
#print ema2
#print money_flow_index(data)
#data2 = data
#print data
print " ---------------------"
# RSI calculation

##['money_flow_index']
data2 = data
data = data.set_index('row_index')
bollinger_bands(data, trend_periods=20, close_col='CLOSE')
data3 = money_flow_index2(data, 10, 'VOLUME')
#print data3
#pd.merge(data2,data3,on='row_index')
#exit(0)
for index,row in data2.iterrows():
	low_n = int(row['row_index'])
	data2.set_value(index, 'money_flow_index', data3.at[int(row['row_index']),'money_flow_index'])
#bol_bands_middle  bol_bands_upper  bol_bands_lower
	data2.set_value(index, 'bol_bands_middle', data3.at[int(row['row_index']),'bol_bands_middle'])
	data2.set_value(index, 'bol_bands_upper', data3.at[int(row['row_index']),'bol_bands_upper'])
	data2.set_value(index, 'bol_bands_lower', data3.at[int(row['row_index']),'bol_bands_lower'])

#data2.plot(x='row_index',y=['ema5','CLOSE'])
#data2.plot(x='row_index',y=['ema5','CLOSE'])
#data2['money_flow_index','ema5','CLOSE'].plot()
#data2['ema5','CLOSE'].plot()
#data2.plot(subplots=True, figsize=(6, 6));
#data2.plot(legend=False)
#plt.legend(loc='best')
#plt.show()
"""
#grap = data2.drop(['OPEN', 'LOW', 'HIGH'])
graph = data2
plt.figure()
#ax.right_ax.set_ylabel('CLOSE')
#graph.plot(legend=False)
ax = graph.plot(secondary_y=['money_flow_index'])
#ax.set_ylabel('money_flow_index')
ax.right_ax.set_ylabel('mfi')
plt.show()

"""
#macd 
macd(data2, period_long=26, period_short=12, period_signal=9, column='CLOSE')

#print data2
data2.to_csv('sample.csv')
