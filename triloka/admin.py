from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import Gallery, Event

# Customizing Admin Branding
admin.site.site_header = "Triloka Club Admin"
admin.site.site_title = "Triloka Admin"
admin.site.index_title = "Welcome to Triloka Dashboard"

# Registering Gallery Model
@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ("title", "date")  # Show title and date in the admin panel
    list_filter = ("date",)

# Registering Event Model
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date')
    search_fields = ('title', 'description')
    list_filter = ('date',)

# Custom Admin Dashboard
def admin_dashboard(request):
    return format_html("<h2>Welcome to Triloka Club Admin Dashboard</h2>")

# Custom admin home page template

