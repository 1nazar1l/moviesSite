from django.shortcuts import render
from .tools import (
    delete_selected_media_items,
    delete_all_media_items,
    start_parsing_media_items
)

from .models import Film, Serial, Actor

from django.shortcuts import redirect

def home(request):
    return render(request, "home.html")

def films_admin_panel(request):
    all_films = Film.objects.all()

    films = all_films.order_by('-id')[0:100]

    messages = request.session.get('custom_messages', [])
    messages = messages[::-1]

    return render(request, "films.html", context={
        "films": films,
        "messages": messages               
    })

def serials_admin_panel(request):
    all_serials = Serial.objects.all()

    serials = all_serials.order_by('-id')[0:100]

    messages = request.session.get('custom_messages', [])
    messages = messages[::-1]

    return render(request, "serials.html", context={
        "serials": serials,
        "messages": messages               
    })

def actors_admin_panel(request):
    all_actors = Actor.objects.all()

    actors = all_actors.order_by('-id')

    messages = request.session.get('custom_messages', [])
    messages = messages[::-1]

    return render(request, "actors.html", context={
        "actors": actors,
        "messages": messages               
    })


def delete_films(request):
    messages = []
    messages_block = []

    media_type = "films"

    delete_selected_media_items(request, media_type, messages, messages_block)
    
    return redirect('films')

def delete_serials(request):
    messages = []
    messages_block = []

    media_type = "serials"

    delete_selected_media_items(request, media_type, messages, messages_block)
    
    return redirect('serials')

def delete_actors(request):
    messages = []
    messages_block = []

    media_type = "actors"

    delete_selected_media_items(request, media_type, messages, messages_block)
    
    return redirect('actors')


def delete_all_films(request):
    messages = []
    messages_block = []

    media_type = "films"

    delete_all_media_items(request, media_type, messages, messages_block)

    return redirect('films')

def delete_all_serials(request):
    messages = []
    messages_block = []

    media_type = "serials"

    delete_all_media_items(request, media_type, messages, messages_block)

    return redirect('serials')

def delete_all_actors(request):
    messages = []
    messages_block = []

    media_type = "actors"

    delete_all_media_items(request, media_type, messages, messages_block)

    return redirect('actors')


def parse_films(request):
    messages = []
    messages_block = []

    media_type = "films"

    start_parsing_media_items(request, media_type, messages, messages_block)

    return redirect('films')

def parse_serials(request):
    messages = []
    messages_block = []

    media_type = "serials"

    start_parsing_media_items(request, media_type, messages, messages_block)

    return redirect('serials')

def parse_actors(request):
    messages = []
    messages_block = []

    media_type = "actors"

    start_parsing_media_items(request, media_type, messages, messages_block)

    return redirect('actors')


def clear_messages(request):
    if 'custom_messages' not in request.session:
        request.session['custom_messages'] = []
    
    request.session['custom_messages'] = [
        ["Сообщения очищены"]
    ]
    request.session.modified = True
    
    return redirect('films')
