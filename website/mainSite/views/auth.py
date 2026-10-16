"""Аутентификация: логин, регистрация, выход."""

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.mail import send_mail
from django.shortcuts import redirect, render


def authPage(request):
    error_message = ""

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("mainPage")
        error_message = "Неверное имя пользователя или пароль"

    return render(
        request,
        "main/auth.html",
        {
            "username": request.user,
            "error_message": error_message,
        },
    )


def regPage(request):
    User = get_user_model()
    message = ""
    message_text = ""

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")

        if username:
            if User.objects.filter(username=username).exists():
                message_text = f"Пользователь с таким именем({username}) уже существует"
                message = "exist"
            elif User.objects.filter(email=email).exists():
                message_text = f"Пользователь с такой почтой({email}) уже существует"
                message = "exist"
            else:
                try:
                    User.objects.create_user(username=username, email=email, password=password)
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        login(request, user)

                        send_mail(
                            "Добро пожаловать!",
                            f"Здравствуйте, {username}! Вы успешно зарегистрировались.",
                            settings.EMAIL_HOST_USER,
                            [email],
                            fail_silently=True,
                        )
                        return redirect("mainPage")
                except Exception as e:
                    message_text = f"Ошибка при создании пользователя: {str(e)}"
                    message = "error"

    return render(
        request,
        "main/reg.html",
        {
            "message": message,
            "username": request.user,
            "message_text": message_text,
        },
    )


def signOut(request):
    logout(request)
    return redirect("mainPage")
