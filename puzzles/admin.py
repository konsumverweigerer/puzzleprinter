import models,shop,syncer

import datetime,time,logging
from django.contrib import admin
from django.contrib.admin.options import StackedInline,TabularInline
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

class AdminImageWidget(AdminFileWidget):
    def render(self,name,value,attrs=None):
        output = []
        if value and getattr(value,"url",None):
            image_url = value.url
            file_name = str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" /></a>' % \
                (image_url,image_url,file_name))
        return mark_safe(u''.join(output))

class AdminPreviewWidget(AdminFileWidget):
    def render(self,name,value,attrs=None):
        output = []
        if value and getattr(value,"url",None):
            image_url = value.url
            file_name = str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" width="%d" height="%d"/></a>' % \
                (image_url,image_url,file_name,120,100))
        return mark_safe(u''.join(output))

class ImageInline(TabularInline):
    model = models.Image
    extra = 1

class PuzzleInline(StackedInline):
    model = models.Puzzle
    readonly_fields = ["printing_status","puzzle_id","puzzle_barcode","count"]
    fieldsets = (
        (None,{
            "fields":("preview","puzzle_type","puzzle_color","puzzle_title",
                      "puzzle_barcode","count"),
        }),
        ("Status",{
            "fields":("printing_status",),
        }),
    )
    extra = 0
    formfield_overrides = {
        models.models.ImageField: {"widget": AdminPreviewWidget}
    }

def make_puzzlereprint(modeladmin,request,queryset):
    for order in queryset:
        syncer.makepuzzlereprint(order)
make_puzzlereprint.short_description = "Add a reprint puzzle for selected"

class PuzzleAdmin(admin.ModelAdmin):
    search_fields = ["puzzle_title","puzzle_id","puzzle_barcode"]
    readonly_fields = ["puzzle_id","puzzle_status","puzzle_barcode","count"]
    fieldsets = (
        (None,{
            "fields":("puzzle_type","puzzle_template","puzzle_orientation",
                      "puzzle_color","puzzle_title","puzzle_text","count"),
        }),
        ("Status",{
            "fields":("printing_status","puzzle_status","puzzle_barcode"),
        }),
        ("Preview",{
            "fields":("preview",),
        }),
    )
    inlines = [ImageInline]
    list_display = ["puzzle_id","puzzle_type","puzzle_title","puzzle_barcode",
                    "puzzle_status","preview"]
    ordering = ["puzzle_type","puzzle_title","printing_status"]
    list_filter = ["puzzle_type","puzzle_template","printing_status"]
    formfield_overrides = {
        models.models.ImageField: {"widget": AdminImageWidget}
    }
    actions = [make_puzzlereprint]
    def save_model(self,request,obj,form,change):
        if obj.printing_status=='N' or not obj.preview:
            syncer.previewpuzzle(obj)
        admin.ModelAdmin.save_model(self,request,obj,form,change)

def make_abort(modeladmin,request,queryset):
    queryset.update(order_status="A")
    queryset.update(approval="N")
make_abort.short_description = "Abort selected orders"

def make_approved(modeladmin,request,queryset):
    queryset.update(approval="A")
    queryset.update(approval_date = time.strftime("%Y-%m-%d %H:%M:%S"))
make_approved.short_description = "Mark selected orders as approved"

def make_reprint(modeladmin,request,queryset):
    for order in queryset:
        syncer.makereprint(order)
make_reprint.short_description = "Add a reprint order for selected"

def make_closed(modeladmin,request,queryset):
    queryset.update(order_status="F",shopsync="S",printsync="S")
    for order in queryset:
        shop.endFullfillment(order.order_id)
make_closed.short_description = "Close selected orders"

def make_print(modeladmin,request,queryset):
    syncer.printorders(queryset)
make_print.short_description = "Print selected orders"

class OrderAdmin(admin.ModelAdmin):
    search_fields = ["shipping_name","order_id","order_number"]
    readonly_fields = ["order_id","shipping_id","shopsync","printsync","order_date","touch_date","shipping_date","approval_date","reprint_number","reprint_reason","order_number"]
    fieldsets = (
        (None, {
            "fields":("order_id","shipping_id","reprint_number","reprint_reason","order_number"),
        }),
        ("Timestamps", {
            "fields":("order_date","shipping_date","approval_date"),
        }),
        ("Address", {
            "fields":("shipping_email","shipping_name","shipping_street","shipping_number","shipping_zipcode","shipping_city","shipping_country")
        }),
    )
    inlines = [ PuzzleInline ]
    list_display = ["order_id","order_date","shipping_name","order_status","approval","touch_date"]
    ordering = ["order_date","shipping_name","touch_date"]
    list_filter = ["order_status","shipping_status","shopsync","printsync","approval"]
    actions = [make_approved,make_closed,make_print,make_reprint,make_abort]
    formfield_overrides = {
        models.models.ImageField: {"widget": AdminPreviewWidget}
    }

admin.site.register(models.Order,OrderAdmin)
admin.site.register(models.Puzzle,PuzzleAdmin)
