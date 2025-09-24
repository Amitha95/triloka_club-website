import os
import django

# Setup Django environment if needed
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")  # replace with your settings module
django.setup()

from django.db import transaction
from triloka.models import Gallery

# Get all "Activities" entries
activities_qs = Gallery.objects.filter(title__iexact="Activities")

if not activities_qs.exists():
    print("No Activities entries found!")
else:
    merged_images = []
    for g in activities_qs:
        merged_images.append({
            "subcategory": (g.subcategory or "").strip(),
            "image_url": g.image.url if g.image else None,
            "date": g.date
        })

    with transaction.atomic():
        main = activities_qs.first()          # Keep first record
        main.subcategory = "All"              # Mark as multiple subcategories
        main.save()

        print("All images from duplicates:")
        for img in merged_images:
            print(f"Subcategory: {img['subcategory']} | URL: {img['image_url']} | Date: {img['date']}")

        for dup in activities_qs.exclude(id=main.id):
            dup.delete()

    print("All Activities merged into one entry!")
