from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout

from django.contrib.contenttypes.models import ContentType
from mainProject.models import Film, Serial, Actor, Comment, Favorite, Genre
from .models import UserList, ListItem
from django.db.models import Q
import os

from django.conf import settings

from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from pathlib import Path

from mainProject.tools import parse_media_item

import requests

from django.db.models import Exists, OuterRef

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

    today = date.today()
    films = Film.objects.exclude(is_parsed=False)
    coming_soon_films = films.filter(release_date__year=today.year)[:10]
    films = films.exclude(release_date__year=today.year).order_by('-rating')[:20]
    serials = Serial.objects.exclude(is_parsed=False)
    coming_soon_serials = serials.filter(first_air_date__year=today.year)[:10]
    serials = serials.exclude(first_air_date__year=today.year).order_by('-first_air_date')[:20]

    for items in [films, coming_soon_films, serials, coming_soon_serials]:
        for item in items:
            check_path(item)

            item.first_genre = item.genres.first()
        
    return render(request, "main/index.html", context={
        "username": request.user,
        "films": films,
        "serials": serials,
        "coming_soon_films": coming_soon_films,
        "coming_soon_serials": coming_soon_serials,
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
    
    title_search = request.GET.get('title_search', '').strip()
    budget_min = request.GET.get('budget_min', '').strip()
    budget_max = request.GET.get('budget_max', '').strip()
    revenue_min = request.GET.get('revenue_min', '').strip()
    revenue_max = request.GET.get('revenue_max', '').strip()
    release_date_min = request.GET.get('release_date_min', '').strip()
    release_date_max = request.GET.get('release_date_max', '').strip()
    duration_min = request.GET.get('duration_min', '').strip()
    duration_max = request.GET.get('duration_max', '').strip()
    rating_min = request.GET.get('rating_min', '').strip()
    rating_max = request.GET.get('rating_max', '').strip()
    selected_genres = request.GET.getlist('genres')
    
    films = Film.objects.exclude(is_parsed=False)
    
    if title_search:
        films_with_default_search = films.filter(
            title__icontains=title_search
        )
        films_with_capitalize_search = films.filter(
            title__icontains=title_search.capitalize()
        )
        films = films_with_default_search.union(films_with_capitalize_search, all=True)    
    if budget_min:
        films = films.filter(budget__gte=budget_min)
    if budget_max:
        films = films.filter(budget__lte=budget_max)
    
    if revenue_min:
        films = films.filter(revenue__gte=revenue_min)
    if revenue_max:
        films = films.filter(revenue__lte=revenue_max)
    
    if release_date_min:
        films = films.filter(release_date__gte=release_date_min)
    if release_date_max:
        films = films.filter(release_date__lte=release_date_max)
    
    if duration_min:
        films = films.filter(duration__gte=duration_min)
    if duration_max:
        films = films.filter(duration__lte=duration_max)
    
    if rating_min:
        films = films.filter(rating__gte=rating_min)
    if rating_max:
        films = films.filter(rating__lte=rating_max)
    
    if selected_genres:
        films = films.filter(genres__search_id__in=selected_genres).distinct()
    
    for film in films:
        check_path(film)
    
    genres = Genre.objects.all()
    media_type = "films"
    
    context = {
        "username": request.user,
        "items": films,
        "media_type": media_type,
        "genres": genres,
        "filter_values": {
            "title_search": title_search,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "revenue_min": revenue_min,
            "revenue_max": revenue_max,
            "release_date_min": release_date_min,
            "release_date_max": release_date_max,
            "duration_min": duration_min,
            "duration_max": duration_max,
            "rating_min": rating_min,
            "rating_max": rating_max,
            "selected_genres": selected_genres,
        }
    }
    
    return render(request, "main/items.html", context=context)

def serialsPage(request):
    request.session['profile_error_messages'] = []
    
    title_search = request.GET.get('title_search', '').strip()
    episodes_min = request.GET.get('episodes_min', '').strip()
    episodes_max = request.GET.get('episodes_max', '').strip()
    seasons_min = request.GET.get('seasons_min', '').strip()
    seasons_max = request.GET.get('seasons_max', '').strip()
    first_air_date_min = request.GET.get('first_air_date_min', '').strip()
    first_air_date_max = request.GET.get('first_air_date_max', '').strip()
    last_air_date_min = request.GET.get('last_air_date_min', '').strip()
    last_air_date_max = request.GET.get('last_air_date_max', '').strip()
    rating_min = request.GET.get('rating_min', '').strip()
    rating_max = request.GET.get('rating_max', '').strip()
    status_filter = request.GET.get('status', '').strip()
    selected_genres = request.GET.getlist('genres')
    
    serials = Serial.objects.exclude(is_parsed=False)
    
    if title_search:
        serials_with_default_search = serials.filter(
            title__icontains=title_search
        )
        serials_with_capitalize_search = serials.filter(
            title__icontains=title_search.capitalize()
        )
        serials = serials_with_default_search.union(serials_with_capitalize_search, all=True) 
    if episodes_min:
        serials = serials.filter(episodes__gte=episodes_min)
    if episodes_max:
        serials = serials.filter(episodes__lte=episodes_max)
    
    if seasons_min:
        serials = serials.filter(seasons__gte=seasons_min)
    if seasons_max:
        serials = serials.filter(seasons__lte=seasons_max)
    
    if first_air_date_min:
        serials = serials.filter(first_air_date__gte=first_air_date_min)
    if first_air_date_max:
        serials = serials.filter(first_air_date__lte=first_air_date_max)
    
    if last_air_date_min:
        serials = serials.filter(last_air_date__gte=last_air_date_min)
    if last_air_date_max:
        serials = serials.filter(last_air_date__lte=last_air_date_max)
    
    if rating_min:
        serials = serials.filter(rating__gte=rating_min)
    if rating_max:
        serials = serials.filter(rating__lte=rating_max)
    
    if status_filter:
        serials = serials.filter(status=status_filter)
    
    if selected_genres:
        serials = serials.filter(genres__search_id__in=selected_genres).distinct()
    
    for serial in serials:
        check_path(serial)
    
    genres = Genre.objects.all()
    
    media_type = "serials"
    
    context = {
        "username": request.user,
        "items": serials,
        "media_type": media_type,
        "genres": genres,
        "filter_values": {
            "title_search": title_search,
            "episodes_min": episodes_min,
            "episodes_max": episodes_max,
            "seasons_min": seasons_min,
            "seasons_max": seasons_max,
            "first_air_date_min": first_air_date_min,
            "first_air_date_max": first_air_date_max,
            "last_air_date_min": last_air_date_min,
            "last_air_date_max": last_air_date_max,
            "rating_min": rating_min,
            "rating_max": rating_max,
            "status": status_filter,
            "selected_genres": selected_genres,
        }
    }
    
    return render(request, "main/items.html", context=context)

from django.db import models

def actorsPage(request):
    request.session['profile_error_messages'] = []
    
    # Получаем параметры фильтра из GET-запроса
    name_search = request.GET.get('name_search', '').strip()
    birthday_min = request.GET.get('birthday_min', '').strip()
    birthday_max = request.GET.get('birthday_max', '').strip()
    deathday_min = request.GET.get('deathday_min', '').strip()
    deathday_max = request.GET.get('deathday_max', '').strip()
    gender_filter = request.GET.get('gender', '').strip()
    project_search = request.GET.get('project_search', '').strip()
    
    # Начинаем с базового QuerySet
    actors = Actor.objects.exclude(is_parsed=False)
    
    # Применяем фильтры
    if name_search:
        actors_with_default_search = actors.filter(
            name__icontains=name_search
        )
        actors_with_capitalize_search = actors.filter(
            name__icontains=name_search.capitalize()
        )
        actors = actors_with_default_search.union(actors_with_capitalize_search, all=True)
    
    if birthday_min:
        actors = actors.filter(birthday__gte=birthday_min)
    if birthday_max:
        actors = actors.filter(birthday__lte=birthday_max)
    
    if deathday_min:
        actors = actors.filter(deathday__gte=deathday_min)
    if deathday_max:
        actors = actors.filter(deathday__lte=deathday_max)
    
    if gender_filter:
        actors = actors.filter(gender=gender_filter)
    
    # Фильтр по названию проекта (ищет и в фильмах и в сериалах)
    if project_search:
        # Поиск в фильмах
        actors_from_movies_default = actors.filter(
            movies__title__icontains=project_search
        )
        actors_from_movies_capitalize = actors.filter(
            movies__title__icontains=project_search.capitalize()
        )
        actors_in_film = actors_from_movies_default.union(actors_from_movies_capitalize, all=True)
        
        # Поиск в сериалах
        actors_from_serials_default = actors.filter(
            serials__title__icontains=project_search
        )
        actors_from_serials_capitalize = actors.filter(
            serials__title__icontains=project_search.capitalize()
        )

        actors_in_serial = actors_from_serials_default.union(actors_from_serials_capitalize, all=True)
        
        # Объединяем все результаты
        actors = actors_in_film.union(actors_in_serial, all=True)
        actors = list(set(actors))
    
    # Проверяем пути для всех отфильтрованных актеров
    for actor in actors:
        check_path(actor)
    
    media_type = "actors"
    
    # Создаем контекст с сохранением значений фильтров
    context = {
        "username": request.user,
        "items": actors,
        "media_type": media_type,
        "filter_values": {
            "name_search": name_search,
            "birthday_min": birthday_min,
            "birthday_max": birthday_max,
            "deathday_min": deathday_min,
            "deathday_max": deathday_max,
            "gender": gender_filter,
            "project_search": project_search,
        }
    }
    
    return render(request, "main/items.html", context=context)

def searchPage(request):
    request.session['profile_error_messages'] = []

    search = request.POST.get('search')

    if search:
        set_previous_page_values(request, search_page_value=search)
    else:
        values = get_previous_page_values(request)
        for item in values:
            for key, value in item.items():
                if key == "search_page_value":
                    search = value

    films = Film.objects.exclude(is_parsed=False)
    serials = Serial.objects.exclude(is_parsed=False)
    actors = Actor.objects.exclude(is_parsed=False)

    films_with_default_search = films.filter(
        title__icontains=search
    )
    films_with_capitalize_search = films.filter(
        title__icontains=search.capitalize()
    )
    films = films_with_default_search.union(films_with_capitalize_search, all=True)

    serials_with_default_search = serials.filter(
        title__icontains=search
    )
    serials_with_capitalize_search = serials.filter(
        title__icontains=search.capitalize()
    )
    serials = serials_with_default_search.union(serials_with_capitalize_search, all=True)
    
    actors_with_default_search = actors.filter(
        name__icontains=search
    )
    actors_with_capitalize_search = actors.filter(
        name__icontains=search.capitalize()
    )
    actors = actors_with_default_search.union(actors_with_capitalize_search, all=True)

    for objects in [films, serials, actors]:
        for object in objects:
            check_path(object)
    
    return render(request, "main/search.html", context={
        "username": request.user,
        "films": films,
        "serials": serials,
        "actors": actors,
        "search_title": search,
        "results_count": len(films) + len(serials) + len(actors),
        "types": {
            "film": "film",
            "serial": "serial",
            "actor": "actor"
        }
    })

def profilePage(request):
    if request.user.is_authenticated:
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

        favorites = user.favorites.all()
        favorites_count = len(favorites)
        favorites = [item for item in favorites]

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
            "user_lists": user_lists
        })
    else:
        return redirect("errorPage", media_type="profilePage")

