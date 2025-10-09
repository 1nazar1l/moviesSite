from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login

def mainPage(request):
    if 'username' not in request.session:
        request.session['username'] = ""

    return render(request, "main/index.html", context={
        "username": request.session['username']
    })

def authPage(request):
    error_message = ""

    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user=user)

            request.session['username'] = username
            return redirect("mainPage")
        else:
            error_message = "Такого пользователя не существует"
    

            return render(request, "main/auth.html", context={
                "username": request.session['username'],
                "error_message": error_message
            })
    else:        
        return render(request, "main/auth.html", context={
            "username": request.session['username'],
            "error_message": error_message
        })

def regPage(request):
    User = get_user_model()

    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')

    message = ""
    request.session['username'] = ""
    error_username = ""

    path = "main/reg.html"

    if username:
        user, created = User.objects.get_or_create(username=username)


        if not created:
            message = "exist"
            error_username = username
        else:
            user.email = email
            user.password = password
            user.save()

            request.session['username'] = username

            path = "main/index.html"
    
    return render(request, path, context={
        "message": message,
        "username": request.session['username'],
        "error_username": error_username,
    })

def filmsPage(request):
    if 'username' not in request.session:
        request.session['username'] = ""

    return render(request, "main/items.html", context={
        "username": request.session['username']
    })

def searchPage(request):
    if 'username' not in request.session:
        request.session['username'] = ""

    return render(request, "main/search.html", context={
        "username": request.session['username']
    })

def profilePage(request):
    if 'username' not in request.session:
        request.session['username'] = ""

    return render(request, "main/profile.html", context={
        "username": request.session['username']
    })

def signOut(request):
    request.session['username'] = ""

    return redirect("mainPage")

def itemPage(request):
    if 'username' not in request.session:
        request.session['username'] = ""

    return render(request, "main/item.html", context={
        "username": request.session['username']
    })