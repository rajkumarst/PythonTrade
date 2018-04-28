#!/usr/bin/python -u

from __future__ import division

import json, os, sys, datetime, csv, urllib2
#import requests, io
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy
 
verbose=0
one_day_scan=0
y = 2018
m = 1
d = 1
CAPITAL=100000
CPS=0
GROSS=CAPITAL
today=False
variance = "Both-Buy-And-Sell"
plot_returns='out.plot_earnings'
plot_hits='out.plot_hits'
RsymsSell = []
RsymsSellDetail = []
RsymsBuy = []
RsymsBuyDetail = []
BackTesting = True
#Interval = 960
Interval = 120
TodayData = {}
OneYearData = {}
SixtyDaysData = {}
VOL_Check=8
CPT_Check=1
E_Check=0
sl_count = 0
tgt_count = 0
sq_count = 0
ProfitPct = 1.5/100
SLPct = 0.75/100
Leverage=False
pcts = []
LOCAL_CACHE=True

NDays = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
Months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

MIS={'BANKBEES':'10',
'GOLDBEES':'10',
'GRANULES':'10',
'LIQUIDBEES':'10',
'NIFTYBEES':'10',
'BHEL':'11',
'BRITANNIA':'11',
'EICHERMOT':'11',
'ENGINERSIN':'11',
'EXIDEIND':'11',
'GLENMARK':'11',
'GRASIM':'11',
'HEXAWARE':'11',
'HINDALCO':'11',
'HINDPETRO':'11',
'HINDZINC':'11',
'INDIACEM':'11',
'JISLJALEQS':'11',
'JUBLFOOD':'11',
'L&TFH':'11',
'LICHSGFIN':'11',
'LUPIN':'11',
'M&MFIN':'11',
'MARICO':'11',
'MCDOWELL-N':'11',
'MCLEODRUSS':'11',
'MOTHERSUMI':'11',
'MRF':'11',
'NCC':'11',
'NMDC':'11',
'NTPC':'11',
'PIDILITIND':'11',
'PTC':'11',
'RECLTD':'11',
'SRF':'11',
'SRTRANSFIN':'11',
'TATACHEM':'11',
'TATAMOTORS':'11',
'TATAMTRDVR':'11',
'TITAN':'11',
'TVSMOTOR':'11',
'UBL':'11',
'ULTRACEMCO':'11',
'UPL':'11',
'VEDL':'11',
'ZEEL':'11',
'ICIL':'13',
'KSCL':'13',
'UNIONBANK':'13',
'ACC':'14',
'AMARAJABAT':'14',
'AMBUJACEM':'14',
'APOLLOHOSP':'14',
'APOLLOTYRE':'14',
'ARVIND':'14',
'ASHOKLEY':'14',
'ASIANPAINT':'14',
'AXISBANK':'14',
'BAJAJ-AUTO':'14',
'BANKBARODA':'14',
'BATAINDIA':'14',
'BHARATFORG':'14',
'BHARTIARTL':'14',
'BOSCHLTD':'14',
'BPCL':'14',
'CANBK':'14',
'CASTROLIND':'14',
'CEATLTD':'14',
'CIPLA':'14',
'COALINDIA':'14',
'COLPAL':'14',
'DABUR':'14',
'DCBBANK':'14',
'FEDERALBNK':'14',
'GAIL':'14',
'HDFC':'14',
'HDFCBANK':'14',
'HEROMOTOCO':'14',
'HINDUNILVR':'14',
'ICICIBANK':'14',
'IGL':'14',
'INDUSINDBK':'14',
'IOC':'14',
'ITC':'14',
'JSWSTEEL':'14',
'KOTAKBANK':'14',
'KTKBANK':'14',
'LT':'14',
'M&M':'14',
'MARUTI':'14',
'OIL':'14',
'ONGC':'14',
'PETRONET':'14',
'POWERGRID':'14',
'RELIANCE':'14',
'SBIN':'14',
'STAR':'14',
'TATASTEEL':'14',
'YESBANK':'14',
'3MINDIA':'3',
'AARTIIND':'3',
'ABAN':'3',
'ABB':'3',
'ABFRL':'3',
'ADANIENT':'3',
'ADANIPORTS':'3',
'AKZOINDIA':'3',
'ALKEM':'3',
'ALLCARGO':'3',
'APLLTD':'3',
'ASAHIINDIA':'3',
'ASTRAZEN':'3',
'ATFL':'3',
'ATUL':'3',
'AUBANK':'3',
'AUTOAXLES':'3',
'BAJAJCORP':'3',
'BAJAJELEC':'3',
'BAJAJFINSV':'3',
'BAJAJHIND':'3',
'BAJAJHLDNG':'3',
'BALKRISIND':'3',
'BALRAMCHIN':'3',
'BANCOINDIA':'3',
'BERGEPAINT':'3',
'BGRENERGY':'3',
'BLUEDART':'3',
'BRNL':'3',
'BSE':'3',
'CANFINHOME':'3',
'CAPACITE':'3',
'CAPF':'3',
'CDSL':'3',
'CENTRALBK':'3',
'CENTURYPLY':'3',
'CHENNPETRO':'3',
'CHOLAFIN':'3',
'COCHINSHIP':'3',
'COROMANDEL':'3',
'COX&KINGS':'3',
'CRISIL':'3',
'CROMPTON':'3',
'CUB':'3',
'CUMMINSIND':'3',
'CYIENT':'3',
'DALMIABHA':'3',
'DBCORP':'3',
'DCMSHRIRAM':'3',
'DIAMONDYD':'3',
'DIXON':'3',
'DMART':'3',
'ECLERX':'3',
'EDELWEISS':'3',
'EIDPARRY':'3',
'EMAMILTD':'3',
'ENDURANCE':'3',
'EQUITAS':'3',
'ERIS':'3',
'ESCORTS':'3',
'EVEREADY':'3',
'FEL':'3',
'FINCABLES':'3',
'FORTIS':'3',
'FRETAIL':'3',
'GANECOS':'3',
'GATI':'3',
'GDL':'3',
'GEPIL':'3',
'GESHIP':'3',
'GICHSGFIN':'3',
'GICRE':'3',
'GILLETTE':'3',
'GLAXO':'3',
'GNA':'3',
'GNFC':'3',
'GODREJCP':'3',
'GODREJPROP':'3',
'GPPL':'3',
'GREAVESCOT':'3',
'GRUH':'3',
'GSFC':'3',
'GSKCONS':'3',
'GSPL':'3',
'GTPL':'3',
'GUJALKALI':'3',
'GUJFLUORO':'3',
'GUJGASLTD':'3',
'HCC':'3',
'HDIL':'3',
'HEIDELBERG':'3',
'HGS':'3',
'HIKAL':'3',
'HONAUT':'3',
'HSCL':'3',
'HSIL':'3',
'HUDCO':'3',
'IBREALEST':'3',
'ICICIGI':'3',
'ICICIPRULI':'3',
'IEX':'3',
'IGPL':'3',
'IIFL':'3',
'IL&FSTRANS':'3',
'INDHOTEL':'3',
'INDIANB':'3',
'INDIGO':'3',
'INFIBEAM':'3',
'INOXLEISUR':'3',
'INOXWIND':'3',
'INTELLECT':'3',
'IOB':'3',
'IPCALAB':'3',
'JAGRAN':'3',
'JAMNAAUTO':'3',
'JETAIRWAYS':'3',
'JINDALPOLY':'3',
'JKCEMENT':'3',
'JKPAPER':'3',
'JKTYRE':'3',
'JPASSOCIAT':'3',
'JSL':'3',
'JSLHISAR':'3',
'JUBILANT':'3',
'JUSTDIAL':'3',
'JYOTHYLAB':'3',
'KAJARIACER':'3',
'KALPATPOWR':'3',
'KANSAINER':'3',
'KARURVYSYA':'3',
'KEC':'3',
'KEI':'3',
'KESORAMIND':'3',
'KHADIM':'3',
'KIRLOSENG':'3',
'KOTAKNIFTY':'3',
'KRBL':'3',
'LALPATHLAB':'3',
'LEEL':'3',
'LGBBROSLTD':'3',
'LINDEINDIA':'3',
'LOVABLE':'3',
'M100':'3',
'M50':'3',
'MAGMA':'3',
'MAHINDCIE':'3',
'MAHLOG':'3',
'MAJESCO':'3',
'MANALIPETC':'3',
'MANAPPURAM':'3',
'MANGALAM':'3',
'MANINFRA':'3',
'MANPASAND':'3',
'MARKSANS':'3',
'MASFIN':'3',
'MATRIMONY':'3',
'MCX':'3',
'MEGH':'3',
'MERCATOR':'3',
'MFSL':'3',
'MGL':'3',
'MINDAIND':'3',
'MOIL':'3',
'MOLDTKPAC':'3',
'MPHASIS':'3',
'MRPL':'3',
'MUKANDLTD':'3',
'MUTHOOTFIN':'3',
'NATIONALUM':'3',
'NAUKRI':'3',
'NBCC':'3',
'NESTLEIND':'3',
'NETWORK18':'3',
'NFL':'3',
'NH':'3',
'NIACL':'3',
'NIF100IWIN':'3',
'NIFTYIWIN':'3',
'NIITLTD':'3',
'NLCINDIA':'3',
'NOCIL':'3',
'NRBBEARING':'3',
'OBEROIRLTY':'3',
'OMAXE':'3',
'ORIENTCEM':'3',
'PARAGMILK':'3',
'PCJEWELLER':'3',
'PEL':'3',
'PERSISTENT':'3',
'PFIZER':'3',
'PGHH':'3',
'PHOENIXLTD':'3',
'PIIND':'3',
'PNBHOUSING':'3',
'POLYPLEX':'3',
'PRAKASH':'3',
'PRESTIGE':'3',
'PVR':'3',
'QUICKHEAL':'3',
'RADICO':'3',
'RADIOCITY':'3',
'RAJESHEXPO':'3',
'RALLIS':'3',
'RAMCOCEM':'3',
'RAMCOIND':'3',
'RBLBANK':'3',
'RCF':'3',
'RCOM':'3',
'RELAXO':'3',
'REPCOHOME':'3',
'RICOAUTO':'3',
'RKFORGE':'3',
'RNAM':'3',
'RNAVAL':'3',
'ROLTA':'3',
'SADBHAV':'3',
'SALASAR':'3',
'SANGHIIND':'3',
'SANOFI':'3',
'SAREGAMA':'3',
'SBILIFE':'3',
'SCHAND':'3',
'SCI':'3',
'SHANKARA':'3',
'SHARDAMOTR':'3',
'SHRIRAMCIT':'3',
'SICAL':'3',
'SINTEX':'3',
'SIS':'3',
'SJVN':'3',
'SKFINDIA':'3',
'SNOWMAN':'3',
'SOBHA':'3',
'SOLARINDS':'3',
'SPARC':'3',
'SPTL':'3',
'SREINFRA':'3',
'SUNDARMFIN':'3',
'SUNDRMFAST':'3',
'SUNTECK':'3',
'SUNTV':'3',
'SUPREMEIND':'3',
'SUZLON':'3',
'SYMPHONY':'3',
'SYNGENE':'3',
'TATACOFFEE':'3',
'TATAINVEST':'3',
'TATASPONGE':'3',
'TBZ':'3',
'TCI':'3',
'TEJASNET':'3',
'THERMAX':'3',
'THOMASCOOK':'3',
'THYROCARE':'3',
'TIFIN':'3',
'TIRUMALCHM':'3',
'TNPETRO':'3',
'TNPL':'3',
'TRENT':'3',
'TRIDENT':'3',
'TTKPRESTIG':'3',
'TWL':'3',
'UCOBANK':'3',
'UJJIVAN':'3',
'VGUARD':'3',
'VIJAYABANK':'3',
'VISHNU':'3',
'VTL':'3',
'WABCOINDIA':'3',
'WELENT':'3',
'WHIRLPOOL':'3',
'WONDERLA':'3',
'ADANIPOWER':'5',
'ALBK':'5',
'ANDHRABANK':'5',
'GMRINFRA':'5',
'IDBI':'5',
'IDFC':'5',
'IDFCBANK':'5',
'IFCI':'5',
'JSWENERGY':'5',
'NHPC':'5',
'PNB':'5',
'RAYMOND':'5',
'RPOWER':'5',
'SAIL':'5',
'SOUTHBANK':'5',
'SYNDIBANK':'5',
'TV18BRDCST':'5',
'AUROPHARMA':'7',
'BAJFINANCE':'7',
'BANKINDIA':'7',
'DHFL':'7',
'DIVISLAB':'7',
'DLF':'7',
'DRREDDY':'7',
'GODREJIND':'7',
'IDEA':'7',
'ORIENTBANK':'7',
'SUNPHARMA':'7',
'TORNTPHARM':'7',
'WOCKPHARMA':'7',
'AJANTPHARM':'8',
'BHARATFIN':'8',
'CENTURYTEX':'8',
'CGPOWER':'8',
'JINDALSTEL':'8',
'KPIT':'8',
'OFSS':'8',
'TORNTPOWER':'8',
'BEL':'9',
'BEML':'9',
'BIOCON':'9',
'CADILAHC':'9',
'CESC':'9',
'CONCOR':'9',
'DISHTV':'9',
'HAVELLS':'9',
'HCLTECH':'9',
'IBULHSGFIN':'9',
'INFRATEL':'9',
'INFY':'9',
'IRB':'9',
'MINDTREE':'9',
'NIITTECH':'9',
'PAGEIND':'9',
'PFC':'9',
'RELCAPITAL':'9',
'RELINFRA':'9',
'SIEMENS':'9',
'TATACOMM':'9',
'TATAELXSI':'9',
'TATAGLOBAL':'9',
'TATAPOWER':'9',
'TCS':'9',
'TECHM':'9',
'VOLTAS':'9',
'WIPRO':'9'
}

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

