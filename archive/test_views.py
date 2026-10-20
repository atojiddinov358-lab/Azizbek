from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from archive.models import Article, Category

SECRET = "UNIQUE-PROTECTED-BODY-TEXT"

def mk(slug, premium):
    c, _ = Category.objects.get_or_create(name="Cat")
    return Article.objects.create(title=slug, slug=slug, summary="public teaser", body=SECRET, category=c,
        is_premium=premium, is_featured=True, status="published", published_at=timezone.now() - timedelta(hours=1))

class ViewTests(TestCase):
    def test_home_and_archive_render(self):
        mk("free", False)
        self.assertContains(self.client.get(reverse("home")), "THE PAST IS NOT AS SIMPLE")
        self.assertContains(self.client.get(reverse("archive") + "?q=free"), "free")

    def test_empty_home_is_graceful(self):
        self.assertContains(self.client.get(reverse("home")), "No stories published yet")

    def test_free_article_shows_body(self):
        mk("free", False)
        self.assertContains(self.client.get(reverse("article", args=["free"])), SECRET)

    def test_premium_body_not_in_html_for_visitors(self):
        mk("prem", True)
        r = self.client.get(reverse("article", args=["prem"]))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, SECRET)
        self.assertContains(r, "Premium Vault")

    def test_draft_is_404(self):
        a = mk("d", False); a.status = "draft"; a.save()
        self.assertEqual(self.client.get(reverse("article", args=["d"])).status_code, 404)

    def test_pages(self):
        for n in ("premium", "login", "surprise"):
            self.assertIn(self.client.get(reverse(n)).status_code, (200, 302))
