from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'location')  # Show these columns in admin
    search_fields = ('name', 'location')  # Allow searching by event name/location
