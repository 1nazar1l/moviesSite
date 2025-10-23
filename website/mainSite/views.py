from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout

from mainProject.models import Film, Serial, Actor
from django.db.models import Q
import os

from django.conf import settings


def set_previous_page(request):
    request.session.modified = True

    if 'previous_page' not in request.session:
        request.session['previous_page'] = ""

    request.session["previous_page"] = request.build_absolute_uri()

def set_previous_page_values(request, **kwargs):
    request.session.modified = True

    if 'previous_page_values' not in request.session:
        request.session["previous_page_values"] = []

    for key, value in kwargs.items():
        request.session["previous_page_values"].append({
            key: value,
        })

def get_previous_page_values(request):
    return request.session.get("previous_page_values", [])

def get_previous_page(request):
    return request.session.get("previous_page", "/")

def check_path(item):
    if hasattr(item, 'local_img_path'):
        img_path = os.path.join(settings.MEDIA_ROOT, str(item.local_img_path))
        if not os.path.exists(img_path):
            item.local_img_path = ""
    else:
        img_path = os.path.join(settings.MEDIA_ROOT, item["local_img_path"])
        if not os.path.exists(img_path):
            item["local_img_path"] = ""

def mainPage(request):
    request.session['profile_error_messages'] = []

    set_previous_page(request)
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
    set_previous_page(request)
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
    set_previous_page(request)
    User = get_user_model()
    emails = list(set(User.objects.values_list("email")))
    emails = [email[0] for email in emails]
    message = ""
    message_text = ""

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if username:
            if User.objects.filter(username=username).exists():
                message_text = f"Пользователь с таким именем({username}) уже существует"
                message = "exist"
            else:
                if email in emails:
                    message_text = f"Пользователь с такой почтой({email}) уже существует"
                    message = "exist"
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
        "message_text": message_text,
    })

def filmsPage(request):
    request.session['profile_error_messages'] = []

    set_previous_page(request)
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
    request.session['profile_error_messages'] = []

    set_previous_page(request)
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
    request.session['profile_error_messages'] = []

    set_previous_page(request)
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
    request.session['profile_error_messages'] = []

    set_previous_page(request)
    search = request.POST.get('search')

    if search:
        set_previous_page_values(request, search_page_value=search)
    else:
        values = get_previous_page_values(request)
        for item in values:
            for key, value in item.items():
                if key == "search_page_value":
                    search = value

    films = Film.objects.filter(
        title__icontains=search  
    )
    serials = Serial.objects.filter(
        title__icontains=search
    )
    actors = Actor.objects.filter(
        name__icontains=search
    )

    for objects in [films, serials, actors]:
        for object in objects:
            check_path(object)
    
    return render(request, "main/search.html", context={
        "username": request.user,
        "films": films,
        "serials": serials,
        "actors": actors,
        "search_title": search.capitalize(),
        "results_count": len(films) + len(serials) + len(actors),
        "types": {
            "film": "film",
            "serial": "serial",
            "actor": "actor"
        }
    })

def profilePage(request):
    error_messages = request.session.get('profile_error_messages', [])

    User = get_user_model()
    user = User.objects.get(id=request.user.id)
    set_previous_page(request)
    return render(request, "main/profile.html", context={
        "username": user.username,
        "icon": str(user.username)[0].upper(),
        "username_value": user.username,
        "email_value": user.email,
        "description_value": user.description,
        "error_messages": error_messages
    })

def signOut(request):
    logout(request)
    return redirect("mainPage")

def itemPage(request, media_type, search_id):
    request.session['profile_error_messages'] = []

    previous_page = get_previous_page(request)
    if media_type == "film" or media_type == "serial" or media_type == "actor":
        media_type = f"{media_type}s"
    
    models = {
        "films": Film,
        "serials": Serial,
        "actors": Actor,
    }

    model = models.get(media_type)
    item = model.objects.get(search_id=search_id)
    if media_type != "actors":
        check_path(item)
        for actor in item.actors:
            check_path(actor)
    else:
        check_path(item)
        for film in item.movies:
            check_path(film)

    return render(request, "main/item.html", context={
        "username": request.user,
        "item": item,
        "media_type": media_type,
        "previous_page": previous_page
    })

def errorPage(request, media_type=""):    
    request.session['profile_error_messages'] = []

    return render(request, "main/error.html", context={
        "username": request.user
    })

def update_user_info(request):
    request.session.modified = True

    request.session['profile_error_messages'] = []

    if request.POST:
        username = request.POST.get("username")
        email = request.POST.get("email")
        description = request.POST.get("description")

        User = get_user_model()
        users = User.objects.all()

        user = users.get(id=request.user.id)

        users = users.exclude(id=request.user.id)

        username_is_exist = users.filter(username=username).exists()
        email_is_exist = users.filter(email=email).exists()


        if(username_is_exist):
            request.session['profile_error_messages'].append(f"Пользователь с никнеймом {username} уже существует")
        else:
            user.username = username
            user.save()

        if(email_is_exist):
            request.session['profile_error_messages'].append(f"Пользователь с почтой {email} уже существует")
        else:
            user.email = email
            user.save()
        
        if(description != user.description):
            user.description = description
            user.save()


    return redirect("profilePage")