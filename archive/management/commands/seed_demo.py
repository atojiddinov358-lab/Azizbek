from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from archive.models import Article, Category, Civilization, HistoricalPeriod

CIVS = ["Ancient Egypt", "Mesopotamia", "Ancient Greece", "Roman Empire", "The Maya",
        "Indus Valley", "Ancient China", "Medieval World", "Lost Cities"]
# Short, conservative summaries. Full researched articles with checked sources come in Stage 5.
DEMO = [
    ("The Great Pyramid: What Archaeology Actually Tells Us", "great-pyramid", "Ancient Egypt",
     "Archaeological discoveries", "Old Kingdom", "Giza, Egypt", False, "verified",
     "Built for Pharaoh Khufu in the Old Kingdom, the pyramid is well documented. How its blocks were moved and raised is still debated."),
    ("The Antikythera Mechanism: An Ancient Mechanical Marvel", "antikythera-mechanism", "Ancient Greece",
     "Ancient technology", "Hellenistic", "Antikythera, Greece", False, "verified",
     "A corroded bronze geared device recovered from a shipwreck in 1901, used to model astronomical cycles."),
    ("The Voynich Manuscript: A Book We Still Cannot Fully Read", "voynich-manuscript", "Medieval World",
     "Mysterious manuscripts", "Late Middle Ages", "Central Europe (probable)", True, "disputed",
     "An illustrated codex written in an unknown script. Its parchment has been radiocarbon dated to the early 15th century."),
    ("The Disappearance of the Roanoke Colony", "roanoke-colony", "Lost Cities",
     "Unsolved historical mysteries", "Early Modern", "North Carolina, USA", False, "hypothesis",
     "In 1590 the governor returned to an abandoned settlement. What happened to the colonists is still debated."),
    ("The Nazca Lines: Ancient Art Across the Desert", "nazca-lines", "Lost Cities",
     "Archaeological discoveries", "Pre-Columbian", "Nazca, Peru", False, "hypothesis",
     "Enormous designs etched into the desert floor. Researchers still debate why they were made."),
    ("Göbekli Tepe: A Monument That Changed Our Understanding of Prehistory", "gobekli-tepe", "Lost Cities",
     "Discoveries that changed history", "Neolithic", "Southeastern Türkiye", True, "hypothesis",
     "Monumental carved stone pillars built by people who, as far as we know, had not yet adopted farming."),
]


class Command(BaseCommand):
    help = "Development only: create civilizations and 6 short demo articles."

    def handle(self, *a, **k):
        if not settings.DEBUG:
            raise CommandError("seed_demo only runs with DJANGO_DEBUG=1.")
        for n in CIVS:
            Civilization.objects.get_or_create(name=n)
        now = timezone.now()
        for i, (t, slug, civ, cat, per, loc, prem, ev, summ) in enumerate(DEMO):
            Article.objects.update_or_create(slug=slug, defaults=dict(
                title=t, summary=summ, location=loc, is_premium=prem, evidence=ev, is_featured=True,
                body="Full researched article with verified sources arrives in Stage 5.\n\nThis is placeholder text.",
                category=Category.objects.get_or_create(name=cat)[0],
                civilization=Civilization.objects.get(name=civ),
                period=HistoricalPeriod.objects.get_or_create(name=per)[0],
                status="published", published_at=now - timedelta(days=i), reading_minutes=6))
        self.stdout.write(self.style.SUCCESS("Demo data ready."))
