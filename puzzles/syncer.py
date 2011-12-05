from puzzlesettings import *
import models,printer,shop,logging

def lock(name):
    pass

def unlock(name):
    Lock.objects.filter(lock_name=name).update(lock_status="U")

def syncall():
    addneworders()
#    addnewprints()
#    addprintstatus()
#    addfulfillments()

def addneworders():
    neworders = shop.openOrders()
    for order in neworders:
        if len(models.Order.objects.filter(order_id=order[0]))==0:
            shipping_address = order[1]["shipping_address"]
            neworder = models.Order(order_id=order[0],order_date=order[1]["created_at"].strftime("%Y-%m-%d %H:%M:%S"),shipping_id=order[0])
            neworder.shipping_name = shipping_address["name"]
            t = models.splitaddress(shipping_address["address1"])
            neworder.shipping_street = t[0]
            neworder.shipping_number = t[1]
            neworder.shipping_zipcode = shipping_address["zip"]
            neworder.shipping_city = shipping_address["city"]
            neworder.shipping_country = shipping_address["country"]
            neworder.shipping_type = "DHL"
            neworder.shopsync = "S" 
            neworder.printsync = "N" 
            neworder.save()
            for product in order[2]:
                prod = product[0]
                opt = product[1]
                newpuzzle = models.Puzzle(puzzle_id=prod["id"])
                newpuzzle.puzzle_type = opt[2]
                newpuzzle.puzzle_template = opt[4]
                newpuzzle.puzzle_orientation = opt[3]
                newpuzzle.puzzle_color = opt[5]
                newpuzzle.puzzle_title = opt[1]
                newpuzzle.puzzle_text = ""
                newpuzzle.printing_status = "N"
                newpuzzle.order = neworder
                newpuzzle.save()
                newimage = models.Image()
                newimage.image_type = "P"
                newimage.image_s3 = opt[6]
                newimage.puzzle = newpuzzle
                newimage.save()

def addnewprints():
    pass

def addprintstatus():
    pass

def addfulfillments():
    pass
