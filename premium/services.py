from django.db.models import Q
from django.utils import timezone


def has_premium(user) -> bool:
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_active and user.is_superuser:
        return True
    now = timezone.now()
    return (user.premium_accesses.filter(is_active=True, starts_at__lte=now)
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now)).exists())
