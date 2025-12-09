from django.contrib import admin
from .models import Movie, Review
class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']
    list_display = ['name', 'price', 'rating']
    fields = ['name', 'price', 'description', 'image', 'rating']
admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