VOLS_check_list = ['CandleVolume > 2% of YesterdaysVolume', 'CandleVolume > 1% of YesterdaysVolume', 'CandleVolume > YesterdayLastCandleVolume', 'CandleVolume > 1.5% of YesterdayLastCandleVolume', 'CandleVolume > AverageofYesterdatLast5CandleVolume', 'CandleVolume > 1.5% of AverageofYesterdatLast5CandleVolume', 'CandleVolume > 1.5% of YesterdaysVolume', 'CandleVolume > 3% of YesterdaysVolume', 'CandleVolume > 3.5% of YesterdaysVolume']

def VolCheck(c, sym, pUTC, prev_utc, c_candle_vol):
    # prev_utc will refer to previous day 3:30 UTC
    # pUTC will refer to previous day 9:16
    #print GetHumanDate(prev_utc), GetHumanDate(pUTC)
    pvol = int(OneYearData[sym][pUTC][4])
    p_candle_vol = int(SixtyDaysData[sym][prev_utc][-1][4])
    if c == 0 and (c_candle_vol/pvol)*100 > 2:
	#log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 1 and (c_candle_vol/pvol)*100 > 1:
	#log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 2 and c_candle_vol > p_candle_vol:
	#log("%s: PreviousDayLastCandleVolume=%d, CurrentCandleVolume=%d" % (sym, p_candle_vol, c_candle_vol))
	return True
    if c == 3 and (c_candle_vol/p_candle_vol)*100 > 1.5:
	#log("%s: PreviousDayLastCandleVolume=%d, CurrentCandleVolume=%d" % (sym, p_candle_vol, c_candle_vol))
	return True
    if c == 4 or c == 5:
	i=1
	vol5=0
	while i < 5:
	    vol5 += int(SixtyDaysData[sym][prev_utc][-i][4])
	    i+=1
	avg_vol5 = vol5/(i-1)
	if c == 4 and c_candle_vol > avg_vol5:
	    #log("%s: PreviousDayLast5CandleVolumeAvg=%d, CurrentCandleVolume=%d" % (sym, avg_vol5, c_candle_vol))
	    return True
	if c == 5 and (c_candle_vol/avg_vol5)*100 > 1.5:
	    #log("%s: PreviousDayLast5CandleVolumeAvg=%d, CurrentCandleVolume=%d" % (sym, avg_vol5, c_candle_vol))
	    return True
    if c == 6 and (c_candle_vol/pvol)*100 > 1.5:
	#log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 7 and (c_candle_vol/pvol)*100 > 3:
	#log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 8 and (c_candle_vol/pvol)*100 > 3.5:
	#log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    return False

