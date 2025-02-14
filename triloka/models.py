from django.db import models

class Gallery(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gallery/')
    date = models.DateField()  # Manually add a date instead of auto timestamp

    def __str__(self):
        return f"{self.title} ({self.date})"

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='events/')
    date = models.DateField()

    def __str__(self):
        return self.title
