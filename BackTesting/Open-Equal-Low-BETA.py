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
today=0
variance = "Both-Buy-And-Sell"
plot_returns='out.plot_earnings'
plot_hits='out.plot_hits'
RsymsSell = []
RsymsSellDetail = []
RsymsBuy = []
RsymsBuyDetail = []
BackTesting = True
Interval = 960
TodayData = {}
OneYearData = {}
SixtyDaysData = {}
VOL_Check=8
sl_count = 0
tgt_count = 0
sq_count = 0
ProfitPct = 1.2/100
SLPct = 1.2/100
pcts = []

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

VOLS_check_list = ['CandleVolume > 1% of YesterdaysVolume', 'CandleVolume > 1.2% of YesterdaysVolume', 'CandleVolume > 1.5% of YesterdaysVolume', 'CandleVolume > 2% of YesterdaysVolume', 'CandleVolume > 2.2% of YesterdaysVolume', 'CandleVolume > 2.5% of YesterdaysVolume', 'CandleVolume > 3% of YesterdaysVolume', 'CandleVolume > 3.2% of YesterdaysVolume', 'CandleVolume > 3.5% of YesterdaysVolume', 'CandleVolume > 4% of YesterdaysVolume']

def VolCheck(c, sym, pUTC, prev_utc, c_candle_vol):
    # prev_utc will refer to previous day 3:30 UTC
    # pUTC will refer to previous day 9:16
    #print GetHumanDate(prev_utc), GetHumanDate(pUTC)
    pvol = int(OneYearData[sym][pUTC][4])
    p_candle_vol = int(SixtyDaysData[sym][prev_utc][-1][4])
    if c == 1 and (c_candle_vol/pvol)*100 > 1:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 2 and (c_candle_vol/pvol)*100 > 1.2:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 3 and (c_candle_vol/pvol)*100 > 1.5:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 5 and (c_candle_vol/pvol)*100 > 2:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 4 and (c_candle_vol/pvol)*100 > 2.2:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 5 and (c_candle_vol/pvol)*100 > 2.5:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 7 and (c_candle_vol/pvol)*100 > 3:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 6 and (c_candle_vol/pvol)*100 > 3.2:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 8 and (c_candle_vol/pvol)*100 > 3.5:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    if c == 9 and (c_candle_vol/pvol)*100 > 4:
	log("%s: PreviousDayVolume=%d, CurrentCandleVolume=%d" % (sym, pvol, c_candle_vol))
	return True
    return False

def IntradayStrategy(strategy, sym, UTC, pUTC):
    global RsymsBuy
    global RsymsSell
    global RsymsBuyDetail
    global RsymsSellDetail

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

    if strategy == 'Buy' or strategy == 'Both':
	if o == low and float(OneYearData[sym][pUTC][0]) < o and VolCheck(VOL_Check, sym, pUTC, prev_utc, int(cdata[0][4])):
	    log("Recommending Buy %s as o == l and pclose < o (%.2f, %.2f, %.2f, %.2f)" % (sym, o, low, float(OneYearData[sym][pUTC][0]), o))
	    log("Buy[%s]:YesterdaysVolume=%s,CurCandleVol=%s(%.2f%%)" % (sym,OneYearData[sym][pUTC][4],cdata[0][4],(int(cdata[0][4])/int(OneYearData[sym][pUTC][4]))*100))
	    RsymsBuy.append(sym)
	    RsymsBuyDetail.append(["%s,Buy=%d,Tgt=%d,SL=%d" % (sym,c,c+(c*ProfitPct),c-(c*SLPct))])

    if strategy == 'Sell' or strategy == 'Both':
	if o == h and float(OneYearData[sym][pUTC][0]) > o and VolCheck(VOL_Check, sym, pUTC, prev_utc, int(cdata[0][4])):
	    log("Recommending Sell %s as o == h and pclose > o (%.2f, %.2f, %.2f, %.2f)" % (sym, o, h, float(OneYearData[sym][pUTC][0]), o))
	    log("Sell[%s]:YesterdaysVolume=%s,CurCandleVol=%s(%.2f%%)" % (sym,OneYearData[sym][pUTC][4],cdata[0][4],(int(cdata[0][4])/int(OneYearData[sym][pUTC][4]))*100))
	    RsymsSell.append(sym)
	    RsymsSellDetail.append(["%s,Buy=%d,Tgt=%d,SL=%d" % (sym,c,c-(c*ProfitPct),c+(c*SLPct))])