def signOut(request):
    logout(request)
    return redirect("mainPage")

def itemPage(request, media_type, search_id):
    request.session['profile_error_messages'] = []

    if media_type == "film" or media_type == "serial" or media_type == "actor":
        media_type = f"{media_type}s"
    
    models = {
        "films": Film,
        "serials": Serial,
        "actors": Actor,
    }

    model = models.get(media_type)

    item = model.objects.get(search_id=search_id)

    if not item.is_parsed:
        return redirect("errorPage", media_type="actor")

    actors = []
    films = []
    serials = []

    if media_type != "actors":
        check_path(item)
        actors = list(item.actors.all())
    else:
        check_path(item)
        films = list(item.movies.all())
        serials = list(item.serials.all())

    content_type = ContentType.objects.get_for_model(item)
    
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=item.id
    ).select_related('user')

    user_lists_with_status = []

    if request.user.is_authenticated:
        User = get_user_model()
        user = User.objects.get(id=request.user.id)

        is_favorite = user.favorites.filter(
            content_type=content_type, 
            object_id=item.id
        ).exists()

        user_lists = user.user_lists.all()

        user_lists_with_status = []
        
        item_exists_subquery = ListItem.objects.filter(
            user_list=OuterRef('pk'),
            content_type=content_type,
            object_id=item.id
        )
        
        user_lists = user.user_lists.annotate(
            has_item=Exists(item_exists_subquery)
        )
        
        user_lists_with_status = [
            {
                'list': user_list,
                'has_item': user_list.has_item
            }
            for user_list in user_lists
        ]
    else:
        is_favorite = False

    return render(request, "main/item.html", context={
        "username": request.user,
        "item": item,
        "films": films,
        "films_count": len(films),
        "serials": serials,
        "serials_count": len(serials),
        "actors": actors,
        "actors_count": len(actors),
        "media_type": media_type,
        "comments": comments,
        "content_type_id": content_type.id,
        "object_id": item.id,
        "is_favorite": is_favorite,
        'user_lists_with_status': user_lists_with_status,
        "types": {
            "film": "film",
            "serial": "serial",
            "actor": "actor"
        }
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
        description = request.POST.get("description")

        User = get_user_model()
        users = User.objects.all()
        user = users.get(id=request.user.id)
        users = users.exclude(id=request.user.id)

        username_is_exist = users.filter(username=username).exists()

        if username_is_exist:
            request.session['profile_error_messages'].append(f"Пользователь с никнеймом {username} уже существует")
        else:
            old_avatar_path = os.path.join(settings.MEDIA_ROOT, "avatars/", f"{user.username}.jpg")
            new_avatar_path = os.path.join(settings.MEDIA_ROOT, "avatars/", f"{username}.jpg")
            
            # Проверяем существование старого файла
            if os.path.exists(old_avatar_path):
                try:
                    # Переименовываем файл (более эффективно чем копирование)
                    os.rename(old_avatar_path, new_avatar_path)
                except Exception as e:
                    request.session['profile_error_messages'].append(f"Ошибка при обновлении аватара: {e}")
            
            # Обновляем username и avatar
            user.username = username
            user.avatar.name = f"avatars/{username}.jpg"
            user.save()
        
        if description != user.description:
            user.description = description
            user.save()

    return redirect("profilePage")

@login_required
def create_comment(request):
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            content_type_id = request.POST.get('content_type_id')
            object_id = request.POST.get('object_id')
            text = request.POST.get('text')
            rating = request.POST.get('rating')
            
            # Проверяем обязательные поля
            if not all([content_type_id, object_id, text]):
                messages.error(request, 'Заполните все обязательные поля.')
                return redirect(request.META.get('HTTP_REFERER', 'profilePage'))
            
            # Получаем ContentType
            content_type = get_object_or_404(ContentType, id=content_type_id)
            
            # Получаем модель объекта
            model_class = content_type.model_class()
            
            # Проверяем существование объекта
            content_object = get_object_or_404(model_class, id=object_id)
            
            # Создаем комментарий
            comment = Comment(
                user=request.user,
                content_type=content_type,
                object_id=object_id,
                text=text,
                rating=rating if rating else None  # rating может быть пустым
            )
            comment.save()
            
            messages.success(request, 'Ваш комментарий успешно добавлен!')
            
            # Перенаправляем обратно на страницу объекта
            # Определяем тип контента для редиректа
            if hasattr(content_object, 'search_id'):
                if model_class == Film:
                    return redirect('itemPage', media_type='film', search_id=content_object.search_id)
                elif model_class == Serial:
                    return redirect('itemPage', media_type='serial', search_id=content_object.search_id)
                elif model_class == Actor:
                    return redirect('itemPage', media_type='actor', search_id=content_object.search_id)
            
        except Exception as e:
            messages.error(request, f'Ошибка при добавлении комментария: {str(e)}')
    
    # Если что-то пошло не так, возвращаем на предыдущую страницу
    return redirect(request.META.get('HTTP_REFERER', 'profilePage'))

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
            
            # Удаляем старый аватар если есть
            if request.user.avatar:
                old_avatar_path = request.user.avatar.path
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            
            # Сохраняем файл вручную
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb+") as f:
                for chunk in avatar_file.chunks():
                    f.write(chunk)
            
            # Обновляем поле в базе данных
            User = get_user_model()
            user = User.objects.get(id=request.user.id)
            user.avatar.name = f"avatars/{new_filename}"
            user.save()
            
            messages.success(request, 'Аватар успешно обновлен!')
            
        except Exception as e:
            messages.error(request, f'Ошибка при загрузке аватара: {str(e)}')
    
    return redirect('profilePage')

@login_required
def add_to_favorite(request):
    if request.method == 'POST':
        try:
            content_type_name = request.POST.get('content_type')
            object_id = request.POST.get('object_id')
            
            if not all([content_type_name, object_id]):
                messages.error(request, 'Ошибка: не указан объект')
                return redirect(request.META.get('HTTP_REFERER', 'home'))
            
            # Получаем ContentType (ищем по имени модели)
            content_type = ContentType.objects.get(model=content_type_name.lower())
            
            # Получаем модель объекта
            model_class = content_type.model_class()
            
            # Проверяем существование объекта
            content_object = model_class.objects.get(id=object_id)
            
            # Проверяем, не добавлен ли уже в избранное
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=object_id
            )
            
            if created:
                messages.success(request, f'{content_object} добавлен в избранное!')
            else:
                messages.info(request, f'{content_object} уже в избранном')
                
        except ContentType.DoesNotExist:
            messages.error(request, 'Ошибка: тип объекта не найден')
        except model_class.DoesNotExist:
            messages.error(request, 'Ошибка: объект не найден')
        except Exception as e:
            messages.error(request, f'Ошибка при добавлении в избранное: {str(e)}')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def remove_from_favorite(request):
    if request.method == 'POST':
        try:
            content_type_name = request.POST.get('content_type')
            print(content_type_name)
            object_id = request.POST.get('object_id')
            print(object_id)
            
            if not all([content_type_name, object_id]):
                messages.error(request, 'Ошибка: не указан объект')
                return redirect(request.META.get('HTTP_REFERER', 'home'))
            
            content_type = ContentType.objects.get(model=content_type_name.lower())
            
            model_class = content_type.model_class()
            
            item = Favorite.objects.get(
                user=request.user,
                content_type=content_type,
                object_id=object_id
            )
            item.delete()
                
        except ContentType.DoesNotExist:
            messages.error(request, 'Ошибка: тип объекта не найден')
        except model_class.DoesNotExist:
            messages.error(request, 'Ошибка: объект не найден')
        except Exception as e:
            messages.error(request, f'Ошибка при добавлении в избранное: {str(e)}')
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def add_new_item(request):
    if request.POST:
        selected_object_search_id = request.POST.get("selected_object_search_id")
        selected_object_media_type = request.POST.get("selected_object_media_type")
        added_object_search_id = request.POST.get("added_object_search_id")
        added_object_media_type = request.POST.get("added_object_media_type")

        films = Film.objects.all()
        serials = Serial.objects.all()
        actors = Actor.objects.all()

        added_object_media_type = added_object_media_type + "s"

        models = {
            "films": films,
            "serials": serials,
            "actors": actors,
        }

        added_object_model = models.get(added_object_media_type)

        selected_item_model = models.get(selected_object_media_type)
        selected_item = selected_item_model.get(search_id=selected_object_search_id)
        try:
            parse_media_item(films, serials, actors, selected_item, selected_object_media_type, added_object_model, added_object_media_type, added_object_search_id)
            return redirect('itemPage', media_type=added_object_media_type[:-1], search_id=added_object_search_id)
        except requests.exceptions.ConnectionError:
            return redirect('errorPage', media_type='error')
    else:
        return redirect('errorPage', media_type='error')
    
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

    favorites = user.favorites.all()
    favorites_count = len(favorites)
    favorites = [item for item in favorites]

    user_lists = list(user.user_lists.filter(is_private=False))

    return render(request, 'main/user.html', context={
        "username": user.username,
        "avatar_url": user.avatar.url,
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
        "user_lists_count": len(user_lists)
    })

def add_list(request):
    if request.POST:
        list_name = request.POST.get('list_name')
        list_description = request.POST.get('list_description')
        list_type = request.POST.get('list_type')
        list_is_private = request.POST.get('list_is_private')

        user_list = UserList.objects.create(
            user=request.user,
            title=list_name,
            description=list_description,
            list_type=list_type,
            is_private=True if list_is_private == "on" else False 
        )   

    return redirect('profilePage') 

def delete_list(request):
    list_id = request.POST.get("list_id")
    user_list = UserList.objects.get(id=list_id)
    user_list.delete()
    return redirect("profilePage")

def add_item_to_list(request):
    if request.method == 'POST':
        # Получаем данные из формы
        item_id = request.POST.get('item_id')
        item_media_type = request.POST.get('item_media_type')
        list_id = request.POST.get('list_id')
        
        # Получаем список пользователя
        user_list = get_object_or_404(UserList, id=list_id, user=request.user)
        
        # Определяем модель контента
        if item_media_type == 'films':
            model_class = Film
        elif item_media_type == 'serials':
            model_class = Serial
        elif item_media_type == 'actors':
            model_class = Actor
        
        # Получаем объект контента
        content_object = get_object_or_404(model_class, id=item_id)
        content_type = ContentType.objects.get_for_model(model_class)

        if not ListItem.objects.filter(user_list=user_list, content_type=content_type, object_id=item_id).exists():
            # Создаем новый элемент списка
            list_item = ListItem.objects.create(
                user_list=user_list,
                content_type=content_type,
                object_id=item_id,
                content_object=content_object
            )
    
    return redirect(request.META.get('HTTP_REFERER', 'home'))
