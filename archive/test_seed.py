from django.core.management import call_command
from django.test import TestCase
from archive.models import Article, Category, Civilization


class SeedTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_stories", verbosity=0)

    def test_at_least_100_unique_published_stories(self):
        self.assertGreaterEqual(Article.objects.published().count(), 100)

    def test_every_story_is_structured_and_sourced(self):
        for a in Article.objects.all():
            self.assertIn("WHAT REMAINS UNCERTAIN", a.body)
            self.assertEqual(a.sources.count(), 1)
            self.assertTrue(a.sources.first().url.startswith("https://en.wikipedia.org/wiki/"))
            self.assertIsNone(a.sources.first().verified_on)   # never claim a check that hasn't happened

    def test_all_twelve_categories_used(self):
        self.assertEqual(Category.objects.filter(articles__isnull=False).distinct().count(), 12)

    def test_idempotent(self):
        n = Article.objects.count()
        call_command("seed_stories", verbosity=0)
        self.assertEqual(Article.objects.count(), n)

    def test_home_shows_six_featured_and_real_count(self):
        r = self.client.get("/")
        self.assertEqual(r.content.decode().count('class="card reveal"'), 6)
        self.assertContains(r, f"<strong>{Article.objects.published().count()}</strong>")
        self.assertTrue(Civilization.objects.count() >= 9)
