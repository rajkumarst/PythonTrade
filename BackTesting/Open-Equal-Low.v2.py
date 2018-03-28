#!/usr/bin/python

from __future__ import division

Months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

symbols = ('ABB','ACC','ADANIPORTS','AMBUJACEM','APOLLOHOSP','ASHOKLEY','ASIANPAINT','AUROPHARMA','AXISBANK','BAJAJ-AUTO','BAJFINANCE','BAJAJFINSV','BANKBARODA','BEL','BHARATFORG','BHEL','BPCL','BHARTIARTL','INFRATEL','BOSCHLTD','BRITANNIA','CADILAHC','CASTROLIND','CIPLA','COALINDIA','COLPAL','CONCOR','CUMMINSIND','DLF','DABUR','DIVISLAB','DRREDDY','EICHERMOT','EMAMILTD','GAIL','GSKCONS','GLAXO','GLENMARK','GODREJCP','GRASIM','HCLTECH','HDFCBANK','HEROMOTOCO','HINDALCO','HINDPETRO','HINDUNILVR','HINDZINC','HDFC','ITC','ICICIBANK','IDEA','IBULHSGFIN','IOC','INDUSINDBK','INFY','JSWSTEEL','KOTAKBANK','LICHSGFIN','LT','LUPIN','MARICO','MARUTI','MOTHERSUMI','NHPC','NMDC','NTPC','ONGC','OIL','OFSS','PIDILITIND','PFC','POWERGRID','PGHH','PNB','RCOM','RELIANCE','RECLTD','SHREECEM','SRTRANSFIN','SIEMENS','SBIN','SAIL','SUNPHARMA','TCS','TATAMTRDVR','TATAMOTORS','TATAPOWER','TATASTEEL','TECHM','TITAN','TORNTPHARM','UPL','ULTRACEMCO','UBL','MCDOWELL-N','VEDL','WIPRO','YESBANK','ZEEL')

sym_maps = {}
rec_sym_maps_int = {}

import matplotlib.pyplot as plt
import pandas as pd
import urllib2
import csv
import time, datetime
 
#for google spredsheet download
import requests

total_count=0
sl_count=0
tgt_count=0
sq_count=0

CASH=10000
Rsyms = []
def IntradayStrategy1(sym, d60, y1):
    global Rsyms
    c = d60[0][0]
    h = float(d60[0][1])
    low = float(d60[0][2])
    o = float(d60[0][3])
    if o == low and float(y1[0]) < o:
	Rsyms.append(sym)

def BackTest(sym, d60, y1):
    global total_count
    global sl_count
    global tgt_count
    global sq_count
    global sym_maps
    global rec_sym_maps_int

    total_count+=1
    lw = 0
    c = d60[0][0]
    h = float(d60[0][1])
    low = float(d60[0][2])
    o = float(d60[0][3])
    pprice = (h+low)//2
    tgt_price = pprice + (pprice * 0.005)
    sl_price = pprice - (pprice * 0.01)
    for l in d60[1:]:
        l1 = l[2]
        h1 = l[1]
        if float(l1) <= sl_price:
            print("%s => SL Hit [Purchase Price=%s, Low=%s, SL=%s]" % (sym, pprice, l1, sl_price))
            sl_count+=1
            return
        if float(h1) >= tgt_price:
            print("%s => TGT Hit [Purchase Price=%s, High=%s, TGT=%s]" % (sym, pprice, h1, tgt_price))
            tgt_count+=1
            return
    print("SquareOff for %s [Low=%s, High=%s, CutOffPrice=%s]" % (sym, l1, h1, (float(l1)+float(h1)/2)))
    sq_count+=1

def GetNifty100Data():
    global sym_maps
    response = requests.get('https://docs.google.com/spreadsheet/ccc?key=1RtKztdvSfTi1uhOzidZX9JGjyjOVf4PfrH6e-lEAJ_Y&output=csv')
    assert response.status_code == 200, 'Wrong status code'
    for l in response.content.splitlines()[1:]:
        sym = l.split(',')[1]
        sym_maps[sym] = l.split(',')        

Data = {}
Interval = 1200