CPT_check_list = ['Open > (Buy) or < (Sell) 0% of PrevClose', 'Open > (Buy) or < (Sell) 0.25% of PrevClose', 'Open > (Buy) or < (Sell) 0.1% of PrevClose', 'Open > (Buy) or < (Sell) 0.2% of PrevClose', 'Open > (Buy) or < (Sell) 0.3% of PrevClose', 'Open > (Buy) or < (Sell) 0.4% of PrevClose', 'Open > (Buy) or < (Sell) 0.5% of PrevClose']
def CPTCheck(cpt):
    if CPT_Check == 0:
	return 0
    elif CPT_Check == 1:
	return abs(cpt) > 0.25
    elif CPT_Check == 2:
	return abs(cpt) > 0.1
    elif CPT_Check == 3:
	return abs(cpt) > 0.2
    elif CPT_Check == 4:
	return abs(cpt) > 0.3
    elif CPT_Check == 5:
	return abs(cpt) > 0.4
    elif CPT_Check == 6:
	return abs(cpt) > 0.5

ECheck_list = ['Echeck Disabled', '2nd Candle Close > (Buy) or < (Sell) 1st Candle Close', '2nd Candle Low > (Buy) or < (Sell) 1st Candle Low', '2nd Candle High > (Buy) or < (Sell) 1st Candle High']
def ECheck(call, c1, c2):
    close=0
    high=1
    low=3
    open=4
    if E_Check == 0:
	return True
    elif E_Check == 1:
	if call == 'Buy':
	    return (float(c2[close]) > float(c1[close]))
	else:
	    return (float(c2[close]) < float(c1[close]))
    elif E_Check == 2:
	if call == 'Buy':
	    return (float(c2[low]) < float(c1[low]))
	else:
	    return (float(c2[low]) > float(c1[low]))
    elif E_Check == 3:
	if call == 'Buy':
	    return (float(c2[high]) > float(c1[high]))
	else:
	    return (float(c2[high]) < float(c1[high]))

