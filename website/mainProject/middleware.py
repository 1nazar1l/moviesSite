from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AdminAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/adminPanel/'):
            if not request.user.is_authenticated:
                return redirect(reverse('errorPage'))
            if not request.user.is_superuser:
                return redirect(reverse('errorPage'))  
        
        response = self.get_response(request)
        return response