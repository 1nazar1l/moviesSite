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
            "username": "",
            "first": request.session['first_visit'],
        })
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if not email:
            email = ""

        if username or username == "":
            media_item_obj, created = User.objects.get_or_create(username=username)

            message = ""

            if not created:
                message = "exist"
            else:
                media_item_obj.email = email
                media_item_obj.password = password
                media_item_obj.save()
        else:
            message = "exist"
        
        request.session['username'] = username

        return render(request, "main/reg.html", context={
            "message": message,
            "username": request.session['username'],
            "first": request.session['first_visit'],
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