from django.http import HttpResponse, JsonResponse
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile, UserFee, UserPoint
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

def base(request):
    return render(request, 'base.html')

def home(request):
    # Group by title (used as category) and count the number of images in each group
    categories = Gallery.objects.values('title').annotate(num_images=Count('id')).filter(num_images__gt=0)

    categories_with_images = []

    for category in categories:
        # Get the first gallery image for each category (title)
        first_gallery = Gallery.objects.filter(title=category['title']).first()
        image_url = first_gallery.image.url if first_gallery else None
        categories_with_images.append({
            'title': category['title'],
            'image': image_url
        })

    return render(request, 'home.html', {'categories': categories_with_images})
def gallery_subcategories(request, title):
    subcategories = Gallery.objects.filter(title=title).values('subcategory').distinct()
    return render(request, 'gallery_subcategories.html', {'subcategories': subcategories, 'title': title})

def gallery_pages(request, title, subcategory):
    gallery_images = Gallery.objects.filter(title=title, subcategory=subcategory)
    year_ranges = gallery_images.values('date__year').distinct().order_by('date__year')
    return render(request, 'gallery_pages.html', {'year_ranges': year_ranges, 'title': title, 'subcategory': subcategory})
def gallery_images(request, title, subcategory, year):
    gallery_images = Gallery.objects.filter(title=title, subcategory=subcategory, date__year=year)
    return render(request, 'gallery_images.html', {'gallery_images': gallery_images, 'year': year, 'title': title, 'subcategory': subcategory})
def about(request):
    return render(request, 'about.html')

def events(request):
    return render(request, 'events.html')

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
                return redirect("admin_home")
            else:
                return redirect("user_home")
        else:
            messages.error(request, "Invalid username or password")  # Use Django messages for error popup
            return redirect("home")  # Redirect to home page so message can be shown

    return render(request, "home.html")

def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def dashboard_view(request):
    username = request.user.username if request.user.is_authenticated else ""
    filtered_username = re.sub(r'[^a-zA-Z]', '', username)

    # Remove 'TV' if it appears at the end of the username
    filtered_username = re.sub(r'TV$', '', filtered_username, flags=re.IGNORECASE)  # Remove numbers
    return render(request, "dashboard.html", {"filtered_username": filtered_username})

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

    # Fetch points grouped by category
    points_data = UserPoint.objects.filter(user=request.user).values('category').annotate(total_points=Sum('points'))
    categories = [entry['category'] for entry in points_data]
    points = [float(entry['total_points']) for entry in points_data]

    # Generate the pie chart using Matplotlib
    plt.figure(figsize=(4, 4))
    
    # Format labels with exact points instead of percentage
    labels = [f"{category}: {point} pts" for category, point in zip(categories, points)]
    plt.pie(points, labels=labels, colors=['red', 'blue', 'yellow', 'green', 'purple'])
    plt.title("Points Distribution by Category")

    # Save the plot to a buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    # Convert plot to Base64 for embedding in HTML
    graph_url = urllib.parse.quote(base64.b64encode(buffer.getvalue()).decode())
    buffer.close()

    return render(request, 'user_home.html', {
        'user_profile': user_profile,
        'months': months,
        'categories': categories,  # Updated from months
        'graph_url': graph_url,  # Updated points data
        'show_donation_popup': show_donation_popup
    })

