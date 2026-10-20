from django.contrib import admin
from .models import Article, ArticleView, Category, Civilization, HistoricalPeriod, SourceReference

for m in (Category, Civilization, HistoricalPeriod):
    admin.site.register(m, admin.ModelAdmin)


class SourceInline(admin.TabularInline):
    model = SourceReference
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "civilization", "is_premium", "evidence", "status", "published_at")
    list_filter = ("status", "is_premium", "evidence", "category", "civilization")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("related",)
    inlines = [SourceInline]
    actions = ["publish_now", "archive_selected"]

    @admin.action(description="Publish now")
    def publish_now(self, request, qs):
        from django.utils import timezone
        qs.update(status="published", published_at=timezone.now())

    @admin.action(description="Archive")
    def archive_selected(self, request, qs):
        qs.update(status="archived")


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ("article", "user", "viewed_at")
    readonly_fields = ("article", "user", "viewed_at")
    def has_add_permission(self, request): return False
