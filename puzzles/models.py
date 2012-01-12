from puzzlesettings import *

from django.db import models

import random,datetime,time,re

def randid(t):
    return "%s%d"%(t,random.randint(1,1<<32))

def splitaddress(ad):
    v = re.findall(" [0-9]+",ad)
    if v:
        t = ad.find(v[-1])
        if t>=0:
            return (ad[:t],ad[(t+1):])
    v = re.findall("[0-9]+",ad)
    if v:
        t = ad.find(v[-1])
        if t>=0:
            return (ad[:t],ad[(t):])
    return (ad,"")

class Order(models.Model):
    STATUS = (
        (u"N", u"New"),
        (u"P", u"Processing"),
        (u"F", u"Finished"),
        (u"A", u"Aborted"),
    )
    SHIPPING = (
        (u"N", u"New"),
        (u"S", u"Shipping"),
        (u"T", u"Reached Target"),
    )
    SHOPSYNC = (
        (u"N", u"Not synchronized"),
        (u"S", u"Synchronized"),
    )
    PRINTSYNC = (
        (u"N", u"Not synchronized"),
        (u"S", u"Synchronized"),
    )
    APPROVAL = (
        (u"N", u"Not approved"),
        (u"A", u"Approved"),
    )
    order_id = models.CharField(max_length=64,default=randid("o"),verbose_name="Shopify Order id")
    order_number = models.CharField(max_length=64,blank=True,null=True,verbose_name="Shopify Order number")
    order_date = models.DateTimeField("order date",default=time.strftime("%Y-%m-%d %H:%M:%S"))
    order_status = models.CharField(max_length=4,choices=STATUS,default="N")
    shipping_id = models.CharField(max_length=64,default=randid("s"),verbose_name="Shopify Shipping id")
    shipping_email = models.CharField(max_length=255,blank=True,null=True)
    shipping_name = models.CharField(max_length=255)
    shipping_street = models.CharField(max_length=255)
    shipping_number = models.CharField(max_length=255)
    shipping_zipcode = models.CharField(max_length=255)
    shipping_city = models.CharField(max_length=255)
    shipping_country = models.CharField(max_length=255)
    shipping_type = models.CharField(max_length=10,blank=True,verbose_name="Delivery Company")
    shipping_status = models.CharField(max_length=4,choices=SHIPPING,default="N")
    shipping_tracking = models.CharField(max_length=50,blank=True,verbose_name="Tracking id")
    shipping_date = models.DateTimeField("shipping date",blank=True,null=True)
    reprint_number = models.IntegerField(null=True,blank=True,verbose_name="Reprint number")
    reprint_reason = models.CharField(max_length=255,blank=True,null=True,verbose_name="Reprint reason")
    shopsync = models.CharField(max_length=4,choices=SHOPSYNC,verbose_name="In sync with shop")
    printsync = models.CharField(max_length=4,choices=PRINTSYNC,verbose_name="In sync with printer")
    approval = models.CharField(max_length=4,choices=APPROVAL,verbose_name="Approved for printing",default="N")
    approval_date = models.DateTimeField("approval date",blank=True,null=True)
    touch_date = models.DateTimeField("touch date",auto_now=True)
    total_lineitems = models.DecimalField(max_digits=12,decimal_places=2,default=0,null=True,verbose_name="Lineitem total")

class Puzzle(models.Model):
    TEMPLATES = (
        (u"1",u"std"),
    )
    TYPES = (
        (u"200",u"200 Parts"),
        (u"500",u"500 Parts"),
        (u"600",u"600 Parts (Heart shaped)"),
        (u"1000",u"1000 Parts"),
    )
    ORIENTATION = (
        (u"1",u"horizontal"),
        (u"2",u"vertical"),
    )
    PRINTINGSTATUS = (
        (u"N", u"New"),
        (u"P", u"Processing"),
        (u"F", u"Finished"),
    )
    COSTSTATUS = (
        (u"N", u"Open"),
        (u"A", u"Accounted"),
    )
    puzzle_id = models.CharField(max_length=64,default=randid("s"),verbose_name="Shopify line item")
    puzzle_barcode = models.CharField(max_length=64,blank=True,null=True,verbose_name="Printer barcode")
    puzzle_status = models.CharField(max_length=255,blank=True,null=True,verbose_name="Printing status")
    puzzle_type = models.CharField(max_length=64,choices=TYPES)
    puzzle_template = models.CharField(max_length=64,choices=TEMPLATES)
    puzzle_orientation = models.CharField(max_length=64,choices=ORIENTATION)
    puzzle_color = models.CharField(max_length=64,choices=COLORTABLE)
    puzzle_title = models.CharField(max_length=256,blank=True)
    puzzle_text = models.CharField(max_length=1000,blank=True)
    coststatus = models.CharField(max_length=64,blank=True,null=True,choices=COSTSTATUS)
    cost = models.DecimalField(max_digits=12,decimal_places=2,default=0,null=True,verbose_name="Incurred cost")
    reprint_number = models.IntegerField(null=True,blank=True,verbose_name="Reprint number")
    reprint_reason = models.CharField(max_length=255,blank=True,null=True,verbose_name="Reprint reason")
    printing_status = models.CharField(max_length=1000,choices=PRINTINGSTATUS,default="N")
    preview = models.ImageField(upload_to='preview',width_field="preview_width",height_field="preview_height",null=True,blank=True)
    preview_width = models.PositiveIntegerField(null=True,blank=True)
    preview_height = models.PositiveIntegerField(null=True,blank=True)
    order = models.ForeignKey(Order)

class Image(models.Model):
    IMAGETYPES = (
        (u"P", u"Puzzle"),
        (u"C", u"Cover"),
        (u"O", u"Other"),
    )
    image_type = models.CharField(max_length=4,choices=IMAGETYPES)
    image_s3 = models.CharField(max_length=255)
    puzzle = models.ForeignKey(Puzzle)

class Lock(models.Model):
    LOCKTYPE = (
        (u"U", u"Unlocked"),
        (u"L", u"Locked"),
    )
    lock_name = models.CharField(max_length=64)
    lock_status = models.CharField(max_length=4,choices=LOCKTYPE,default="U")

