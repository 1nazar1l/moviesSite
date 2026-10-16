"""Утилиты парсинга TMDB.

Тонкий фасад — вся логика в `services/`. Импортируй отсюда:
    from mainProject.tools import get_trailer_url, parsing_media_items
"""

from mainProject.services.media_download import download_media_item
from mainProject.services.messages import create_error_message, create_success_message, create_warning_message
from mainProject.services.parsing import (
    delete_all_media_items,
    delete_selected_media_items,
    parse_media_item,
    parsing_media_items,
)
from mainProject.services.tmdb import BASE_URL, URL_PARTS
from mainProject.services.trailers import get_trailer_url, get_trailer_url_bs4

__all__ = [
    "BASE_URL",
    "URL_PARTS",
    "download_media_item",
    "get_trailer_url",
    "get_trailer_url_bs4",
    "parse_media_item",
    "parsing_media_items",
    "delete_selected_media_items",
    "delete_all_media_items",
    "create_error_message",
    "create_warning_message",
    "create_success_message",
]