def IntradayStrategy(strategy, sym, UTC, pUTC):
    global RsymsBuy
    global RsymsSell

    if today:
	cdata = TodayData[sym][UTC]
    else:
	cdata = SixtyDaysData[sym][UTC]
    c = float(cdata[0][0])
    h = float(cdata[0][1])
    low = float(cdata[0][2])
    o = float(cdata[0][3])
    prev_utc = GetPrevUTC(SixtyDaysData[sym], UTC)
    if prev_utc is None:
	return

    pclose = float(OneYearData[sym][pUTC][0])
    cvol=int(cdata[0][4])
    cpt = ((o-pclose)/pclose)*100
    if strategy == 'Buy' or strategy == 'Both':
	if o == low and pclose < o and VolCheck(VOL_Check, sym, pUTC, prev_utc, cvol) and CPTCheck(cpt) and ECheck('Buy', cdata[0], cdata[1]):
	    #log("Recommending Buy %s as o == l and pclose < o (%.2f, %.2f, %.2f, %.2f)" % (sym, o, low, pclose, o))
	    #print("%s: Recommended Buy Stocks = %s [o=%.2f,h=%.2f,l=%.2f,c=%.2f]" % (GetHumanDate(UTC), sym, o, h, low, c))
	    RsymsBuy.append(sym)

    if strategy == 'Sell' or strategy == 'Both':
	if o == h and pclose > o and VolCheck(VOL_Check, sym, pUTC, prev_utc, cvol) and CPTCheck(cpt) and ECheck('Sell', cdata[0], cdata[1]):
	    #log("Recommending Sell %s as o == h and pclose > o (%.2f, %.2f, %.2f, %.2f)" % (sym, o, h, pclose, o))
	    #print("%s: Recommended Sell Stocks = %s [o=%.2f,h=%.2f,l=%.2f,c=%.2f]" % (GetHumanDate(UTC), sym, o, h, low, c))
	    RsymsSell.append(sym)

