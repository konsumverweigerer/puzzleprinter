from django.db import models

class Order(models.Model):
    STATUS = (
        (u'N', u'New'),
        (u'P', u'Processing'),
        (u'F', u'Finished'),
    )
    SHIPPING = (
        (u'N', u'New'),
        (u'S', u'Shipping'),
        (u'T', u'Reached Target'),
    )
    SHOPSYNC = (
        (u'N', u'Not synchronized'),
        (u'S', u'Synchronized'),
    )
    PRINTSYNC = (
        (u'N', u'Not synchronized'),
        (u'S', u'Synchronized'),
    )
    order_status = models.CharField(max_length=4,choices=STATUS)
    order_id = models.CharField(max_length=64)
    shipping_id = models.CharField(max_length=64)
    shipping_name = models.CharField(max_length=255)
    shipping_street = models.CharField(max_length=255)
    shipping_number = models.CharField(max_length=255)
    shipping_zipcode = models.CharField(max_length=255)
    shipping_city = models.CharField(max_length=255)
    shipping_country = models.CharField(max_length=255)
    shipping_status = models.CharField(max_length=4,choices=SHIPPING)
    shipping_tracking = models.CharField(max_length=4,choices=TRACKING)
    shopsync = models.CharField(max_length=4,choices=SHOPSYNC)
    printsync = models.CharField(max_length=4,choices=PRINTSYNC)

class Puzzle(models.Model):
    puzzle_id = models.CharField(max_length=64)
    puzzle_type = models.CharField(max_length=64)
    puzzle_template = models.CharField(max_length=64)
    puzzle_title = models.CharField(max_length=255)
    printing_status = models.CharField(max_length=1000)
    order = models.ForeignKey(Order)

class Image(models.Model):
    IMAGETYPES = (
        (u'P', u'Puzzle'),
        (u'C', u'Cover'),
        (u'O', u'Other'),
    )
    image_type = models.CharField(max_length=4,choices=IMAGETYPES)
    image_s3 = models.CharField(max_length=255)
    puzzle = models.ForeignKey(Puzzle)

