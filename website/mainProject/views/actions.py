"""POST-обёртки: удаление, парсинг, очистка сообщений."""
from django.shortcuts import redirect

from mainProject.models import Message
from mainProject.tools import (
    delete_all_media_items,
    delete_selected_media_items,
    parsing_media_items,
)


# --- Delete selected -----------------------------------------------------

def delete_films(request):
    delete_selected_media_items(request, "films")
    return redirect('films')


def delete_serials(request):
    delete_selected_media_items(request, "serials")
    return redirect('serials')


def delete_actors(request):
    delete_selected_media_items(request, "actors")
    return redirect('actors')


# --- Delete all ----------------------------------------------------------

def delete_all_films(request):
    delete_all_media_items(request, "films")
    return redirect('films')


def delete_all_serials(request):
    delete_all_media_items(request, "serials")
    return redirect('serials')


def delete_all_actors(request):
    delete_all_media_items(request, "actors")
    return redirect('actors')


# --- Parse ---------------------------------------------------------------

def parse_films(request):
    parsing_media_items(request, "films")
    return redirect('films')


def parse_serials(request):
    parsing_media_items(request, "serials")
    return redirect('serials')


def parse_actors(request):
    parsing_media_items(request, "actors")
    return redirect('actors')


# --- Misc ----------------------------------------------------------------

def clear_messages(request):
    Message.objects.all().delete()
    next_url = request.POST.get('next', '/films/')
    return redirect(next_url)