def BackTest(call, sym, UTC, prev_utc, cps):
    global sl_count
    global tgt_count
    global sq_count
    global GROSS

    if E_Check == 0:
	pcandle = 1
    else:
	pcandle = 2
    if Leverage:
	if sym in MIS.keys():
	    cps *= int(MIS[sym])

    sq_off=1
    pft_list = []
    sl_list = []
    if today:
	cdata = TodayData[sym][UTC]
    else:
	cdata = SixtyDaysData[sym][UTC]
    c = float(cdata[pcandle][0])
    h = float(cdata[pcandle][1])
    low = float(cdata[pcandle][2])
    o = float(cdata[pcandle][3])
    pprice = (h+c)/2
    if call == 'Buy':
	#pprice = h
	tgt_price = pprice + (pprice * ProfitPct)
	sl_price = pprice - (pprice * SLPct)
    else:
	#pprice = low
	tgt_price = pprice - (pprice * ProfitPct)
	sl_price = pprice + (pprice * SLPct)
    l1 = 0
    h1 = 0
    #log("Sym=%s, ProfitPct=%.2f, Tgt Price = %.2f, SLPct=%.2f, SL Pric = %.2f" % (sym, ProfitPct, tgt_price, SLPct, sl_price))
    i=1
    for each_candle in cdata[pcandle+1:]:
	c1 = float(each_candle[0])
	h1 = float(each_candle[1])
	l1 = float(each_candle[2])
	o1 = float(each_candle[3])
	# c h l o format, retrive the low and high
	for idx in (3, 2, 1, 0):
	    if sq_off == 0:
		break
	    if ((call == 'Buy' and float(each_candle[idx]) <= sl_price) or (call == 'Sell' and float(each_candle[idx]) >= sl_price)):
		#if call == 'Buy':
		    #log("Buy: %s: %s => %d <= sl_price" % (sym, GetHumanDate(UTC), idx))
		#else:
		    #log("Sell: %s: %s => %d <= tgt_price" % (sym, GetHumanDate(UTC), idx))
		sl_count+=1
		if i == 1:
		    sl_price1 = float(each_candle[idx])
	    	else:
		    sl_price1 = sl_price
		loss = (cps*abs((sl_price1-pprice)/pprice))
		GROSS -= loss
		log("SL Hit: %s: %s => GROSS=%.2f, SLPct=%.2f%%, PurchasePrice=%.2f, SL=%.2f, ActualSLPct=%.2f%%, ActualLoss=%.2f, G-LOSS=%.2f" % (GetHumanDate(UTC), sym, GROSS, SLPct*100, pprice, sl_price, ((float(each_candle[idx])-pprice)/pprice)*100, loss, GROSS-loss))
		log("%s: %s => PossibleTgtHits = %s" % (sym, GetHumanDate(UTC), ','.join(pft_list)))
		sq_off=0
		break
	    if ((call == 'Buy' and float(each_candle[idx]) >= tgt_price) or (call == 'Sell' and float(each_candle[idx]) <= tgt_price)):
		#if call == 'Buy':
		    #log("Buy: %s: %s => %d >= tgt_price" % (sym, GetHumanDate(UTC), idx))
		#else:
		    #log("Sell: %s: %s => %d >= sl_price" % (sym, GetHumanDate(UTC), idx))
		tgt_count+=1
		log("TGT Hit: %s: %s => GROSS=%.2f, ProfitPct=%.2f%%, PurchasePrice=%.2f, TGT=%.2f, G+Earning=%.2f" % (GetHumanDate(UTC), sym, GROSS, ProfitPct*100, pprice, tgt_price, GROSS+(cps*ProfitPct)))
		log("%s: %s => PossibleSLHits = %s" % (sym, GetHumanDate(UTC), ','.join(sl_list)))
		GROSS += (cps*ProfitPct)
		sq_off=0
		break
	    if call == 'Buy':
		if float(each_candle[idx]) < pprice:
		    sl_list.append("%s(%.2f%%)" % (each_candle[idx],((float(each_candle[idx])-pprice)/pprice)*100))
		    #sl_list.append("%s" % each_candle[idx])
		    break
		if float(each_candle[idx]) > pprice:
		    pft_list.append("%s(%.2f%%)" % (each_candle[idx],((float(each_candle[idx])-pprice)/pprice)*100))
		    #pft_list.append("%s" % float(each_candle[idx]))
		    break
	    elif call == 'Sell':
		if float(each_candle[idx]) > pprice:
		    sl_list.append("%s(%.2f%%)" % (each_candle[idx],(((pprice-float(each_candle[idx]))/pprice))*100));
		    #sl_list.append("%s" % each_candle[idx])
		    break
		if float(each_candle[idx]) < pprice:
		    pft_list.append("%s(%.2f%%)" % (each_candle[idx],(((pprice-float(each_candle[idx]))/pprice))*100));
		    #pft_list.append("%s" % each_candle[idx])
		    break
	# 182th Candle is 3:20PM Candle
	if i == 182:
	    #log("%s: CandleTime is %s" % (sym, GetHumanDate(str(int(UTC)+((pcandle-1+i)*Interval)))))
	    break
	i+=1
    if sq_off == 1:
	sq_off_change = (cps*(((l1+c1)/2)-pprice)/pprice)
	log("SquareOff Hit: %d: %s: %s => Purchase Price=%.2f, Low=%.2f, High=%.2f, Close=%.2f, CutOffPrice=%.2f, GROSS=%.2f, CPCT=%.2f, G+Earning=%.2f" % (i, GetHumanDate(UTC), sym, pprice, l1, h1, c1, (l1+c1)/2, GROSS, sq_off_change, GROSS + sq_off_change))
	sq_count+=1
	GROSS += sq_off_change
	log("%s: %s => PossibleTgtHits = %s" % (sym, GetHumanDate(UTC), ','.join(pft_list)))
	log("%s: %s => PossibleSLHits = %s" % (sym, GetHumanDate(UTC), ','.join(sl_list)))

