#!/usr/bin/env python2.7

from __future__ import division

import datetime, urllib2, csv, multiprocessing

# Important Parameters
CAPITAL=50000
cap=CAPITAL*(80/100)
Interval = 60
VolInc = 1.5
PriceInc = 0.3

# Candle index
close = 0
high = 1
low = 2
open = 3
vol = 4

# Variables
utc = 0
utcl = 0
DailyData = {}
TodayCandleData = {}

#Nsyms=['BHARTIARTL']
#Nsyms=['EICHERMOT', 'UNIONBANK', 'DRREDDY', 'MCLEODRUSS']

# Symbols we scan
Nsyms=['YESBANK', 'TATASTEEL', 'STAR', 'SBIN', 'RELIANCE', 'POWERGRID', 'PETRONET', 'ONGC', 'OIL', 'MARUTI', 'M&M', 'LT', 'KTKBANK', 'KOTAKBANK', 'JSWSTEEL', 'ITC', 'IOC', 'INDUSINDBK', 'IGL', 'ICICIBANK', 'HINDUNILVR', 'HEROMOTOCO', 'HDFCBANK', 'HDFC', 'GAIL', 'FEDERALBNK', 'DCBBANK', 'DABUR', 'COLPAL', 'COALINDIA', 'CIPLA', 'CEATLTD', 'CASTROLIND', 'CANBK', 'BPCL', 'BOSCHLTD', 'BHARTIARTL', 'BHARATFORG', 'BATAINDIA', 'BANKBARODA', 'BAJAJ-AUTO', 'AXISBANK', 'ASIANPAINT', 'ASHOKLEY', 'ARVIND', 'APOLLOTYRE', 'APOLLOHOSP', 'AMBUJACEM', 'AMARAJABAT', 'ACC', 'UNIONBANK', 'KSCL', 'ICIL', 'ZEEL', 'VEDL', 'UPL', 'ULTRACEMCO', 'UBL', 'TVSMOTOR', 'TITAN', 'TATAMTRDVR', 'TATAMOTORS', 'TATACHEM', 'SRTRANSFIN', 'SRF', 'RECLTD', 'PTC', 'PIDILITIND', 'NTPC', 'NMDC', 'NCC', 'MRF', 'MOTHERSUMI', 'MCLEODRUSS', 'MCDOWELL-N', 'MARICO', 'M&MFIN', 'LUPIN', 'LICHSGFIN', 'L&TFH', 'JUBLFOOD', 'JISLJALEQS', 'INDIACEM', 'HINDZINC', 'HINDPETRO', 'HINDALCO', 'HEXAWARE', 'GRASIM', 'GLENMARK', 'EXIDEIND', 'ENGINERSIN', 'EICHERMOT', 'BRITANNIA', 'BHEL', 'GRANULES', 'GOLDBEES', 'BANKBEES', 'WIPRO', 'VOLTAS', 'TECHM', 'TCS', 'TATAPOWER', 'TATAGLOBAL', 'TATAELXSI', 'TATACOMM', 'SIEMENS', 'RELINFRA', 'RELCAPITAL', 'PFC', 'PAGEIND', 'NIITTECH', 'MINDTREE', 'IRB', 'INFY', 'INFRATEL', 'IBULHSGFIN', 'HCLTECH', 'HAVELLS', 'DISHTV', 'CONCOR', 'CESC', 'CADILAHC', 'BIOCON', 'BEML', 'BEL', 'TORNTPOWER', 'OFSS', 'KPIT', 'JINDALSTEL', 'CGPOWER', 'CENTURYTEX', 'BHARATFIN', 'AJANTPHARM', 'WOCKPHARMA', 'TORNTPHARM', 'SUNPHARMA', 'ORIENTBANK', 'IDEA', 'GODREJIND', 'DRREDDY', 'DLF', 'DIVISLAB', 'DHFL', 'BANKINDIA', 'BAJFINANCE', 'AUROPHARMA']

# Zerodha Margin information
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

# Get data from finance.google.com
def GetURLData(p, sym, candle):
    if candle == False:
	url = 'https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=%sd' % (sym.replace('&','%26'), p)
    else:
	url = 'https://finance.google.com/finance/getprices?x=NSE&q=%s&f=d,c,h,l,o,v&p=%sd&i=%s' % (sym.replace('&','%26'), p, Interval)
    response = urllib2.urlopen(url)
    content = csv.reader(response.read().splitlines()[7:])
    return content

# Get 1 year data for a given symbol
def GetDailyData(sym):
    data = {}
    content = GetURLData(9, sym, False)
    for d in content:
	if d[0][0] == 'a':
	    lutc = d[0].replace('a','');
	    data[lutc] = d[1:]
	else:
	    llutc = str(int(lutc)+(int(d[0])*86400))
	    data[llutc] = d[1:]
    return data

# Get candle data for a given symbol for given days
def GetScripCandleData(days, sym):
    data = {}
    content = GetURLData(days, sym, True)
    lutc = 0
    for d in content:
	if d[0][0] == 'a':
	    utc = d[0].replace('a', '')
	    rutc = int(utc)
	else:
	    utc = rutc + (int(d[0]) * Interval)
	hr = int(datetime.datetime.fromtimestamp(int(utc)).strftime("%H"))
	min = int(datetime.datetime.fromtimestamp(int(utc)).strftime("%M"))
	if hr == 9 and min == 16:
	    data[str(utc)] = [d[1:]]
	    lutc = utc
	elif (hr == 9 and min > 16) or (hr > 9 and hr < 15) or (hr == 15 and min <= 30):
	    if lutc == 0:
		return {}
	    data[str(lutc)].append(d[1:])
    return data

