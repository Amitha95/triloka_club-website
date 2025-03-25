from django.db import models
import cloudinary
import cloudinary.models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.IntegerField()
    photo = cloudinary.models.CloudinaryField('photo')  # Store profile photo
    blood_group = models.CharField(max_length=5)
    name = models.TextField()

    def __str__(self):
        return self.user.username
    
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
