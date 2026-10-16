"""Внутренние хелперы для views mainSite."""
import os

from django.conf import settings


def set_previous_page_values(request, **kwargs):
    request.session.modified = True

    if 'previous_page_values' not in request.session:
        request.session["previous_page_values"] = []

    for key, value in kwargs.items():
        request.session["previous_page_values"].append({key: value})


def get_previous_page_values(request):
    return request.session.get("previous_page_values", [])


def check_path(item):
    """Обнуляет local_img_path, если файл не существует на диске."""
    if hasattr(item, 'local_img_path'):
        img_path = os.path.join(settings.MEDIA_ROOT, str(item.local_img_path))
        if not os.path.exists(img_path):
            item.local_img_path = ""
    else:
        img_path = os.path.join(settings.MEDIA_ROOT, item["local_img_path"])
        if not os.path.exists(img_path):
            item["local_img_path"] = ""