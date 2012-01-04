from puzzlesettings import *

import models,printer,shop,mechanize

from django.core.files.base import ContentFile
from xhtml2pdf import document
from pyPdf import pdf

import logging,StringIO,os
import string,sys
import random,datetime,time,re
reload(sys)

COUNTRYMAP = {
    "Germany" : "Deutschland",
}

def readinvoice(orderid=None):
    if not orderid:
        return ("","")
    cj = mechanize.CookieJar()
    br = mechanize.Browser()
    br.set_cookiejar(cj)
    url = "%s%s?shop=%s"%(SHOPINVOICEURL,orderid,SHOPIFYSHOP)
    br.set_handle_robots(False)
    br.open(url)
    form = [x for x in br.forms()][0]
    form.set_value(SHOPPWD,'password')
    form.set_value(SHOPLOGIN,'login')
    br.form = form
    r = br.submit()
    t = r.read()
    hh = mechanize.HTTPHandler()
    hsh = mechanize.HTTPSHandler()
    opener = mechanize.build_opener(hh, hsh)
    mechanize.install_opener(opener)
    data = [t]
    for inv in INVOICEID.split(","):
        req = mechanize.Request("%s%s?template_id=%s"%(SHOPINVOICEURL,orderid,inv))
        req.add_header('Accept','text/javascript, text/html, application/xml, text/xml, */*')
        req.add_header('X-Requested-With','XMLHttpRequest')
        req.add_header('Referer',url)
        cj.add_cookie_header(req)
        res = mechanize.urlopen(req)
        data.append((inv,res.read()))
    return data

def addinvoicewrap(i):
    return "<div id=\"preview\" class=\"clearfix preview-content\"><div id=\"preview-%s\">%s</div></div>"%(i[0],i[1])

def renderinvoice(invoice):
    writer = pdf.PdfFileWriter()
    w = open(os.path.join(BASEDIR,"puzzles","templates","invoicewrap.html")).read()
    for i in (w%(addinvoicewrap(x)) for x in invoice[1:]):
        o = StringIO.StringIO()
        document.pisaDocument(StringIO.StringIO(i),o)
        writer.addPage(pdf.PdfFileReader(StringIO.StringIO(o.getvalue())).getPage(0))
    o = StringIO.StringIO()
    writer.write(o)
    return o.getvalue()

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
    addneworders(True)
    addnewprints()
    addprintstatus()
    addfulfillments()

def addneworders(force=False):
    if not lock("neworders"):
        return
    try:
        if force:
            neworders = shop.openOrders()
            for order in neworders:
                addneworder(order)
        else:
            since_id = None
            v = models.Order.objects.order_by('-id')[0:1].get() 
            if v:
                since_id = v.order_id
            print "searching orders since: "+str(since_id)
            neworders = shop.openOrders(since_id=since_id)
            for order in neworders:
                addneworder(order)
    finally:
        unlock("neworders")

def addneworder(order):
    if len(models.Order.objects.filter(order_id=order[0]))==0:
        shipping_address = order[1]["shipping_address"]
        neworder = models.Order(order_id=order[0],order_date=order[1]["created_at"].strftime("%Y-%m-%d %H:%M:%S"),shipping_id=order[0])
        neworder.shipping_name = shipping_address["name"]
        t = models.splitaddress(shipping_address["address1"])
        neworder.shipping_street = t[0]
        neworder.shipping_number = t[1]
        neworder.shipping_zipcode = shipping_address["zip"]
        neworder.shipping_city = shipping_address["city"]
        t = shipping_address["country"]
        if t in COUNTRYMAP.keys():
            t = COUNTRYMAP[t]
        neworder.shipping_country = t
        neworder.shipping_type = "DHL"
        neworder.shopsync = "S" 
        neworder.printsync = "N" 
        neworder.approval = "N" 
        neworder.total_lineitems = order[1]["total_price"]
        neworder.order_number = order[1]["order_number"]
        neworder.save()
        barcodes = []
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
            barcodes.append(printer.makebarcode(neworder.order_id,newpuzzle.puzzle_id))
            newimage = models.Image()
            newimage.image_type = "P"
            newimage.image_s3 = opt[6]
            newimage.puzzle = newpuzzle
            newimage.save()
        sys.setdefaultencoding("utf8")
        order[4].attributes["note_attributes"] = {
            "invoiceid": neworder.id,
            "barcodes": string.join(barcodes,","),
        }
        order[4].save()
        sys.setdefaultencoding("ascii")
        previeworder(neworder)

