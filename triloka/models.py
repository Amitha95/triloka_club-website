from django.db import models
import cloudinary
import cloudinary.models

class Gallery(models.Model):
    title = models.CharField(max_length=255)
    image = cloudinary.models.CloudinaryField('image')
    date = models.DateField() # Auto add date when created

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d')}"

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = cloudinary.models.CloudinaryField('image')  # Use Cloudinary instead of local storage
    date = models.DateField()

    def __str__(self):
        return self.title


    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d')}"
