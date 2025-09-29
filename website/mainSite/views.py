from django.shortcuts import render

def mainPage(request):
    return render(request, "main/index.html")

def authPage(request):
    return render(request, "main/auth.html")

def regPage(request):
    return render(request, "main/reg.html")

def filmsPage(request):
    return render(request, "main/items.html")

def searchPage(request):
    return render(request, "main/search.html")

def profilePage(request):
    return render(request, "main/profile.html")