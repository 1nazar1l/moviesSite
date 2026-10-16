"""Клиент TMDB API — тонкая обёртка над requests."""

import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.themoviedb.org/3"

URL_PARTS = {
    "films": "movie",
    "serials": "tv",
    "actors": "person",
}


def tmdb_get(path: str, **params):
    """
    GET-запрос к TMDB с автоматической подстановкой api_key и language.

    :param path: путь после BASE_URL, например 'movie/550'
    :param params: дополнительные параметры (page, append_to_response и т.п.)
    :returns: распарсенный JSON (dict)
    :raises requests.HTTPError: если статус != 2xx
    """
    params.setdefault("api_key", settings.TMDB_API_KEY)
    params.setdefault("language", "ru")
    response = requests.get(f"{BASE_URL}/{path}", params=params)
    response.raise_for_status()
    return response.json()
