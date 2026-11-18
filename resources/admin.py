from django.contrib import admin

from .models import Item, Mobilisation, StockMovement


class MovementInline(admin.TabularInline):
    model = StockMovement
    extra = 0


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "department", "unit_price", "is_active")
    list_filter = ("category", "department", "is_active")
    search_fields = ("name",)
    inlines = [MovementInline]


@admin.register(Mobilisation)
class MobilisationAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "source", "amount", "status", "department", "date")
    list_filter = ("status", "kind", "department")