def BackTestBuy(sym, UTC, cps):
    global sl_count
    global tgt_count
    global sq_count
    global GROSS

    cps *= int(MIS[sym])
    no_sq_off=1
    pft_list = []
    sl_list = []
    if today:
	cdata = TodayData[sym][UTC]
    else:
	cdata = SixtyDaysData[sym][UTC]
    lw = 0
    c = float(cdata[0][0])
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
	    log("SL Hit: %s: %s => GROSS=%.2f, SLPct=%.2f%%, PurchasePrice=%.2f, SL=%.2f, ActualSLPct=%.2f%%, ActualLoss=%.2f, G-LOSS=%.2f" % (GetHumanDate(UTC), sym, GROSS, SLPct*100, pprice, sl_price, (l1-pprice)/pprice*100, cps*((l1-pprice)/pprice), GROSS-((l1-pprice)/pprice)))
	    GROSS -= (cps*abs((l1-pprice)/pprice))
	    no_sq_off=2
	if no_sq_off == 1 and h1 >= tgt_price:
	    tgt_count+=1
	    log("TGT Hit: %s: %s => GROSS=%.2f, ProfitPct=%.2f%%, PurchasePrice=%.2f, TGT=%.2f, G+Earning=%.2f" % (GetHumanDate(UTC), sym, GROSS, ProfitPct*100, pprice, tgt_price, GROSS+(cps*ProfitPct)))
	    GROSS += (cps*ProfitPct)
	    no_sq_off=3
	if l1 < pprice:
	    sl_list.append("%s(%.2f%%)" % (l1,(((pprice-l1)/pprice))*100));
	if h1 > pprice:
	    pft_list.append("%s(%.2f%%)" % (h1,(((h1-pprice)/pprice))*100));
    if no_sq_off==2:
	log("%s: %s => PossibleSLHits = %s" % (sym, GetHumanDate(UTC), ','.join(sl_list)))
    elif no_sq_off==3:
	log("%s: %s => PossibleTgtHits = %s" % (sym, GetHumanDate(UTC), ','.join(pft_list)))
    else:
	log("SquareOff Hit: %s: %s => Purchase Price=%.2f, Low=%.2f, High=%.2f, Close=%.2f, CutOffPrice=%.2f], GROSS=%.2f, CPCT=%.2f, G+Earning=%.2f,PossibleTgtHits[%s],PossibleSLHits[%s]" % (GetHumanDate(UTC), sym, pprice, l1, h1, c1, l1, GROSS, (l1-pprice)/pprice, GROSS + (cps*((l1-pprice)/pprice)), ','.join(pft_list), ','.join(sl_list)))
	sq_count+=1
	GROSS += (cps*((l1-pprice)/pprice))

def BackTestSell(sym, UTC, cps):
    global sl_count
    global tgt_count
    global sq_count
    global GROSS

    cps *= int(MIS[sym])
    no_sq_off=1
    pft_list = []
    sl_list = []
    if today:
	cdata = TodayData[sym][UTC]
    else:
	cdata = SixtyDaysData[sym][UTC]
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
	    log("SL Hit: %s: %s => GROSS=%.2f, SLPct=%.2f%%, PurchasePrice=%.2f, SL=%.2f, ActualSLPct=%.2f%%, ActualLoss=%.2f, G-LOSS=%.2f" % (GetHumanDate(UTC), sym, GROSS, SLPct*100, pprice, sl_price, (h1-pprice)/pprice*100, cps*((h1-pprice)/pprice), GROSS-((h1-pprice)/pprice)))
	    sl_count+=1
	    GROSS -= (cps*abs((h1-pprice)/pprice))
	    no_sq_off=2
	if no_sq_off==1 and l1 <= tgt_price:
	    log("SL Hit: %s: %s => GROSS=%.2f, SLPct=%.2f%%, PurchasePrice=%.2f, SL=%.2f, ActualSLPct=%.2f%%, ActualLoss=%.2f, G-LOSS=%.2f" % (GetHumanDate(UTC), sym, GROSS, SLPct*100, pprice, sl_price, (l1-pprice)/pprice*100, cps*((l1-pprice)/pprice), GROSS-((l1-pprice)/pprice)))
	    tgt_count+=1
	    GROSS += (cps*ProfitPct)
	    no_sq_off=3
	if h1 >= pprice:
	    sl_list.append("%s(%.2f%%)" % (h1,((h1/pprice)-1)*100));
	if l1 <= pprice:
	    pft_list.append("%s(%.2f%%)" % (l1,((l1/pprice)-1)*100));
    if no_sq_off==2:
	log("%s: %s => PossibleSLHits = %s" % (sym, GetHumanDate(UTC), ','.join(sl_list)))
    elif no_sq_off==3:
	log("%s: %s => PossibleTgtHits = %s" % (sym, GetHumanDate(UTC), ','.join(pft_list)))
    else:
	log("SquareOff Hit: %s: %s => Purchase Price=%.2f, Low=%.2f, High=%.2f, Close=%.2f, CutOffPrice=%.2f], GROSS=%.2f, CPCT=%.2f, G+Earning=%.2f,PossibleTgtHits[%s],PossibleSLHits[%s]" % (GetHumanDate(UTC), sym, pprice, l1, h1, c1, l1, GROSS, (l1-pprice)/pprice, GROSS + (cps*((l1-pprice)/pprice)), ','.join(pft_list), ','.join(sl_list)))
	sq_count+=1
	GROSS += (cps*((pprice-l1)/pprice))

