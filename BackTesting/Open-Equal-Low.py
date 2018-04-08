#!/usr/bin/python -u

from __future__ import division

import os, sys, datetime, csv, urllib2
#import requests, io
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
 
BackTesting = True

NDays = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

Months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

Interval = 960
TodayData = {}
OneYearData = {}
SixtyDaysData = {}

sl_count = 0
tgt_count = 0
sq_count = 0

ProfitPct = 1/100
SLPct = 0.4/100

def log(str):
    if verbose:
	print str

def GetHumanDate(utc):
    return datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S')

def CalculateSMA(sym, prev_utc):
    sma5=0
    sma10=0
    sma20=0
    sma30=0
    i=1
    keys = OneYearData[sym].keys()
    while i <= 20:
	if prev_utc not in keys:
	    prev_utc = GetPrevUTC(sym, prev_utc)
	    if prev_utc is None:
		return [0, 0, 0, 0]
	close = float(OneYearData[sym][prev_utc][0])
	if i <= 5:
	    sma5+=close
	if i <= 10:
	    sma10+=close
	if i <= 20:
	    sma20+=close
	#if i <= 30:
	    #sma30+=close
	prev_utc = GetPrevUTC(sym, prev_utc)
	i+=1
    log("%s[5,10,20,30] = [%d, %d, %d, %d]" % (sym, sma5/5, sma10/10, sma20/20, sma30/30))
    return [sma5/5, sma10/10, sma20/20, sma30/30]

def CandleData(sym, UTC):
    global today

    if today:
	return TodayData[sym][UTC]
    else:
	return SixtyDaysData[sym][UTC]

def IntradayStrategy(strategy, sym, UTC, pUTC):
    global RsymsBuy
    global RsymsSell

    cdata = CandleData(sym, UTC)
    c = cdata[0][0]
    h = float(cdata[0][1])
    low = float(cdata[0][2])
    o = float(cdata[0][3])
    if strategy == 'Buy' or strategy == 'Both':
	if o == low and float(OneYearData[sym][pUTC][0]) < o:
	    RsymsBuy.append(sym)
    if strategy == 'Sell' or strategy == 'Both':
	if o == h and float(OneYearData[sym][pUTC][0]) > o:
	    RsymsSell.append(sym)

def BackTestBuy(sym, UTC):
    global sl_count
    global tgt_count
    global sq_count
    global GROSS
    global CPS

    cdata = CandleData(sym, UTC)
    lw = 0
    c = cdata[0][0]
    h = float(cdata[0][1])
    low = float(cdata[0][2])
    o = float(cdata[0][3])
    pprice = (h+low)/2
    tgt_price = pprice + (pprice * ProfitPct)
    sl_price = pprice - (pprice * SLPct)
    l1 = 0
    h1 = 0
    #log("Sym=%s, ProfitPct=%f, Tgt Price = %f, SLPct=%f, SL Pric = %f" % (sym, ProfitPct, tgt_price, SLPct, sl_price))
    for l in cdata[1:]:
	# c h l o format, retrive the low and high
	h1 = float(l[1])
	l1 = float(l[2])
	if l1 == 0 or h1 == 0:
	    break
	if l1 <= sl_price:
	    log("%s => %s => SL Hit [Purchase Price=%f, Low=%f, SL=%f], GROSS=%f, CPCT=%f, G-LOSS=%f" % (sym, GetHumanDate(UTC), pprice, l1, sl_price, GROSS, (CPS*SLPct), GROSS-(CPS*SLPct)))
	    sl_count+=1
	    GROSS -= (CPS*SLPct)
	    return
	if h1 >= tgt_price:
	    log("%s => %s => TGT Hit [Purchase Price=%f, High=%f, TGT=%f], GROSS=%f, CPCT=%f, G+Earning=%f" % (sym, GetHumanDate(UTC), pprice, h1, tgt_price, GROSS, (CPS*ProfitPct), GROSS+(CPS*ProfitPct)))
	    tgt_count+=1
	    GROSS += (CPS*ProfitPct)
	    return
    if l1 > 0 and h1 > 0:
	log("%s => %s => SquareOff Hit [Purchase Price=%f, Low=%f, High=%f, CutOffPrice=%f], GROSS=%f, CPCT=%f, G+Earning=%f" % (sym, GetHumanDate(UTC), pprice, l1, h1, (l1+h1)/2, GROSS, (CPS*((((l1+h1)/2)-pprice)/pprice)), GROSS + (CPS*((((l1+h1)/2)-pprice)/pprice))))
	sq_count+=1
	GROSS += (CPS*((((l1+h1)/2)-pprice)/pprice))

