from unittest import mock
from django.core.management import call_command
from django.test import TestCase
from archive.management.commands import fetch_images as fi
from archive.models import Article


class ImageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_stories", verbosity=0)

    def test_only_commons_images_accepted(self):
        good = {"originalimage": {"source": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Giza%20pyramid.jpg"}}
        local = {"originalimage": {"source": "https://upload.wikimedia.org/wikipedia/en/a/a1/Poster.jpg"}}
        self.assertEqual(fi.commons_filename(good), "Giza pyramid.jpg")
        self.assertIsNone(fi.commons_filename(local))
        self.assertIsNone(fi.commons_filename({}))

    def test_non_free_licence_rejected_and_html_stripped(self):
        self.assertIsNone(fi.license_info({"LicenseShortName": {"value": "Fair use"}}))
        self.assertIsNone(fi.license_info({}))
        artist, lic = fi.license_info({"LicenseShortName": {"value": "CC BY-SA 4.0"},
                                       "Artist": {"value": '<a href="x">Jane &amp; Co</a>'}})
        self.assertEqual((artist, lic), ("Jane & Co", "CC BY-SA 4.0"))

    def test_command_fills_cover_credit_and_source(self):
        def fake(url):
            if "rest_v1" in url:
                return {"description": "Pyramid in Egypt",
                        "originalimage": {"source": "https://upload.wikimedia.org/wikipedia/commons/a/a1/Pyr.jpg"}}
            return {"query": {"pages": [{"imageinfo": [{"extmetadata": {
                "LicenseShortName": {"value": "CC BY 2.0"}, "Artist": {"value": "<b>Ann</b>"}}}]}]}}
        with mock.patch.object(fi, "get_json", fake), mock.patch.object(fi.time, "sleep"):
            call_command("fetch_images", verbosity=0)
        a = Article.objects.first()
        self.assertIn("Special:FilePath/Pyr.jpg", a.cover_image_url)
        self.assertEqual(a.cover_credit, "Ann · CC BY 2.0")
        self.assertIn("File:Pyr.jpg", a.cover_source_url)
        self.assertEqual(Article.objects.filter(cover_image_url="").count(), 0)
        r = self.client.get(a.get_absolute_url())
        self.assertContains(r, "Ann · CC BY 2.0")

    def test_missing_images_keep_placeholder(self):
        with mock.patch.object(fi, "get_json", lambda u: {}), mock.patch.object(fi.time, "sleep"):
            call_command("fetch_images", verbosity=0)
        self.assertEqual(Article.objects.exclude(cover_image_url="").count(), 0)
        self.assertContains(self.client.get("/archive/"), "cover-ph")
