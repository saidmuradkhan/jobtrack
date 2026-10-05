from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["position", "company", "status", "applied_on", "salary", "currency", "user"]
    list_filter = ["status", "currency"]
    search_fields = ["company", "position", "notes"]
    date_hierarchy = "applied_on"