def BackTestSell(sym, UTC):
    global sl_count
    global tgt_count
    global sq_count
    global GROSS
    global CPS

    cdata = CandleData(sym, UTC)
    lw = 0
    c = float(cdata[0][0])
    h = float(cdata[0][1])
    low = float(cdata[0][2])
    o = float(cdata[0][3])
    pprice = (h+low+c)/3
    tgt_price = pprice - (pprice * ProfitPct)
    sl_price = pprice + (pprice * SLPct)
    l1 = 0
    h1 = 0
    for l in cdata[1:]:
	# c h l o format, retrive the low and high
	c1 = float(l[0])
	h1 = float(l[1])
	l1 = float(l[2])
	if l1 == 0 or h1 == 0:
	    break
	if h1 >= sl_price:
	    log("%s => %s => SL Hit [Purchase Price=%f, Low=%f, SL=%f]" % (sym, GetHumanDate(UTC), pprice, h1, sl_price))
	    log("GROSS=%f, CPCT=%f, G-LOSS=%f" % (GROSS, (CPS*SLPct), GROSS-(CPS*SLPct)))
	    sl_count+=1
	    GROSS -= (CPS*SLPct)
	    return
	if l1 <= tgt_price:
	    log("%s => %s => TGT Hit [Purchase Price=%f, High=%f, TGT=%f]" % (sym, GetHumanDate(UTC), pprice, l1, tgt_price))
	    log("GROSS=%f, CPCT=%f, G+Earning=%f" % (GROSS, (CPS*ProfitPct), GROSS+(CPS*ProfitPct)))
	    tgt_count+=1
	    GROSS += (CPS*ProfitPct)
	    return
    if l1 > 0 and h1 > 0:
	log("%s => %s => SquareOff Hit [Purchase Price=%f, Low=%f, High=%f, CutOffPrice=%f]" % (sym, GetHumanDate(UTC), pprice, l1, h1, (l1+h1)/2))
	log("GROSS=%f, CPCT=%f, G+Earning=%f" % (GROSS, (CPS*((((l1+h1)/2)-pprice)/pprice)), GROSS + (CPS*((((l1+h1)/2)-pprice)/pprice))))
	sq_count+=1
	GROSS += (CPS*((pprice-((l1+h1+c1)/3))/pprice))

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
CAPITAL=100000
CPS=0
GROSS=CAPITAL
today=0
variance = "Always-Buy"
plot_returns='out.plot_earnings'
plot_hits='out.plot_hits'
RsymsBuy = []
RsymsSell = []

def Initialize():
    global sl_count
    global tgt_count
    global sq_count
    global y
    global m
    global d
    global RsymsBuy
    global RsymsSell
    global CAPITAL
    global GROSS

    sl_count = 0
    tgt_count = 0
    sq_count = 0
    y = 2018
    m = 1
    d = 1
    CAPITAL=100000
    GROSS=CAPITAL

