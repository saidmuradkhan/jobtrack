from django.contrib import admin

from .models import InboundEmail, Inbox


@admin.register(Inbox)
class InboxAdmin(admin.ModelAdmin):
    list_display = ["user", "key", "created_at"]
    search_fields = ["user__username"]


@admin.register(InboundEmail)
class InboundEmailAdmin(admin.ModelAdmin):
    list_display = ["received_at", "user", "company", "status", "outcome"]
    list_filter = ["outcome", "status"]
    search_fields = ["company", "position", "subject", "user__username"]
    raw_id_fields = ["application"]
