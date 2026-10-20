# The Hidden Archive (Django)

Status: Stage 5 (first content pass) done: 105 stories.

## Architecture
- accounts: UserProfile, Favorite
- archive: Category, Civilization, HistoricalPeriod, Article, SourceReference, ArticleView
- premium: PremiumPlan, Payment, AccessCode, CodeRedemption, PremiumAccess, has_premium()
- core: NewsletterSubscriber, ContactMessage, AuditLog
- Payments, access-code views and favorites UI will live inside these apps (fewer moving parts than 8 apps).
- Access rule: Article.can_read(user) is the single server-side check. Views must call it before sending `body`.

## Run on Windows (PowerShell)
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    copy .env.example .env
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py test
    python manage.py runserver
Admin: http://127.0.0.1:8000/admin/

## Content policy
Articles need real, checked sources (SourceReference.verified_on). No invented citations.

## Dev demo content
    python manage.py seed_stories    (105 short sourced stories; safe to re-run)
    python manage.py check_sources   (run on your PC: opens each link and marks it verified)

## Images
    python manage.py fetch_images     (needs internet; set WIKI_USER_AGENT in .env first)
Uses only freely licensed Wikimedia Commons files, stores the author and licence, and shows a credit with a link on every article.
Stories with no free image keep a patterned placeholder. You can also paste any Commons image URL in the admin.