def MainLoop(s):
    global tgt_count
    global sl_count
    global plot_returns
    global plot_hits
    global y
    global m
    global d
    global RsymsBuy
    global RsymsSell
    global GROSS
    global CPS
    tdays=0

    plot_returns=plot_returns.replace('.csv','_%s.csv' % s)
    plot_hits=plot_hits.replace('.csv','_%s.csv' % s)
    tdt = datetime.datetime.today();
    tm = int(tdt.strftime("%m"))
    td = int(tdt.strftime("%d"))

    plot_returns_handle = open(plot_returns, 'w')
    plot_hits_handle = open(plot_hits, 'w')
    print >>plot_returns_handle, "Date,Gross"
    print >>plot_hits_handle, "Date,Miss,Hit,SQO"

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

	if s == 'Nifty':
	    prev_utc = GetPrevUTCNifty(str(int(utcl)))
	    if prev_utc is None:
		#print("ERROR: Could not find Previous day for %s" % GetHumanDate(utc))
		d+=1
		continue
	    if utc not in NiftyIndex60DCandle.keys():
	        d+=1
	        #log("No scanning for %s" % GetHumanDate(utc))
	        continue
	    Ncpt = ((float(NiftyIndex60DCandle[utc][0][0])-float(NiftyIndex1YCandle[prev_utc][0]))/float(NiftyIndex1YCandle[prev_utc][0]))*100
	    strategy = "Buy"
	    if Ncpt <= -1:
		strategy = "Sell"
	    log("[%s]: Ncpt = %f, Strategy=%s" % (GetHumanDate(utc), Ncpt, strategy))
	else:
	    strategy = s

	RsymsBuy = []
	RsymsSell = []

	# Shortlist complete list of stocks in one iteration
	for sym in Nsyms:
	    prev_utc = GetPrevUTC(sym, utcl)
	    if prev_utc is None:
		continue
	    #log("Iteration for %s, %s,%s" % (sym, GetHumanDate(prev_utc), GetHumanDate(utc)))
	    if today:
		utcs = TodayData[sym].keys()
	    else:
		utcs = SixtyDaysData[sym].keys()

	    if utc in utcs and prev_utc is not None:
		IntradayStrategy(strategy, sym, utc, prev_utc)
	    #else:
		#log("Symbol %s is not shortlisted for %s" % (sym, GetHumanDate(utc)))

	if len(RsymsBuy) > 0 or len(RsymsSell) > 0:
	    if (strategy == "Buy" or strategy == "Both") and len(RsymsBuy) > 0:
		for sym in RsymsBuy:
		    SMA_list = CalculateSMA(sym, prev_utc)
		    if SMA_Check and SMA_list[0] > CandleData(sym, utc)[0][3]:
			log("Removing %s from shortlisted stocks [%s > %s]" % (sym, SMA_list[0], CandleData(sym, utc)[0][3]))
			RsymsBuy.remove(sym)
	    if (strategy == "Sell" or strategy == "Both") and len(RsymsSell) > 0:
		for sym in RsymsSell:
		    SMA_list = CalculateSMA(sym, prev_utc)
		    if SMA_Check and SMA_list[0] < CandleData(sym, utc)[0][3]:
			log("Removing %s from shortlisted stocks [%s < %s]" % (sym, SMA_list[0], CandleData(sym, utc)[0][3]))
			RsymsSell.remove(sym)

	    total_count=len(RsymsBuy)+len(RsymsSell)

	    if len(RsymsBuy) > 0:
		log("Recommended Buy Stocks = %s" % ','.join(RsymsBuy))
	    if len(RsymsSell) > 0:
		log("Recommended Sell Stocks = %s" % ','.join(RsymsSell))

	    if BackTesting is True:
		sl_count=0
		tgt_count=0
		sq_count=0

		if GROSS == 0:
		    GROSS=CAPITAL

		if strategy == "Buy" and len(RsymsBuy) > 0:
		    CPS=GROSS/len(RsymsBuy)
		elif strategy == "Sell" and len(RsymsSell) > 0:
		    CPS=GROSS/len(RsymsSell)
		else:
		    CPS=GROSS/(len(RsymsBuy)+len(RsymsSell))

		if (strategy == "Buy" or strategy == "Both") and len(RsymsBuy) > 0:
		    for sym in RsymsBuy:
			log("%s[5,10,20,30] = [%s,%s,%s,%s]" % (sym, SMA_list[0], SMA_list[1], SMA_list[2], SMA_list[3]))
			BackTestBuy(sym, utc)

		if (strategy == "Sell" or strategy == "Both") and len(RsymsSell) > 0:
		    for sym in RsymsSell:
			log("%s[5,10,20,30] = [%s,%s,%s,%s]" % (sym, SMA_list[0], SMA_list[1], SMA_list[2], SMA_list[3]))
			BackTestSell(sym, utc)

		if total_count > 0:
		    cdate = GetHumanDate(utc)
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
    print("Nifty%d[%s]: Capital=%d, Gross=%d, Pct=%.2f%% (ProfitPct=%s,SLPct=%s,SMA=%s)" % (len(Nsyms), strategy, CAPITAL, GROSS, float((GROSS-CAPITAL)/CAPITAL)*100, ProfitPct, SLPct, SMA_Check))
    print "Total number of trade days=%d" % tdays
    plot_returns_handle.close();
    plot_hits_handle.close();