def makereprint(order,reprint_reason="Reprinting"):
    if not lock("newprints"):
        return
    try:
        reprint_number = 1
        while len(models.Order.objects.filter(order_id=order.order_id,reprint_number=reprint_number))>0:
            reprint_number = reprint_number+1
        neworder = models.Order(order_id=order.order_id,order_date=order.order_date,shipping_id=order.shipping_id)
        neworder.shipping_name = order.shipping_name
        neworder.shipping_street = order.shipping_street
        neworder.shipping_number = order.shipping_number
        neworder.shipping_zipcode = order.shipping_zipcode
        neworder.shipping_city = order.shipping_city
        neworder.shipping_country = order.shipping_country
        neworder.shipping_type = order.shipping_type
        neworder.shopsync = "S"
        neworder.printsync = "N" 
        neworder.total_lineitems = order.total_lineitems
        neworder.save()
        for puzzle in models.Puzzle.objects.filter(order=order):
            newpuzzle = models.Puzzle(puzzle_id=puzzle.puzzle_id)
            newpuzzle.puzzle_type = puzzle.puzzle_type
            newpuzzle.puzzle_template = puzzle.puzzle_template
            newpuzzle.puzzle_orientation = puzzle.puzzle_orientation
            newpuzzle.puzzle_color = puzzle.puzzle_color
            newpuzzle.puzzle_title = puzzle.puzzle_title
            newpuzzle.puzzle_text = puzzle.puzzle_text
            newpuzzle.printing_status = "N"
            newpuzzle.order = neworder
            newpuzzle.save()
            for image in models.Image.objects.filter(puzzle=puzzle):
                newimage = models.Image()
                newimage.image_type = image.image_type
                newimage.image_s3 = image.image_s3
                newimage.puzzle = newpuzzle
                newimage.save()
    finally:
        unlock("newprints")

def printorders(orders):
    if not lock("newprints"):
        return
    try:
        for order in orders:
            printorder(order)
    finally:
        unlock("newprints")

def previewpuzzle(puzzle,puzzle_id=None):
    if puzzle_id and not puzzle:
        t = models.Puzzle.objects.filter(puzzle_id=puzzle_id)
        if len(t)>0:
            puzzle = t[0]
    if not puzzle:
        return
    order = puzzle.order
    s3 = None
    for image in models.Image.objects.filter(puzzle=puzzle):
        if image.image_type=="P":
            s3 = image.image_s3
    if s3:
        p = printer.Order()
        r = ""
        if order.reprint_number:
            r = r+str(order.reprint_number)
        if puzzle.reprint_number:
            r = r+str(puzzle.reprint_number)
        if len(r)>0:
            p.reprint = r
        p.puzzle_s3 = "s3://"+AWSBUCKET+AWSPATH+s3
        p.puzzle_title = puzzle.puzzle_title
        p.puzzle_id = puzzle.puzzle_id
        p.puzzle_type = puzzle.puzzle_type
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
        p.makepreview()
        if p.preview:
            puzzle.preview.save("%s.jpg"%(puzzle.puzzle_id),ContentFile(p.preview),save=False)
        if p.barcode:
            puzzle.puzzle_barcode = p.barcode
        puzzle.save()

