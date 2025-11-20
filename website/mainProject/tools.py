import requests
import os
from environs import env
from datetime import datetime, date

from .models import Film, Serial, Actor, Message, Genre

from django.conf import settings

from bs4 import BeautifulSoup  # Добавлен импорт BeautifulSoup

env.read_env()
api_key = env("API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


def create_error_message(request, media_type, text):
    Message.objects.create(
        message_type="error",
        from_page=media_type,
        text=text,
        date=datetime.now().replace(microsecond=0),
        time=0.0,
        admin=request.user,
    )

def create_warning_message(request, media_type, text):
    Message.objects.create(
        message_type="warning",
        from_page=media_type,
        text=text,
        date=datetime.now().replace(microsecond=0),
        time=0.0,
        admin=request.user,
    )

def create_success_message(request, media_type, start_time, lead_time, text):
    Message.objects.create(
        message_type="success",
        from_page=media_type,
        text=text,
        date=start_time,
        time=lead_time,
        admin=request.user,
    )

def delete_selected_media_items(request, media_type):
    media_ids = request.POST.getlist('media_ids')

    if not media_ids:
        create_error_message(request, media_type, "Не выбрано ни одного объекта для удаления")
        return

    try:
        models = {
            "films": Film,
            "serials": Serial,
            "actors": Actor,
        }

        model = models.get(media_type)
        
        if not model:
            create_error_message(request, media_type, "Модель не найдена(delete_selected_media_items)")
            return

        start_time = datetime.now()
        media_items_to_delete = model.objects.filter(id__in=media_ids)

        if media_type != "actors":
            deleted_media_items = [[media_item.title, media_item.search_id] for media_item in media_items_to_delete]
        else:
            deleted_media_items = [[media_item.name, media_item.search_id] for media_item in media_items_to_delete]

        deleted_count = media_items_to_delete.delete()[0]

        end = datetime.now()
        lead_time = end - start_time

        create_success_message(
            request, 
            media_type, 
            str(start_time.replace(microsecond=0)),
            str(lead_time.total_seconds()),
            f"Успешно удалено {deleted_count} объектов!"
        )

        for media_item in deleted_media_items:
            create_success_message(
                request, 
                media_type, 
                str(start_time.replace(microsecond=0)),
                "0.000000",
                f"Объект {media_item[0]}(id {media_item[1]}) успешно удалён!"
            )

    except Exception as e:
        create_error_message(request, media_type, f"Ошибка при удалении: {str(e)}")

def delete_all_media_items(request, media_type):
    models = {
        "films": Film,
        "serials": Serial,
        "actors": Actor,
    }

    model = models.get(media_type)

    if not model:
        create_error_message(request, media_type, "Модель не найдена(delete_all_media_items)")
        return
    
    start_time = datetime.now()
    model.objects.all().delete()
    end = datetime.now()
    lead_time = end - start_time

    create_success_message(
        request,
        media_type,
        str(start_time.replace(microsecond=0)),
        str(lead_time.total_seconds()),
        "Все объекты успешно удалены!"
    )

def get_trailer_url(search_id, media_type, title=None, release_date=None):
    """
    Получение ссылки на трейлер фильма/сериала
    Сначала пытается через API TMDB, затем через BeautifulSoup на YouTube
    """
    # Пытаемся получить трейлер через API TMDB
    if media_type in ["films", "serials"]:
        url_part = "movie" if media_type == "films" else "tv"
        videos_url = f"{BASE_URL}/{url_part}/{search_id}/videos"
        
        params = {
            "api_key": api_key,
            "language": "ru",
        }
        
        try:
            response = requests.get(videos_url, params=params)
            response.raise_for_status()
            videos_data = response.json()
            
            # Ищем официальные трейлеры на YouTube
            if videos_data and 'results' in videos_data:
                trailers = [video for video in videos_data['results'] 
                           if video['site'] == 'YouTube' and 
                           video['type'] in ['Trailer', 'Teaser']]
                
                if trailers:
                    # Сортируем по официальности и дате публикации
                    trailers.sort(key=lambda x: (x.get('official', False), x.get('published_at', '')), reverse=True)
                    trailer = trailers[0]
                    return f"https://www.youtube.com/watch?v={trailer['key']}"
        
        except requests.exceptions.RequestException:
            # Если API не сработало, продолжаем к BeautifulSoup
            pass
    
    # Если через API не нашли, используем BeautifulSoup
    if title:
        return get_trailer_url_bs4(title, release_date)
    
    return None

def get_trailer_url_bs4(title, release_date=None):
    """
    Получение ссылки на трейлер с помощью BeautifulSoup через YouTube
    """
    search_query = f"{title} {release_date[:4] if release_date else ''} официальный трейлер"
    search_query = search_query.replace(" ", "+")
    
    # Поиск на YouTube
    youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(youtube_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Поиск ссылок на видео в структуре YouTube
        video_links = []
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            script_text = script.string
            if script_text and 'videoId' in script_text:
                # Ищем videoId в JSON структуре
                import re
                video_ids = re.findall(r'"videoId":"([^"]+)"', script_text)
                video_links.extend(video_ids)
        
        # Альтернативный метод поиска по ссылкам
        if not video_links:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/watch?v=' in href and href not in video_links:
                    video_links.append(href)
        
        # Обработка найденных ссылок
        processed_links = []
        for link in video_links:
            if link.startswith('/watch?v='):
                video_id = link.split('watch?v=')[1].split('&')[0]
                processed_links.append(video_id)
            elif len(link) == 11:  # Длина YouTube video ID
                processed_links.append(link)
        
        if processed_links:
            # Берем первую найденную ссылку
            return f"https://www.youtube.com/watch?v={processed_links[0]}"
        
        return None
        
    except (requests.exceptions.RequestException, Exception) as e:
        print(f"Ошибка при поиске трейлера через BeautifulSoup: {e}")
        return None

def download_media_item(media_type, img_index, media_item_data, model, img_url, cast = []):
    # Получаем трейлер для фильмов и сериалов
    trailer_url = None
    if media_type in ["films", "serials"]:
        title = media_item_data.get("title") if media_type == "films" else media_item_data.get("name")
        release_date = media_item_data.get("release_date") if media_type == "films" else media_item_data.get("first_air_date")
        trailer_url = get_trailer_url(media_item_data["id"], media_type, title, release_date)

    if media_item_data[img_index] is None:
        site_img_path = ""
        local_img_path = ""
    else:
        site_img_path = f"{img_url}/{media_item_data[img_index]}"
        local_img_path = f"{media_type}/{media_item_data['id']}.jpg"


    if media_type == "films":
        release_date = media_item_data["release_date"]

        if media_item_data["release_date"] is None or media_item_data["release_date"] == "":
            release_date = None

    if media_type == "films":
        defaults = {
            "is_parsed": True,
            "title": media_item_data["title"],
            "budget": media_item_data["budget"],
            "revenue": media_item_data["revenue"],
            "overview": media_item_data["overview"],
            "site_img_path": site_img_path,
            "local_img_path": local_img_path,
            "release_date": release_date,
            "runtime": media_item_data["runtime"],
            "status": media_item_data["status"],
            "rating": media_item_data["vote_average"],
            "trailer_url": trailer_url,  # Добавлено поле для трейлера
        }
    elif media_type == "serials":
        defaults = {
            "is_parsed": True,
            "first_air_date": media_item_data["first_air_date"],
            "last_air_date": media_item_data["last_air_date"],
            "title": media_item_data["name"],
            "episodes": media_item_data["number_of_episodes"],
            "seasons": media_item_data["number_of_seasons"],
            "overview": media_item_data["overview"],
            "site_img_path": site_img_path,
            "local_img_path": local_img_path,
            "status": media_item_data["status"],
            "rating": media_item_data["vote_average"],
            "trailer_url": trailer_url,  # Добавлено поле для трейлера
        }
    elif media_type == "actors":
        defaults = {
            "is_parsed": True,
            "name": media_item_data["name"],
            "biography": media_item_data["biography"],
            "birthday": media_item_data["birthday"],
            "deathday": media_item_data["deathday"],
            "gender": media_item_data["gender"],
            "site_img_path": site_img_path,
            "local_img_path": local_img_path,
        }

    media_item_obj, created = model.get_or_create(
        search_id=media_item_data["id"],
        defaults=defaults
    )

    # Если объект уже существовал, обновляем трейлер
    if not created and media_type in ["films", "serials"] and trailer_url:
        media_item_obj.trailer_url = trailer_url
        media_item_obj.save()

    if media_type != "actors":
        for genre_item in media_item_data["genres"]:
            genre, created = Genre.objects.get_or_create(search_id=genre_item["id"], defaults={
                "name": genre_item["name"]
            })
            print(genre, created)
            media_item_obj.genres.add(genre)

    img_filepath = os.path.join(settings.MEDIA_ROOT, local_img_path)

    if not os.path.exists(img_filepath):
        if site_img_path != "":
            p = requests.get(site_img_path)
        
            with open(img_filepath, "wb") as out:
                out.write(p.content)

def parse_media_item(films, serials, actors, selected_item, selected_item_media_type, added_object_model, media_type, search_id):   
    url_parts = {
        "films": "movie",
        "serials": "tv",
        "actors": "person",
    }

    url_part = url_parts.get(media_type)

    img_url = "https://media.themoviedb.org/t/p/w220_and_h330_face/"            
    data_url = f"{BASE_URL}/{url_part}/{search_id}"

    if media_type != "actors":
        params = {
            "api_key": api_key,
            "language": "ru",
        }
    else:
        params = {
            "api_key": api_key,
            "language": "ru",
            "append_to_response": "movie_credits"
        }

    img_index = "profile_path" if media_type == "actors" else "poster_path"

    response = requests.get(data_url, params=params)
    response.raise_for_status()

    media_item_data = response.json()

    cast = []

    data_url = f"{BASE_URL}/{url_part}/{search_id}/credits"

    response = requests.get(data_url, params=params)
    response.raise_for_status()

    if len(response.json()["cast"]) < 10:
        cast = response.json()["cast"]
    else:
        cast = response.json()["cast"][0:10]

    delete_item = added_object_model.get(search_id=search_id)
    delete_item.delete()

    download_media_item(media_type, img_index, media_item_data, added_object_model, img_url, cast)

    if media_type == "actors":
        actor = actors.get(search_id=search_id)
        selected_item.actors.add(actor)
        if selected_item_media_type == "film" or selected_item_media_type == "films":
            actor.movies.add(selected_item)
        elif selected_item_media_type == "serial" or selected_item_media_type == "serials":
            actor.serials.add(selected_item)

        for item in cast:
            defaults = {
                "is_parsed": False,
                "title": item["title"]
            }

            if item["id"] != selected_item.search_id:
                film, created = films.get_or_create(search_id=item["id"], defaults=defaults)

                actor.movies.add(film)
                film.actors.add(actor)

    elif media_type == "films":
        film = films.get(search_id=search_id)
        selected_item.movies.add(film)
        film.actors.add(selected_item)
        for item in cast:
            defaults = {
                "is_parsed": False,
                "name": item["name"]
            }

            if item["id"] != selected_item.search_id:
                actor, created = actors.get_or_create(search_id=item["id"], defaults=defaults)

                film.actors.add(actor)
                actor.movies.add(film)

    elif media_type == "serials":
        serial = serials.get(search_id=search_id)
        selected_item.serials.add(serial)
        serial.actors.add(selected_item)
        for item in cast:
            defaults = {
                "is_parsed": False,
                "name": item["name"]
            }

            if item["id"] != selected_item.search_id:
                actor, created = actors.get_or_create(search_id=item["id"], defaults=defaults)

                serial.actors.add(actor)
                actor.serials.add(serial)

def parsing_media_items(request, media_type):
    start_page = request.POST.get('start_page')
    end_page = request.POST.get('end_page')

    films = Film.objects.all()
    serials = Serial.objects.all()
    actors = Actor.objects.all()

    models = {
        "films": films,
        "serials": serials,
        "actors": actors,
    }

    url_parts = {
        "films": "movie",
        "serials": "tv",
        "actors": "person",
    }

    model = models.get(media_type)

    url_part = url_parts.get(media_type)

    img_url = "https://media.themoviedb.org/t/p/w220_and_h330_face/"

    directory = f"{settings.MEDIA_ROOT}/{media_type}"
    os.makedirs(directory, exist_ok=True)

    try:
        for page_number in range(int(start_page), int(end_page) + 1):
            start = datetime.now()

            params = {
                "api_key": api_key,
                "language": "ru",
                "page": page_number,         
            }

            ids_url = f"{BASE_URL}/{url_part}/popular"
            response = requests.get(ids_url, params=params)
            response.raise_for_status()
            
            data = response.json()

            for media_item in data["results"]:
                is_exist = model.filter(search_id = media_item["id"]).exists()
                if is_exist:
                    is_parsed = model.get(search_id=media_item["id"]).is_parsed

                    if is_parsed:
                        continue

                if media_type == "actors" and media_item["known_for_department"] != "Acting":
                    continue
                
                data_url = f"{BASE_URL}/{url_part}/{media_item['id']}"

                if media_type != "actors":
                    params = {
                        "api_key": api_key,
                        "language": "ru",
                    }
                else:
                    params = {
                        "api_key": api_key,
                        "language": "ru",
                        "append_to_response": "movie_credits"
                    }
            
                img_index = "profile_path" if media_type == "actors" else "poster_path"

                response = requests.get(data_url, params=params)
                response.raise_for_status()

                media_item_data = response.json()

                cast = []

                data_url = f"{BASE_URL}/{url_part}/{media_item['id']}/credits"

                response = requests.get(data_url, params=params)
                response.raise_for_status()

                if len(response.json()["cast"]) < 10:
                    cast = response.json()["cast"]
                else:
                    cast = response.json()["cast"][0:10]

                if media_type == "films" and media_item_data["budget"] == 0:
                    continue

                if media_type != "actors" and media_item_data["vote_average"] < 5.2:
                    continue

                if media_type == "actors" and media_item_data["birthday"] is None:
                    continue

                if media_type == "actors":
                    ratings_sum = sum([item["vote_average"] for item in cast])
                    if ratings_sum < 0:
                        continue

                    if len(cast) == 0:
                        continue

                    average_rating = ratings_sum / len(cast)
                    if average_rating < 5.2:
                        continue

                download_media_item(media_type, img_index, media_item_data, model, img_url, cast)

                if media_type == "actors":
                    for item in cast:
                        defaults = {
                            "is_parsed": False,
                            "title": item["title"]
                        }

                        film, created = Film.objects.get_or_create(search_id=item["id"], defaults=defaults)

                        actor = actors.get(search_id=media_item["id"])
                        actor.movies.add(film)
                        film.actors.add(actor)
                elif media_type == "films":
                    for item in cast:
                        defaults = {
                            "is_parsed": False,
                            "name": item["name"]
                        }

                        actor, created = Actor.objects.get_or_create(search_id=item["id"], defaults=defaults)

                        film = films.get(search_id=media_item["id"])
                        film.actors.add(actor)
                        actor.movies.add(film)
                elif media_type == "serials":
                    for item in cast:
                        defaults = {
                            "is_parsed": False,
                            "name": item["name"]
                        }

                        actor, created = Actor.objects.get_or_create(search_id=item["id"], defaults=defaults)

                        serial = serials.get(search_id=media_item["id"])
                        serial.actors.add(actor)
                        actor.serials.add(serial)

            end = datetime.now()
            lead_time = end - start

            create_success_message(
                request, 
                media_type, 
                str(start.replace(microsecond=0)),
                str(lead_time.total_seconds()),
                f"Страница {page_number} успешно скачана!"
            )

    except requests.exceptions.ConnectionError:
        create_error_message(request, media_type, "VPN не включен!")
        return