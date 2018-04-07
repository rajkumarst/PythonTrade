#!/usr/bin/python -u

from __future__ import division

import os, sys, datetime, csv, urllib2
#import requests, io
import pandas as pd
import matplotlib.pyplot as plt
 
BackTesting = True

NDays = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

Months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

Interval = 960
TodayData = {}
OneYearData = {}
SixtyDaysData = {}

total_count = 0
sl_count = 0
tgt_count = 0
sq_count = 0

ProfitPct = 1/100
SLPct = 0.4/100

CAPITAL=100000
GROSS=CAPITAL
CAPITAL_PER_SHARE=0
RsymsBuy = []
RsymsSell = []

def log(str):
    if verbose:
	print str

def IntradayStrategy(strategy, sym, d60, y1):
    global RsymsBuy
    global RsymsSell
    c = d60[0][0]
    h = float(d60[0][1])
    low = float(d60[0][2])
    o = float(d60[0][3])
    if strategy == 'Buy' or strategy == 'Both':
	if o == low and float(y1[0]) < o:
	    RsymsBuy.append(sym)
    if strategy == 'Sell' or strategy == 'Both':
	if o == h and float(y1[0]) > o:
	    RsymsSell.append(sym)

def BackTestBuy(sym, utc, d60, y1):
    global total_count
    global sl_count
    global tgt_count
    global sq_count
    global GROSS
    global CAPITAL_PER_SHARE

    total_count+=1
    lw = 0
    c = d60[0][0]
    h = float(d60[0][1])
    low = float(d60[0][2])
    o = float(d60[0][3])
    pprice = (h+low)/2
    tgt_price = pprice + (pprice * ProfitPct)
    sl_price = pprice - (pprice * SLPct)
    l1 = 0
    h1 = 0
    log("Sym=%s, ProfitPct=%f, Tgt Price = %f, SLPct=%f, SL Pric = %f" % (sym, ProfitPct, tgt_price, SLPct, sl_price))
    for l in d60[1:]:
	# c h l o format, retrive the low and high
	h1 = float(l[1])
	l1 = float(l[2])
	if l1 == 0 or h1 == 0:
	    break
	if l1 <= sl_price:
	    log("%s => %s => SL Hit [Purchase Price=%f, Low=%f, SL=%f]" % (sym, datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'), pprice, l1, sl_price))
	    log("GROSS=%f, CPS=%f, G-LOSS=%f" % (GROSS, (CAPITAL_PER_SHARE*SLPct), GROSS-(CAPITAL_PER_SHARE*SLPct)))
	    sl_count+=1
	    GROSS -= (CAPITAL_PER_SHARE*SLPct)
	    return
	if h1 >= tgt_price:
	    log("%s => %s => TGT Hit [Purchase Price=%f, High=%f, TGT=%f]" % (sym, datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'), pprice, h1, tgt_price))
	    log("GROSS=%f, CPS=%f, G+Earning=%f" % (GROSS, (CAPITAL_PER_SHARE*ProfitPct), GROSS+(CAPITAL_PER_SHARE*ProfitPct)))
	    tgt_count+=1
	    GROSS += (CAPITAL_PER_SHARE*ProfitPct)
	    return
    if l1 > 0 and h1 > 0:
	log("%s => %s => SquareOff Hit [Purchase Price=%f, Low=%f, High=%f, CutOffPrice=%f]" % (sym, datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'), pprice, l1, h1, (l1+h1)/2))
	log("GROSS=%f, CPS=%f, G+Earning=%f" % (GROSS, (CAPITAL_PER_SHARE*((((l1+h1)/2)-pprice)/pprice)), GROSS + (CAPITAL_PER_SHARE*((((l1+h1)/2)-pprice)/pprice))))
	sq_count+=1
	GROSS += (CAPITAL_PER_SHARE*((((l1+h1)/2)-pprice)/pprice))

def BackTestSell(sym, utc, d60, y1):
    global total_count
    global sl_count
    global tgt_count
    global sq_count
    global GROSS
    global CAPITAL_PER_SHARE

    total_count+=1
    lw = 0
    c = float(d60[0][0])
    h = float(d60[0][1])
    low = float(d60[0][2])
    o = float(d60[0][3])
    pprice = (h+low+c)/3
    tgt_price = pprice - (pprice * ProfitPct)
    sl_price = pprice + (pprice * SLPct)
    l1 = 0
    h1 = 0
    for l in d60[1:]:
	# c h l o format, retrive the low and high
	c1 = float(l[0])
	h1 = float(l[1])
	l1 = float(l[2])
	if l1 == 0 or h1 == 0:
	    break
	if h1 >= sl_price:
	    log("%s => %s => SL Hit [Purchase Price=%f, Low=%f, SL=%f]" % (sym, datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'), pprice, h1, sl_price))
	    log("GROSS=%f, CPS=%f, G-LOSS=%f" % (GROSS, (CAPITAL_PER_SHARE*SLPct), GROSS-(CAPITAL_PER_SHARE*SLPct)))
	    sl_count+=1
	    GROSS -= (CAPITAL_PER_SHARE*SLPct)
	    return
	if l1 <= tgt_price:
	    log("%s => %s => TGT Hit [Purchase Price=%f, High=%f, TGT=%f]" % (sym, datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'), pprice, l1, tgt_price))
	    log("GROSS=%f, CPS=%f, G+Earning=%f" % (GROSS, (CAPITAL_PER_SHARE*ProfitPct), GROSS+(CAPITAL_PER_SHARE*ProfitPct)))
	    tgt_count+=1
	    GROSS += (CAPITAL_PER_SHARE*ProfitPct)
	    return
    if l1 > 0 and h1 > 0:
	log("%s => %s => SquareOff Hit [Purchase Price=%f, Low=%f, High=%f, CutOffPrice=%f]" % (sym, datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'), pprice, l1, h1, (l1+h1)/2))
	log("GROSS=%f, CPS=%f, G+Earning=%f" % (GROSS, (CAPITAL_PER_SHARE*((((l1+h1)/2)-pprice)/pprice)), GROSS + (CAPITAL_PER_SHARE*((((l1+h1)/2)-pprice)/pprice))))
	sq_count+=1
	GROSS += (CAPITAL_PER_SHARE*((pprice-((l1+h1+c1)/3))/pprice))

def Get_1Y_Data(sym):
    data = {}
    response = urllib2.urlopen('https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=1Y' % sym.replace('&','%26'))
    content = csv.reader(response.read().splitlines()[7:])
    for d in content:
	if d[0][0] == 'a':
	    lutc = d[0].replace('a','');
	    data[lutc] = d[1:]
	else:
	    llutc = str(int(lutc)+(int(d[0])*86400))
	    data[llutc] = d[1:]
    return data

NiftyIndex60DCandle = {}
def GetNiftyIndex60DCandleData():
    global NiftyIndex60DCandle
    response = urllib2.urlopen('https://finance.google.com/finance/getprices?x=NSE&q=NIFTY&f=d,c,h,l,o,v&p=60d&i=%s' % Interval)
    content = csv.reader(response.read().splitlines()[7:])
    prate=0
    lutc= ''
    for d in content:
	if d[0][0] == 'a':
	    lutc = d[0].replace('a', '')
	    llutc = lutc
	    if lutc not in NiftyIndex60DCandle.keys():
		NiftyIndex60DCandle[lutc] = [d[1:]]
	    else:
		print ERROR1
		exit(0)
	    prate=0
	elif prate+1 == int(d[0]):
	    prate = int(d[0])
	    NiftyIndex60DCandle[lutc].append(d[1:])
	else:
	    prate = int(d[0])
	    lutc = str(int(llutc) + (int(d[0])*Interval))
	    if lutc not in NiftyIndex60DCandle.keys():
		NiftyIndex60DCandle[lutc] = [d[1:]]
	    else:
		NiftyIndex60DCandle[lutc].append(d[1:])

NiftyIndex1YCandle = {}
def GetNiftyIndex1YCandleData():
    global NiftyIndex1YCandle
    lutc= ''
    llutc= ''
    response = urllib2.urlopen('https://finance.google.com/finance/getprices?x=NSE&q=NIFTY&f=d,c,h,l,o,v&p=1Y')
    content = csv.reader(response.read().splitlines()[7:])
    for d in content:
	if d[0][0] == 'a':
	    lutc = d[0].replace('a','');
	    NiftyIndex1YCandle[lutc] = d[1:]
	else:
	    llutc = str(int(lutc)+(int(d[0])*86400))
	    NiftyIndex1YCandle[llutc] = d[1:]

def GetScripCandleData(days, sym):
    data = {}
    url = 'https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=%sd&i=%s' % (sym.replace('&','%26'), days, Interval)
    response = urllib2.urlopen(url)
    content = csv.reader(response.read().splitlines()[7:])
    prate=0
    lutc= ''
    for d in content:
	if d[0][0] == 'a':
	    lutc = d[0].replace('a', '')
	    llutc = lutc
	    if lutc not in data.keys():
		data[lutc] = [d[1:]]
	    else:
		print ERROR1
		exit(0)
	    prate=0
	elif prate+1 == int(d[0]):
	    prate = int(d[0])
	    data[lutc].append(d[1:])
	else:
	    prate = int(d[0])
	    lutc = str(int(llutc) + (int(d[0])*Interval))
	    if lutc not in data.keys():
		data[lutc] = [d[1:]]
	    else:
		data[lutc].append(d[1:])
    return data

def GetPrevUTCNifty(Putc):
    keys = NiftyIndex1YCandle.keys()
    i=1
    while i < 6:
	Putc = str(int(Putc) - (i*86400))
	if Putc in keys:
	    return Putc
	i+=1
    return None

def GetPrevUTC(sym, Putc):
    keys = OneYearData[sym].keys()
    i=1
    while i < 6:
	Putc = str(int(Putc) - (i*86400))
	if Putc in keys:
	    return Putc
	i+=1
    return None

def GetNifty50Symbols():
    Nifty50 = []
    syms = []
    with open('ind_niftynext50list.csv', 'rb') as f:
	reader = csv.reader(f)
	Nifty50.extend(list(reader))
    f.close()
    for sym in Nifty50[1:]:
	syms.append(sym[2])
    return syms

def GetNifty100Symbols():
    Nifty100 = []
    syms = []
    with open('ind_nifty100list.csv', 'rb') as f:
	reader = csv.reader(f)
	Nifty100.extend(list(reader))
    f.close()
    for sym in Nifty100[1:]:
	syms.append(sym[2])
    return syms

def GetNifty200Symbols():
    Nifty200 = []
    syms = []
    with open('ind_nifty200list.csv', 'rb') as f:
	reader = csv.reader(f)
	Nifty200.extend(list(reader))
    f.close()
    for sym in Nifty200[1:]:
	syms.append(sym[2])
    return syms

verbose=0
one_day_scan=0
y = 2018
m = 1
d = 1
today=0
varience = "Always-Buy"
plot_returns='out.plot_earnings'
plot_hits='out.plot_hits'

if __name__=="__main__":
    #if (sys.argv[1] = "--nifty50")
    Nsyms = []
    # Get Nifty symbols
    if len(sys.argv) > 0:
	i=1
	while i <= len(sys.argv[1:]):
	    if sys.argv[i] == "--verbose":
		verbose=1
	    if sys.argv[i] == "--nifty50":
		plot_returns+='_'+'n50'
		plot_hits+='_'+'n50'
		Nsyms.extend(GetNifty50Symbols())
	    elif sys.argv[i] == "--nifty100":
		plot_returns+='_'+'n100'
		plot_hits+='_'+'n100'
		Nsyms.extend(GetNifty100Symbols())
	    elif sys.argv[i] == "--nifty200":
		plot_returns+='_'+'n200'
		plot_hits+='_'+'n200'
		Nsyms.extend(GetNifty200Symbols())
	    elif sys.argv[i] == "--profit":
		plot_returns+='_'+sys.argv[i+1]
		plot_hits+='_'+sys.argv[i+1]
		ProfitPct = float(sys.argv[i+1])/100;
		i+=1
	    elif sys.argv[i] == "--sl":
		plot_returns+='_'+sys.argv[i+1]
		plot_hits+='_'+sys.argv[i+1]
		SLPct = float(sys.argv[i+1])/100;
		i+=1
	    elif sys.argv[i] == '--today':
		plot_returns+='_'+'today'
		plot_hits+='_'+'today'
		dt = datetime.datetime.today();
		y = int(dt.strftime("%Y"))
		m = int(dt.strftime("%m"))
		d = int(dt.strftime("%d"))
		one_day_scan=1
		today=1
	    elif sys.argv[i] == '--yesterday':
		plot_returns+='yesterday'
		plot_hits+='yesterday'
		dt = datetime.datetime.today() - datetime.timedelta(1);
		y = int(dt.strftime("%Y"))
		m = int(dt.strftime("%m"))
		d = int(dt.strftime("%d"))
		one_day_scan=1
	    elif sys.argv[i] == '--Both-Buy-And-Sell':
		plot_returns+='_'+sys.argv[i]
		plot_hits+='_'+sys.argv[i]
		varience = "Both-Buy-And-Sell"
	    elif sys.argv[i] == '--Go_with_Nifty':
		plot_returns+='_'+sys.argv[i]
		plot_hits+='_'+sys.argv[i]
		varience = "Go_with_Nifty"
	    elif sys.argv[i] == '--Always-Buy':
		plot_returns+='_'+sys.argv[i]
		plot_hits+='_'+sys.argv[i]
		varience = "Always-Buy"
	    elif sys.argv[i] == '--no-back-testing':
		BackTesting=False
	    i+=1

    if len(Nsyms) == 0:
	plot_returns+='_n100_%s_%s_%s' % (varience, ProfitPct, SLPct)
	plot_hits+='_n100_%s_%s_%s' % (varience, ProfitPct, SLPct)
	Nsyms.extend(GetNifty100Symbols())
    plot_returns+='.csv'
    plot_hits+='.csv'

    plot_returns_handle = open(plot_returns, 'w')
    plot_hits_handle = open(plot_hits, 'w')
    print >>plot_returns_handle, "Date,Gross"
    print >>plot_hits_handle, "Date,Miss,Hit,SQO"

    # Collect Nifty Candle data for the same period and interval as symbols.
    if varience == "Go_with_Nifty":
	GetNiftyIndex60DCandleData()
	GetNiftyIndex1YCandleData()

    tdays=0
    for sym in Nsyms:
	# Collect Candle data for the each symbol for last 2 months and 1 year
	OneYearData[sym] = Get_1Y_Data(sym)
	if today == 1:
	    TodayData[sym] = GetScripCandleData(1, sym)
	else:
	    SixtyDaysData[sym] = GetScripCandleData(60, sym)

    tdt = datetime.datetime.today();
    tm = int(tdt.strftime("%m"))
    td = int(tdt.strftime("%d"))
    while True:
	if m == tm and d > td:
	    break
	if d > NDays[m-1]:
	    d=1
	    m+=1
	    if m > 12:
		m=1
		y+=1
	    continue
	dt = datetime.datetime(y, m, d, 9, 16, 0)
	utc = dt.strftime("%s")
	dtl = datetime.datetime(y, m, d, 15, 30, 0)
	utcl = dtl.strftime("%s")

	if varience == "Always-Buy":
	    strategy = "Buy"
	if varience == "Both-Buy-And-Sell":
	    strategy = "Both"
	elif varience == "Go_with_Nifty":
	    prev_utc = GetPrevUTCNifty(str(int(utcl)))
	    if prev_utc is None:
		print("ERROR: Could not find Previous day for %s" % datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'))
		exit(1);
	    if utc not in NiftyIndex60DCandle.keys():
		d+=1
		log("No scanning for %s" % datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'))
		continue
	    Ncpt = ((float(NiftyIndex60DCandle[utc][0][0])-float(NiftyIndex1YCandle[prev_utc][0]))/float(NiftyIndex1YCandle[prev_utc][0]))*100
	    strategy = "Buy"
	    if Ncpt <= -1:
		strategy = "Sell"
	    log("[%s]: Ncpt = %f, Strategy=%s" % (datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'), Ncpt, strategy))

	RsymsBuy = []
	RsymsSell = []

	# Shortlist complete list of stocks in one iteration
	for sym in Nsyms:
	    prev_utc = GetPrevUTC(sym, int(utcl))
	    if prev_utc is None:
		continue
	    log("Iteration for %s, %s,%s" % (sym, datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.fromtimestamp(int(prev_utc)).strftime('%Y-%m-%d %H:%M:%S')))
	    if today == 1:
		utcs = TodayData[sym].keys()
	    else:
		utcs = SixtyDaysData[sym].keys()
	    #if (today == 1 and utc in SixtyDaysData[sym].keys() and prev_utc is not None) or (utc in SixtyDaysData[sym].keys() and prev_utc is not None):
	    if utc in utcs and prev_utc is not None:
		if today:
		    IntradayStrategy(strategy, sym, TodayData[sym][utc], OneYearData[sym][prev_utc])
		else:
		    IntradayStrategy(strategy, sym, SixtyDaysData[sym][utc], OneYearData[sym][prev_utc])
	    #else:
		#log("Symbol %s is not shortlisted for %s" % (sym, datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S')))

	if len(RsymsBuy) > 0 or len(RsymsSell) > 0:
	    if BackTesting is True:
		log("[%s]: RsymsBuy=%s, RsymsSell=%s" % (datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S'), ' '.join(RsymsBuy), ' '.join(RsymsSell)))
		total_count=0
		sl_count=0
		tgt_count=0
		sq_count=0

		if GROSS == 0:
		    GROSS==CAPITAL
		if (strategy == "Buy" or strategy == "Both") and len(RsymsBuy) > 0:
		    CAPITAL_PER_SHARE=GROSS/len(RsymsBuy)
		    for sym in RsymsBuy:
			if today:
			    BackTestBuy(sym, utc, TodayData[sym][utc], OneYearData[sym][prev_utc])
			else:
			    BackTestBuy(sym, utc, SixtyDaysData[sym][utc], OneYearData[sym][prev_utc])
		if (strategy == "Sell" or strategy == "Both") and len(RsymsSell) > 0:
		    CAPITAL_PER_SHARE=GROSS/len(RsymsSell)
		    for sym in RsymsSell:
			if today:
			    BackTestSell(sym, utc, TodayData[sym][utc], OneYearData[sym][prev_utc])
			else:
			    BackTestSell(sym, utc, SixtyDaysData[sym][utc], OneYearData[sym][prev_utc])
		if total_count > 0:
		    cdate = datetime.datetime.fromtimestamp(int(utc)).strftime('%d-%m-%Y')
		    print >>plot_returns_handle, "%s,%s" % (cdate,GROSS)
		    print >>plot_hits_handle, "%s,%d,%d,%d" % (cdate,sl_count,tgt_count,sq_count)
		    print("%s %d: Total Count=%d" % (Months[m-1], d, total_count))
		    print("%s %d: STP Count=%d, Hit Ratio=%d" % (Months[m-1], d, sl_count, (sl_count/total_count*100)))
		    print("%s %d: TGT Count=%d, Hit Ratio=%d" % (Months[m-1], d, tgt_count, (tgt_count/total_count*100)))
		    print("%s %d: SQO Count=%d, Hit Ratio=%d" % (Months[m-1], d, sq_count, (sq_count/total_count*100)))
		    tdays+=1
	    else:
		print("Recommended Buy Stocks = %s" % ','.join(RsymsBuy))
		print("Recommended Sell Stocks = %s" % ','.join(RsymsSell))
	d+=1
	if one_day_scan == 1:
	    break
    if BackTesting is True:
	plot_returns_handle.close();
	plot_hits_handle.close();
	print("Nifty%d: Capital=%d, Gross=%d, Pct=%.2f%% (ProfitPct=%s,SLPct=%s)" % (len(Nsyms), CAPITAL, GROSS, float((GROSS-CAPITAL)/CAPITAL)*100, ProfitPct, SLPct))
	print "Total number of trade days=%d" % tdays
