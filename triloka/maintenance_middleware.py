from django.shortcuts import render
from django.conf import settings

class MaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, 'MAINTENANCE_MODE', False):
            return render(request, 'maintenance.html', status=503)
        return self.get_response(request)
