import logging
from kiteconnect.connect import KiteConnect
import time
import datetime

logging.basicConfig(level=logging.DEBUG)

print("Kite Connect Program Stated!")
kite = KiteConnect(api_key="your_api_key")

# Redirect the user to the login url obtained
# from kite.login_url(), and receive the request_token
# from the registered redirect url after the login flow.
# Once you have the request_token, obtain the access_token as follows.
data = kite.generate_session("request_token_here", api_secret="your_secret")
kite.set_access_token(data["access_token"])

try:
    ordersList = kite.orders()
    print ("/n Order List: /n" + str(ordersList))

    for order in ordersList:
        if(order.status == "OPEN" and order.parent_order_id != None):
            # This might be the target order for executed BO order.
            print("Order ignored:" + order.id)
        elif(order.status == "OPEN" and order.parent_order_id == None):
            # This might be the open BO order, cancel it.
            kite.cancel_order(variety= kite.VARIETY_BO, 
                            order_id= order.id, 
                            parent_order_id= None )
        elif(order.status == "TRIGGER PENDING" and order.parent_order_id != None):
            # This might be the SL order for executed BO order. Exit this order.
            kite.cancel_order(variety= kite.VARIETY_BO, 
                            order_id= order.id, 
                            parent_order_id=order.parent_order_id)
except Exception as e:
    logging.info("Order Cancellation failed: {}".format(e))
