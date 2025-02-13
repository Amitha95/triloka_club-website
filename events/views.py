from django.http import HttpResponse

def events(request):
    return HttpResponse("Welcome to the Events Page")