def MarketHours():
    tdt = datetime.datetime.today();
    th = int(tdt.strftime("%H"))
    tm = int(tdt.strftime("%M"))
    mins = th*60+tm
    if (mins > 555 and mins < 931):
	return True
    return False

def Get_1Y_Data(sym):
    data = {}
    sym_file = "UPDATED-DATA/%s.1Y.csv" % sym
    if MarketHours() == False and os.path.exists(sym_file):
	with open(sym_file, 'r') as sym_file_handle:
	    data = json.load(sym_file_handle)
    else:
	1111
	response = urllib2.urlopen('https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=1Y' % sym.replace('&','%26'))
	content = csv.reader(response.read().splitlines()[7:])
	for d in content:
	    if d[0][0] == 'a':
		lutc = d[0].replace('a','');
		data[lutc] = d[1:]
	    else:
		llutc = str(int(lutc)+(int(d[0])*86400))
		data[llutc] = d[1:]
	sym_file = "%s.1Y.csv" % sym
	with open(sym_file, "w") as sym_file_handle:
	    json.dump(data, sym_file_handle)
    return data

def GetScripCandleData(days, sym):
    data = {}
    sym_file = "UPDATED-DATA/%s.Candles.csv" % sym
    if MarketHours() == False and os.path.exists(sym_file):
	with open(sym_file, 'r') as sym_file_handle:
	    data = json.load(sym_file_handle)
    else:
	url = 'https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=%sd&i=%s' % (sym.replace('&','%26'), days, Interval)
	1111
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
	sym_file = "%s.Candles.csv" % sym
	with open(sym_file, "w") as sym_file_handle:
	    json.dump(data, sym_file_handle)
    #print sorted(data.keys())
    return data

NiftyIndex60DCandle = {}
def GetNiftyIndex60DCandleData():
    global NiftyIndex60DCandle
    sym_file = "UPDATED-DATA/NiftyCandles.csv"
    if MarketHours() == False and os.path.exists(sym_file):
	with open(sym_file, 'r') as sym_file_handle:
	    NiftyIndex60DCandle = json.load(sym_file_handle)
    else:
	1111
	response = urllib2.urlopen('https://finance.google.com/finance/getprices?x=NSE&q=NIFTY&f=d,c,h,l,o,v&p=60d&i=%s' % Interval)
	content = csv.reader(response.read().splitlines()[7:])
	lutc = 0
	for d in content:
	    if d[0][0] == 'a':
		utc = d[0].replace('a', '')
	    else:
		utc = lutc + (int(d[0]) * Interval)
	    if (int(utc) - int(lutc)) < 86400:
		#print "Appending to %s" % GetHumanDate(lutc)
		NiftyIndex60DCandle[str(lutc)].append(d[1:])
	    else:
		lutc = int(utc)
		#print "Making new entry for %s" % GetHumanDate(lutc)
		NiftyIndex60DCandle[str(lutc)] = [d[1:]]
	sym_file = "NiftyCandles.csv"
	with open(sym_file, "w") as sym_file_handle:
	    json.dump(NiftyIndex60DCandle, sym_file_handle)

