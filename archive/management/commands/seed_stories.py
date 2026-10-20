from datetime import timedelta
from urllib.parse import quote

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from archive.models import Article, Category, Civilization, SourceReference
from archive.stories_data import CATS, CIVS, STORIES

EV = {"v": "verified", "h": "hypothesis", "d": "disputed", "s": "speculation"}
FEATURED = {"The Great Pyramid: What Archaeology Actually Tells Us",
            "The Antikythera Mechanism: An Ancient Mechanical Marvel",
            "The Voynich Manuscript: A Book We Still Cannot Fully Read",
            "The Disappearance of the Roanoke Colony",
            "The Nazca Lines: Ancient Art Across the Desert",
            "Göbekli Tepe: A Monument That Changed Our Understanding of Prehistory"}
OLD_DEMO = ["great-pyramid", "antikythera-mechanism", "voynich-manuscript", "roanoke-colony",
            "nazca-lines", "gobekli-tepe"]


class Command(BaseCommand):
    help = "Create or update the editorial story set. Safe to run repeatedly."

    @transaction.atomic
    def handle(self, *a, **k):
        Article.objects.filter(slug__in=OLD_DEMO).delete()          # remove old placeholder demos
        civs = {c: Civilization.objects.get_or_create(name=n)[0] for c, n in CIVS.items()}
        cats = [Category.objects.get_or_create(name=n)[0] for n in CATS]
        now = timezone.now()
        made, by_civ = [], {}
        for i, (title, wiki, civ, cat, period, loc, ev, summ, known, unk, why) in enumerate(STORIES):
            body = (f"{summ}\n\nWHAT IS KNOWN\n\n{known}\n\nWHAT REMAINS UNCERTAIN\n\n{unk}\n\n"
                    f"WHY IT MATTERS\n\n{why}")
            art, _ = Article.objects.update_or_create(slug=slugify(title)[:200], defaults=dict(
                title=title, summary=summ[:300], body=body, category=cats[cat], civilization=civs[civ],
                location=loc, evidence=EV[ev], is_premium=False, is_featured=title in FEATURED,
                status="published", published_at=now - timedelta(hours=i),
                reading_minutes=max(2, round(len(body.split()) / 200)),
                seo_description=summ[:160]))
            url = "https://en.wikipedia.org/wiki/" + quote(wiki, safe="_(),'")
            art.sources.all().delete()
            SourceReference.objects.create(article=art, title=f"{wiki.replace('_', ' ')} (encyclopedia article)",
                                           publisher="Wikipedia", url=url)
            made.append(art)
            by_civ.setdefault(civ, []).append(art)
        for group in by_civ.values():          # related stories: next 3 in the same civilization
            for n, art in enumerate(group):
                art.related.set([g for g in (group[(n + j) % len(group)] for j in (1, 2, 3)) if g != art])
        self.stdout.write(self.style.SUCCESS(f"{len(made)} stories ready."))
