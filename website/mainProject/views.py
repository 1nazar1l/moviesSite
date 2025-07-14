from django.shortcuts import render
from .tools import download_movies, delete_everything_in_folder, json_to_db
import json
from django.http import JsonResponse
from .models import Film

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def index(request):
    all_films = Film.objects.all()

    films = all_films.order_by('-id')[:10]

    return render(request, "index.html", context={
        "films": films,
        "upgraded_fields": [
            "search_id", 
            "title", 
            "overview", 
            "img_path", 
            "release_date", 
            "rating", 
            "title_lang", 
            "is_adult"
        ]                        
    })
        
def delete_film(request):
    film_id = request.POST.get('film_id')
    
    if not film_id:
        messages.error(request, "Не указан ID фильма для удаления")
        return redirect('home')
    
    try:
        film = Film.objects.get(id=film_id)
        film_title = film.title
        film.delete()
        messages.success(request, f'Фильм "{film_title}" успешно удалён')
    except Film.DoesNotExist:
        messages.error(request, "Фильм не найден")
    except Exception as e:
        messages.error(request, f"Ошибка при удалении: {str(e)}")
    
    return redirect('home')

def parse_films(request):
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
                raise ValueError("Поддерживаются только положительные целочисленные типы данных")
            else:
                if start_page > end_page:
                    start_page, end_page = end_page, start_page
            
            # print(f"start_page:{start_page}; end_page: {end_page}, delete_jsons:{delete_jsons}; update_db:{update_db}")
            download_movies(start_page, end_page)
            print("Фильмы скачаны!")

        except Exception as e:
            print("Поддерживаются только положительные целочисленные типы данных", e)

    if update_db:
        print("upgraded_field", upgraded_field)
        json_to_db(upgraded_field)
        print("Фильмы перенесены в базу данных!")

    if delete_jsons:
        delete_everything_in_folder()
        print("Папка с json файлами очищена!")

    return redirect('home')