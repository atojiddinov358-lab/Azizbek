from datetime import timedelta
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from accounts.models import Favorite
from premium.models import AccessCode, PremiumAccess
from premium.services import has_premium
from .models import Article, Category

User = get_user_model()


def make_article(slug, premium=False, status="published"):
    c, _ = Category.objects.get_or_create(name="Ancient Egypt")
    return Article.objects.create(
        title=slug, slug=slug, summary="s", body="secret body", category=c, is_premium=premium,
        status=status, published_at=timezone.now() - timedelta(days=1))


class AccessTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("a", password="x12345678")

    def test_profile_created(self):
        self.assertTrue(hasattr(self.user, "profile"))

    def test_free_article_readable_by_anyone(self):
        from django.contrib.auth.models import AnonymousUser
        a = make_article("free")
        self.assertTrue(a.can_read(AnonymousUser()))

    def test_premium_blocked_without_access(self):
        a = make_article("prem", premium=True)
        self.assertFalse(a.can_read(self.user))

    def test_premium_allowed_with_active_access_and_blocked_when_expired(self):
        a = make_article("prem", premium=True)
        pa = PremiumAccess.objects.create(user=self.user, source="admin",
                                          expires_at=timezone.now() + timedelta(days=5))
        self.assertTrue(a.can_read(self.user))
        pa.expires_at = timezone.now() - timedelta(seconds=1)
        pa.save()
        self.assertFalse(has_premium(self.user))

    def test_users_cannot_make_themselves_premium_by_flag(self):
        self.user.is_staff = True
        self.user.save()
        self.assertFalse(has_premium(self.user))

    def test_published_requires_date(self):
        c = Category.objects.create(name="X")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Article.objects.create(title="t", slug="t", summary="s", body="b", category=c, status="published")

    def test_only_published_in_queryset(self):
        make_article("pub")
        make_article("draft", status="draft")
        self.assertEqual(Article.objects.published().count(), 1)

    def test_duplicate_favorite_rejected(self):
        a = make_article("fav")
        Favorite.objects.create(user=self.user, article=a)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Favorite.objects.create(user=self.user, article=a)

    def test_code_usability(self):
        c = AccessCode.objects.create(code_hash="h", max_uses=1)
        self.assertTrue(c.is_usable())
        c.used_count = 1
        self.assertFalse(c.is_usable())
