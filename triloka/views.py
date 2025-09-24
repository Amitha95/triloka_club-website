import time
from django.http import HttpResponse, JsonResponse
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.models import User
from .models import UserProfile, UserFee, UserPoint, WeeklyTask
from .models import  Gallery, Event
from datetime import date
from django.utils.timezone import now
import re
from datetime import datetime
from django.contrib import messages
from django.db.models import Sum
import matplotlib.pyplot as plt
import io
import urllib
import base64
from django.utils import timezone
from django.db.models import Count
from decimal import Decimal 
from django.core.paginator import Paginator
from django.core.files.base import ContentFile

import cloudinary.uploader
import requests
from io import BytesIO
from PIL import Image, ImageEnhance

from django.db.models.functions import Lower

def maintenance(request):
    return render(request, 'maintenance.html')

from PIL import Image, ImageEnhance
from io import BytesIO
import requests
import cloudinary.uploader


def add_watermark_from_cloudinary(user,new_photo_file):
    """
    Applies a watermark to the uploaded new photo (on user edit), uploads to Cloudinary,
    and updates the user's photo URL.
    
    :param user: User instance being edited
    :param new_photo_file: Uploaded file object (e.g., request.FILES.get('photo'))
    :return: Updated photo URL or None
    """
    if not new_photo_file:
        return None  # No new photo uploaded

    # Load the new uploaded photo
    image = Image.open(new_photo_file).convert("RGBA")

    # Load watermark from Cloudinary (or replace with a local path if needed)
    watermark_url = "https://res.cloudinary.com/dr9p29qpa/image/upload/v1743137961/watermark1_rv1fpm.png"
    response_wm = requests.get(watermark_url)
    if response_wm.status_code != 200:
        return None

    watermark = Image.open(BytesIO(response_wm.content)).convert("RGBA")

    # Resize watermark to 40% of image width
    scale_factor = 0.4
    wm_width = int(image.width * scale_factor)
    wm_height = int(watermark.height * (wm_width / watermark.width))
    watermark = watermark.resize((wm_width, wm_height))

    # Adjust transparency of watermark
    watermark = ImageEnhance.Brightness(watermark).enhance(0.7)

    # Position watermark in the center
    position = ((image.width - wm_width) // 2, (image.height - wm_height) // 2)

    # Combine original image with watermark
    transparent = Image.new("RGBA", image.size, (0, 0, 0, 0))
    transparent.paste(image, (0, 0))
    transparent.paste(watermark, position, mask=watermark)

    # Convert to JPEG and save to buffer
    output_buffer = BytesIO()
    transparent.convert("RGB").save(output_buffer, format="JPEG")
    output_buffer.seek(0)

    # Upload to Cloudinary
    result = cloudinary.uploader.upload(output_buffer, folder="watermarked/")

    # Update user photo
    user.photo = result["secure_url"]
    user.save()

    return user.photo


from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image, ImageEnhance
import requests

from PIL import Image, ImageEnhance
from io import BytesIO
import requests
import cloudinary.uploader

def add_watermark_to_uploaded_photo(photo_file, user):
    """
    Applies a watermark to a newly uploaded photo and uploads it to Cloudinary.
    
    :param photo_file: In-memory uploaded file object (e.g., request.FILES['photo'])
    :param user: The user instance to update with the new photo URL
    """
    if not photo_file:
        return None

    # Load uploaded photo into PIL
    image = Image.open(photo_file).convert("RGBA")

    # Load watermark image from Cloudinary (or use a local path if preferred)
    watermark_url = "https://res.cloudinary.com/dr9p29qpa/image/upload/v1743137961/watermark1_rv1fpm.png"
    response_wm = requests.get(watermark_url)
    if response_wm.status_code != 200:
        return None

    watermark = Image.open(BytesIO(response_wm.content)).convert("RGBA")

    # Resize watermark to 40% of image width
    scale_factor = 0.4
    wm_width = int(image.width * scale_factor)
    wm_height = int(watermark.height * (wm_width / watermark.width))
    watermark = watermark.resize((wm_width, wm_height))

    # Optional: Reduce watermark brightness
    watermark = ImageEnhance.Brightness(watermark).enhance(0.7)

    # Position watermark at center
    position = ((image.width - wm_width) // 2, (image.height - wm_height) // 2)

    # Create new image with watermark
    transparent = Image.new("RGBA", image.size, (0, 0, 0, 0))
    transparent.paste(image, (0, 0))
    transparent.paste(watermark, position, mask=watermark)

    # Save image to buffer
    output_buffer = BytesIO()
    transparent.convert("RGB").save(output_buffer, format="JPEG")
    output_buffer.seek(0)

    # Upload to Cloudinary
    result = cloudinary.uploader.upload(output_buffer, folder="watermarked/")

    # Save new Cloudinary URL to user
    user.photo = result["secure_url"]
    user.save()

    return user.photo


def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        photo = request.FILES.get("photo")
        blood_group = request.POST.get("blood_group")
        registration_number = request.POST.get("registration_number")
        idproof = request.POST.get("idproof")
        gaurdian_name = request.POST.get("gaurdian_name")
        relation = request.POST.get("relation")

        print(f"Username: {username}, Email: {email}, DOB: {dob}, Phone: {phone_number}")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "register.html")

        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
            today = datetime.today().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            user = User.objects.create_user(username=username, email=email, password=password)

            if photo:
                # ✅ Apply watermark before uploading
                watermarked_photo = add_watermark_to_uploaded_photo(photo)
                
                # ✅ Upload to Cloudinary
                cloudinary_result = cloudinary.uploader.upload(watermarked_photo, folder="watermarked/")
                photo_url = cloudinary_result["secure_url"]
            else:
                photo_url = None  # No photo uploaded

            print(f"Creating UserProfile for: {username}")

            profile = UserProfile.objects.create(
                user=user,
                name=name,
                phone_number=phone_number,
                address=address,
                gender=gender,
                dob=dob,
                age=age,
                photo=photo_url,  # Save Cloudinary URL instead of file
                blood_group=blood_group,
                registration_number=registration_number,
                idproof=idproof,
                gaurdian_name=gaurdian_name,
                relation=relation,
            )

            print("UserProfile created successfully!", profile)

            messages.success(request, "Registered successfully!")
            return render(request, "register.html")

        except Exception as e:
            print("Error creating user profile:", e)
            messages.error(request, f"Error: {e}")
            return render(request, "register.html")

    return render(request, "register.html")


def edit_user(request, user_id):
    user = get_object_or_404(UserProfile, user__id=user_id)

    if request.method == "POST":
        user.name = request.POST.get('name')
        user.phone_number = request.POST.get('phone_number')
        user.dob = request.POST.get('dob')

        # Recalculate the age based on the updated dob
        if user.dob:
            user.age = calculate_age(user.dob)

        user.gaurdian_name = request.POST.get('gaurdian_name')
        user.relation = request.POST.get('relation')
        user.idproof = request.POST.get('idproof')
        user.address = request.POST.get('address')
        user.gender = request.POST.get('gender')
        user.blood_group = request.POST.get('blood_group')

        willing_to_donate = request.POST.get('willing_to_donate_blood')
        if willing_to_donate == 'True':
            user.willing_to_donate_blood = True
        elif willing_to_donate == 'False':
            user.willing_to_donate_blood = False
        else:
            user.willing_to_donate_blood = None

        # ✅ Update related User model fields
        user.user.username = request.POST.get('username')
        user.user.email = request.POST.get('email')

        # ✅ Save the User model first
        user.user.save()

        # ✅ Handle optional profile photo upload
        if request.FILES.get("photo"):
            photo = request.FILES["photo"]

            try:
                watermarked_photo = add_watermark_to_uploaded_photo(photo)

                if watermarked_photo:
                    cloudinary_result = cloudinary.uploader.upload(
                        watermarked_photo,
                        folder="watermarked/",
                        public_id=f"user_{user_id}_{int(time.time())}",
                        overwrite=True
                    )

                    if "secure_url" in cloudinary_result:
                        user.photo = cloudinary_result["secure_url"]
                        print(f"✅ User photo updated successfully: {user.photo}")
                    else:
                        print("❌ Cloudinary upload failed")

            except Exception as e:
                print(f"❌ Error uploading to Cloudinary: {e}")

        # ✅ Save the UserProfile after all updates
        user.save()

        return redirect("user_list")

    return render(request, "edit_user.html", {"user": user})


def edit_user(request, user_id):
    user = get_object_or_404(UserProfile, user__id=user_id)  # Assuming user has a related User model
    
    if request.method == 'POST':
        # Update fields manually without using a form
        user.name = request.POST.get('name')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        user.dob = request.POST.get('dob')
        
        # Recalculate the age based on the updated dob
        if user.dob:
            user.age = calculate_age(user.dob)
        
        user.gaurdian_name = request.POST.get('gaurdian_name')
        user.relation = request.POST.get('relation')
        user.idproof = request.POST.get('idproof')
        user.address = request.POST.get('address')
        user.gender = request.POST.get('gender')
        
        # Handle file upload (for photo)
        new_photo_file = request.FILES.get('photo')
        # other user updates here

        if new_photo_file:
            add_watermark_from_cloudinary(user, new_photo_file)
        
        user.blood_group = request.POST.get('blood_group')
        
        willing_to_donate = request.POST.get('willing_to_donate_blood')
        if willing_to_donate == 'True':
            user.willing_to_donate_blood = True
        elif willing_to_donate == 'False':
            user.willing_to_donate_blood = False
        else:
    # Leave the field unchanged if None or not provided
            user.willing_to_donate_blood = None

        user.save()
        return redirect('user_list')  # Redirect to the user list page after saving

    return render(request, 'edit_user.html', {'user': user})

def base(request):
    return render(request, 'base.html')

def home(request):
    today = date.today()

    glowing_events = Event.objects.filter(
        created_at__date=today  # Added today
    ) | Event.objects.filter(
        created_at__date__lt=today,  # Added earlier
        end_date__isnull=False,
        end_date__gte=today  # Still ongoing
    ) | Event.objects.filter(
        created_at__date__lt=today,
        end_date__isnull=True  # No end date
    )
    # Get distinct categories (grouped by title)
    categories = (
        Gallery.objects.values('title')
        .annotate(num_images=Count('id'))
        .filter(num_images__gt=0)
    )

    categories_with_images = {}

    for category in categories:
        title = category['title']

        # Get the first image for this category
        first_gallery = Gallery.objects.filter(title=title).first()
        image_url = first_gallery.image.url if first_gallery else None

        # Get subcategories under this title
        subcategories = (
            Gallery.objects.filter(title=title)
            .order_by(Lower('subcategory'))
            .values_list('subcategory', flat=True)
            .distinct()
        )

        categories_with_images[title] = {
            'title': title,
            'image': image_url,
            'subcategories': list(subcategories),  # Convert to list for iteration in template
        }

    return render(request, 'home.html', {'categories': categories_with_images,'has_glowing_event': glowing_events.exists()})

# Main Gallery → Categories
from django.utils.text import slugify

def main_gallery(request):
    categories = (
        Gallery.objects.values('title')
        .annotate(num_images=Count('id'))
        .filter(num_images__gt=0)
    )

    categories_with_images = {}
    for category in categories:
        title = category['title']
        first_gallery = Gallery.objects.filter(title=title).first()
        image_url = first_gallery.image.url if first_gallery else None

        categories_with_images[title] = {
            'title': title,
            'slug': slugify(title),  # <-- add slug
            'image': image_url,
        }

    return render(request, 'main_gallery.html', {'categories': categories_with_images})


# Step 2: Show available years for a category
from django.db.models.functions import ExtractYear, Substr

def gallery_years(request, title):
    year_ranges = (
        Gallery.objects.filter(title__iexact=title)   # <-- ignore case
        .values('date__year')
        .distinct()
        .order_by('date__year')
    )

    return render(request, 'gallery_years.html', {
        'year_ranges': year_ranges,
        'title': title.upper()  # or keep as is
    })


# Step 3: Show subcategories inside a year
def gallery_subcategories(request, title, year):
    subcategories = (
        Gallery.objects.filter(title=title, date__year=year)
        .values('subcategory')
        .distinct()
        .order_by('subcategory')
    )

    return render(request, 'gallery_subcategories.html', {
        'subcategories': subcategories,
        'title': title,
        'year': year
    })


# Step 4: Show images for a subcategory & year
def gallery_images(request, title, year, subcategory):
    gallery_images = Gallery.objects.filter(
        title=title, subcategory=subcategory, date__year=year
    )

    return render(request, 'gallery_images.html', {
        'gallery_images': gallery_images,
        'year': year,
        'title': title,
        'subcategory': subcategory
    })


def gallery_pages(request, title, subcategory):
    year_ranges = (
        Gallery.objects.filter(title=title, subcategory=subcategory)
        .values('date__year')
        .distinct()
        .order_by('date__year')
    )

    return render(request, 'gallery_pages.html', {
        'year_ranges': year_ranges,
        'title': title,
        'subcategory': subcategory
    })


def about(request):
    return render(request, 'about.html')

def focus(request):
    return render(request, 'focus.html')

def gallery(request):
    return render(request, 'gallery.html')

def contact(request):
    return render(request, 'contact.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser or user.groups.filter(name="admin").exists():
                return redirect("admin_home")  # Use name if set in urls.py
            else:
                return redirect("user_home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("home")

    return render(request, "home.html")

def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def dashboard_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    username = request.user.username if request.user.is_authenticated else ""
    filtered_username = re.sub(r'[^a-zA-Z]', '', username)

    # Remove 'TV' if it appears at the end of the username
    filtered_username = re.sub(r'TV$', '', filtered_username, flags=re.IGNORECASE)  # Remove numbers
    return render(request, "dashboard.html", {"filtered_username": filtered_username, "user_profile": user_profile})

@login_required
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")

@login_required
def user_home(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    show_donation_popup = user_profile.willing_to_donate_blood is None

    # Fetch fee details (grouping by month)
    user_fees = UserFee.objects.filter(user=request.user).order_by('year', 'month')
    months = [fee.month for fee in user_fees]

    top_users = UserPoint.objects.values('user').annotate(total_points=Sum('points')).order_by('-total_points')[:10]
    # Fetch points grouped by category
    points_data = UserPoint.objects.filter(user=request.user).values('category').annotate(total_points=Sum('points'))
    categories = [entry['category'] for entry in points_data]
    points = [float(entry['total_points']) for entry in points_data]

    # Generate the pie chart using Matplotlib
    plt.figure(figsize=(6, 6))
    
    # Format labels with exact points instead of percentage
    labels = [f"{category}: {point} pts" for category, point in zip(categories, points)]
    plt.pie(points, labels=labels, colors=['red', 'blue', 'yellow', 'green', 'purple'])
    plt.title("Points Distribution")

    # Save the plot to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Convert plot to Base64 for embedding in HTML
    graph_url = urllib.parse.quote(base64.b64encode(buffer.getvalue()).decode())
    buffer.close()

    top_user_profiles = []
    for entry in top_users:
        try:
            profile = UserProfile.objects.get(user_id=entry['user'])
            top_user_profiles.append({
                'profile': profile,
                'points': float(entry['total_points']),
                'stars': min(int(entry['total_points'] // 10), 5)  # Convert points to stars (1 star per 10 points, max 5)
            })
        except UserProfile.DoesNotExist:
            continue

    return render(request, 'user_home.html', {
        'user_profile': user_profile,
        'months': months,
        'categories': categories,  # Updated from months
        'graph_url': graph_url,  # Updated points data
        'show_donation_popup': show_donation_popup,
        'top_user_profiles': top_user_profiles,
    })


def upload_gallery_image(request):
    if request.method == "POST":
        title = request.POST.get("title") or request.POST.get("new_title")
        subcategory = request.POST.get("subcategory") or request.POST.get("new_subcategory")
        image = request.FILES.get("image")
        date = request.POST.get("date")

        if title and image:
            Gallery.objects.create(
                title=title,
                subcategory=subcategory,
                image=image,
                date=date
            )
            return redirect("gallery_list")

    # Get distinct titles & subcategories for dropdowns
    titles = Gallery.objects.values_list("title", flat=True).distinct()
    subcategories = Gallery.objects.values_list("subcategory", flat=True).distinct()

    return render(request, "galleryupload.html", {
        "titles": titles,
        "subcategories": subcategories,
    })


def gallery_list(request):
    """Displays all uploaded images."""
    images = Gallery.objects.all().order_by('-date')
    return render(request, "gallery_list.html", {"images": images})

def edit_image(request, image_id):
    image = get_object_or_404(Gallery, id=image_id)

    if request.method == 'POST':
        image.title = request.POST.get('title')
        image.subcategory = request.POST.get('subcategory')
        image.date = request.POST.get('date')

        if request.FILES.get('image'):
            image.image = request.FILES['image']
        
        image.save()
        return redirect('gallery_list')

    return render(request, 'edit_image.html', {'image': image})

def delete_image(request, image_id):
    """Deletes an image from the gallery."""
    image = get_object_or_404(Gallery, id=image_id)
    image.delete()
    messages.success(request, "Image deleted successfully.")
    return redirect('gallery_list')  # Redirect back to the gallery page



def gallery_view(request, year_start, year_end):
    year_start = int(year_start)
    year_end = int(year_end)
    photos = Gallery.objects.filter(date__year__gte=year_start, date__year__lte=year_end)
    return render(request, "gallery.html", {"photos": photos, "year_start": year_start, "year_end": year_end})

def gallery_page(request):
    return render(request, 'gallery_years.html')

def gallery_all(request):
    year_range = request.GET.get("year_range", None)
    images = Gallery.objects.all()

    if year_range:
        try:
            start_year, end_year = map(int, year_range.split('-'))
            images = images.filter(date__year__gte=start_year, date__year__lte=end_year)
        except ValueError:
            return JsonResponse({"error": "Invalid year range format. Use YYYY-YYYY."}, status=400)

    image_list = [{"image": img.image.url, "title": img.title, "year": img.date.year} for img in images]
    return JsonResponse(image_list, safe=False)

from django.db.models import Q

def events_view(request):
    today = date.today()

    # Past events: events with end_date before today
    all_events = Event.objects.filter(end_date__lt=today).order_by('-date')

    # Upcoming events:
    # 1. end_date >= today
    # 2. OR date >= today
    # 3. OR both date and end_date are null (TBA)
    upcoming_events = Event.objects.filter(
        Q(end_date__gte=today) |
        Q(date__gte=today) |
        (Q(date__isnull=True) & Q(end_date__isnull=True))
    ).order_by('date')

    return render(request, "events.html", {
        'all_events': all_events,
        'upcoming_events': upcoming_events
    })

def upload_event(request):
    """Handles event uploads."""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        date = request.POST.get("date") or None
        end_date = request.POST.get("end_date") or None

        if title and description and image:
            Event.objects.create(
                title=title,
                description=description,
                image=image,
                date=date if date else None,
                end_date=end_date if end_date else None

            )
            return redirect("event_list")  # Redirect to event list page after upload

    return render(request, "upload_event.html")

def event_list(request):
    """Displays all uploaded events."""
    events = Event.objects.all().order_by('-date')
    return render(request, "event_list.html", {"events": events})

def delete_event(request, event_id):
    """Deletes an event from the database."""
    event = get_object_or_404(Event, id=event_id)  # Ensure the event exists
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('event_list')  # Redirect back to the event list page

@login_required
def user_list(request):
    users = UserProfile.objects.select_related('user').order_by('registration_number')

    # Calculate age based on DOB and total fees/points for each user
    for user in users:
        user.age = (date.today() - user.dob).days // 365  # Calculate age in years

        # Calculate total fees for the user
        
        user.total_fees = UserFee.objects.filter(user=user.user).aggregate(total_fees=Sum('amount'))['total_fees'] or 0

        # Calculate total points for the user
        user.total_points = UserPoint.objects.filter(user=user.user).aggregate(total_points=Sum('points'))['total_points'] or 0

    # Set up pagination
    paginator = Paginator(users, 7)  # Show 7 users per page
    page_number = request.GET.get('page')  # Get the current page from the URL
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    return render(request, "user_list.html", {"page_obj": page_obj})


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect("user_list")

    return redirect("user_list")


@login_required
def user_fees(request, user_id):
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    user = get_object_or_404(User, id=user_id)
    current_year = datetime.now().year

    if request.method == "POST":
        fee_id = request.POST.get("fee_id")
        month = request.POST.get("month")
        year = request.POST.get("year")
        amount = request.POST.get("amount")

        if month and year and amount:
            if fee_id:  # Edit existing fee
                fee = get_object_or_404(UserFee, id=fee_id, user=user)
                fee.month = month
                fee.year = year
                fee.amount = Decimal(amount)
                fee.save()
            else:  # Create new fee
                UserFee.objects.create(user=user, month=month, year=year, amount=Decimal(amount))

            return redirect("user_fees", user_id=user.id)

    # Fetch fees and construct fee_table
    paid_fees = UserFee.objects.filter(user=user, year=current_year)
    paid_fees_dict = {fee.month: fee.amount for fee in paid_fees}
    total_fees_paid = sum(paid_fees_dict.values())
    current_month = datetime.now().month
    fee_per_month = Decimal("10.00")
    expected_payment = sum(fee_per_month for _ in range(1, current_month + 1))

    fee_table = []
    for i, month in enumerate(months, start=1):
        fee_obj = next((f for f in paid_fees if f.month == month), None)
        amount = fee_obj.amount if fee_obj else 0
        status = "✅ Paid" if amount > 0 else "❌ Pending"

        fee_table.append({
            "id": fee_obj.id if fee_obj else '',
            "month": month,
            "year": current_year,
            "amount": f"{amount:.2f}",
            "status": status
        })

    pending_fees = expected_payment - total_fees_paid

    return render(request, 'user_fees.html', {
        "user": user,
        "months": months,
        "fee_table": fee_table,
        "total_fees_paid": f"₹{total_fees_paid:.2f}",
        "pending_fees": f"₹{pending_fees:.2f}",
    })


@login_required

def user_fee_details(request):
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    user = request.user  # Get the logged-in user
    current_year = datetime.now().year

    if request.method == "POST":
        month = request.POST.get("month")
        year = request.POST.get("year")
        amount = request.POST.get("amount")

        if month and year and amount:
            UserFee.objects.create(user=user, month=month, year=year, amount=Decimal(amount))
            return redirect("user_fees")  # Redirect to refresh the page

    # Fetch all fees paid by the user for the current year
    paid_fees = UserFee.objects.filter(user=user, year=current_year).values_list('month', 'amount')
    paid_fees_dict = {fee[0]: fee[1] for fee in paid_fees}
    total_fees_paid = sum(paid_fees_dict.values())

    current_month = datetime.now().month
    fee_per_month = Decimal("10.00")
    expected_payment = sum(fee_per_month for i in range(1, current_month + 1))

    # Build fee table to show to the user
    fee_table = []
    for i, month in enumerate(months, start=1):
        amount = paid_fees_dict.get(month, 0)
        status = "✅ Paid" if amount > 0 else "❌ Pending"

        fee_table.append({
            "month": month,
            "year": current_year,
            "amount": f"₹{amount:.2f}",
            "status": status
        })

    pending_fees = expected_payment - total_fees_paid

    return render(request, 'user_fee_details.html', {
        "user": user,
        "months": months,  # Pass months to template
        "fee_table": fee_table,
        "total_fees_paid": f"₹{total_fees_paid:.2f}",
        "pending_fees": f"₹{pending_fees:.2f}",
    })

from decimal import Decimal,InvalidOperation

@login_required
def user_points(request, user_id):
    user = get_object_or_404(User, id=user_id)
    points = UserPoint.objects.filter(user=user)

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

    if request.method == "POST":
        edit_id = request.POST.get("edit_id")
        category = request.POST.get("category")
        points_value = request.POST.get("points")

        try:
            points_value = Decimal(points_value)
        except (ValueError, InvalidOperation):
            messages.error(request, "Invalid points value!")
            return redirect("user_points", user_id=user.id)

        if edit_id:
            # Editing an existing entry
            point_entry = get_object_or_404(UserPoint, id=edit_id, user=user)
            point_entry.category = category
            point_entry.points = points_value
            point_entry.save()
            messages.success(request, "Points updated successfully!")
        else:
            # Adding new or updating existing category
            point_entry, created = UserPoint.objects.get_or_create(user=user, category=category)
            point_entry.points += points_value
            point_entry.save()
            messages.success(request, "Points added successfully!")

        return redirect("user_points", user_id=user.id)

    # Calculate total points
    total_points = sum(point.points for point in points)

    return render(request, "user_points.html", {
        "user": user,
        "points": points,
        "total_points": total_points,
        "category_choices": CATEGORY_CHOICES,
    })

@login_required
def update_donation_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        willing_to_donate_blood = data.get("willing_to_donate_blood")

        user_profile = get_object_or_404(UserProfile, user=request.user)
        user_profile.willing_to_donate_blood = willing_to_donate_blood
        user_profile.save()

        return JsonResponse({"message": "Donation preference updated successfully"})
    
    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def point_redemption_rules(request):
    user_points = UserPoint.objects.filter(user=request.user)
    total_points = sum(point.points for point in user_points)
    
    # Redemption Calculation
    redemption_rate = 10  # ₹10 for 100 points
    redeemable_amount = (total_points // 100) * redemption_rate
    can_redeem = total_points >= 100  # Eligible if points >= 100

    context = {
        'total_points': total_points,
        'redeemable_amount': redeemable_amount,
        'can_redeem': can_redeem
    }
    return render(request, 'point_redemption.html', context)

@login_required
def redeem_points(request):
    user_points = UserPoint.objects.filter(user=request.user)
    total_points = sum(point.points for point in user_points)

    if total_points >= 100:
        # Deduct redeemed points
        redeemable_points = (total_points // 100) * 100
        remaining_points = total_points - redeemable_points
        UserPoint.objects.filter(user=request.user).delete()  # Reset points
        
        # Add remaining points back
        if remaining_points > 0:
            UserPoint.objects.create(user=request.user, category="Remaining", points=remaining_points)

    return redirect('point_redemption_rules')

@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name="admin").exists())
def admin_home(request):
    today = now().date()  # Get today's date
    new_registrations = UserProfile.objects.filter(user__date_joined__date=today).count()  # Count today's registrations

    context = {
        'title': 'Admin Dashboard',
        'user_count': UserProfile.objects.count(),  # Total registered users
        'new_registrations': new_registrations,  # New users today
    }
    return render(request, 'admin_home.html', context)

ALL_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

def blood_group_list(request):
    selected_group = request.GET.get('blood_group', 'All')

    if selected_group == "All":
        profiles = UserProfile.objects.all().order_by('name')  # Sort by name ASC
    else:
        profiles = UserProfile.objects.filter(blood_group=selected_group).order_by('name')

    return render(request, 'blood_group_list.html', {
        'profiles': profiles,
        'blood_groups': ALL_BLOOD_GROUPS,
        'selected_group': selected_group,
    })

ALL_BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]


def donor_list(request):
    selected_group = request.GET.get('blood_group', 'All')

    # Filter users willing to donate blood
    if selected_group == "All":
        profiles = UserProfile.objects.filter(willing_to_donate_blood=True).order_by('registration_number')
    else:
        profiles = UserProfile.objects.filter(blood_group=selected_group, willing_to_donate_blood=True).order_by('registration_number')

    return render(request, 'donor_list.html', {
        'profiles': profiles,
        'blood_groups': ALL_BLOOD_GROUPS,
        'selected_group': selected_group,
    })


def calculate_age(dob):
    """Calculate age from DOB"""
    today = timezone.now().date()
    dob = datetime.strptime(dob, "%Y-%m-%d").date()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

@login_required
def user_profile_view(request):
    # Fetch the user's profile
    user_profile = get_object_or_404(UserProfile, user=request.user)

    return render(request, 'user_profile.html', {
        'user_profile': user_profile,
    })


# views.py
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.http import JsonResponse
import json
from django.conf import settings

@csrf_exempt  # Disable CSRF protection for this view
def send_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            message = data.get('message')

            # Prepare the email message
            subject = f"Contact Form Submission from {name}"
            body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = ['trilokavellimon1@gmail.com']

            # Send the email
            send_mail(subject, body, from_email, recipient_list)

            return JsonResponse({"status": "success", "message": "Email sent successfully!"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

def elective_members(request):
    # Example static data (you can load from DB instead)
    

    return render(request, "elective_members.html")

def add_weekly_task(request):
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]

    if request.method == "POST":
        month = request.POST.get("month")
        week = request.POST.get("week")
        user_id = request.POST.get("user")
        new_mark = int(request.POST.get("new_mark") or 0)
        old_mark = int(request.POST.get("old_mark") or 0)
        total = int(request.POST.get("total") or 0)
        
        user = UserProfile.objects.get(id=user_id)

        WeeklyTask.objects.create(
            user=user,
            month=month,
            week=week,
            total=total
        )
        return redirect("add_weekly_task")

    users = UserProfile.objects.all().order_by("name")
    tasks = WeeklyTask.objects.select_related("user").all()

    return render(request, "add_weekly_task.html", {
        "months": months,
        "users": users,
        "old_mark": 0
    })