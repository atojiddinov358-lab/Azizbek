import random

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Article, ArticleView, Civilization


def home(request):
    qs = Article.objects.published().select_related("category", "civilization", "period")
    featured = list(qs.filter(is_featured=True)[:6])
    civs = Civilization.objects.annotate(
        n=Count("articles", filter=Q(articles__status="published"))).order_by("name")
    return render(request, "home.html", {
        "featured": featured, "civs": civs, "total": qs.count(),
        "premium_total": qs.filter(is_premium=True).count(),
        "price": settings.PREMIUM_PRICE_USD, "days": settings.PREMIUM_DURATION_DAYS,
    })


def archive_list(request):
    qs = Article.objects.published().select_related("category", "civilization", "period")
    q = request.GET.get("q", "").strip()[:100]
    civ = request.GET.get("civ", "")
    tier = request.GET.get("tier", "")
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(summary__icontains=q) | Q(body__icontains=q))
    if civ:
        qs = qs.filter(civilization__slug=civ)
    if tier == "free":
        qs = qs.filter(is_premium=False)
    elif tier == "premium":
        qs = qs.filter(is_premium=True)
    page = Paginator(qs, 12).get_page(request.GET.get("page"))
    return render(request, "archive/list.html", {
        "page": page, "q": q, "civ": civ, "tier": tier, "civs": Civilization.objects.all()})


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.published().select_related("category", "civilization", "period"), slug=slug)
    allowed = article.can_read(request.user)
    if allowed:
        ArticleView.objects.create(
            article=article, user=request.user if request.user.is_authenticated else None)
    return render(request, "archive/detail.html", {
        "a": article, "allowed": allowed, "sources": article.sources.all() if allowed else [],
        "related": article.related.published()[:3],
        "price": settings.PREMIUM_PRICE_USD, "days": settings.PREMIUM_DURATION_DAYS,
    })


def surprise(request):
    ids = [a.pk for a in Article.objects.published().only("pk", "is_premium")
           if a.can_read(request.user)]
    if not ids:
        return redirect("archive")
    return redirect(Article.objects.get(pk=random.choice(ids)).get_absolute_url())
