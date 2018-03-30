#!/usr/bin/python -u

from __future__ import division

import urllib2
import csv
import datetime
 
BackTesting = True

NDays = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

Months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

Interval = 480
OneYearData = {}
SixtyDaysData = {}

total_count = 0
sl_count = 0
tgt_count = 0
sq_count = 0

ProfitPct = 0.8/100
SLPct = 0.4/100
#ProfitPct = 0.3/100
#SLPct = 1/100

CAPITAL=100000
GROSS=CAPITAL
CAPITAL_PER_SHARE=0
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
    for l in d60[1:]:
        # c h l o format, retrive the low and high
        l1 = float(l[2])
        h1 = float(l[1])
        if l1 == 0 or h1 == 0:
            break
        if l1 <= sl_price:
            print("%s => SL Hit [Purchase Price=%f, Low=%f, SL=%f]" % (sym, pprice, l1, sl_price))
            sl_count+=1
	    print("GROSS=%f, CPS=%f, G-LOSS=%f" % (GROSS, (CAPITAL_PER_SHARE*SLPct), GROSS-(CAPITAL_PER_SHARE*SLPct)))
            GROSS -= (CAPITAL_PER_SHARE*SLPct)
            return
        if h1 >= tgt_price:
            print("%s => TGT Hit [Purchase Price=%f, High=%f, TGT=%f]" % (sym, pprice, h1, tgt_price))
            tgt_count+=1
	    print("GROSS=%f, CPS=%f, G+Earning=%f" % (GROSS, (CAPITAL_PER_SHARE*ProfitPct), GROSS+(CAPITAL_PER_SHARE*ProfitPct)))
            GROSS += (CAPITAL_PER_SHARE*ProfitPct)
            return
    if l1 > 0 and h1 > 0:
        print("%s => SquareOff [Low=%f, High=%f, CutOffPrice=%f]" % (sym, l1, h1, (l1+h1)/2))
	print("GROSS=%f, CPS=%f, G+Earning=%f" % (GROSS, (CAPITAL_PER_SHARE*((((l1+h1)/2)-pprice)/pprice)), GROSS + (CAPITAL_PER_SHARE*((((l1+h1)/2)-pprice)/pprice))))
        GROSS += (CAPITAL_PER_SHARE*((((l1+h1)/2)-pprice)/pprice))
        sq_count+=1

def Get_1Y_Data(sym):
    data = {}
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
    response = urllib2.urlopen('https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=60d&i=%s' % (sym, Interval))
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

def GetPrevUTC(putc):
    prev_utc = putc
    if putc not in OneYearData[sym].keys():
        i=1
        while i < 5:
            putc = str(int(putc) - (i*86400))
            if putc in OneYearData[sym].keys():
                return putc
                break
            i+=1
    return prev_utc

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

if __name__=="__main__":
    ndays = 0
    Nsyms = []
    #Nsyms.append(GetNifty50Symbols())
    Nsyms.append(GetNifty100Symbols())
    #Nsyms.append(GetNifty200Symbols())
    for symbols in Nsyms:
        for sym in symbols:
            OneYearData[sym] = Get_1Y_Data(sym)
            SixtyDaysData[sym] = Get_60D_Data(sym)
        y = 2018
        m = 1
        d = 1
        while True:
            if m > 3:
                break
            if (m == 2 and d > 27) or d > 30:
                d=2
                m+=1
                continue
            Rsyms = []
            dt = datetime.datetime(y, m, d, 9, 16, 0)
            utc = dt.strftime("%s")
            pm = m
            py = y
            if d == 1:
                if m == 1:
                    pday = NDays[11]
                    pm = 12
                    py -= 1
                else:
                    pday = NDays[m-1]
            else:
                pday = d-1
            dt = datetime.datetime(py, pm, pday, 15, 30, 0)
            prev_utc = GetPrevUTC(dt.strftime("%s"))
            #print("Iteration for %s" % (datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S')))
            for sym in symbols:
                if utc in SixtyDaysData[sym].keys() and prev_utc in OneYearData[sym].keys():
                    IntradayStrategy1(sym, SixtyDaysData[sym][utc], OneYearData[sym][prev_utc])
                #else:
                    #print("Symbol %s is not shortlisted for %s(%s)" % (sym, utc, datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S')))
            if BackTesting is True and len(Rsyms) > 0:
                ndays+=1
                total_count=0
                sl_count=0
                tgt_count=0
                sq_count=0
		if GROSS == 0:
                    CAPITAL_PER_SHARE=CAPITAL/len(Rsyms)
                else:
                    CAPITAL_PER_SHARE=GROSS/len(Rsyms)
                for sym in Rsyms:
                    if utc in SixtyDaysData[sym].keys() and prev_utc in OneYearData[sym].keys():
                        BackTest(sym, SixtyDaysData[sym][utc], OneYearData[sym][prev_utc])
                if total_count > 0:
                    print("%s %d: Total Count=%d" % (Months[m-1], d, total_count))
                    print("%s %d: STP Count=%d, Hit Ratio=%d" % (Months[m-1], d, sl_count, (sl_count/total_count*100)))
                    print("%s %d, TGT Count=%d, Hit Ratio=%d" % (Months[m-1], d, tgt_count, (tgt_count/total_count*100)))
                    print("%s %d, SQO Count=%d, Hit Ratio=%d" % (Months[m-1], d, sq_count, (sq_count/total_count*100)))
            d+=1
            #break
        print("Nifty%d: Initial Capital=%d, Gross amount=%d, Pct=%.2f%%" % (len(symbols), CAPITAL, GROSS, float((GROSS-CAPITAL)/CAPITAL)*100))
    print ndays
