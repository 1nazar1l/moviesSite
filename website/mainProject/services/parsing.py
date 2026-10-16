"""Парсинг TMDB: выбранный объект и страницы popular."""
import logging
import os

import requests
from django.conf import settings
from django.utils import timezone

from mainProject.models import Actor, Film, Serial

from .media_download import download_media_item
from .messages import create_error_message, create_success_message
from .tmdb import BASE_URL, URL_PARTS

logger = logging.getLogger(__name__)

POPULAR_IMG_URL = "https://media.themoviedb.org/t/p/w220_and_h330_face/"

MEDIA_MODELS = {
    "films": Film,
    "serials": Serial,
    "actors": Actor,
}


def delete_selected_media_items(request, media_type):
    media_ids = request.POST.getlist('media_ids')
    if not media_ids:
        create_error_message(request, media_type, "Не выбрано ни одного объекта для удаления")
        return

    try:
        model = MEDIA_MODELS.get(media_type)
        if not model:
            create_error_message(request, media_type, "Модель не найдена(delete_selected_media_items)")
            return

        start_time = timezone.now()
        media_items_to_delete = model.objects.filter(id__in=media_ids)

        if media_type != "actors":
            deleted_media_items = [[m.title, m.search_id] for m in media_items_to_delete]
        else:
            deleted_media_items = [[m.name, m.search_id] for m in media_items_to_delete]

        deleted_count = media_items_to_delete.delete()[0]

        lead_time = timezone.now() - start_time

        create_success_message(
            request, media_type,
            str(start_time.replace(microsecond=0)),
            str(lead_time.total_seconds()),
            f"Успешно удалено {deleted_count} объектов!",
        )

        for media_item in deleted_media_items:
            create_success_message(
                request, media_type,
                str(start_time.replace(microsecond=0)),
                "0.000000",
                f"Объект {media_item[0]}(id {media_item[1]}) успешно удалён!",
            )

    except Exception as e:
        create_error_message(request, media_type, f"Ошибка при удалении: {str(e)}")


def delete_all_media_items(request, media_type):
    model = MEDIA_MODELS.get(media_type)
    if not model:
        create_error_message(request, media_type, "Модель не найдена(delete_all_media_items)")
        return

    start_time = timezone.now()
    model.objects.all().delete()
    lead_time = timezone.now() - start_time

    create_success_message(
        request, media_type,
        str(start_time.replace(microsecond=0)),
        str(lead_time.total_seconds()),
        "Все объекты успешно удалены!",
    )


def parse_media_item(films, serials, actors, selected_item,
                     selected_item_media_type, added_object_model,
                     media_type, search_id):
    url_part = URL_PARTS.get(media_type)
    img_url = POPULAR_IMG_URL
    data_url = f"{BASE_URL}/{url_part}/{search_id}"

    if media_type != "actors":
        params = {"api_key": settings.TMDB_API_KEY, "language": "ru"}
    else:
        params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "ru",
            "append_to_response": "movie_credits",
        }

    img_index = "profile_path" if media_type == "actors" else "poster_path"

    response = requests.get(data_url, params=params)
    response.raise_for_status()
    media_item_data = response.json()

    data_url = f"{BASE_URL}/{url_part}/{search_id}/credits"
    response = requests.get(data_url, params=params)
    response.raise_for_status()

    cast_raw = response.json()["cast"]
    cast = cast_raw if len(cast_raw) < 10 else cast_raw[:10]

    delete_item = added_object_model.get(search_id=search_id)
    delete_item.delete()

    download_media_item(media_type, img_index, media_item_data, added_object_model, img_url)

    if media_type == "actors":
        actor = actors.get(search_id=search_id)
        if selected_item_media_type in ("film", "films"):
            actor.movies.add(selected_item)
        elif selected_item_media_type in ("serial", "serials"):
            actor.serials.add(selected_item)

        for item in cast:
            defaults = {"is_parsed": False, "title": item["title"]}
            if item["id"] != selected_item.search_id:
                film, created = films.get_or_create(search_id=item["id"], defaults=defaults)
                actor.movies.add(film)

    elif media_type == "films":
        film = films.get(search_id=search_id)
        selected_item.movies.add(film)
        for item in cast:
            defaults = {"is_parsed": False, "name": item["name"]}
            if item["id"] != selected_item.search_id:
                actor, created = actors.get_or_create(search_id=item["id"], defaults=defaults)
                actor.movies.add(film)

    elif media_type == "serials":
        serial = serials.get(search_id=search_id)
        selected_item.serials.add(serial)
        for item in cast:
            defaults = {"is_parsed": False, "name": item["name"]}
            if item["id"] != selected_item.search_id:
                actor, created = actors.get_or_create(search_id=item["id"], defaults=defaults)
                actor.serials.add(serial)


