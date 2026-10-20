from django.contrib import admin
from .models import Favorite, UserProfile
admin.site.register(UserProfile)
admin.site.register(Favorite)
