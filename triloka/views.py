from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserProfile, Gallery, Event
from datetime import date
from django.utils.timezone import now
import re

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
            return render(request, "home.html", {"error": "Invalid username or password"})

    return render(request, "home.html")

def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def dashboard_view(request):
    username = request.user.username if request.user.is_authenticated else ""
    filtered_username = re.sub(r'\d+', '', username)  # Remove numbers
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
        age = request.POST.get("age")
        photo = request.FILES.get("photo")
        blood_group = request.POST.get("blood_group")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already taken"})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        UserProfile.objects.create(
            user=user,
            name=name,
            phone_number=phone_number,
            address=address,
            gender=gender,
            age=age,
            photo=photo,
            blood_group=blood_group,
        )

        return redirect("login")

    return render(request, "register.html")

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