NiftyIndex1YCandle = {}
def GetNiftyIndex1YCandleData():
    global NiftyIndex1YCandle
    sym_file = "UPDATED-DATA/Nifty1Y.csv"
    if MarketHours() == False and os.path.exists(sym_file):
	with open(sym_file, 'r') as sym_file_handle:
	    NiftyIndex1YCandle = json.load(sym_file_handle)
    else:
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
    sym_file = "Nifty1Y.csv"
    with open(sym_file, "w") as sym_file_handle:
	json.dump(NiftyIndex1YCandle, sym_file_handle)

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
    global RsymsBuyDetail
    global RsymsSellDetail
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

	prev_utcl = GetPrevUTCNifty(str(utcl))
	if prev_utcl is None:
	    #print("ERROR: Could not find Previous day for %s" % GetHumanDate(utc))
	    d+=1
	    continue
	if utc not in NiftyIndex60DCandle.keys():
	    d+=1
	    continue
	Ncpt = ((float(NiftyIndex60DCandle[utc][0][0])-float(NiftyIndex1YCandle[prev_utcl][0]))/float(NiftyIndex1YCandle[prev_utcl][0]))*100
	log("[%s]: Ncpt = %.2f" % (GetHumanDate(utc), Ncpt))
	if Ncpt <= -2:
	    d+=1
	    continue
	if s == 'Nifty':
	    strategy = "Buy"
	    if Ncpt <= -1:
		strategy = "Sell"
	else:
	    strategy = s

	RsymsBuy = []
	RsymsSell = []
	RsymsBuyDetail = []
	RsymsSellDetail = []

	# Shortlist complete list of stocks in one iteration
	for sym in Nsyms:
	    prev_utc = GetPrevUTC(OneYearData[sym], utcl)
	    if prev_utc is None:
		continue
	    if today:
		utcs = TodayData[sym].keys()
	    else:
		utcs = SixtyDaysData[sym].keys()

	    if utc in utcs and prev_utc is not None:
		log("Iteration for %s, %s,%s" % (sym, GetHumanDate(prev_utc), GetHumanDate(utc)))
		IntradayStrategy(strategy, sym, utc, prev_utc)
	    #else:
		#log("Symbol %s is not shortlisted for %s-%s" % (sym, GetHumanDate(utc), GetHumanDate(prev_utc)))

	if len(RsymsBuy) > 0:
	    print("Recommended Buy Stocks:")
	    for sym_detail in RsymsBuyDetail:
		print sym_detail

	if len(RsymsSell) > 0:
	    print("Recommended Sell Stocks:")
	    for sym_detail in RsymsSellDetail:
		print sym_detail
	    #print("Recommended Sell Stocks = %s" % ','.join(RsymsSell))

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
		for sym in RsymsBuy:
		    SMA_list = CalculateSMA(sym, prev_utc)
		    log("%s[5,10,20,30] = [%s,%s,%s,%s]" % (sym, SMA_list[0], SMA_list[1], SMA_list[2], SMA_list[3]))
		    BackTestBuy(sym, utc, CPS)

	    if (strategy == "Sell" or strategy == "Both") and len(RsymsSell) > 0:
		for sym in RsymsSell:
		    SMA_list = CalculateSMA(sym, prev_utc)
		    log("%s[5,10,20,30] = [%s,%s,%s,%s]" % (sym, SMA_list[0], SMA_list[1], SMA_list[2], SMA_list[3]))
		    BackTestSell(sym, utc, CPS)

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
	if float((GROSS-CAPITAL)/CAPITAL)*100 > 3 and t_tgt_count >= 0:
	    print("Nifty%d[%s]: Capital=%d, Gross=%d, Pct=%.2f%% (ProfitPct=%s,SLPct=%s,VolumeCondition=%s, TotalStocks=%d, Tgt-Hit=%d, SL-Hit=%d, SQ-Hit=%d)" % (len(Nsyms), s, CAPITAL, GROSS, float((GROSS-CAPITAL)/CAPITAL)*100, ProfitPct, SLPct, VOLS_check_list[VOL_Check], t_count, t_tgt_count, t_sl_count, t_sq_count))
	    print("CSV,%s,%.2f,%s,%s,%s,%d,%d,%d,%d" % (s, float((GROSS-CAPITAL)/CAPITAL)*100, ProfitPct, SLPct, VOLS_check_list[VOL_Check], t_tgt_count, t_sl_count, t_sq_count, tdays))
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
	TodayData[sym] = GetScripCandleData(1, sym)
	SixtyDaysData[sym] = GetScripCandleData(60, sym)

    # Collect Nifty Candle data for the same period and interval as symbols.
    GetNiftyIndex60DCandleData()
    GetNiftyIndex1YCandleData()

    plot_returns1=deepcopy(plot_returns)
    plot_hits1=deepcopy(plot_hits)
    VOL_Check=8
    if len(pcts) > 0:
	for pft_sl in pcts.split(','):
	    pft_sl_list = pft_sl.split(':')
	    ProfitPct = float(pft_sl_list[0])/100
	    SLPct = float(pft_sl_list[1])/100
	    for s in (['Both']):
		plot_returns=plot_returns1.replace('.csv','_%s_%s_VOL_%s.csv' % (ProfitPct, SLPct, VOL_Check))
		plot_hits=plot_hits1.replace('.csv','_%s_%s_VOL_%s.csv' % (ProfitPct, SLPct, VOL_Check))
		MainLoop(s)
		Initialize()
    else:
	MainLoop('Both')
