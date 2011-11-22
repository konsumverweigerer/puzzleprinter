from django.db import models

class Order(models.Model):
    order_id = models.CharField(max_length=64)

class Puzzle(models.Model):
    puzzle_id = models.CharField(max_length=64)
    order = models.ForeignKey(Order)

class Image(models.Model):
    IMAGETYPES = (
        (u'P', u'Puzzle'),
        (u'C', u'Cover'),
        (u'O', u'Other'),
    )
    image_type = models.CharField(max_length=4,choices=IMAGETYPES)
    puzzle = models.ForeignKey(Puzzle)

