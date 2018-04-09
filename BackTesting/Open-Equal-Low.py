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
SMA_Check=False
VOL_Check=1

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
	    prev_utc = GetPrevUTC(OneYearData[sym], prev_utc)
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
	prev_utc = GetPrevUTC(OneYearData[sym], prev_utc)
	i+=1
    log("%s[5,10,20,30] = [%d, %d, %d, %d]" % (sym, sma5/5, sma10/10, sma20/20, sma30/30))
    return [sma5/5, sma10/10, sma20/20, sma30/30]

def CandleData(sym, UTC):
    global today

    if today:
	return TodayData[sym][UTC]
    else:
	return SixtyDaysData[sym][UTC]

def VolCheck(c, sym, pUTC, prev_utc, c_candle_vol):
    # prev_utc will refer to previous day 3:30 UTC
    # pUTC will refer to previous day 9:16
    #print GetHumanDate(prev_utc), GetHumanDate(pUTC)
    pvol = int(OneYearData[sym][pUTC][4])
    p_candle_vol = int(SixtyDaysData[sym][prev_utc][-1][4])
    if c == 1 and (int(c_candle_vol)/pvol)*100 > 1:
	return True
    if c == 2 and (int(c_candle_vol)/pvol)*100 >= 1:
	return True
    if c == 3 and int(c_candle_vol) > p_candle_vol:
	return True
    if c == 4 and (int(c_candle_vol)/pvol)*100 > 1 and int(c_candle_vol) > p_candle_vol:
	return True
    if c == 5 and (int(c_candle_vol)/pvol)*100 >= 1 and int(c_candle_vol) > p_candle_vol:
	return True
    if c == 6:
	i=1
	vol5=0
	while i < 6:
	    vol5 += int(SixtyDaysData[sym][prev_utc][-i][4])
	    i+=1
	avg_vol5 = vol5/(i-1)
	if int(c_candle_vol) > avg_vol5:
	    return True
    return False

def IntradayStrategy(strategy, sym, UTC, pUTC):
    global RsymsBuy
    global RsymsSell

    cdata = CandleData(sym, UTC)
    c = cdata[0][0]
    h = float(cdata[0][1])
    low = float(cdata[0][2])
    o = float(cdata[0][3])
    prev_utc = GetPrevUTC(SixtyDaysData[sym], UTC)
    if prev_utc is None:
	return

    if strategy == 'Buy' or strategy == 'Both':
	if o == low and float(OneYearData[sym][pUTC][0]) < o and VolCheck(VOL_Check, sym, pUTC, prev_utc, cdata[0][4]):
	    log("Recommending Buy %s as o == l and pclose < o (%.2f, %.2f, %.2f, %.2f)" % (sym, o, low, float(OneYearData[sym][pUTC][0]), o))
	    log("Buy[%s]:YesterdaysVolume=%s,CurCandleVol=%s(%.2f%%)" % (sym,OneYearData[sym][pUTC][4],cdata[0][4],(int(cdata[0][4])/int(OneYearData[sym][pUTC][4]))*100))
	    RsymsBuy.append(sym)

    if strategy == 'Sell' or strategy == 'Both':
	if o == h and float(OneYearData[sym][pUTC][0]) < o and VolCheck(VOL_Check, sym, pUTC, prev_utc, cdata[0][4]):
	    log("Recommending Sell %s as o == h and pclose > o (%.2f, %.2f, %.2f, %.2f)" % (sym, o, h, float(OneYearData[sym][pUTC][0]), o))
	    log("Buy[%s]:YesterdaysVolume=%s,CurCandleVol=%s(%.2f%%)" % (sym,OneYearData[sym][pUTC][4],cdata[0][4],(int(cdata[0][4])/int(OneYearData[sym][pUTC][4]))*100))
	    RsymsSell.append(sym)

