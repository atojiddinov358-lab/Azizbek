import urllib.request
from django.core.management.base import BaseCommand
from django.utils import timezone
from archive.models import SourceReference


class Command(BaseCommand):
    help = "Open every source link; set verified_on for links that load. Run on a machine with internet."

    def handle(self, *a, **k):
        ok = bad = 0
        for s in SourceReference.objects.exclude(url=""):
            try:
                req = urllib.request.Request(s.url, headers={"User-Agent": "HiddenArchiveLinkCheck/1.0"})
                with urllib.request.urlopen(req, timeout=15) as r:
                    good = 200 <= r.status < 300
            except Exception as e:
                good = False
                self.stdout.write(f"FAIL {s.url} ({e})")
            if good:
                s.verified_on = timezone.localdate(); s.save(update_fields=["verified_on"]); ok += 1
            else:
                s.verified_on = None; s.save(update_fields=["verified_on"]); bad += 1
        self.stdout.write(self.style.SUCCESS(f"{ok} links loaded, {bad} failed."))
