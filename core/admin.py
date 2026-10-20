from django.contrib import admin
from .models import AuditLog, ContactMessage, NewsletterSubscriber

admin.site.register(NewsletterSubscriber)

@admin.register(ContactMessage)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("subject", "email", "is_resolved", "created_at")
    list_filter = ("is_resolved",)

@admin.register(AuditLog)
class AuditAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "actor", "target")
    readonly_fields = [f.name for f in AuditLog._meta.fields]
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
