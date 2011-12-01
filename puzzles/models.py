from puzzlesettings import *
from django.db import models
import random,datetime,time

def randid(t):
    return "%s%d"%(t,random.randint(1,1<<32))

class Order(models.Model):
    STATUS = (
        (u"N", u"New"),
        (u"P", u"Processing"),
        (u"F", u"Finished"),
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
    order_id = models.CharField(max_length=64,default=randid("o"),unique=True,verbose_name="Shopify Order id")
    order_date = models.DateTimeField("order date",default=time.strftime("%Y-%m-%d %H:%M:%S"))
    order_status = models.CharField(max_length=4,choices=STATUS)
    shipping_id = models.CharField(max_length=64,default=randid("s"),unique=True,verbose_name="Shopify Shipping id")
    shipping_name = models.CharField(max_length=255)
    shipping_street = models.CharField(max_length=255)
    shipping_number = models.CharField(max_length=255)
    shipping_zipcode = models.CharField(max_length=255)
    shipping_city = models.CharField(max_length=255)
    shipping_country = models.CharField(max_length=255)
    shipping_type = models.CharField(max_length=10,blank=True,verbose_name="Delivery Company")
    shipping_status = models.CharField(max_length=4,choices=SHIPPING)
    shipping_tracking = models.CharField(max_length=50,blank=True,verbose_name="Tracking id")
    shipping_date = models.DateTimeField("shipping date",blank=True)
    shopsync = models.CharField(max_length=4,choices=SHOPSYNC,verbose_name="In sync with shop")
    printsync = models.CharField(max_length=4,choices=PRINTSYNC,verbose_name="In sync with printer")
    approval = models.CharField(max_length=4,choices=APPROVAL,verbose_name="Approved for printing")
    approval_date = models.DateTimeField("approval date",blank=True)
    touch_date = models.DateTimeField("touch date",auto_now=True)

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
    puzzle_id = models.CharField(max_length=64,default=randid("s"),unique=True,verbose_name="Shopify line item")
    puzzle_type = models.CharField(max_length=64,choices=TYPES)
    puzzle_template = models.CharField(max_length=64,choices=TEMPLATES)
    puzzle_orientation = models.CharField(max_length=64,choices=ORIENTATION)
    puzzle_color = models.CharField(max_length=64,choices=COLORTABLE)
    puzzle_title = models.CharField(max_length=255)
    puzzle_text = models.CharField(max_length=1000,blank=True)
    printing_status = models.CharField(max_length=1000,choices=PRINTINGSTATUS)
    order = models.ForeignKey(Order)

class Image(models.Model):
    IMAGETYPES = (
        (u"P", u"Puzzle"),
        (u"C", u"Cover"),
        (u"O", u"Other"),
    )
    image_type = models.CharField(max_length=4,choices=IMAGETYPES)
    image_s3 = models.CharField(max_length=255,unique=True)
    puzzle = models.ForeignKey(Puzzle)

