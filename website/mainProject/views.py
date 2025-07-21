from django.shortcuts import render
from .tools import (
    parse_media_items,
    update_info,
    delete_selected_media_items,
    delete_all_media_items,
    parse_actors_item
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
        "upgraded_fields": [
            "search_id", 
            "title", 
            "overview", 
            "local_img_path", 
            "site_img_path",
            "release_date", 
            "rating", 
            "title_lang", 
            "is_adult"
        ],
        "messages": messages               
    })

def serials_admin_panel(request):
    all_serials = Serial.objects.all()

    serials = all_serials.order_by('-id')[0:100]

    messages = request.session.get('custom_messages', [])
    messages = messages[::-1]

    return render(request, "serials.html", context={
        "serials": serials,
        "upgraded_fields": [
            "search_id", 
            "title", 
            "overview", 
            "local_img_path", 
            "site_img_path",
            "release_date", 
            "rating", 
            "title_lang", 
            "is_adult"
        ],
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

    parse_media_items(request, media_type, messages, messages_block)

    return redirect('films')

def parse_serials(request):
    messages = []
    messages_block = []

    media_type = "serials"

    parse_media_items(request, media_type, messages, messages_block)

    return redirect('serials')

def parse_actors(request):
    messages = []
    messages_block = []

    media_type = "actors"

    parse_actors_item(request, media_type, messages, messages_block)

    return redirect('actors')

def update_films_info(request):
    messages = []
    messages_block = []

    media_type = "films"

    update_info(request, media_type, messages, messages_block)
    
    return redirect('films')

def update_serials_info(request):
    messages = []
    messages_block = []

    media_type = "serials"

    update_info(request, media_type, messages, messages_block)
    
    return redirect('serials')


def clear_messages(request):
    if 'custom_messages' not in request.session:
        request.session['custom_messages'] = []
    
    request.session['custom_messages'] = [
        ["Сообщения очищены", "end"]
    ]
    request.session.modified = True
    
    return redirect('films')
