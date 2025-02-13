from django.http import HttpResponse

def users(request):
    return HttpResponse("Welcome to the Users Page")
