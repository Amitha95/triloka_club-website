from django.http import HttpResponse
from django.shortcuts import render,redirect
from .models import Gallery, Event
from datetime import date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

def base(request):
    return render(request, 'base.html')

def home(request):
    return render(request, 'home.html')

def events(request):
    return render(request, 'events.html')

def gallery(request):
    return render(request, 'gallery.html')

def contact(request):
    return render(request, 'contact.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard_view")  # Redirect to the dashboard after login
        else:
            return render(request, "home.html", {"error": "Invalid username or password"})

    return redirect("home")

def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")

def gallery_years(request):
    # Extract unique years from images
    years = list(set(img.date.year for img in Gallery.objects.all()))
    years.sort(reverse=True)  # Sort years descending

    # Create year ranges like 2023-2024, 2022-2023, etc.
    year_ranges = [(year, year + 1) for year in years]

    return render(request, "gallery_years.html", {"year_ranges": year_ranges})

def gallery_view(request, year_start, year_end):
    # Convert URL parameters to integers
    year_start = int(year_start)
    year_end = int(year_end)

    # Filter images within the selected year range
    photos = Gallery.objects.filter(
        date__year__gte=year_start, date__year__lte=year_end
    )

    return render(request, "gallery.html", {"photos": photos, "year_start": year_start, "year_end": year_end})

def events_view(request):
    today = date.today()
    
    # Fetch all events for cards
    
    all_events = Event.objects.filter(date__lt=now().date()) 

    # Fetch only upcoming events for marquee
    upcoming_events = Event.objects.filter(date__gte=today).order_by('date')

    return render(request, 'events.html', {'all_events': all_events, 'upcoming_events': upcoming_events})