def BackTestBuy(sym, UTC):
    global sl_count
    global tgt_count
    global sq_count
    global GROSS
    global CPS

    no_sq_off=1
    pft_list = []
    sl_list = []
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
    #log("Sym=%s, ProfitPct=%.2f, Tgt Price = %.2f, SLPct=%.2f, SL Pric = %.2f" % (sym, ProfitPct, tgt_price, SLPct, sl_price))
    for l in cdata[1:]:
	# c h l o format, retrive the low and high
	c1 = float(l[0])
	h1 = float(l[1])
	l1 = float(l[2])
	o1 = float(l[3])
	if l1 == 0 or h1 == 0:
	    break
	if no_sq_off == 1 and l1 <= sl_price:
	    sl_count+=1
	    log("SL Hit: %s: %s => GROSS=%.2f, SLPct=%.2f%%, PurchasePrice=%.2f, SL=%.2f, ActualSLPct=%.2f%%, ActualLoss=%.2f, G-LOSS=%.2f" % (GetHumanDate(UTC), sym, GROSS, SLPct*100, pprice, sl_price, (l1-pprice)/pprice*100, CPS*((l1-pprice)/pprice), GROSS-((l1-pprice)/pprice)))
	    GROSS -= (CPS*abs((l1-pprice)/pprice))
	    no_sq_off=2
	if no_sq_off == 1 and (o1 >= tgt_price or h1 >= tgt_price or c1 >= tgt_price):
	#if no_sq_off == 1 and h1 >= tgt_price:
	    tgt_count+=1
	    log("TGT Hit: %s: %s => GROSS=%.2f, ProfitPct=%.2f%%, PurchasePrice=%.2f, TGT=%.2f, G+Earning=%.2f" % (GetHumanDate(UTC), sym, GROSS, ProfitPct*100, pprice, tgt_price, GROSS+(CPS*ProfitPct)))
	    GROSS += (CPS*ProfitPct)
	    no_sq_off=3
	if l1 < pprice:
	    sl_list.append("%s(%.2f%%)" % (l1,(((pprice-l1)/pprice))*100));
	if h1 > pprice:
	    pft_list.append("%s(%.2f%%)" % (h1,(((h1-pprice)/pprice))*100));
    if no_sq_off==2:
	log("%s: %s => PossibleSLHits = %s" % (sym, GetHumanDate(UTC), ','.join(sl_list)))
    elif no_sq_off==3:
	log("%s: %s => PossibleTgtHits = %s" % (sym, GetHumanDate(UTC), ','.join(pft_list)))
    elif l1 > 0 and h1 > 0:
	log("SquareOff Hit: %s: %s => Purchase Price=%.2f, Low=%.2f, High=%.2f, Close=%.2f, CutOffPrice=%.2f], GROSS=%.2f, CPCT=%.2f, G+Earning=%.2f,PossibleTgtHits[%s],PossibleSLHits[%s]" % (GetHumanDate(UTC), sym, pprice, l1, h1, c1, (l1+c1)/2, GROSS, (((l1+c1)/2)-pprice)/pprice, GROSS + (CPS*((((l1+c1)/2)-pprice)/pprice)), ','.join(pft_list), ','.join(sl_list)))
	sq_count+=1
	GROSS += (CPS*((((l1+c1)/2)-pprice)/pprice))

def BackTestSell(sym, UTC):
    global sl_count
    global tgt_count
    global sq_count
    global GROSS
    global CPS

    no_sq_off=1
    pft_list = []
    sl_list = []
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
	o1 = float(l[3])
	if l1 == 0 or h1 == 0:
	    break
	if no_sq_off==1 and h1 >= sl_price:
	    log("SL Hit: %s: %s => GROSS=%.2f, SLPct=%.2f%%, PurchasePrice=%.2f, SL=%.2f, ActualSLPct=%.2f%%, ActualLoss=%.2f, G-LOSS=%.2f" % (GetHumanDate(UTC), sym, GROSS, SLPct*100, pprice, sl_price, (h1-pprice)/pprice*100, CPS*((h1-pprice)/pprice), GROSS-((h1-pprice)/pprice)))
	    sl_count+=1
	    GROSS -= (CPS*abs((h1-pprice)/pprice))
	    no_sq_off=0
	if no_sq_off==1 and (o1 <= tgt_price or l1 <= tgt_price or c1 <= tgt_price):
	    log("SL Hit: %s: %s => GROSS=%.2f, SLPct=%.2f%%, PurchasePrice=%.2f, SL=%.2f, ActualSLPct=%.2f%%, ActualLoss=%.2f, G-LOSS=%.2f" % (GetHumanDate(UTC), sym, GROSS, SLPct*100, pprice, sl_price, (l1-pprice)/pprice*100, CPS*((l1-pprice)/pprice), GROSS-((l1-pprice)/pprice)))
	    tgt_count+=1
	    GROSS += (CPS*ProfitPct)
	    no_sq_off=0
	if l1 < pprice:
	    pft_list.append("%s(%.2f%%)" % (l1,((l1/pprice)-1)*100));
	if h1 > pprice:
	    sl_list.append("%s(%.2f%%)" % (h1,((h1/pprice)-1)*100));
    if l1 > 0 and h1 > 0 and no_sq_off==1:
	log("%s => %s => SquareOff Hit [Purchase Price=%.2f, Low=%.2f, High=%.2f, CutOffPrice=%.2f]" % (sym, GetHumanDate(UTC), pprice, l1, h1, (l1+h1)/2))
	log("GROSS=%.2f, CPCT=%.2f, G+Earning=%.2f,PossibleTgtHits[%s],PossibleSLHits[%s]" % (GROSS, (CPS*((((l1+h1)/2)-pprice)/pprice)), GROSS + (CPS*((((l1+h1)/2)-pprice)/pprice)), ','.join(pft_list), ','.join(sl_list)))
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
    lutc = 0
    for d in content:
	if d[0][0] == 'a':
	    utc = d[0].replace('a', '')
	else:
	    utc = lutc + (int(d[0]) * Interval)
	if (int(utc) - int(lutc)) < 86400:
	    #print "Appending to %s" % GetHumanDate(lutc)
	    data[str(lutc)].append(d[1:])
	else:
	    lutc = int(utc)
	    #print "Making new entry for %s" % GetHumanDate(lutc)
	    data[str(lutc)] = [d[1:]]
    #print sorted(data.keys())
    return data