# Return valid previous time/day for a given time/day
def GetPrevUTC(data, pUTC):
    keys = data.keys()
    i=1
    while i < 6:
	pUTC = str(int(pUTC) - (i*86400))
	if pUTC in keys:
	    return pUTC
	i+=1
    return None

# Return Human readable data for a givne UTC (in seconds)
def GetHumanDate(utc):
    return datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d %H:%M:%S')
    #return datetime.datetime.fromtimestamp(int(utc)).strftime('%Y-%m-%d')

# Get previous day close price, and previous day traded vol for a given symbol
def GetPastData(sym, PastData):
    DailyData[sym] = GetDailyData(sym)
    prev_utcl = GetPrevUTC(DailyData[sym], utcl)
    if prev_utcl is None:
	return
    pclose = float(DailyData[sym][prev_utcl][0])
    pvol = int(DailyData[sym][prev_utcl][4])
    if pclose > 0 and pvol > 0:
	ValHash = {}
	ValHash['CLOSE'] = float(pclose)
	ValHash['VOL'] = int(pvol)
	PastData[sym] = ValHash

# This is the core function
# Shortlist each symbol based on the startegy
def IntradayStrategy(sym, BuySyms, SellSyms):
    # Collect today's Candle data for each symbol
    TodayCandleData[sym] = GetScripCandleData(1, sym)

    if utc not in TodayCandleData[sym].keys():
	return

    cdata = TodayCandleData[sym][utc]

    c1 = float(cdata[0][close])
    h1 = float(cdata[0][high])
    l1 = float(cdata[0][low])
    o1 = float(cdata[0][open])

    c_candle_vol=int(cdata[0][vol])
    pvol = PastData[sym]['VOL']
    pclose = PastData[sym]['CLOSE']
    cpt = abs((o1-pclose)/pclose)*100
    c2 = float(cdata[1][close])

    if o1 == l1 and pclose < o1 and (c_candle_vol/pvol)*100 > VolInc and cpt > PriceInc and (c2+(c1*(0.1/100))) > c1:
	    BuySyms[sym] = c2
    elif o1 == h1 and pclose > o1 and (c_candle_vol/pvol)*100 > VolInc and cpt > PriceInc and (c1+(c1*(0.1/100))) > c2:
	    SellSyms[sym] = c2

if __name__ == '__main__':
    dt = datetime.datetime.today();
    #dt = datetime.datetime.today() - datetime.timedelta(1);
    y = int(dt.strftime("%Y"))
    m = int(dt.strftime("%m"))
    d = int(dt.strftime("%d"))

    dt = datetime.datetime(y, m, d, 9, 16, 0)
    utc = dt.strftime("%s")
    dtl = datetime.datetime(y, m, d, 15, 30, 0)
    utcl = dtl.strftime("%s")

    # Collect Nifty Candle data for 1 year and today
    NiftyIndexDailyData = GetDailyData('NIFTY')
    NiftyIndex60DCandle = GetScripCandleData(1, 'NIFTY')

    pnifty = GetPrevUTC(NiftyIndexDailyData, utcl)
    if pnifty is None:
	print "Could not find previous Nifty"
	exit(0)
    pnifty = NiftyIndexDailyData[pnifty][0]
    if utc in NiftyIndex60DCandle.keys():
	cnifty = NiftyIndex60DCandle[utc][0][0]
    else:
	print 'Could not find current Nifty'
	exit(0)
    Ncpt = ((float(cnifty)-float(pnifty))/float(pnifty))*100
    if Ncpt <= -2:
	print "Better dont trade today as Nifty is down by %.2f%% :)" % Ncpt
	exit(0)

    jobs = []
    manager = multiprocessing.Manager()
    PastData = manager.dict()
    for sym in Nsyms:
        p = multiprocessing.Process(target=GetPastData, args=(sym, PastData))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    jobs = []
    BuySyms = manager.dict()
    SellSyms = manager.dict()

    for sym in Nsyms:
        p = multiprocessing.Process(target=IntradayStrategy, args=(sym, BuySyms, SellSyms))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    if (len(BuySyms.keys())+len(SellSyms.keys())) > 0:
	cps = int(cap/(len(BuySyms.keys())+len(SellSyms.keys())))
	for sym in sorted(BuySyms.keys()):
	    # ExecutBuyOrderAPI()
	    print "Buy %d %s @ %.2f (Leverage=%s applied)" % (int((cps*int(MIS[sym]))/float(BuySyms[sym])), sym, BuySyms[sym], MIS[sym])

	for sym in sorted(SellSyms.keys()):
	    # ExecutSellOrderAPI()
	    print "Sell %d %s @ %.2f (Leverage=%s applied)" % (int((cps*int(MIS[sym]))/float(SellSyms[sym])), sym, SellSyms[sym], MIS[sym])
	    #print "Sell %s @ %.2f (Leverage=%s applied)" % (sym, SellSyms[sym], MIS[sym])
    else:
	print 'No stocks shortlisted'