def MarketHours():
    tdt = datetime.datetime.today();
    th = int(tdt.strftime("%H"))
    tm = int(tdt.strftime("%M"))
    mins = th*60+tm
    if (mins > 555 and mins < 931):
        return True
    return False

def GetURLData(p, sym):
    if p == '1Y':
	url = 'https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=%s' % (sym.replace('&','%26'), p)
    else:
	url = 'https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=%s&i=%s' % (sym.replace('&','%26'), p, Interval)
    response = urllib2.urlopen(url)
    content = csv.reader(response.read().splitlines()[7:])
    return content

def Get_1Y_Data(sym):
    data = {}
    data_cache = {}
    sym_file = "DATA/%s.1Y.json" % sym
    if (today == 0 or LOCAL_CACHE == True) and os.path.exists(sym_file):
	with open(sym_file, 'r') as sym_file_handle:
	    data_cache = json.load(sym_file_handle)
    if LOCAL_CACHE ==  True and len(data_cache) > 0:
	return data_cache
    content = GetURLData('1Y', sym)
    for d in content:
	if d[0][0] == 'a':
	    lutc = d[0].replace('a','');
	    data[lutc] = d[1:]
	else:
	    llutc = str(int(lutc)+(int(d[0])*86400))
	    data[llutc] = d[1:]
    data_new = {key: value for (key, value) in (data_cache.items() + data.items())}
    sym_file = "NEW/%s.1Y.json" % sym
    if os.path.exists(sym_file):
	os.rename(sym_file, "%s.moved" % sym_file)
    with open(sym_file, "w") as sym_file_handle:
	json.dump(data_new, sym_file_handle)
    if data is None:
	exit(0)
    return data

