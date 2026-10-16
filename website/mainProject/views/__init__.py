"""Пакет views mainProject. Реэкспорт публичного API."""

from .actions import (
    clear_messages,
    delete_actors,
    delete_all_actors,
    delete_all_films,
    delete_all_serials,
    delete_films,
    delete_serials,
    parse_actors,
    parse_films,
    parse_serials,
)
from .panels import actors_admin_panel, films_admin_panel, genres_admin_panel, serials_admin_panel

__all__ = [
    "films_admin_panel",
    "serials_admin_panel",
    "actors_admin_panel",
    "genres_admin_panel",
    "delete_films",
    "delete_serials",
    "delete_actors",
    "delete_all_films",
    "delete_all_serials",
    "delete_all_actors",
    "parse_films",
    "parse_serials",
    "parse_actors",
    "clear_messages",
]
