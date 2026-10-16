"""Создание/обновление объекта Film/Serial/Actor из данных TMDB и скачивание постера."""

import logging
import os

import requests
from django.conf import settings

from mainProject.models import Genre

from .trailers import get_trailer_url

logger = logging.getLogger(__name__)


def download_media_item(media_type, img_index, media_item_data, model, img_url):
    """Создать/обновить Film|Serial|Actor, скачать постер."""
    trailer_url = None
    if media_type in ["films", "serials"]:
        title = media_item_data.get("title") if media_type == "films" else media_item_data.get("name")
        release_date = (
            media_item_data.get("release_date")
            if media_type == "films"
            else media_item_data.get("first_air_date")
        )
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
            "trailer_url": trailer_url,
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
            "trailer_url": trailer_url,
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

    manager = model.objects if hasattr(model, "objects") else model
    media_item_obj, created = manager.get_or_create(
        search_id=media_item_data["id"],
        defaults=defaults,
    )

    if not created and media_type in ["films", "serials"] and trailer_url:
        media_item_obj.trailer_url = trailer_url
        media_item_obj.save()

    if media_type != "actors":
        for genre_item in media_item_data["genres"]:
            genre, created = Genre.objects.get_or_create(
                search_id=genre_item["id"],
                defaults={"name": genre_item["name"]},
            )
            logger.debug("Жанр %s (created=%s) для объекта %s", genre, created, media_item_obj)
            media_item_obj.genres.add(genre)

    img_filepath = os.path.join(settings.MEDIA_ROOT, local_img_path)

    if not os.path.exists(img_filepath) and site_img_path:
        try:
            response = requests.get(site_img_path, timeout=10)
            response.raise_for_status()
            with open(img_filepath, "wb") as out:
                out.write(response.content)
        except requests.RequestException:
            logger.warning("Не удалось скачать постер %s", site_img_path)