def previeworder(order,order_id=None):
    if order_id and not order:
        t = models.Order.objects.filter(order_id=order_id)
        if len(t)>0:
            order = t[0]
    print "preview for "+str(order)
    if not order:
        return
    for puzzle in models.Puzzle.objects.filter(order=order):
        s3 = None
        for image in models.Image.objects.filter(puzzle=puzzle):
            if image.image_type=="P":
                s3 = image.image_s3
        if s3:
            p = printer.Order()
            r = ""
            if order.reprint_number:
                r = r+str(order.reprint_number)
            if puzzle.reprint_number:
                r = r+str(puzzle.reprint_number)
            if len(r)>0:
                p.reprint = r
            p.puzzle_s3 = "s3://"+AWSBUCKET+AWSPATH+s3
            p.puzzle_title = puzzle.puzzle_title
            p.puzzle_id = puzzle.puzzle_id
            p.puzzle_type = puzzle.puzzle_type
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
            p.makepreview()
            if p.preview:
                puzzle.preview.save("%s.jpg"%(puzzle.puzzle_id),ContentFile(p.preview),save=False)
            if p.barcode:
                puzzle.puzzle_barcode = p.barcode
            puzzle.save()

def printdemo(order,order_id=None,directory="/tmp"):
    if order_id and not order:
        t = models.Order.objects.filter(order_id=order_id)
        if len(t)>0:
            order = t[0]
    print "demo for "+str(order)
    for puzzle in models.Puzzle.objects.filter(order=order):
        s3 = None
        for image in models.Image.objects.filter(puzzle=puzzle):
            if image.image_type=="P":
                s3 = image.image_s3
        if s3:
            p = printer.Order()
            r = ""
            if order.reprint_number:
                r = r+str(order.reprint_number)
            if puzzle.reprint_number:
                r = r+str(puzzle.reprint_number)
            if len(r)>0:
                p.reprint = r
            p.puzzle_s3 = "s3://"+AWSBUCKET+AWSPATH+s3
            p.puzzle_title = puzzle.puzzle_title
            p.puzzle_id = puzzle.puzzle_id
            p.puzzle_type = puzzle.puzzle_type
            p.order_id = order.order_id
            p.shipping_name = order.shipping_name
            p.shipping_street = order.shipping_street
            p.shipping_number = order.shipping_number
            p.shipping_zipcode = order.shipping_zipcode
            p.shipping_city = order.shipping_city
            p.shipping_country = order.shipping_country
            p.shipping_provider = order.shipping_type
            p.additionaldata = renderinvoice(readinvoice(order.order_id))
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
            p.write(directory)

def printorder(order,force=False):
    if not order:
        return
    if not force:
        if order.printsync!="N" or order.approval!="A":
            return
    for puzzle in models.Puzzle.objects.filter(order=order):
        if puzzle.printing_status!="N" and not force:
            continue
        s3 = None
        for image in models.Image.objects.filter(puzzle=puzzle):
            if image.image_type=="P":
                s3 = image.image_s3
        if s3:
            p = printer.Order()
            r = ""
            if order.reprint_number:
                r = r+str(order.reprint_number)
            if puzzle.reprint_number:
                r = r+str(puzzle.reprint_number)
            if len(r)>0:
                p.reprint = r
            p.puzzle_s3 = "s3://"+AWSBUCKET+AWSPATH+s3
            p.puzzle_title = puzzle.puzzle_title
            p.puzzle_id = puzzle.puzzle_id
            p.puzzle_type = puzzle.puzzle_type
            p.order_id = order.order_id
            p.shipping_name = order.shipping_name
            p.shipping_street = order.shipping_street
            p.shipping_number = order.shipping_number
            p.shipping_zipcode = order.shipping_zipcode
            p.shipping_city = order.shipping_city
            p.shipping_country = order.shipping_country
            p.shipping_provider = order.shipping_type
            p.additionaldata = renderinvoice(readinvoice(order.order_id))
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
            try:
                p.write()
                if p.preview:
                    puzzle.preview.save("%s.jpg"%(puzzle.puzzle_id),ContentFile(p.preview),save=False)
                if p.barcode:
                    puzzle.puzzle_barcode = p.barcode
                puzzle.printing_status = "P"
            except Exception,e:
                print "could not transfer puzzle "+p.barcode+" "+str(e)
            puzzle.save()
    order.printsync = "S"
    order.order_status = "P"
    order.save()

