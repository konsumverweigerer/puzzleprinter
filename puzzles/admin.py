import models
from django.contrib import admin

class ImageInline(admin.TabularInLine):
    model = models.Image
    extra = 0

class PuzzleInline(admin.TabularInLine):
    model = models.Puzzle
    fieldsets = (
        (None, {
            "fields":("puzzle_type","puzzle_template","puzzle_orientation","puzzle_color","puzzle_title","puzzle_text"),
            "classes":("collapse",),
        }),
        ("Status", {
            "fields":("printing_status"),
        }),
    )
    inlines = [ ImageInline ]
    extra = 1

def make_approved(modeladmin, request, queryset):
    queryset.update(status="A")
make_approved.short_description = "Mark selected orders as approved"

class OrderAdmin(admin.ModelAdmin):
    search_fields = []
    readonly_fields = ["order_id","shipping_id","shopsync","printsync","order_date","touch_date"]
    prepopulated_fields = {}
    fieldsets = (
        (None, {
            "fields":("order_id","shipping_id"),
        }),
        ("Address", {
            "classes":("collapse",),
            "fields":("shipping_name","shipping_street","shipping_number","shipping_zipcode","shipping_city","shipping_country")
        }),
    )
    inlines = [ PuzzleInline ]
    list_display = ["order_id","shipping_name","order_status","approval"]
    ordering = ["oder_date"]
    actions = [make_approved]

admin.site.register(models.Order,OrderAdmin)
