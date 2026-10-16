"""Обёртки для вызова парсинга из UI (админские действия на клиентской части)."""
import requests
from django.shortcuts import redirect

from mainProject.models import Actor, Film, Serial
from mainProject.tools import parse_media_item


def add_new_item(request):
    if not request.POST:
        return redirect('errorPage', media_type='error')

    selected_object_search_id = request.POST.get("selected_object_search_id")
    selected_object_media_type = request.POST.get("selected_object_media_type")
    added_object_search_id = request.POST.get("added_object_search_id")
    added_object_media_type = request.POST.get("added_object_media_type")

    films = Film.objects.all()
    serials = Serial.objects.all()
    actors = Actor.objects.all()

    models = {"films": films, "serials": serials, "actors": actors}
    added_object_model = models.get(added_object_media_type + "s")
    selected_item_model = models.get(selected_object_media_type)
    selected_item = selected_item_model.get(search_id=selected_object_search_id)

    try:
        parse_media_item(
            films, serials, actors,
            selected_item, selected_object_media_type,
            added_object_model, added_object_media_type + "s",
            added_object_search_id,
        )
        return redirect(
            'itemPage',
            media_type=added_object_media_type,
            search_id=added_object_search_id,
        )
    except requests.exceptions.ConnectionError:
        return redirect('errorPage', media_type='error')