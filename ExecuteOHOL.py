from __future__ import division

import datetime, urllib2, csv, multiprocessing
from threading import Timer
"""
from kiteconnect.connect import KiteConnect
"""
import logging, time

from ohol import FindOHOLStocks, MIS

# Important parameters
CAPITAL=10000
cap=CAPITAL*(80/100)
SLPct=(1.1/100)
ProfitPct=(1.1/100)

def GetTicks(price):
    tgt=round(0.05 * round(float(price * ProfitPct)/0.05), 2)
    sl=round(0.05 * round(float(price * SLPct)/0.05), 2)
    tsl=round(0.05 * round(float(price * 0.005)/0.05), 2)
    return (tgt, sl, tsl)

def PlaceOrder(call, sym, rprice, Orders):
    # Derive price to buy/sell from recommended price
    price = round(float(rprice), 2)

    numberOfStocks = int((cps*int(MIS[sym]))/price)
    #print "%s %d %s @ %.2f (Leverage=%s applied)" % (call, numberOfStocks, sym, price, MIS[sym])

    # Get Ticks values for SqOff, SL, and Trailing SL used for BO
    (tgt, sl, tsl) = GetTicks(price)

    i=1
    # Place a BO order
    if (call == 'Buy'):
	try:
	    """
	    order_id = kite.place_order(tradingsymbol=sym,
	                                exchange=kite.EXCHANGE_NSE,
	                                transaction_type=kite.TRANSACTION_TYPE_BUY,
	                                quantity=numberOfStocks,
	                                order_type=kite.ORDER_TYPE_LIMIT,
	                                product=kite.PRODUCT_MIS,
	                                variety=kite.VARIETY_BO,
	                                price=price,
	                                squareoff=tgt,
	                                stoploss=sl,
	                                trailing_stoploss=tsl
	                                )
	    """
	    order_id = str(i)
	    OrderDetails = [price, tgt, sl, tsl]
	    Orders[order_id] = OrderDetails
	    print Orders[str(1)]
	    print("Buy Order Id: " + str(order_id) + ", Price: " + str(Orders[order_id][0])  + ", SQTick: " + str(Orders[order_id][1]) + ", SLTick: " + str(Orders[order_id][2]) + ", TSLTick: " + str(Orders[order_id][3]))
	    i+=1
	except Exception as e:
	    logging.info("Order placement failed: {}".format(e))
    elif (call == 'Sell'):
	try:
	    """
	    order_id = kite.place_order(tradingsymbol=sym,
	                                exchange=kite.EXCHANGE_NSE,
	                                transaction_type=kite.TRANSACTION_TYPE_SELL,
	                                quantity=numberOfStocks,
	                                order_type=kite.ORDER_TYPE_LIMIT,
	                                product=kite.PRODUCT_MIS,
	                                variety=kite.VARIETY_BO,
	                                price=price,
	                                squareoff=tgt,
	                                stoploss=sl,
	                                trailing_stoploss=tsl
	                                )
	    """
	    order_id = str(i)
	    i+=1
	    OrderDetails = [price, tgt, sl, tsl]
	    Orders[order_id] = OrderDetails
	    print Orders[str(1)]
	    print("Sell Order Id: " + str(order_id) + ", Price: " + str(Orders[order_id][0])  + ", SQTick: " + str(Orders[order_id][1]) + ", SLTick: " + str(Orders[order_id][2]) + ", TSLTick: " + str(Orders[order_id][3]))
	except Exception as e:
	    logging.info("Order placement failed: {}".format(e))
    
#(BuySyms, SellSyms) = FindOHOLStocks()
BuySyms = {'IDEA': 154.4}
SellSyms = {'HCLTECH': 930.1}

if (len(BuySyms.keys())+len(SellSyms.keys())) > 0:
    jobs = []
    manager = multiprocessing.Manager()

    cps = int(cap/(len(BuySyms.keys())+len(SellSyms.keys())))

    """
    kite = KiteConnect(api_key="your_api_key")

    # Redirect the user to the login url obtained
    # from kite.login_url(), and receive the request_token
    # from the registered redirect url after the login flow.
    # Once you have the request_token, obtain the access_token as follows.
    data = kite.generate_session("request_token_here", api_secret="your_secret")
    kite.set_access_token(data["access_token"])
    """

    BuyOrders = manager.dict()
    for bsym in BuySyms.keys():
        p = multiprocessing.Process(target=PlaceOrder, args=('Buy', bsym, BuySyms[bsym], BuyOrders))
        jobs.append(p)
        p.start()

    SellOrders = manager.dict()
    for ssym in SellSyms.keys():
        p = multiprocessing.Process(target=PlaceOrder, args=('Sell', ssym, SellSyms[ssym], SellOrders))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()
