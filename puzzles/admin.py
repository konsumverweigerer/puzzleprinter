import models
from django.contrib import admin
from django.contrib.admin.options import StackedInline, TabularInline
import datetime,time

class ImageInline(TabularInline):
    model = models.Image
    extra = 0

class PuzzleInline(TabularInline):
    model = models.Puzzle
    fieldsets = (
        (None, {
            "fields":("puzzle_type","puzzle_template","puzzle_orientation","puzzle_color","puzzle_title","puzzle_text"),
            "classes":("collapse",),
        }),
        ("Status", {
            "fields":("printing_status",),
        }),
    )

class PuzzleAdmin(admin.ModelAdmin):
    model = models.Puzzle
    fieldsets = (
        (None, {
            "fields":("puzzle_type","puzzle_template","puzzle_orientation","puzzle_color","puzzle_title","puzzle_text"),
            "classes":("collapse",),
        }),
        ("Status", {
            "fields":("printing_status",),
        }),
    )
    inlines = [ ImageInline ]
    extra = 1


def make_approved(modeladmin, request, queryset):
    queryset.update(approval="A")
    queryset.update(approval_date=time.strftime("%Y-%m-%d %H:%M:%S"))
make_approved.short_description = "Mark selected orders as approved"

class OrderAdmin(admin.ModelAdmin):
    search_fields = []
    readonly_fields = ["order_id","shipping_id","shopsync","printsync","order_date","touch_date","shipping_date","approval_date"]
    prepopulated_fields = {}
    fieldsets = (
        (None, {
            "fields":("order_id","shipping_id"),
        }),
        ("Address", {
            "classes":("collapse",),
            "fields":("shipping_name","shipping_street","shipping_number","shipping_zipcode","shipping_city","shipping_country")
        }),
        ("Timestamps", {
            "fields":("order_date","shipping_date","approval_date"),
        }),
    )
    inlines = [ PuzzleInline ]
    list_display = ["order_id","shipping_name","order_status","approval"]
    ordering = ["order_date"]
    actions = [make_approved]

admin.site.register(models.Order,OrderAdmin)
admin.site.register(models.Puzzle,PuzzleAdmin)
