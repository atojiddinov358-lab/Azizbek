"""Find a freely licensed Wikimedia Commons image for each story and store its credit.

Run on a computer with internet access:
    python manage.py fetch_images            (only stories without a cover)
    python manage.py fetch_images --force    (redo all)
Set WIKI_USER_AGENT in .env, e.g. "HiddenArchive/1.0 (you@example.com)" (Wikimedia asks for this).
"""
import html
import json
import os
import re
import time
import urllib.request
from urllib.parse import quote, unquote

from django.core.management.base import BaseCommand

from archive.models import Article

UA = os.getenv("WIKI_USER_AGENT", "HiddenArchive/1.0 (set WIKI_USER_AGENT in .env)")
OK_EXT = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def wiki_title(article):
    src = article.sources.exclude(url="").first()
    if not src or "/wiki/" not in src.url:
        return None
    return unquote(src.url.split("/wiki/", 1)[1])


def commons_filename(summary):
    """Return the Commons file name from a Wikipedia summary, or None if the image is not on Commons."""
    src = (summary.get("originalimage") or {}).get("source", "")
    if "/wikipedia/commons/" not in src:
        return None            # local (possibly non-free) file: never use
    name = unquote(src.rsplit("/", 1)[-1])
    return name if name.lower().endswith(OK_EXT) else None


def clean(text):
    return html.unescape(re.sub(r"<[^>]+>", "", text or "")).strip()


def license_info(meta):
    lic = clean((meta.get("LicenseShortName") or {}).get("value"))
    if not lic or "fair use" in lic.lower() or "non-free" in lic.lower():
        return None
    artist = clean((meta.get("Artist") or {}).get("value")) or "Unknown author"
    return artist[:110], lic[:40]


class Command(BaseCommand):
    help = "Attach freely licensed Wikimedia Commons cover images, with credits."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, **opts):
        qs = Article.objects.all() if opts["force"] else Article.objects.filter(cover_image_url="")
        done, missing = 0, []
        for a in qs:
            try:
                ok = self.one(a)
            except Exception as e:          # network or parsing problem: report, keep going
                self.stdout.write(f"  ! {a.title}: {e}")
                ok = False
            if ok:
                done += 1
            else:
                missing.append(a.title)
            time.sleep(0.25)               # be polite to Wikimedia
        self.stdout.write(self.style.SUCCESS(f"{done} images added."))
        if missing:
            self.stdout.write(f"No free image found for {len(missing)} stories (placeholder is used):")
            for t in missing:
                self.stdout.write(f"  - {t}")

    def one(self, a):
        title = wiki_title(a)
        if not title:
            return False
        s = get_json("https://en.wikipedia.org/api/rest_v1/page/summary/" + quote(title, safe="_(),'"))
        fname = commons_filename(s)
        if not fname:
            return False
        data = get_json("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=extmetadata"
                        "&format=json&formatversion=2&titles=" + quote("File:" + fname))
        pages = data.get("query", {}).get("pages", [])
        meta = (pages[0].get("imageinfo") or [{}])[0].get("extmetadata", {}) if pages else {}
        info = license_info(meta)
        if not info:
            return False
        artist, lic = info
        desc = s.get("description") or ""
        a.cover_image_url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + quote(fname) + "?width=900"
        a.cover_credit = f"{artist} · {lic}"
        a.cover_alt = (f"{title.replace('_', ' ')}: {desc}" if desc else title.replace("_", " "))[:200]
        a.cover_source_url = "https://commons.wikimedia.org/wiki/File:" + quote(fname)
        a.save(update_fields=["cover_image_url", "cover_credit", "cover_alt", "cover_source_url"])
        return True
