from django.shortcuts import render

def mainPage(request):
    return render(request, "main/index.html")

def authPage(request):
    return render(request, "main/auth.html")

def regPage(request):
    return render(request, "main/reg.html")