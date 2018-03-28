#!/usr/bin/python

from __future__ import division

import urllib2
import csv
import time, datetime
 
NDays = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

Months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

Nifty100 = []
with open('ind_nifty100list.csv', 'rb') as f:
    reader = csv.reader(f)
    Nifty100.extend(list(reader))

Nifty50 = []
with open('ind_nifty50list.csv', 'rb') as f:
    reader = csv.reader(f)
    Nifty50.extend(list(reader))

total_count = 0
sl_count = 0
tgt_count = 0
sq_count = 0

ProfitPct = 0.005
SLPct = 0.01
SQOFFPct=0

CAPITAL=100000
GROSS=CAPITAL
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
    global GROSS

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
        l1 = l[2]
        h1 = l[1]
        if float(l1) <= sl_price:
            print("%s => SL Hit [Purchase Price=%s, Low=%s, SL=%s]" % (sym, pprice, l1, sl_price))
            sl_count+=1
            GROSS -= (GROSS*ProfitPct)
            return
        if float(h1) >= tgt_price:
            print("%s => TGT Hit [Purchase Price=%s, High=%s, TGT=%s]" % (sym, pprice, h1, tgt_price))
            tgt_count+=1
            GROSS += (GROSS*SLPct)
            return
    print("SquareOff for %s [Low=%s, High=%s, CutOffPrice=%s]" % (sym, l1, h1, (float(l1)+float(h1)/2)))
    GROSS += (GROSS*((pprice-low)/pprice))
    sq_count+=1

def GetNifty100Data():
    global sym_maps
    response = requests.get('https://docs.google.com/spreadsheet/ccc?key=1RtKztdvSfTi1uhOzidZX9JGjyjOVf4PfrH6e-lEAJ_Y&output=csv')
    assert response.status_code == 200, 'Wrong status code'
    for l in response.content.splitlines()[1:]:
        sym = l.split(',')[1]
        sym_maps[sym] = l.split(',')        

Interval = 120
OneYearData = {}
SixtyDaysData = {}

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

if __name__=="__main__":
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
        for sym in symbols:
            if utc in SixtyDaysData[sym].keys() and prev_utc in OneYearData[sym].keys():
                IntradayStrategy1(sym, SixtyDaysData[sym][utc], OneYearData[sym][prev_utc])
        total_count=0
        sl_count=0
        tgt_count=0
        sq_count=0
        for sym in Rsyms:
            if utc in SixtyDaysData[sym].keys() and prev_utc in OneYearData[sym].keys():
                BackTest(sym, SixtyDaysData[sym][utc], OneYearData[sym][prev_utc])
        if total_count > 0:
            print("%s %d: Total Count=%d" % (Months[m-1], d, total_count))
            print("%s %d: STP Count=%d, Hit Ratio=%d" % (Months[m-1], d, sl_count, (sl_count/total_count*100)))
            print("%s %d, TGT Count=%d, Hit Ratio=%d" % (Months[m-1], d, tgt_count, (tgt_count/total_count*100)))
            print("%s %d, SQO Count=%d, Hit Ratio=%d" % (Months[m-1], d, sq_count, (sq_count/total_count*100)))
        d+=1
    print("Initial Capital=%d, Gross amount=%d, Pct=%.2f" % (CAPITAL, GROSS, (GROSS-CAPITAL)/CAPITAL))
