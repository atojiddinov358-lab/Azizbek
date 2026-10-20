from django.conf import settings
from django.db import models


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_confirmed = models.BooleanField(default=False)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    name = models.CharField(max_length=80)
    email = models.EmailField()
    subject = models.CharField(max_length=120)
    message = models.TextField(max_length=3000)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    action = models.CharField(max_length=64, db_index=True)
    target = models.CharField(max_length=128, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
