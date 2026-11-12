from django.contrib import admin

from .models import Contact, Interaction, Organisation


class InteractionInline(admin.TabularInline):
    model = Interaction
    extra = 0


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "location")
    list_filter = ("kind",)
    search_fields = ("name",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "organisation", "category", "email", "phone")
    list_filter = ("category",)
    search_fields = ("full_name", "organisation__name", "expertise")
    inlines = [InteractionInline]
