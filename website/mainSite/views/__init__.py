"""Пакет views mainSite.

Реэкспорт публичного API — `mainSite/urls.py` импортирует `from . import views`
и вызывает `views.mainPage`, `views.authPage` и т.д.
"""

from .admin_tools import add_new_item
from .auth import authPage, regPage, signOut
from .comments import create_comment
from .favorites import add_to_favorite, remove_from_favorite
from .lists import (
    add_item_to_list,
    add_list,
    delete_item_from_list,
    delete_list,
    edit_list,
    listPage,
    userListPage,
)
from .pages import actorsPage, errorPage, filmsPage, itemPage, mainPage, searchPage, serialsPage
from .profile import add_avatar, profilePage, update_user_info, userPage

__all__ = [
    "mainPage",
    "authPage",
    "regPage",
    "filmsPage",
    "serialsPage",
    "actorsPage",
    "searchPage",
    "profilePage",
    "userPage",
    "itemPage",
    "errorPage",
    "signOut",
    "update_user_info",
    "add_avatar",
    "create_comment",
    "add_to_favorite",
    "remove_from_favorite",
    "add_list",
    "delete_list",
    "edit_list",
    "listPage",
    "userListPage",
    "add_item_to_list",
    "delete_item_from_list",
    "add_new_item",
]