def parsing_media_items(request, media_type):
    start_page = request.POST.get('start_page')
    end_page = request.POST.get('end_page')

    films = Film.objects.all()
    serials = Serial.objects.all()
    actors = Actor.objects.all()

    models = {"films": films, "serials": serials, "actors": actors}

    url_part = URL_PARTS.get(media_type)
    model = models.get(media_type)
    img_url = POPULAR_IMG_URL

    directory = f"{settings.MEDIA_ROOT}/{media_type}"
    os.makedirs(directory, exist_ok=True)

    try:
        for page_number in range(int(start_page), int(end_page) + 1):
            start = timezone.now()

            params = {
                "api_key": settings.TMDB_API_KEY,
                "language": "ru",
                "page": page_number,
            }

            ids_url = f"{BASE_URL}/{url_part}/popular"
            response = requests.get(ids_url, params=params)
            response.raise_for_status()
            data = response.json()

            for media_item in data["results"]:
                is_exist = model.filter(search_id=media_item["id"]).exists()
                if is_exist and model.get(search_id=media_item["id"]).is_parsed:
                    continue

                if media_type == "actors" and media_item["known_for_department"] != "Acting":
                    continue

                data_url = f"{BASE_URL}/{url_part}/{media_item['id']}"

                if media_type != "actors":
                    params = {"api_key": settings.TMDB_API_KEY, "language": "ru"}
                else:
                    params = {
                        "api_key": settings.TMDB_API_KEY,
                        "language": "ru",
                        "append_to_response": "movie_credits",
                    }

                img_index = "profile_path" if media_type == "actors" else "poster_path"

                response = requests.get(data_url, params=params)
                response.raise_for_status()
                media_item_data = response.json()

                data_url = f"{BASE_URL}/{url_part}/{media_item['id']}/credits"
                response = requests.get(data_url, params=params)
                response.raise_for_status()

                cast_raw = response.json()["cast"]
                cast = cast_raw if len(cast_raw) < 10 else cast_raw[:10]

                if media_type == "films" and media_item_data["budget"] == 0:
                    continue
                if media_type != "actors" and media_item_data["vote_average"] < 5.2:
                    continue
                if media_type == "actors" and media_item_data["birthday"] is None:
                    continue

                if media_type == "actors":
                    ratings_sum = sum(item["vote_average"] for item in cast)
                    if ratings_sum < 0 or len(cast) == 0:
                        continue
                    if ratings_sum / len(cast) < 5.2:
                        continue

                download_media_item(media_type, img_index, media_item_data, model, img_url)

                if media_type == "actors":
                    for item in cast:
                        defaults = {"is_parsed": False, "title": item["title"]}
                        film, created = Film.objects.get_or_create(
                            search_id=item["id"], defaults=defaults,
                        )
                        actor = actors.get(search_id=media_item["id"])
                        actor.movies.add(film)

                elif media_type == "films":
                    for item in cast:
                        defaults = {"is_parsed": False, "name": item["name"]}
                        actor, created = Actor.objects.get_or_create(
                            search_id=item["id"], defaults=defaults,
                        )
                        film = films.get(search_id=media_item["id"])
                        actor.movies.add(film)

                elif media_type == "serials":
                    for item in cast:
                        defaults = {"is_parsed": False, "name": item["name"]}
                        actor, created = Actor.objects.get_or_create(
                            search_id=item["id"], defaults=defaults,
                        )
                        serial = serials.get(search_id=media_item["id"])
                        actor.serials.add(serial)

            lead_time = timezone.now() - start
            create_success_message(
                request, media_type,
                str(start.replace(microsecond=0)),
                str(lead_time.total_seconds()),
                f"Страница {page_number} успешно скачана!",
            )

    except requests.exceptions.ConnectionError:
        create_error_message(request, media_type, "VPN не включен!")
        return