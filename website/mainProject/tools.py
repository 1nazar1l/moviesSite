import requests
import os
from environs import env
from datetime import datetime, date

from .models import Film, Serial, Actor, Message

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

def download_movies_by_actors(request, media_type, ids):
    models = {
        "films": Film,
        "serials": Serial,
        "actors": Actor,
    }

    model = models.get(media_type)

    img_url = "https://media.themoviedb.org/t/p/w220_and_h330_face/"

    try:
        url = f"{BASE_URL}/movie/{ids[0]}"

        params = {
            "api_key": api_key,
            "language": "en",
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

    except requests.exceptions.ConnectionError:
        create_error_message(request, media_type, "VPN не включен!")
        return
    
    added_films = 0

    start = datetime.now()

    for id in ids:
        is_exist = model.objects.filter(search_id = id).exists()
        if is_exist:
            continue

        url = f"{BASE_URL}/movie/{id}"

        params = {
            "api_key": api_key,
            "language": "en",
        }

        img_index = "poster_path"

        response = requests.get(url, params=params)
        response.raise_for_status()

        media_item = response.json()

        download_media_item(media_type, img_index, media_item, model, img_url)
        added_films += 1
    end = datetime.now()
    lead_time = end - start

    create_success_message(request, media_type, start, lead_time, f"Успешно добавлено {added_films} объектов!")

def download_media_item(media_type, img_index, media_item_data, model, img_url, cast = []):
    if media_item_data[img_index] is None:
        site_img_path = ""
        local_img_path = ""
    else:
        site_img_path = f"{img_url}/{media_item_data[img_index]}"
        local_img_path = f"images/{media_type}/{media_item_data["id"]}.jpg"


    if media_type == "films":
        release_date = media_item_data["release_date"]

        if media_item_data["release_date"] is None or media_item_data["release_date"] == "":
            release_date = date(2050, 1, 1)

    if media_type == "films":
        actors = []
        for actor in cast:
            if actor["profile_path"] is None:
                site_actor_img_path = ""
                local_actor_img_path = ""
            else:
                site_actor_img_path = f"{img_url}/{actor["profile_path"]}"
                local_actor_img_path = f"images/films/{actor["id"]}.jpg"
            
            names = actor["name"].split(" ")
            if (len(names) == 2):
                first_name, second_name = names[0], names[1]
            else:
                first_name = names[0]
                second_name = ""

            actors.append({
                "id": actor["id"],
                "first_name": first_name.strip(),
                "second_name": second_name.strip(),
                "site_img_path": site_actor_img_path,
                "local_img_path": local_actor_img_path
            })

        defaults = {
            "id": media_item_data["id"],
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
            "genres": [{"id": genre["id"], "name": genre["name"]} for genre in media_item_data["genres"]],
            "actors": actors
        }

    elif media_type == "serials":
        actors = []
        for actor in cast:
            if actor["profile_path"] is None:
                site_actor_img_path = ""
                local_actor_img_path = ""
            else:
                site_actor_img_path = f"{img_url}/{actor["profile_path"]}"
                local_actor_img_path = f"images/serials/{actor["id"]}.jpg"
            
            names = actor["name"].split(" ")
            if (len(names) == 2):
                first_name, second_name = names[0], names[1]
            else:
                first_name = names[0]
                second_name = ""

            actors.append({
                "id": actor["id"],
                "first_name": first_name.strip(),
                "second_name": second_name.strip(),
                "site_img_path": site_actor_img_path,
                "local_img_path": local_actor_img_path
            })

        defaults = {
            "id": media_item_data["id"],
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
            "genres": [{"id": genre["id"], "name": genre["name"]} for genre in media_item_data["genres"]],
            "actors": actors
        }
    elif media_type == "actors":
        films = []
        for film in cast:
            if film["poster_path"] is None:
                site_film_img_path = ""
                local_film_img_path = ""
            else:
                site_film_img_path = f"{img_url}/{film["poster_path"]}"
                local_film_img_path = f"images/films/{film["id"]}.jpg"
            
            title = film["title"]

            films.append({
                "id": film["id"],
                "title": title,
                "site_img_path": site_film_img_path,
                "local_img_path": local_film_img_path
            })

        defaults = {
            "id": media_item_data["id"],
            "name": media_item_data["name"],
            "biography": media_item_data["biography"],
            "birthday": media_item_data["birthday"],
            "deathday": media_item_data["deathday"],
            "gender": media_item_data["gender"],
            "site_img_path": site_img_path,
            "local_img_path": local_img_path,
            "movies": films
        }

    media_item_obj, created = model.objects.get_or_create(
        search_id=media_item_data["id"],
        defaults=defaults
    )

    img_filepath = os.path.join("mainProject/static", local_img_path)

    if not os.path.exists(img_filepath):
        if site_img_path != "":
            p = requests.get(site_img_path)
        
            with open(img_filepath, "wb") as out:
                out.write(p.content)

def parsing_media_items(request, media_type):
    start_page = request.POST.get('start_page')
    end_page = request.POST.get('end_page')

    models = {
        "films": Film,
        "serials": Serial,
        "actors": Actor,
    }

    url_parts = {
        "films": "movie",
        "serials": "tv",
        "actors": "person",
    }

    model = models.get(media_type)

    url_part = url_parts.get(media_type)

    img_url = "https://media.themoviedb.org/t/p/w220_and_h330_face/"

    directory = f"mainProject/static/images/{media_type}"
    os.makedirs(directory, exist_ok=True)

    try:
        for page_number in range(int(start_page), int(end_page) + 1):
            start = datetime.now()

            params = {
                "api_key": api_key,
                "language": "en",
                "page": page_number,         
            }

            ids_url = f"{BASE_URL}/{url_part}/popular"
            response = requests.get(ids_url, params=params)
            response.raise_for_status()
            
            data = response.json()

            for media_item in data["results"]:
                is_exist = model.objects.filter(search_id = media_item["id"]).exists()
                if is_exist:
                    continue

                if media_type == "actors" and media_item["known_for_department"] != "Acting":
                    continue
                
                data_url = f"{BASE_URL}/{url_part}/{media_item["id"]}"

                if media_type != "actors":
                    params = {
                        "api_key": api_key,
                        "language": "en",
                    }

                    img_index = "poster_path"
                else:
                    params = {
                        "api_key": api_key,
                        "language": "en",
                        "append_to_response": "movie_credits"
                    }

                    img_index = "profile_path"

                response = requests.get(data_url, params=params)
                response.raise_for_status()

                media_item_data = response.json()

                cast = []

                data_url = f"{BASE_URL}/{url_part}/{media_item["id"]}/credits"

                response = requests.get(data_url, params=params)
                response.raise_for_status()

                if len(response.json()["cast"]) < 10:
                    cast = response.json()["cast"]
                else:
                    cast = response.json()["cast"][0:10]

                if media_type == "films" and media_item_data["budget"] == 0:
                    continue

                download_media_item(media_type, img_index, media_item_data, model, img_url, cast)

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
