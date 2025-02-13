from django.http import HttpResponse

def adminpanel(request):
    return HttpResponse("Welcome to the Admin Panel")