NiftyIndex60DCandle = {}
def GetNiftyIndex60DCandleData():
    global NiftyIndex60DCandle
    response = urllib2.urlopen('https://finance.google.com/finance/getprices?x=NSE&q=NIFTY&f=d,c,h,l,o,v&p=60d&i=%s' % Interval)
    content = csv.reader(response.read().splitlines()[7:])
    lutc = 0
    for d in content:
	if d[0][0] == 'a':
	    utc = d[0].replace('a', '')
	else:
	    utc = lutc + (int(d[0]) * Interval)
	if (int(utc) - int(lutc)) < 86400:
	    #print "Appending to %s" % GetHumanDate(utc)
	    NiftyIndex60DCandle[str(lutc)].append(d[1:])
	else:
	    lutc = int(utc)
	    #print "Making new entry for %s" % GetHumanDate(lutc)
	    NiftyIndex60DCandle[str(lutc)] = [d[1:]]

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

def GetPrevUTCNifty(pUTC):
    keys = NiftyIndex1YCandle.keys()
    i=1
    while i < 6:
	pUTC = str(int(pUTC) - (i*86400))
	if pUTC in keys:
	    return pUTC
	i+=1
    return None

def GetPrevUTC(data, pUTC):
    keys = data.keys()
    i=1
    while i < 6:
	pUTC = str(int(pUTC) - (i*86400))
	if pUTC in keys:
	    return pUTC
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
    global sq_count
    global plot_returns
    global plot_hits
    global y
    global m
    global d
    global RsymsBuy
    global RsymsSell
    global GROSS
    global CPS
    global SMA_Check
    tdays=0
    t_count=0
    t_tgt_count=0
    t_sl_count=0
    t_sq_count=0

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
	    prev_utc = GetPrevUTCNifty(str(utcl))
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
	    #log("[%s]: Ncpt = %.2f, Strategy=%s" % (GetHumanDate(utc), Ncpt, strategy))
	else:
	    strategy = s

	RsymsBuy = []
	RsymsSell = []

	# Shortlist complete list of stocks in one iteration
	for sym in Nsyms:
	    prev_utc = GetPrevUTC(OneYearData[sym], utcl)
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
		#log("Symbol %s is not shortlisted for %s-%s" % (sym, GetHumanDate(utc), GetHumanDate(prev_utc)))

	if len(RsymsBuy) > 0:
	    print("Recommended Buy Stocks = %s" % ','.join(RsymsBuy))

	if len(RsymsSell) > 0:
	    print("Recommended Sell Stocks = %s" % ','.join(RsymsSell))

	if BackTesting is True and (len(RsymsBuy) > 0 or len(RsymsSell) > 0):
	    if (strategy == "Buy" or strategy == "Both") and len(RsymsBuy) > 0:
		for sym in RsymsBuy:
		    SMA_list = CalculateSMA(sym, prev_utc)
		    if SMA_Check:
			if float(CandleData(sym, utc)[0][3]) < float(SMA_list[2]):
			    log("Removing %s from shortlisted stocks [%s < %s]" % (sym, CandleData(sym, utc)[0][3], SMA_list[0]))
			    RsymsBuy.remove(sym)
			#else:
			    #log("Retaining %s in shortlisted stocks [%s > %s]" % (sym, CandleData(sym, utc)[0][3], SMA_list[0]))
	    if (strategy == "Sell" or strategy == "Both") and len(RsymsSell) > 0:
		for sym in RsymsSell:
		    SMA_list = CalculateSMA(sym, prev_utc)
		    if SMA_Check:
			if float(CandleData(sym, utc)[0][3]) > float(SMA_list[2]):
			    log("Removing %s from shortlisted stocks [%s > %s]" % (sym, CandleData(sym, utc)[0][3], SMA_list[0]))
			    RsymsSell.remove(sym)
		        #else:
			    #log("Retaining %s in shortlisted stocks [%s < %s]" % (sym, CandleData(sym, utc)[0][3], SMA_list[0]))

	    total_count=len(RsymsBuy)+len(RsymsSell)

	    sl_count=0
	    tgt_count=0
	    sq_count=0

	    if GROSS <= 0:
		break

	    if strategy == "Buy" and len(RsymsBuy) > 0:
		CPS=GROSS/len(RsymsBuy)
	    elif strategy == "Sell" and len(RsymsSell) > 0:
		CPS=GROSS/len(RsymsSell)
	    elif len(RsymsBuy) > 0 or len(RsymsSell) > 0:
		CPS=GROSS/(len(RsymsBuy)+len(RsymsSell))

	    if CPS <= 0:
		break

	    if (strategy == "Buy" or strategy == "Both") and len(RsymsBuy) > 0:
		for sym in RsymsBuy:
		    #log("%s[5,10,20,30] = [%s,%s,%s,%s]" % (sym, SMA_list[0], SMA_list[1], SMA_list[2], SMA_list[3]))
		    BackTestBuy(sym, utc)

	    if (strategy == "Sell" or strategy == "Both") and len(RsymsSell) > 0:
		for sym in RsymsSell:
		    #log("%s[5,10,20,30] = [%s,%s,%s,%s]" % (sym, SMA_list[0], SMA_list[1], SMA_list[2], SMA_list[3]))
		    BackTestSell(sym, utc)

	    if total_count > 0:
		cdate = GetHumanDate(utc)
		print >>plot_returns_handle, "%s,%s" % (cdate,GROSS)
		print >>plot_hits_handle, "%s,%d,%d,%d" % (cdate,sl_count,tgt_count,sq_count)
		print("%s %d: Total Count=%d" % (Months[m-1], d, total_count))
		print("%s %d: STP Count=%d, Hit Ratio=%d" % (Months[m-1], d, sl_count, (sl_count/total_count*100)))
		print("%s %d: TGT Count=%d, Hit Ratio=%d" % (Months[m-1], d, tgt_count, (tgt_count/total_count*100)))
		print("%s %d: SQO Count=%d, Hit Ratio=%d" % (Months[m-1], d, sq_count, (sq_count/total_count*100)))
		t_count+=total_count
		t_tgt_count+=tgt_count
		t_sl_count+=sl_count
		t_sq_count+=sq_count
		tdays+=1
	d+=1
	if one_day_scan == 1:
	    break
    if BackTesting == True:
	print("Nifty%d[%s]: Capital=%d, Gross=%d, Pct=%.2f%% (ProfitPct=%s,SLPct=%s,SMA=%s, VOL=%s, TotalStocks=%d, Tgt-Hit=%d, SL-Hit=%d, SQ-Hit=%d)" % (len(Nsyms), s, CAPITAL, GROSS, float((GROSS-CAPITAL)/CAPITAL)*100, ProfitPct, SLPct, SMA_Check, VOL_Check, t_count, t_tgt_count, t_sl_count, t_sq_count))
	print "Total number of trade days=%d" % tdays
	plot_returns_handle.close();
	plot_hits_handle.close();

pcts = []

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
	    elif sys.argv[i] == "--scrips":
		Nsyms.extend(sys.argv[i+1].split(','))
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
	if variance == "Go_with_Nifty":
	    MainLoop('Nifty');
	elif variance == "ALL":
	    for sma in (0, 1):
		if sma == 1:
		    SMA_Check=True
		else:
		    SMA_Check=False
		for vol in (1, 2, 3, 4, 5, 6):
		    VOL_Check=vol
		    for pft_sl in pcts.split(','):
			pft_sl_list = pft_sl.split(':')
			ProfitPct = float(pft_sl_list[0])/100
			SLPct = float(pft_sl_list[1])/100
			for s in ('Buy', 'Both', 'Nifty'):
			    plot_returns=plot_returns1.replace('.csv','_%s_%s_SMA_%s_VOL_%s.csv' % (ProfitPct, SLPct, sma, vol))
			    plot_hits=plot_hits1.replace('.csv','_%s_%s_SMA_%s_VOL_%s.csv' % (ProfitPct, SLPct, sma, vol))
			    MainLoop(s)
			    Initialize()
