from puzzlesettings import *
import models,printer,shop,logging

def lock(name):
    if len(models.Lock.objects.filter(lock_name=name,lock_status="L"))>0:
        return False
    t = models.Lock.objects.filter(lock_name=name,lock_status="U").update(lock_status="L")
    if t==1:
        return True
    l = models.Lock(lock_name=name)
    l.save()
    return lock(name)

def unlock(name):
    models.Lock.objects.filter(lock_name=name).update(lock_status="U")

def syncall():
    addneworders()
#    addnewprints()
#    addprintstatus()
#    addfulfillments()

def addneworders():
    if not lock("neworders"):
        return
    try:
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
                    for t in PUZZLETABLE:
                        if t[0]==opt[2]:
                            newpuzzle.puzzle_type = t[1]
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
    finally:
        unlock("neworders")

def addnewprints():
    if not lock("newprints"):
        return
    try:
        orders = models.Order.objects.filter(printsync="N",approval="A")
        for order in orders:
            for puzzle in models.Puzzle.objects.filter(order=order):
                s3 = None
                for image in models.Image.objects.filter(puzzle=puzzle):
                    if image.image_type=="P":
                        s3 = image.image_s3
                if s3:
                    p = printer.Order()
                    p.puzzle_s3 = "s3://"+AWSBUCKET+AWSPATH+s3
                    p.puzzle_title = puzzle.puzzle_title
                    p.puzzle_id = puzzle.puzzle_id
                    p.order_id = order.order_id
                    p.shipping_name = order.shipping_name
                    p.shipping_street = order.shipping_street
                    p.shipping_number = order.shipping_number
                    p.shipping_zipcode = order.shipping_zipcode
                    p.shipping_city = order.shipping_city
                    p.shipping_country = order.shipping_country
                    p.shipping_provider = order.shipping_type
                    for t in COLORTABLE:
                        if puzzle.puzzle_color==t[0]:
                            p.color = t[1]
                            break
                    for t in ORIENTATIONTABLE:
                        if puzzle.puzzle_orientation==t[0]:
                            p.orientation = t[1]
                            break
                    for t in PUZZLETABLE:
                        if puzzle.puzzle_type==t[0]:
                            p.puzzle_type = t[1]
                            break
                    for t in TEMPLATETABLE:
                        if puzzle.puzzle_template==t[0]:
                            p.template = t[1]
                            break
                    p.write()
                    puzzle.printing_status = "P"
                    puzzle.save()
            order.printsync = "S"
            order.order_status = "P"
            order.save()
    finally:
        unlock("newprints")

def addprintstatus():
    if not lock("printstatus"):
        return
    try:
        pass
    finally:
        unlock("printstatus")

def addfulfillments():
    if not lock("fulfillments"):
        return
    try:
        pass
    finally:
        unlock("fulfillments")
