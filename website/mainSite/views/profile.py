"""Профиль пользователя: свой и чужой, обновление, аватар."""
import os
from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def profilePage(request):
    if not request.user.is_authenticated:
        return redirect("errorPage", media_type="profilePage")

    create_list_errors = request.session.get("list_error_messages", [])
    error_messages = request.session.get('profile_error_messages', [])

    today = date.today()
    User = get_user_model()
    user = User.objects.get(id=request.user.id)
    registration_date = user.date_joined.date()

    comments = user.comments.all()
    comments_count = len(comments)
    ratings_count = len(user.comments.filter(rating__isnull=False))

    days_from_registration = (today - registration_date).days
    if days_from_registration == 0:
        days_from_registration = 1

    favorites = list(user.favorites.all())
    favorites_count = len(favorites)

    user_lists = user.user_lists.all()

    return render(request, "main/profile.html", context={
        "username": user.username,
        "icon": str(user.username)[0].upper(),
        "username_value": user.username,
        "description_value": user.description,
        "error_messages": error_messages,
        "days": days_from_registration,
        "comments_count": comments_count,
        "ratings_count": ratings_count,
        "favorites_count": favorites_count,
        "favorites": favorites,
        "comments": comments,
        "user_lists": user_lists,
        "create_list_errors": create_list_errors,
    })


def userPage(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)

    today = date.today()
    registration_date = user.date_joined.date()

    comments = user.comments.all()
    comments_count = len(comments)
    ratings_count = len(user.comments.filter(rating__isnull=False))

    days_from_registration = (today - registration_date).days
    if days_from_registration == 0:
        days_from_registration = 1

    favorites = list(user.favorites.all())
    favorites_count = len(favorites)

    user_lists = list(user.user_lists.filter(is_private=False))

    avatar_url = user.avatar.url if user.avatar else ""

    return render(request, 'main/user.html', context={
        "username": user.username,
        "avatar_url": avatar_url,
        "icon": str(user.username)[0].upper(),
        "username_value": user.username,
        "email_value": user.email,
        "description_value": user.description,
        "days": days_from_registration,
        "comments_count": comments_count,
        "ratings_count": ratings_count,
        "favorites_count": favorites_count,
        "favorites": favorites,
        "comments": comments,
        "user_lists": user_lists,
        "user_lists_count": len(user_lists),
        "user_id": user.id,
    })


def update_user_info(request):
    request.session.modified = True
    request.session['profile_error_messages'] = []

    if request.POST:
        username = request.POST.get("username")
        description = request.POST.get("description")

        User = get_user_model()
        users = User.objects.all()
        user = users.get(id=request.user.id)
        users = users.exclude(id=request.user.id)

        if users.filter(username=username).exists():
            request.session['profile_error_messages'].append(
                f"Пользователь с никнеймом {username} уже существует"
            )
        else:
            old_avatar_path = os.path.join(settings.MEDIA_ROOT, "avatars/", f"{user.username}.jpg")
            new_avatar_path = os.path.join(settings.MEDIA_ROOT, "avatars/", f"{username}.jpg")

            if os.path.exists(old_avatar_path):
                try:
                    os.rename(old_avatar_path, new_avatar_path)
                except Exception as e:
                    request.session['profile_error_messages'].append(
                        f"Ошибка при обновлении аватара: {e}"
                    )

            user.username = username
            user.avatar.name = f"avatars/{username}.jpg"
            user.save()

        if description != user.description:
            user.description = description
            user.save()

    return redirect("profilePage")


@login_required
def add_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        try:
            avatar_file = request.FILES['avatar']

            if avatar_file.size > 5 * 1024 * 1024:
                messages.error(request, 'Размер файла не должен превышать 5MB')
                return redirect('profilePage')

            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if avatar_file.content_type not in allowed_types:
                messages.error(request, 'Допустимые форматы: JPEG, PNG, GIF, WebP')
                return redirect('profilePage')

            file_extension = Path(avatar_file.name).suffix.lower()
            new_filename = f"{request.user.username}{file_extension}"
            file_path = os.path.join(settings.MEDIA_ROOT, "avatars", new_filename)

            if request.user.avatar:
                old_avatar_path = request.user.avatar.path
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb+") as f:
                for chunk in avatar_file.chunks():
                    f.write(chunk)

            User = get_user_model()
            user = User.objects.get(id=request.user.id)
            user.avatar.name = f"avatars/{new_filename}"
            user.save()

            messages.success(request, 'Аватар успешно обновлен!')

        except Exception as e:
            messages.error(request, f'Ошибка при загрузке аватара: {str(e)}')

    return redirect('profilePage')