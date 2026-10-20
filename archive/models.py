from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify


class Named(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["name"]

    def save(self, *a, **k):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*a, **k)

    def __str__(self):
        return self.name


class Category(Named):
    class Meta(Named.Meta):
        verbose_name_plural = "categories"


class Civilization(Named):
    pass


class HistoricalPeriod(Named):
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=Article.Status.PUBLISHED, published_at__lte=timezone.now())


class Article(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    class Evidence(models.TextChoices):
        VERIFIED = "verified", "Verified fact"
        HYPOTHESIS = "hypothesis", "Credible hypothesis"
        DISPUTED = "disputed", "Disputed claim"
        SPECULATION = "speculation", "Unsupported speculation"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    subtitle = models.CharField(max_length=250, blank=True)
    summary = models.CharField(max_length=300, help_text="Public teaser. Never put protected content here.")
    body = models.TextField(help_text="Full article (Markdown/HTML-safe text). Served only to authorised readers.")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="articles")
    civilization = models.ForeignKey(Civilization, null=True, blank=True, on_delete=models.SET_NULL, related_name="articles")
    period = models.ForeignKey(HistoricalPeriod, null=True, blank=True, on_delete=models.SET_NULL, related_name="articles")
    location = models.CharField(max_length=120, blank=True)
    cover_image_url = models.URLField(blank=True)
    cover_credit = models.CharField(max_length=200, blank=True, help_text="Photographer / museum / licence")
    cover_alt = models.CharField(max_length=200, blank=True)
    cover_source_url = models.URLField(max_length=500, blank=True, help_text="Page where the image and its licence can be checked")
    reading_minutes = models.PositiveSmallIntegerField(default=5)
    is_premium = models.BooleanField(default=False, db_index=True)
    is_featured = models.BooleanField(default=False)
    evidence = models.CharField(max_length=16, choices=Evidence.choices, default=Evidence.VERIFIED)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    related = models.ManyToManyField("self", blank=True)
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    author = models.CharField(max_length=80, default="Editorial team")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ArticleQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at"]
        indexes = [models.Index(fields=["status", "is_premium", "-published_at"])]
        constraints = [
            models.CheckConstraint(
                condition=~Q(status="published") | Q(published_at__isnull=False),
                name="published_needs_date"),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("article", args=[self.slug])

    def can_read(self, user):
        """Single source of truth for access. Views must call this before rendering body."""
        if not self.is_premium:
            return True
        from premium.services import has_premium
        return has_premium(user)


class SourceReference(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="sources")
    title = models.CharField(max_length=250)
    publisher = models.CharField(max_length=150, blank=True, help_text="Museum, university, journal...")
    url = models.URLField(blank=True)
    verified_on = models.DateField(null=True, blank=True, help_text="Date an editor opened and checked this link")

    def __str__(self):
        return self.title


class ArticleView(models.Model):
    """Privacy-conscious: no IP or user agent stored; user optional."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="views")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    viewed_at = models.DateTimeField(auto_now_add=True, db_index=True)
