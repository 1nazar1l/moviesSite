from django.shortcuts import render
from .tools import (
    download_movies, 
    delete_everything_in_folder, 
    json_to_db, 
    download_images, 
    upgrade_local_imgs_path, 
    collect_special_messages_block
)

import json
from django.http import JsonResponse
from .models import Film

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def home(request):
    return render(request, "home.html")

def films_admin_panel(request):
    all_films = Film.objects.all()

    films = all_films.order_by('-id')[0:100]

    messages = request.session.get('custom_messages', [])
    messages = messages[::-1]

    return render(request, "index.html", context={
        "films": films,
        "upgraded_fields": [
            "search_id", 
            "title", 
            "overview", 
            "local_img_path", 
            "site_img_path",
            "release_date", 
            "rating", 
            "title_lang", 
            "is_adult"
        ],
        "messages": messages               
    })

def delete_films(request):
    messages = []
    messages_block = []

    film_ids = request.POST.getlist('film_ids')
    
    if not film_ids:
        messages.append("Не выбрано ни одного фильма для удаления")
    else:
        try:
            films_to_delete = Film.objects.filter(id__in=film_ids)
            deleted_films = [[film.title, film.search_id] for film in films_to_delete]

            deleted_count = films_to_delete.delete()[0]
            messages.append(f"Успешно удалено {deleted_count} фильмов!")

            for film in deleted_films:
                messages.append(f"Фильм {film[0]}(id {film[1]}) успешно удалён!")


        except Exception as e:
            messages.append(f"Ошибка при удалении: {str(e)}")

    collect_special_messages_block(messages, messages_block, request)
    
    return redirect('films')

def delete_all_films(request):
    messages = []
    messages_block = []

    films = Film.objects.all().delete()
    messages.append(f"Все фильмы успешно удалены!")
    
    collect_special_messages_block(messages, messages_block, request)

    return redirect('films')

def parse_films(request):
    messages = []
    messages_block = []

    start_page = request.POST.get('start_page')
    end_page = request.POST.get('end_page')
    delete_jsons = request.POST.get('delete_jsons')
    update_db = request.POST.get('update_db')
    vpn_is_connected = request.POST.get('vpn_is_connected')
    upgraded_field = request.POST.get('upgraded_field')

    if vpn_is_connected:
        try:
            start_page = int(start_page)
            end_page = int(end_page)

            if start_page < 0 or end_page < 0:
                messages.append("Нельзя вводить числа меньше чем ноль")
                raise ValueError("Поддерживаются только положительные целочисленные типы данных")
            else:
                if start_page > end_page:
                    start_page, end_page = end_page, start_page
            try:
                download_movies(start_page, end_page)
                messages.append("Фильмы скачаны!")
            except:
                messages.append("Возможно не включен VPN. Ошибка при запросе к TMDB API!")

        except Exception as e:
            messages.append(f"Можно вводить только целые числа: {e}")
        
    if update_db:
        json_to_db(upgraded_field, messages)
        messages.append("Фильмы перенесены в базу данных!")
        if upgraded_field:
            messages.append(f"Обновленно поле {upgraded_field}!")

    if delete_jsons:
        delete_everything_in_folder()
        messages.append("Папка с json файлами очищена!")

    collect_special_messages_block(messages, messages_block, request)

    return redirect('films')

def update_info(request):
    messages = []
    messages_block = []

    should_download_images = request.POST.get("should_download_images")
    update_local_img_path = request.POST.get("update_local_img_path")
    vpn_is_connected = request.POST.get('vpn_is_connecteD')
    
    if vpn_is_connected and should_download_images:
        try:
            download_images()
            messages.append("Постеры к фильмам скачаны!")
        except:
            messages.append("Возможно не включен VPN. Ошибка при запросе к TMDB API!")

    if update_local_img_path:
        upgrade_local_imgs_path()
        messages.append("Пути к скачаным постерам обновлены!")

    collect_special_messages_block(messages, messages_block, request)
    
    return redirect('films')


def clear_messages(request):
    if 'custom_messages' not in request.session:
        request.session['custom_messages'] = []
    
    request.session['custom_messages'] = [
        ["Сообщения очищены", "end"]
    ]
    request.session.modified = True
    
    return redirect('films')