def GetScripCandleData(days, sym):
    data = {}
    data_cache = {}
    sym_cache_file = "DATA/%s.%sCandles.json" % (sym, days)
    if (today == 0 or LOCAL_CACHE == True) and os.path.exists(sym_cache_file):
	with open(sym_cache_file, 'r') as sym_file_handle:
	    data_cache = json.load(sym_file_handle)
	sym_file_handle.close()
    if LOCAL_CACHE ==  True and len(data_cache) > 0:
	return data_cache
    content = GetURLData(days, sym)
    lutc = 0
    for d in content:
	if d[0][0] == 'a':
	    utc = d[0].replace('a', '')
	    rutc = int(utc)
	else:
	    utc = rutc + (int(d[0]) * Interval)
	if (int(utc) - int(lutc)) < 86400:
	    #print "Appending %s to %s" % (GetHumanDate(utc), GetHumanDate(lutc))
	    data[str(lutc)].append(d[1:])
	else:
	    #print "Making new entry for %s" % GetHumanDate(utc)
	    data[str(utc)] = [d[1:]]
	    lutc = utc
    data_new = {key: value for (key, value) in (data_cache.items() + data.items())}
    sym_file = "NEW/%s.%sCandles.json" % (sym, days)
    if os.path.exists(sym_file):
	os.rename(sym_file, "%s.moved" % sym_file)
    with open(sym_file, "w") as sym_file_handle:
	json.dump(data_new, sym_file_handle)
    sym_file_handle.close()
    #print sorted(data.keys())
    return data

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

