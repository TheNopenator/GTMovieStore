from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'max_content_rating']
    list_filter = ['user', 'max_content_rating']
    search_fields = ['user__username']
    fields = ['user', 'profile_picture', 'max_content_rating']
