from puzzlesettings import *
from shopify import *

import logging

logger = logging.getLogger(__name__)

ShopifyResource.site = "https://%s:%s@%s.myshopify.com/admin"%(SHOPIFYKEY,SHOPIFYPWD,SHOPIFYSHOP)

# Variant string: #puzzle_name#|#box_title#|#sizeId#|#formatId#|#boxTypeId#|#boxColorId#|#imgToken#
#puzzle_name
#===========
#Titel der Produkt Variante.
#
#box_title
#=========
#Text der auf die Box geschrieben werden soll. Darf nicht das (|) Zeichen enthalten.
#
#sizeId
#=======
#Puzzel groesse / Anzahl der Teile.
#
#1 = 100 Teile
#2 = 200 Teile
#3 = 500 Teile
#4 = 1000 Teile
#
#formatId
#===========
#Format des bildes in der demo war auch eine Herzform. Nach meinem letzten stand gibt es dieses feature
#nicht mehr also alles ist im Querformat. (Die Formatid wird trotzdem uebertragen.)
#1 = Querformat
#2 = Hochformat
#
#boxTypeId
#=========
#Die art der Schachtel geplant wurden verschiedene arten von boxen. Nach meinem letzten stand gibt es dieses feature
#nicht mehr also alles ist boxTypeId 1)
#
#colorId
#=======
#Die id der Schachtel Farbe, die farben sind auf der webseite folgende RGB- Hex Codes zugewiesen. Eventuell muss andi dir die pantone oder ral farb codes raussuchen.
#
#1 = #333333
#2 = #FFFFFF
#3 = #7D0E19
#4 = #DD5B78
#5 = #FF8E1D
#6 = #FFFF00
#7 = #91B329
#8 = #1B8B34
#9 = #003E6F
#10 = #2DC0C8
#
#imgToken
#========
#Name des Puzzlebild inklusive Datei Endung. 


def openOrders(since_id=None,financial_status="paid"):
    orders = [(details(0,order=x.to_dict()),x) for x in Order.find(limit=250,financial_status=financial_status,since_id=since_id) if x.attributes["fulfillment_status"]==None]
    logging.info("have %s orders from shopify"%(len(orders)))
    return [(x[0][0],x[0][1],x[0][2],x[0][3],x[1]) for x in orders if len(x[0][2])>0]

def deadOrders(financial_status="abandoned"):
    orders = [(x.to_dict(),x) for x in Order.find(limit=250,financial_status=financial_status)]
    return orders

def oldOrders(financial_status="abandoned"):
    orders = [(x.to_dict(),x) for x in Order.find(limit=250,financial_status=financial_status)]
    return orders

def sentOrders():
    orders = [x.to_dict() for x in Order.find(limit=250,financial_status="paid") if x.attributes["fulfillment_status"]!=None]
    return [x for x in orders if len(x["fulfillments"])>0]

def details(orderid,order=None):
    if not order:
        order = Order.get(int(orderid))
    try:
        products = [(x[0],x[0]["variants"][0]["option1"].split("|"),x[1]) 
                    for x in [(Product.get(p["product_id"]),p["quantity"]) 
                              for p in order["line_items"] 
                              if p["requires_shipping"] and p["fulfillment_status"]==None] if len(x[0]["variants"])==1]
    except:
        print "could not get product for "+str(order["id"])
        products = []
    shipping = {}
    if "shipping_address" in order.keys():
        shipping = order["shipping_address"]
    return (order["id"],order,products,shipping)

def startFullfillment(orderid):
    order = Order.find(int(orderid))
    fs = order.attributes["fulfillments"]
    if len(fs)>0:
        return fs[0]
    f = Fulfillment(dict(order_id=orderid,line_items=[]))
    f.save()
    return f

def updateFullfillment(orderid,tracking_company=None,tracking_number=None,status=None):
    order = Order.find(int(orderid))
    fs = order.attributes["fulfillments"]
    if len(fs)>0:
        fulfillment = fs[0]
        if fulfillment and (tracking_number or tracking_company):
            fulfillment.attributes["tracking_company"] = tracking_company
            fulfillment.attributes["tracking_number"] = tracking_number
            fulfillment.save()
        return fulfillment
    else:
        startFullfillment(orderid)
        return updateFullfillment(orderid,tracking_company=tracking_company,tracking_number=tracking_number,status=status)
    return None

def endFullfillment(orderid,status=None):
    order = Order.find(int(orderid))
    if order:
        order.close()
    return order

def deleteProduct(productid):
    try:
        shopify.Product.delete(productid)
    except:
        return False
    return True
