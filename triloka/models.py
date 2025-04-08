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
    willing_to_donate_blood = models.BooleanField(null=True, blank=True, default=None)  # Nullable field

    def __str__(self):
        return self.user.username

    
class UserFee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=20, choices=[
        ('January', 'January'), ('February', 'February'), ('March', 'March'),
        ('April', 'April'), ('May', 'May'), ('June', 'June'),
        ('July', 'July'), ('August', 'August'), ('September', 'September'),
        ('October', 'October'), ('November', 'November'), ('December', 'December')
    ])
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'month', 'year')

    def __str__(self):
        return f"{self.user.username} - {self.month} {self.year} - ${self.amount}"


class UserPoint(models.Model):
    CATEGORY_CHOICES = [
        ('Participation', 'Participation'),
        ('Electivemember', 'Electivemember'),
        ('Joining', 'Joining'),
        ('Willingtodonateblood', 'Willingtodonateblood'),
        ('Fees', 'Fees'),
        ('Achievement', 'Achievement'),
        ('Leadership', 'Leadership'),
        ('DonateParticipation', 'DonateParticipation'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    points = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.points} points"
    
class Gallery(models.Model):
    title = models.CharField(max_length=255)
    image = cloudinary.models.CloudinaryField('image')
    date = models.DateField(null=True, blank=True)
    subcategory = models.CharField(max_length=255, blank=True, null=True)  # Free-text input for subcategories

    def __str__(self):
        return f"{self.title} - {self.subcategory if self.subcategory else 'No Subcategory'} - {self.date.strftime('%Y-%m-%d') if self.date else 'No Date'}"

    class Meta:
        ordering = ['date']

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = cloudinary.models.CloudinaryField('image')
    date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Used for glow logic

    def __str__(self):
        return f"{self.title} - {self.date.strftime('%Y-%m-%d') if self.date else 'No Date'} to {self.end_date.strftime('%Y-%m-%d') if self.end_date else 'Ongoing'}"