def Initialize():
    global sl_count
    global tgt_count
    global sq_count
    global y
    global m
    global d
    global CAPITAL
    global GROSS

    sl_count = 0
    tgt_count = 0
    sq_count = 0
    y = 2018
    m = 1
    d = 1
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

    #plot_returns_handle = open(plot_returns, 'w')
    #plot_hits_handle = open(plot_hits, 'w')
    #print >>plot_returns_handle, "Date,Gross"
    #print >>plot_hits_handle, "Date,Miss,Hit,SQO"

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

	pnifty = GetPrevUTCNifty(utcl)
	if pnifty is None:
	    d+=1
	    #log("Could not find Nifty value for %s (3:30)" % GetHumanDate(utcl))
	    continue
	pnifty = NiftyIndex1YCandle[pnifty][0]
	if today == 1:
	    cnifty = NiftyIndexTodayCandle[utc][0][0]
	elif utc in NiftyIndex60DCandle.keys():
	    cnifty = NiftyIndex60DCandle[utc][0][0]
	else:
	    d+=1
	    #log("Could not find Nifty value for %s (9:16)" % GetHumanDate(utc))
	    continue
	#Ncpt = ((float(NiftyIndex60DCandle[utc][0][0])-float(NiftyIndex1YCandle[prev_utc][0]))/float(NiftyIndex1YCandle[prev_utc][0]))*100
	Ncpt = ((float(cnifty)-float(pnifty))/float(pnifty))*100
	#log("[%s]: Ncpt = %.2f" % (GetHumanDate(utc), Ncpt))
	if Ncpt <= -2:
	    d+=1
	    log("Skipping trade on %s" % (GetHumanDate(utc)))
	    continue
	if s == 'Nifty':
	    strategy = "Both"
	    if Ncpt <= -1:
		strategy = "Sell"
	else:
	    strategy = s

	RsymsBuy = []
	RsymsSell = []

	# Shortlist complete list of stocks in one iteration
	for sym in Nsyms:
	    prev_utc = GetPrevUTC(OneYearData[sym], utcl)
	    if prev_utc is None:
		continue
	    if today:
		utcs = TodayData[sym].keys()
	    else:
		utcs = SixtyDaysData[sym].keys()

	    if utc in utcs:
		if prev_utc is not None:
		    #log("Iteration for %s, %s,%s" % (sym, GetHumanDate(prev_utc), GetHumanDate(utc)))
		    IntradayStrategy(strategy, sym, utc, prev_utc)
		#else:
		    #log("Data is not available for %s(%s)" % (sym, GetHumanDate(prev_utc)))
	    #else:
		#log("Data is not available for %s(%s)" % (sym, GetHumanDate(utc)))

	if BackTesting is True and (len(RsymsBuy) > 0 or len(RsymsSell) > 0):
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
		print 'Buy Stocks:', ','.join(RsymsBuy)
		for sym in RsymsBuy:
		    #log("%s[5,10,20,30] = [%s,%s,%s,%s]" % (sym, SMA_list[0], SMA_list[1], SMA_list[2], SMA_list[3]))
		    BackTest('Buy', sym, utc, prev_utc, CPS)

	    if (strategy == "Sell" or strategy == "Both") and len(RsymsSell) > 0:
		print 'Sell Stocks:', ','.join(RsymsSell)
		for sym in RsymsSell:
		    #log("%s[5,10,20,30] = [%s,%s,%s,%s]" % (sym, SMA_list[0], SMA_list[1], SMA_list[2], SMA_list[3]))
		    BackTest('Sell', sym, utc, prev_utc, CPS)

	    if total_count > 0:
		cdate = GetHumanDate(utc)
		#print >>plot_returns_handle, "%s,%s" % (cdate,GROSS)
		#print >>plot_hits_handle, "%s,%d,%d,%d" % (cdate,sl_count,tgt_count,sq_count)
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
	if float((GROSS-CAPITAL)/CAPITAL)*100 > 0 and t_count > 0:
	    print("Nifty%d[%s]: Capital=%d, Gross=%d, Pct=%.2f%% (ProfitPct=%s,SLPct=%s,VolumeCondition=%s,CptCheck=%d,TotalStocks=%d,Tgt-Hit=%d,SL-Hit=%d,SQ-Hit=%d,TradedDays=%d)" % (len(Nsyms), s, CAPITAL, GROSS, float((GROSS-CAPITAL)/CAPITAL)*100, ProfitPct, SLPct, VOLS_check_list[VOL_Check], CPT_Check, t_count, t_tgt_count, t_sl_count, t_sq_count, tdays))
	    print("CSV,%s,%.2f,%s,%s,%s,%s,%s,%d,%d,%d,%d" % (s, float((GROSS-CAPITAL)/CAPITAL)*100, ProfitPct, SLPct, VOLS_check_list[VOL_Check], CPT_check_list[CPT_Check], ECheck_list[E_Check], t_tgt_count, t_sl_count, t_sq_count, tdays))
	#plot_returns_handle.close();
	#plot_hits_handle.close();

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
	    elif sys.argv[i] == "--no-cache":
		LOCAL_CACHE=False
		i+=1
	    elif sys.argv[i] == '--today':
		dt = datetime.datetime.today();
		y = int(dt.strftime("%Y"))
		m = int(dt.strftime("%m"))
		d = int(dt.strftime("%d"))
		if not LOCAL_CACHE and MarketHours() == True:
		    LOCAL_CACHE=False
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
	    elif sys.argv[i] == '--leverage':
		Leverage=True
	    elif sys.argv[i] == '--no-back-testing':
		BackTesting=False
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
	SixtyDaysData[sym] = GetScripCandleData('60d', sym)
	if today == True:
	    TodayData[sym] = GetScripCandleData('1d', sym)

    # Collect Nifty Candle data for the same period and interval as symbols.
    NiftyIndex1YCandle = Get_1Y_Data('NIFTY')
    NiftyIndex60DCandle = GetScripCandleData('60d', 'NIFTY')
    if today:
	NiftyIndexTodayCandle = GetScripCandleData('1d', 'NIFTY')

    if variance == "Always-Buy":
	MainLoop("Buy");
    elif variance == "Both-Buy-And-Sell":
	MainLoop("Both");
    else:
	plot_returns1=deepcopy(plot_returns)
	plot_hits1=deepcopy(plot_hits)
	if variance == "Go_with_Nifty":
	    MainLoop('Nifty');
	elif variance == "ALL":
		for vol in (0, 1, 2, 3, 4, 5, 6, 7, 8):
		    VOL_Check=vol
		    for cpt in (0, 1, 2, 3, 4, 5, 6):
			CPT_Check=cpt
			for echk in (0, 1, 2, 3):
			    E_Check=echk
			    for pft_sl in pcts.split(','):
				pft_sl_list = pft_sl.split(':')
				ProfitPct = float(pft_sl_list[0])/100
				SLPct = float(pft_sl_list[1])/100
				for s in ('Buy', 'Both', 'Nifty'):
				    plot_returns=plot_returns1.replace('.csv','_%s_%s_VOL_%s_CPT_%s_ECheck_%s.csv' % (ProfitPct, SLPct, vol, CPT_Check, E_Check))
				    plot_hits=plot_hits1.replace('.csv','_%s_%s_VOL_%s_CPT_%s_ECheck_%s.csv' % (ProfitPct, SLPct, vol, CPT_Check, E_Check))
				    MainLoop(s)
				    Initialize()