def addnewprints():
    if not lock("newprints"):
        return
    try:
        orders = models.Order.objects.filter(printsync="N",approval="A")
        for order in orders:
            printorder(order)
    finally:
        unlock("newprints")

def addprintstatus():
    if not lock("printstatus"):
        return
    try:
        prints = printer.readorders()
        for p in prints:
            try:
                order = models.Order.objects.get(order_id=p.order_id)
                puzzles = models.Puzzle.objects.filter(order=order)
            except:
                if p.barcode:
                    try:
                        puzzles = models.Puzzle.objects.filter(puzzle_barcode=p.barcode)[0:1]
                        for puzzle in puzzles:
                            order = puzzle.order
                    except:
                        print "could not find order for "+str(p.barcode)
                        continue
                if not puzzles or not order:
                    print "could not find order for "+str(p.order_id)+" "+str(p.barcode)
                    continue
            for puzzle in puzzles:
                r = ""
                if order.reprint_number:
                    r = r+str(order.reprint_number)
                if puzzle.reprint_number:
                    r = r+str(puzzle.reprint_number)
                if len(r)>0:
                    bc = printer.makebarcode(order.order_id,puzzle.puzzle_id,r)
                else:
                    bc = printer.makebarcode(order.order_id,puzzle.puzzle_id)
                if bc==p.barcode:
                    t = "%s: %s"%(p.printing_status,p.shipping_status)
                    if t and len(t)>255:
                        puzzle.puzzle_status = t[0:255]
                    else:
                        puzzle.puzzle_status = t
                    if p.finished() and puzzle.printing_status!="F":
                        puzzle.printing_status = "F"
                        order.shopsync = "N"
                    elif p.valid() and puzzle.printing_status=="N":
                        puzzle.printing_status = "P"
                        order.shopsync = "N"
                    if p.shipping_status and order.shipping_status=="N":
                        order.shipping_status = "S"
                        t = p.shipping_status.split(";")
                        if len(t)>3:
                            order.shipping_type = t[1]
                            order.shipping_tracking = t[0]
                        if not order.shipping_date:
                            order.shipping_date = time.strftime("%Y-%m-%d %H:%M:%S")
                        order.shopsync = "N"
                    puzzle.save()
                    order.save()
    finally:
        unlock("printstatus")

def addbarcodes():
    if not lock("barcode"):
        return
    try:
        puzzles = models.Puzzle.objects.all()
        for puzzle in puzzles:
            if not puzzle.puzzle_barcode:
                order = puzzle.order
                r = ""
                if order.reprint_number:
                    r = r+str(order.reprint_number)
                if puzzle.reprint_number:
                    r = r+str(puzzle.reprint_number)
                if len(r)>0:
                    puzzle.puzzle_barcode = printer.makebarcode(order.order_id,puzzle.puzzle_id,r)
                else:
                    puzzle.puzzle_barcode = printer.makebarcode(order.order_id,puzzle.puzzle_id)
                puzzle.save()
    finally:
        unlock("barcode")

def pruneoldproducts():
    orders = shop.deadOrders()
    for order in orders:
        productid = order[1].attributes["line_items"][0].attributes["product_id"]
        if len(models.Puzzle.objects.filter(puzzle_id=productid))==0:
            shop.deleteProduct(productid)
        else:
            print "not pruning used product "+str(productid)

def addfulfillments():
    if not lock("fulfillments"):
        return
    try:
        orders = models.Order.objects.filter(shopsync="N")
        for order in orders:
            if order.reprint_number:
                continue
            if order.shipping_status=="S":
                shop.updateFullfillment(order.order_id,tracking_company=order.shipping_type,tracking_number=order.shipping_tracking)
                order.order_status = "F"
            else:
                puzzles = models.Puzzle.objects.filter(order=order)
                for puzzle in puzzles:
                    if puzzle.reprint_number:
                        continue
                    if puzzle.printing_status=="F" or puzzle.printing_status=="P":
                        shop.startFullfillment(order.order_id)
                        break
            order.shopsync = "S"
            order.save()
    finally:
        unlock("fulfillments")
