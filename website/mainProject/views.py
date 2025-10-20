from django.shortcuts import render
from .tools import (
    delete_selected_media_items,
    delete_all_media_items,
    parsing_media_items,
    download_movies_by_actors
)

from .models import Film, Serial, Actor, Message

from django.shortcuts import redirect

from django.db.models import Q

def films_admin_panel(request):
    all_films = Film.objects.all()
    films = all_films.order_by('-id')

    messages = Message.objects.all().order_by('-id')

    messages_type = {
        "success": 0,
        "warning": 0,
        "error": 0,
        "clear": 0
    }

    for message in messages:
        messages_type[message.message_type] += 1

    id_search = request.GET.get("id_search")

    if id_search:
        films = films.filter(
            Q(search_id__icontains=id_search)
        )

    return render(request, "adminPanel/films.html", context={
        "films": films,
        "messages": messages,
        "messages_type": messages_type      
    })

def serials_admin_panel(request):
    all_serials = Serial.objects.all()

    serials = all_serials.order_by('-id')[0:100]

    messages = Message.objects.all().order_by('-id')

    messages_type = {
        "success": 0,
        "warning": 0,
        "error": 0,
        "clear": 0
    }

    for message in messages:
        messages_type[message.message_type] += 1

    return render(request, "adminPanel/serials.html", context={
        "serials": serials,
        "messages": messages,
        "messages_type": messages_type      
    })

def actors_admin_panel(request):
    all_actors = Actor.objects.all()

    actors = all_actors.order_by('-id')

    messages = Message.objects.all().order_by('-id')

    messages_type = {
        "success": 0,
        "warning": 0,
        "error": 0,
        "clear": 0
    }

    for message in messages:
        messages_type[message.message_type] += 1

    return render(request, "adminPanel/actors.html", context={
        "actors": actors,
        "messages": messages,
        "messages_type": messages_type      
    })


def delete_films(request):
    media_type = "films"

    delete_selected_media_items(request, media_type)
    
    return redirect('films')

def delete_serials(request):
    media_type = "serials"

    delete_selected_media_items(request, media_type)
    
    return redirect('serials')

def delete_actors(request):
    media_type = "actors"

    delete_selected_media_items(request, media_type)
    
    return redirect('actors')


def delete_all_films(request):
    media_type = "films"

    delete_all_media_items(request, media_type)

    return redirect('films')

def delete_all_serials(request):
    media_type = "serials"

    delete_all_media_items(request, media_type)

    return redirect('serials')

def delete_all_actors(request):
    media_type = "actors"

    delete_all_media_items(request, media_type)

    return redirect('actors')


def parse_films(request):
    media_type = "films"

    parsing_media_items(request, media_type)

    return redirect('films')

def parse_serials(request):
    media_type = "serials"

    parsing_media_items(request, media_type)

    return redirect('serials')

def parse_actors(request):
    media_type = "actors"

    parsing_media_items(request, media_type)

    return redirect('actors')

def clear_messages(request):
    Message.objects.all().delete()

    next_url = request.POST.get('next', '/films/')
    return redirect(next_url)

    

def parse_movies_by_actors(request):
    media_type = "films"

    films = Film.objects.all()
    actors = Actor.objects.all()

    ids = []
    for actor in actors:
        for id in actor.movies:
            ids.append(id)

    ids = list(set(ids))

    for film in films:
        if film.search_id in ids:
            ids.remove(film.search_id)

    ids = list(set(ids))

    download_movies_by_actors(request, media_type, ids)

    return redirect('films')

