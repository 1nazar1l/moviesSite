from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout

from django.contrib.contenttypes.models import ContentType
from mainProject.models import Film, Serial, Actor, Comment, Favorite
from django.db.models import Q
import os

from django.conf import settings

from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from pathlib import Path


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
    films = Film.objects.exclude(is_parsed=False)
    films = films.order_by('-id')[:10]
    serials = Serial.objects.exclude(is_parsed=False)
    serials = serials.order_by('-id')[:10]

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
    films = Film.objects.exclude(is_parsed=False)

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
    serials = Serial.objects.exclude(is_parsed=False)

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
    actors = Actor.objects.exclude(is_parsed=False)

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

    films = Film.objects.exclude(is_parsed=False)
    serials = Serial.objects.exclude(is_parsed=False)
    actors = Actor.objects.exclude(is_parsed=False)

    films = films.filter(
        title__icontains=search  
    )
    serials = serials.filter(
        title__icontains=search
    )
    actors = actors.filter(
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
    set_previous_page(request)

    today = date.today()

    User = get_user_model()
    user = User.objects.get(id=request.user.id)
    registration_date = user.date_joined.date()

    comments_count = len(user.comments.all())
    ratings_count = len(request.user.comments.filter(rating__isnull=False))

    days_from_registration = (today - registration_date).days
    if days_from_registration == 0:
        days_from_registration = 1

    User = get_user_model()
    user = User.objects.get(id=request.user.id)

    favorites = user.favorites.all()
    favorites_count = len(favorites)
    favorites = [item for item in favorites]
    print(favorites)
    
    return render(request, "main/profile.html", context={
        "username": user.username,
        "icon": str(user.username)[0].upper(),
        "username_value": user.username,
        "email_value": user.email,
        "description_value": user.description,
        "error_messages": error_messages,
        "days": days_from_registration,
        "comments_count": comments_count,
        "ratings_count": ratings_count,
        "favorites_count": favorites_count,
        "favorites": favorites
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

    additional_data = []

    if media_type != "actors":
        check_path(item)
        additional_data = item.actors.all()
    else:
        check_path(item)
        movies = list(item.movies.all())
        serials = list(item.serials.all())
        additional_data = movies + serials

    # Получаем ContentType для текущего объекта
    content_type = ContentType.objects.get_for_model(item)
    
    # Получаем комментарии для этого объекта
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=item.id
    ).select_related('user')

    User = get_user_model()
    user = User.objects.get(id=request.user.id)

    is_favorite = user.favorites.filter(
        content_type=content_type, 
        object_id=item.id
    )

    return render(request, "main/item.html", context={
        "username": request.user,
        "item": item,
        "additional_data": additional_data,
        "media_type": media_type,
        "previous_page": previous_page,
        "comments": comments,
        "content_type_id": content_type.id,
        "object_id": item.id,
        "is_favorite": is_favorite
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