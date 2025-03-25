from django.http import HttpResponse, JsonResponse
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

def base(request):
    return render(request, 'base.html')

def home(request):
    return render(request, 'home.html')

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
                return redirect("admin_dashboard")
            else:
                return redirect("dashboard_view")
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
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already taken"})

        # Calculate age from DOB
        birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
        today = datetime.today().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        # Create user and profile
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(
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

        return redirect("login")

    return render(request, "register.html")

def upload_gallery_image(request):
    
    if request.method == "POST":
        title = request.POST.get("title")
        image = request.FILES.get("image")
        date=request.POST.get("date")
        if title and image:
            Gallery.objects.create(title=title, image=image, date=date)
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
    users = UserProfile.objects.select_related('user').all()  # Fetch all users sorted by username
    print(users) 
    return render(request, "user_list.html", {"users": users})

@login_required
def user_fees(request, user_id):
    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]
    
    user = get_object_or_404(User, id=user_id)  # Fetch user by ID
    
    # Handle form submission
    if request.method == "POST":
        month = request.POST.get("month")
        year = request.POST.get("year")
        amount = request.POST.get("amount")

        if month and year and amount:
            UserFee.objects.create(user=user, month=month, year=year, amount=amount)
        
        return redirect('user_fees', user_id=user.id)  # Redirect to refresh page

    # Calculate total fees paid
    total_fees = UserFee.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
    total_fees_x10 = total_fees  # Multiply by 10 (if needed)

    return render(request, 'user_fees.html', {
        'user': user,
        'months': months,
        'total_fees_x10': total_fees_x10,
    })

@login_required
def user_fee_details(request):
    user = request.user  # Get the logged-in user

    months = ["January", "February", "March", "April", "May", "June", 
              "July", "August", "September", "October", "November", "December"]

    # Get current month index (0-based)
    current_month_index = datetime.now().month - 1  # January = 0, February = 1, etc.

    # Fetch months where the user has paid fees
    paid_months = set(UserFee.objects.filter(user=user).values_list('month', flat=True))

    fee_status = []
    pending_fees = 0

    for i, month in enumerate(months):
        if i < current_month_index:  # Past months (should be marked as paid or pending)
            if month in paid_months:
                fee_status.append((month, "✔"))  # Green check for paid
            else:
                fee_status.append((month, "❌"))  # Red cross for missed payments
                pending_fees += 10  # Add ₹10 for each missed month
        elif i == current_month_index:  # Current month (optional logic)
            fee_status.append((month, "Pending"))  # Mark as pending
        else:  # Future months
            fee_status.append((month, "-"))  # Display hyphen for upcoming months

    # Calculate total fees paid
    total_fees_paid = UserFee.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'user_fee_details.html', {
        'fee_status': fee_status,
        'total_fees_paid': total_fees_paid,
        'pending_fees': pending_fees,
    })

@login_required
def user_points(request, user_id):
    user = get_object_or_404(User, id=user_id)
    points = UserPoint.objects.filter(user=user)

    if request.method == "POST":
        category = request.POST.get("category")
        points_value = request.POST.get("points")

        point_entry, created = UserPoint.objects.get_or_create(user=user, category=category)
        point_entry.points = points_value
        point_entry.save()

        messages.success(request, "Points updated successfully!")
        return redirect("user_points", user_id=user.id)

    return render(request, "user_points.html", {"user": user, "points": points})