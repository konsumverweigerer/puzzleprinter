from puzzlesettings import *
from shopify import *

ShopifyResource.site = "https://%s:%s@%s.myshopify.com/admin"%(SHOPIFYKEY,SHOPIFYPWD,SHOPIFYSHOP)

# Variant string: #puzzle_name#|#box_title#|#sizeId#|#formatId#|#boxTypeId#|#boxColorId#|#imgToken#

def openOrders():
    orders = [details(0,order=x.to_dict()) for x in Order.find(limit=250,financial_status="paid") if x.attributes["fulfillment_status"]==None]
    return [x for x in orders if len(x[1])>0]

def details(orderid,order=None):
    if not order:
        order = Order.get(int(orderid))
    products = [(x,x["variants"][0]["option1"].split("|")) for x in [Product.get(p["product_id"]) for p in order["line_items"] if p["requires_shipping"] and p["fulfillment_status"]==None] if len(x["variants"])==1]
    return (order,products,order["shipping_address"])

def startFullfillment(orderid):
    pass

def updateFullfillment(orderid):
    pass

def endFullfillment(orderid):
    pass