if __name__=="__main__":
    Nsyms = []
    # Get Nifty symbols
    if len(sys.argv) > 0:
	i=1
	while i <= len(sys.argv[1:]):
	    plot_returns+='_'+sys.argv[i].replace('--','')
	    plot_hits+='_'+sys.argv[i].replace('--','')
	    if sys.argv[i] == "--verbose":
		verbose=1
	    if sys.argv[i] == "--nifty50":
		Nsyms.extend(GetNifty50Symbols())
	    elif sys.argv[i] == "--nifty100":
		Nsyms.extend(GetNifty100Symbols())
	    elif sys.argv[i] == "--nifty200":
		Nsyms.extend(GetNifty200Symbols())
	    elif sys.argv[i] == "--profit-sl-combo":
		pcts = sys.argv[i+1]
		i+=1
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
		dt = datetime.datetime.today();
		y = int(dt.strftime("%Y"))
		m = int(dt.strftime("%m"))
		d = int(dt.strftime("%d"))
		one_day_scan=1
		today=1
	    elif sys.argv[i] == '--yesterday':
		dt = datetime.datetime.today() - datetime.timedelta(1);
		y = int(dt.strftime("%Y"))
		m = int(dt.strftime("%m"))
		d = int(dt.strftime("%d"))
		one_day_scan=1
	    elif sys.argv[i] == '--Both-Buy-And-Sell':
		variance = "Both-Buy-And-Sell"
	    elif sys.argv[i] == '--Go_with_Nifty':
		variance = "Go_with_Nifty"
	    elif sys.argv[i] == '--Always-Buy':
		variance = "Always-Buy"
	    elif sys.argv[i] == '--all':
		variance = "ALL"
	    elif sys.argv[i] == '--no-back-testing':
		BackTesting=False
	    elif sys.argv[i] == '--sma-check':
		SMA_Check=True
	    i+=1

    if len(Nsyms) == 0:
	plot_returns+='_n100_%s' % variance
	plot_hits+='_n100_%s' % variance
	if pcts is None:
	    plot_returns+='_n100_%s_%s' % (ProfitPct, SLPct)
	    plot_hits+='_n100_%s_%s' % (ProfitPct, SLPct)
	Nsyms.extend(GetNifty100Symbols())
	#Nsyms.append('BPCL')
    plot_returns+='.csv'
    plot_hits+='.csv'

    for sym in Nsyms:
	# Collect Candle data for the each symbol for last 2 months and 1 year
	OneYearData[sym] = Get_1Y_Data(sym)
	if today == 1:
	    TodayData[sym] = GetScripCandleData(1, sym)
	else:
	    SixtyDaysData[sym] = GetScripCandleData(60, sym)
	    a=1

    if variance == "Always-Buy":
	MainLoop("Buy");
    elif variance == "Both-Buy-And-Sell":
	MainLoop("Both");
    else:
	# Collect Nifty Candle data for the same period and interval as symbols.
	GetNiftyIndex60DCandleData()
	GetNiftyIndex1YCandleData()
	plot_returns1=deepcopy(plot_returns)
	plot_hits1=deepcopy(plot_hits)
 	print plot_returns
	if variance == "Go_with_Nifty":
	    MainLoop('Nifty');
	elif variance == "ALL":
	    for val in (0, 1):
		if val == 1:
		    plot_returns=plot_returns.replace('.csv','_SMA_Check.csv')
		    SMA_Check=True
		else:
		    SMA_Check=False
		for pft_sl in pcts.split(','):
		    pft_sl_list = pft_sl.split(':')
		    ProfitPct = float(pft_sl_list[0])/100
		    SLPct = float(pft_sl_list[1])/100
		    for s in ('Buy', 'Both', 'Nifty'):
			plot_returns=plot_returns1.replace('.csv','_%s_%s_SMA_%s.csv' % (ProfitPct, SLPct, val))
			plot_hits=plot_hits1.replace('.csv','_%s_%s_SMA_%s.csv' % (ProfitPct, SLPct, val))
			MainLoop(s)
			Initialize()
