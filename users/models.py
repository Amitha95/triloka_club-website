from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    registration_number = models.CharField(max_length=20, unique=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    joined_date = models.DateField()  # Removed auto_now_add=True to allow manual entry

    def __str__(self):
        return self.user.username