def Get_1Y_Data(sym):
    data = {}
    data1 = []
    response = urllib2.urlopen('https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=1Y' % sym)
    content = csv.reader(response.read().splitlines()[7:])
    for d in content:
        if d[0][0] == 'a':
            lutc = d[0].replace('a','');
            data[lutc] = d[1:]
        else:
            llutc = str(int(lutc)+(int(d[0])*86400))
            data[llutc] = d[1:]
    return data

def Get_60D_Data(sym):
    data = {}
    data1 = []
    response = urllib2.urlopen('https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=60d&i=%s' % (sym, Interval))
    content = csv.reader(response.read().splitlines()[7:])
    prate=0
    lutc= ''
    for d in content:
        if d[0][0] == 'a':
            lutc = d[0].replace('a', '')
            llutc = lutc
	    #print "LOOP1", lutc, datetime.datetime.fromtimestamp(int(lutc)).strftime('%Y-%m-%d %H:%M:%S')
            if lutc not in data.keys():
                data[lutc] = [d[1:]]
	    else:
		print ERROR1
		exit(0)
            prate=0
        elif prate+1 == int(d[0]):
	    #print "LOOP2", lutc, datetime.datetime.fromtimestamp(int(lutc)).strftime('%Y-%m-%d %H:%M:%S')
	    prate = int(d[0])
            data[lutc].append(d[1:])
        else:
	    prate = int(d[0])
            lutc = str(int(llutc) + (int(d[0])*Interval))
	    #print "LOOP3", lutc, datetime.datetime.fromtimestamp(int(lutc)).strftime('%Y-%m-%d %H:%M:%S')
            if lutc not in data.keys():
                data[lutc] = [d[1:]]
	    else:
		data[lutc].append(d[1:])
    #print(data); #exit(0)
    return data

OneYearData = {}
SixtyDaysData = {}
if __name__=="__main__":
    d = 2
    m = 1
    while True:
	if m > 3:
	    break
	if (m == 2 and d > 27) or d > 30:
	    d=2
	    m+=1
	    continue
	Rsyms = []
        for sym in symbols:
            if sym not in OneYearData.keys():
                OneYearData[sym] = Get_1Y_Data(sym)
            dt = datetime.datetime(2018, m, d, 9, 20, 0)
            utc = dt.strftime("%s")
            dt = datetime.datetime(2018, m, d-1, 15, 30, 0)
            prev_utc = dt.strftime("%s")
            if sym not in SixtyDaysData.keys():
                SixtyDaysData[sym] = Get_60D_Data(sym)
	    if utc in SixtyDaysData[sym].keys() and prev_utc in OneYearData[sym].keys():
        	#print("SixtyDaysData[%s][%s][0]=%s" % (sym, utc, SixtyDaysData[sym][utc][0]))
                #print prev_utc, OneYearData[prev_utc]
                IntradayStrategy1(sym, SixtyDaysData[sym][utc], OneYearData[sym][prev_utc])
	    else:
		print("Sym %s not traded @ UTC %s" % (sym, utc))
        total_count=0
        sl_count=0
        tgt_count=0
        sq_count=0
	for sym in Rsyms:
            dt = datetime.datetime(2018, m, d, 9, 20, 0)
            utc = dt.strftime("%s")
            dt = datetime.datetime(2018, m, d-1, 15, 30, 0)
            prev_utc = dt.strftime("%s")
	    if utc in SixtyDaysData[sym].keys() and prev_utc in OneYearData[sym].keys():
                BackTest(sym, SixtyDaysData[sym][utc], OneYearData[sym][prev_utc])
        if total_count > 0:
            print("%s %d: Total Count=%d" % (Months[m-1], d, total_count))
            print("%s %d: STP Count=%d, Hit Ratio=%d" % (Months[m-1], d, sl_count, (sl_count/total_count*100)))
            print("%s %d, TGT Count=%d, Hit Ratio=%d" % (Months[m-1], d, tgt_count, (tgt_count/total_count*100)))
            print("%s %d, SQO Count=%d, Hit Ratio=%d" % (Months[m-1], d, sq_count, (sq_count/total_count*100)))
        d+=1