def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")  # Get date of birth
        photo = request.FILES.get("photo")
        blood_group = request.POST.get("blood_group")
        registration_number = request.POST.get("registration_number")
        idproof = request.POST.get("idproof")
        gaurdian_name = request.POST.get("gaurdian_name")
        relation = request.POST.get("relation")

        # Debugging print statements
        print(f"Username: {username}, Email: {email}, DOB: {dob}, Phone: {phone_number}")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
            return render(request, "register.html")

        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
            today = datetime.today().date()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Debugging print statement before saving UserProfile
            print(f"Creating UserProfile for: {username}")

            profile = UserProfile.objects.create(
                user=user,
                name=name,
                phone_number=phone_number,
                address=address,
                gender=gender,
                dob=dob,
                age=age,
                photo=photo,
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
            print("Error creating user profile:", e)  # Debugging
            messages.error(request, f"Error: {e}")
            return render(request, "register.html")

    return render(request, "register.html")


def upload_gallery_image(request):
    
    if request.method == "POST":
        title = request.POST.get("title")
        subcategory = request.POST.get("subcategory")
        image = request.FILES.get("image")
        date=request.POST.get("date")
        if title and image:
            Gallery.objects.create(title=title,subcategory=subcategory, image=image, date=date)
            return redirect("gallery_list")  # Redirect to gallery page after upload

    return render(request, "galleryupload.html")

def gallery_list(request):
    """Displays all uploaded images."""
    images = Gallery.objects.all().order_by('-date')
    return render(request, "gallery_list.html", {"images": images})

def gallery_years(request):
    years = sorted(set(img.date.year for img in Gallery.objects.all()), reverse=True)
    year_ranges = [(year, year + 1) for year in years]
    return render(request, "gallery_years.html", {"year_ranges": year_ranges})

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

def events_view(request):
    today = date.today()
    all_events = Event.objects.filter(date__lt=now().date())
    upcoming_events = Event.objects.filter(date__gte=today).order_by('date')
    return render(request, 'events.html', {'all_events': all_events, 'upcoming_events': upcoming_events})

def upload_event(request):
    """Handles event uploads."""
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        date = request.POST.get("date")
        end_date = request.POST.get("end_date")

        if title and description and image and date and end_date:
            Event.objects.create(
                title=title,
                description=description,
                image=image,
                date=date,
                end_date=end_date
            )
            return redirect("event_list")  # Redirect to event list page after upload

    return render(request, "upload_event.html")

def event_list(request):
    """Displays all uploaded events."""
    events = Event.objects.all().order_by('-date')
    return render(request, "event_list.html", {"events": events})

@login_required
def user_list(request):
    users = UserProfile.objects.select_related('user').order_by('registration_number')

    # Calculate age based on DOB
    for user in users:
        user.age = (date.today() - user.dob).days // 365  # Calculate age in years

    # Set up pagination
    paginator = Paginator(users, 7)  # Show 10 users per page
    page_number = request.GET.get('page')  # Get the current page from the URL
    page_obj = paginator.get_page(page_number)  # Get the page object for the current page

    return render(request, "user_list.html", {"page_obj": page_obj})


@login_required
def user_fees(request, user_id):
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    user = get_object_or_404(User, id=user_id)
    current_year = datetime.now().year

    if request.method == "POST":
        month = request.POST.get("month")
        year = request.POST.get("year")
        amount = request.POST.get("amount")

        if month and year and amount:
            UserFee.objects.create(user=user, month=month, year=year, amount=Decimal(amount))
            return redirect("user_fees", user_id=user.id)  # Redirect to refresh the page

    # Fetch all fees paid by the user
    paid_fees = UserFee.objects.filter(user=user, year=current_year).values_list('month', 'amount')
    paid_fees_dict = {fee[0]: fee[1] for fee in paid_fees}
    total_fees_paid = sum(paid_fees_dict.values())

    current_month = datetime.now().month
    fee_per_month = Decimal("10.00")
    expected_payment = sum(fee_per_month for i in range(1, current_month + 1))

    # Build fee table
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

    return render(request, 'user_fees.html', {
        "user": user,
        "months": months,  # ✅ Pass months to template
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

from decimal import Decimal

@login_required
def user_points(request, user_id):
    user = get_object_or_404(User, id=user_id)
    points = UserPoint.objects.filter(user=user)

    if request.method == "POST":
        category = request.POST.get("category")
        points_value = request.POST.get("points")

        try:
            points_value = Decimal(points_value)  # Convert to Decimal
        except ValueError:
            messages.error(request, "Invalid points value!")
            return redirect("user_points", user_id=user.id)

        point_entry, created = UserPoint.objects.get_or_create(user=user, category=category)

        # Ensure proper Decimal addition
        point_entry.points += points_value  
        point_entry.save()

        messages.success(request, "Points updated successfully!")
        return redirect("user_points", user_id=user.id)

    # Calculate total points correctly using Decimal
    total_points = sum(point.points for point in points)

    return render(request, "user_points.html", {"user": user, "points": points, "total_points": total_points})


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
        profiles = UserProfile.objects.all()
    else:
        profiles = UserProfile.objects.filter(blood_group=selected_group)

    # Ensure all possible blood groups appear in the dropdown
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
        profiles = UserProfile.objects.filter(willing_to_donate_blood=True)
    else:
        profiles = UserProfile.objects.filter(blood_group=selected_group, willing_to_donate_blood=True)

    return render(request, 'donor_list.html', {
        'profiles': profiles,
        'blood_groups': ALL_BLOOD_GROUPS,
        'selected_group': selected_group,
    })

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
        if request.FILES.get('photo'):
            user.photo = request.FILES.get('photo')
        
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
