from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

def mainPage(request):
    if 'username' not in request.session:
        request.session['username'] = ""

    return render(request, "main/index.html", context={
        "username": request.session['username']
    })

def authPage(request):
    request.session['first_visit'] = True
    if 'username' not in request.session:
        request.session['username'] = ""

    return render(request, "main/auth.html", context={
        "username": request.session['username']
    })

def regPage(request):
    User = get_user_model()
    if request.session['first_visit']:
        request.session['first_visit'] = False
        return render(request, "main/reg.html", context={
            "message": "",
            "username": ""
        })
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        message = ""
        request.session['username'] = ""
        error_username = ""

        path = "main/reg.html"

        if username:
            media_item_obj, created = User.objects.get_or_create(username=username)


            if not created:
                message = "exist"
                error_username = username
            else:
                media_item_obj.email = email
                media_item_obj.password = password
                media_item_obj.save()

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