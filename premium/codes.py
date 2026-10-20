import hashlib, hmac
from django.conf import settings

def normalize_code(raw):
    return "".join((raw or "").split()).upper()

def hash_code(raw):
    return hmac.new(settings.ACCESS_CODE_PEPPER.encode(), normalize_code(raw).encode(), hashlib.sha256).hexdigest()
