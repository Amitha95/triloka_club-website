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
    registration_number = models.CharField(max_length=10, unique=True)
    dob = models.DateField()
    gaurdian_name = models.TextField()
    relation = models.TextField()
    idproof = models.TextField()
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
    date = models.DateField(null=True, blank=True)  # Allow NULL values temporarily

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d') if self.date else 'No Date'}"

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = cloudinary.models.CloudinaryField('image')  # Store event images in Cloudinary
    date = models.DateField(null=True, blank=True)  # Allow NULL values
    end_date = models.DateField(null=True, blank=True)  # Allow NULL values

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d') if self.date else 'No Date'} to {self.end_date.strftime('%Y-%m-%d') if self.end_date else 'Ongoing'}"
