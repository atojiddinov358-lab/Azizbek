from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class PremiumPlan(models.Model):
    """What a payment buys. Price and duration are shown before checkout."""
    name = models.CharField(max_length=60)
    price_usd = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    duration_days = models.PositiveIntegerField(help_text="Length of access granted by one purchase")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (${self.price_usd} / {self.duration_days} days)"


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        REFUNDED = "refunded", "Refunded"

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="payments")
    plan = models.ForeignKey(PremiumPlan, on_delete=models.PROTECT)
    provider = models.CharField(max_length=32)
    order_id = models.CharField(max_length=64, unique=True)
    provider_txn_id = models.CharField(max_length=128, null=True, blank=True)
    amount_usd = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(
            fields=["provider", "provider_txn_id"], condition=Q(provider_txn_id__isnull=False),
            name="uniq_provider_txn")]


class AccessCode(models.Model):
    class Kind(models.TextChoices):
        PROMO = "promo", "Promotional"
        REVIEWER = "reviewer", "Reviewer access"
        INVITE = "invite", "Private invitation"

    code_hash = models.CharField(max_length=64, unique=True, editable=False)
    hint = models.CharField(max_length=4, editable=False, blank=True)
    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.PROMO)
    label = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Empty = unlimited, 1 = single use")
    used_count = models.PositiveIntegerField(default=0, editable=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    grant_days = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=Q(max_uses__isnull=True) | Q(used_count__lte=models.F("max_uses")),
            name="code_used_not_over_max")]

    def __str__(self):
        return f"{self.label or self.kind} (…{self.hint})"

    def is_usable(self, now=None):
        now = now or timezone.now()
        return (self.is_active and (not self.expires_at or self.expires_at > now)
                and (self.max_uses is None or self.used_count < self.max_uses))


class PremiumAccess(models.Model):
    class Source(models.TextChoices):
        PAYMENT = "payment", "Payment"
        CODE = "code", "Access code"
        ADMIN = "admin", "Granted by admin"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="premium_accesses")
    source = models.CharField(max_length=10, choices=Source.choices)
    payment = models.OneToOneField(Payment, null=True, blank=True, on_delete=models.PROTECT, related_name="access")
    code = models.ForeignKey(AccessCode, null=True, blank=True, on_delete=models.PROTECT, related_name="accesses")
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "is_active", "expires_at"])]


class CodeRedemption(models.Model):
    code = models.ForeignKey(AccessCode, on_delete=models.CASCADE, related_name="redemptions")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    redeemed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["code", "user"], name="uniq_code_user")]
