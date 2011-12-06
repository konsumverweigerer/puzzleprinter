import models,shop,syncer
from django.contrib import admin
from django.contrib.admin.options import StackedInline, TabularInline
import datetime,time

class ImageInline(TabularInline):
    model = models.Image
    extra = 1

class PuzzleInline(TabularInline):
    model = models.Puzzle
    readonly_fields = ["printing_status","puzzle_id","preview"]
    fieldsets = (
        (None,{
            "fields":("preview","puzzle_type","puzzle_color","puzzle_title"),
            "classes":("collapse",),
        }),
        ("Status",{
            "fields":("printing_status",),
        }),
    )
    extra = 1

class PuzzleAdmin(admin.ModelAdmin):
    class MyModelAdmin(admin.ModelAdmin):
        def get_urls(self):
            urls = super(MyModelAdmin,self).get_urls()
            my_urls = patterns('',
                (r'^pimages/$',self.admin_site.admin_view(self.rimage)))
            return my_urls+urls

        def rimage(self,request):
            pass

    readonly_fields = ["puzzle_id","preview"]
    fieldsets = (
        (None,{
            "fields":("puzzle_type","puzzle_template","puzzle_orientation","puzzle_color","puzzle_title","puzzle_text"),
        }),
        ("Status",{
            "fields":("printing_status",),
        }),
        ("Preview",{
            "fields":("preview",),
        }),
    )
    inlines = [ImageInline]
    list_display = ["puzzle_id","puzzle_type","puzzle_title"]
    ordering = ["puzzle_type","puzzle_title","printing_status"]
    list_filter = ["puzzle_type","puzzle_template","printing_status"]

def make_approved(modeladmin,request,queryset):
    queryset.update(approval="A")
    queryset.update(approval_date = time.strftime("%Y-%m-%d %H:%M:%S"))
make_approved.short_description = "Mark selected orders as approved"

def make_closed(modeladmin,request,queryset):
    queryset.update(order_status="F",shopsync="S",printsync="S")
    for order in queryset:
        shop.endFullfillment(order.order_id)
make_closed.short_description = "Close selected orders"

def make_print(modeladmin,request,queryset):
    syncer.printorders(queryset)
make_print.short_description = "Print selected orders"

class OrderAdmin(admin.ModelAdmin):
    search_fields = ["shipping_name","order_id"]
    readonly_fields = ["order_id","shipping_id","shopsync","printsync","order_date","touch_date","shipping_date","approval_date"]
    fieldsets = (
        (None, {
            "fields":("order_id","shipping_id"),
        }),
        ("Timestamps", {
            "fields":("order_date","shipping_date","approval_date"),
        }),
        ("Address", {
            "classes":("collapse",),
            "fields":("shipping_name","shipping_street","shipping_number","shipping_zipcode","shipping_city","shipping_country")
        }),
    )
    inlines = [ PuzzleInline ]
    list_display = ["order_id","shipping_name","order_status","approval"]
    ordering = ["order_date","shipping_name"]
    list_filter = ["order_status","shipping_status","shopsync","printsync","approval"]
    actions = [make_approved,make_closed,make_print]

admin.site.register(models.Order,OrderAdmin)
admin.site.register(models.Puzzle,PuzzleAdmin)
