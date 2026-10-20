from django.conf import settings
from django.shortcuts import render
from .models import PremiumPlan


def info(request):
    plan = PremiumPlan.objects.filter(is_active=True).first()
    return render(request, "premium/info.html", {
        "price": plan.price_usd if plan else settings.PREMIUM_PRICE_USD,
        "days": plan.duration_days if plan else settings.PREMIUM_DURATION_DAYS})
