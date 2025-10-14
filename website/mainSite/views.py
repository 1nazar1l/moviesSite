from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout

from mainProject.models import Film, Serial, Actor
from django.db.models import Q
import os

def check_path(item):
    root = "C:/Users/Nazar/Desktop/moviesSite/website/mainProject/static"
    img_path = os.path.join(root, item.local_img_path)

    if not os.path.exists(img_path):
        item.local_img_path = ""

def mainPage(request):
    films = Film.objects.all()
    films = films.order_by('-rating')[:10]
    serials = Serial.objects.all()
    serials = serials.order_by('rating')[:10]

    for film in films:
        check_path(film)
        
        film.genres = film.genres[0]["name"]

    for serial in serials:
        check_path(serial)

        serial.genres = serial.genres[0]["name"]
        
    return render(request, "main/index.html", context={
        "username": request.user,
        "films": films,
        "serials": serials,
        "types": {
            "film": "film",
            "serial": "serial",
            "actor": "actor"
        }
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
    films = Film.objects.all()

    for film in films:
        check_path(film)

    media_type = "films"
    return render(request, "main/items.html", context={
        "username": request.user,
        "items": films,
        "media_type": media_type
    })

def serialsPage(request):
    serials = Serial.objects.all()
    for serial in serials:
        check_path(serial)

    media_type = "serials"
    return render(request, "main/items.html", context={
        "username": request.user,
        "items": serials,
        "media_type": media_type
    })

def actorsPage(request):
    actors = Actor.objects.all()
    for actor in actors:
        check_path(actor)
        
    media_type = "actors"
    return render(request, "main/items.html", context={
        "username": request.user,
        "items": actors,
        "media_type": media_type
    })

def searchPage(request):
    search = request.POST.get('search')
    if search:
        films = Film.objects.filter(
            title__icontains=search
        )
        serials = Serial.objects.filter(
            title__icontains=search
        )
        actors = Actor.objects.filter(
            name__icontains=search
        )

    return render(request, "main/search.html", context={
        "username": request.user,
        "films": films,
        "serials": serials,
        "actors": actors,
        "search_title": search.capitalize(),
        "results_count": len(films) + len(serials) + len(actors),
    })

def profilePage(request):
    return render(request, "main/profile.html", context={
        "username": request.user,
        "icon": str(request.user)[0].upper()
    })

def signOut(request):
    logout(request)
    return redirect("mainPage")

def itemPage(request, media_type, search_id):
    if media_type == "film" or media_type == "serial" or media_type == "actor":
        media_type = f"{media_type}s"
    
    models = {
        "films": Film,
        "serials": Serial,
        "actors": Actor,
    }

    model = models.get(media_type)
    item = model.objects.get(search_id=search_id)
    return render(request, "main/item.html", context={
        "username": request.user,
        "item": item,
        "media_type": media_type
    })

def errorPage(request, media_type=""):        
    return render(request, "main/error.html", context={
        "username": request.user
    })