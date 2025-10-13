from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout

from mainProject.models import Film, Serial
from django.db.models import Q
import os

def mainPage(request):
    films = Film.objects.all()
    films = films.order_by('-rating')[:10]
    serials = Serial.objects.all()
    serials = serials.order_by('rating')[:10]

    root = "C:/Users/Nazar/Desktop/moviesSite/website/mainProject/static"

    for film in films:
        img_path = os.path.join(root, film.local_img_path)

        if not os.path.exists(img_path):
            film.local_img_path = ""
        
        film.genres = film.genres[0]["name"]

    for serial in serials:
        img_path = os.path.join(root, serial.local_img_path)
        if not os.path.exists(img_path):
            serial.local_img_path = ""

        serial.genres = serial.genres[0]["name"]
        
    return render(request, "main/index.html", context={
        "username": request.user,
        "films": films,
        "serials": serials
    })

def authPage(request):
    error_message = ""

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("mainPage")
        else:
            error_message = "Неверное имя пользователя или пароль"
            
    return render(request, "main/auth.html", {
        "username": request.user,
        "error_message": error_message
    })

def regPage(request):
    User = get_user_model()
    message = ""
    error_username = ""

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if username:
            if User.objects.filter(username=username).exists():
                message = "exist"
                error_username = username
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password  
                )
                
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect("mainPage")

    return render(request, "main/reg.html", {
        "message": message,
        "username": request.user,
        "error_username": error_username,
    })

def filmsPage(request):
    return render(request, "main/items.html", context={
        "username": request.user
    })

def searchPage(request):
    items = []
    search = request.POST.get('search')
    if search:
        films = Film.objects.filter(
            title__icontains=search
        )
        serials = Serial.objects.filter(
            title__icontains=search
        )

    return render(request, "main/search.html", context={
        "username": request.user,
        "films": films,
        "serials": serials,
        "search_title": search.capitalize(),
        "results_count": len(films) + len(serials),
    })

def profilePage(request):
    return render(request, "main/profile.html", context={
        "username": request.user,
        "icon": str(request.user)[0].upper()
    })

def signOut(request):
    logout(request)
    return redirect("mainPage")

def itemPage(request):
    return render(request, "main/item.html", context={
        "username": request.user
    })