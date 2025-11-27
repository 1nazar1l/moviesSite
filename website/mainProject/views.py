from django.shortcuts import render
from .tools import (
    delete_selected_media_items,
    delete_all_media_items,
    parsing_media_items,
)

from .models import Film, Serial, Actor, Message, Genre

from django.shortcuts import redirect

from django.db.models import Q

from django.db.models import Exists, OuterRef


def films_admin_panel(request):
    title_search = request.GET.get('title_search', '').strip()
    budget_min = request.GET.get('budget_min', '').strip()
    budget_max = request.GET.get('budget_max', '').strip()
    revenue_min = request.GET.get('revenue_min', '').strip()
    revenue_max = request.GET.get('revenue_max', '').strip()
    release_date_min = request.GET.get('release_date_min', '').strip()
    release_date_max = request.GET.get('release_date_max', '').strip()
    duration_min = request.GET.get('duration_min', '').strip()
    duration_max = request.GET.get('duration_max', '').strip()
    rating_min = request.GET.get('rating_min', '').strip()
    rating_max = request.GET.get('rating_max', '').strip()
    selected_genres = request.GET.getlist('genres')
    is_parsed = request.GET.get('is_parsed', '').strip()
    is_not_parsed = request.GET.get('is_not_parsed', '').strip()
    
    films = Film.objects.all()
    
    if title_search:
        films_with_default_search = films.filter(
            title__icontains=title_search
        )
        films_with_capitalize_search = films.filter(
            title__icontains=title_search.capitalize()
        )
        films = films_with_default_search.union(films_with_capitalize_search, all=True)    
    if budget_min:
        films = films.filter(budget__gte=budget_min)
    if budget_max:
        films = films.filter(budget__lte=budget_max)
    
    if revenue_min:
        films = films.filter(revenue__gte=revenue_min)
    if revenue_max:
        films = films.filter(revenue__lte=revenue_max)
    
    if release_date_min:
        films = films.filter(release_date__gte=release_date_min)
    if release_date_max:
        films = films.filter(release_date__lte=release_date_max)
    
    if duration_min:
        films = films.filter(duration__gte=duration_min)
    if duration_max:
        films = films.filter(duration__lte=duration_max)
    
    if rating_min:
        films = films.filter(rating__gte=rating_min)
    if rating_max:
        films = films.filter(rating__lte=rating_max)
    
    if selected_genres:
        films = films.filter(genres__search_id__in=selected_genres).distinct()
          
    if is_parsed:
        films = films.filter(is_parsed=True)

    if is_not_parsed:
        films = films.filter(is_parsed=False)

    films = set(list(films))

    messages = Message.objects.all().order_by('-id')

    messages_type = {
        "success": 0,
        "warning": 0,
        "error": 0,
        "clear": 0
    }

    for message in messages:
        messages_type[message.message_type] += 1

    genres = Genre.objects.all()

    return render(request, "adminPanel/films.html", context={
        "films": films,
        "messages": messages,
        "messages_type": messages_type,
        "genres": genres,
        "filter_values": {
            "title_search": title_search,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "revenue_min": revenue_min,
            "revenue_max": revenue_max,
            "release_date_min": release_date_min,
            "release_date_max": release_date_max,
            "duration_min": duration_min,
            "duration_max": duration_max,
            "rating_min": rating_min,
            "rating_max": rating_max,
            "selected_genres": selected_genres,
            "is_parsed": is_parsed,
            "is_not_parsed": is_not_parsed
        }
    })

def serials_admin_panel(request):
    title_search = request.GET.get('title_search', '').strip()
    episodes_min = request.GET.get('episodes_min', '').strip()
    episodes_max = request.GET.get('episodes_max', '').strip()
    seasons_min = request.GET.get('seasons_min', '').strip()
    seasons_max = request.GET.get('seasons_max', '').strip()
    first_air_date_min = request.GET.get('first_air_date_min', '').strip()
    first_air_date_max = request.GET.get('first_air_date_max', '').strip()
    last_air_date_min = request.GET.get('last_air_date_min', '').strip()
    last_air_date_max = request.GET.get('last_air_date_max', '').strip()
    rating_min = request.GET.get('rating_min', '').strip()
    rating_max = request.GET.get('rating_max', '').strip()
    status_filter = request.GET.get('status', '').strip()
    selected_genres = request.GET.getlist('genres')
    is_parsed = request.GET.get('is_parsed', '').strip()
    is_not_parsed = request.GET.get('is_not_parsed', '').strip()
    
    serials = Serial.objects.all()
    
    if title_search:
        serials_with_default_search = serials.filter(
            title__icontains=title_search
        )
        serials_with_capitalize_search = serials.filter(
            title__icontains=title_search.capitalize()
        )
        serials = serials_with_default_search.union(serials_with_capitalize_search, all=True) 
    if episodes_min:
        serials = serials.filter(episodes__gte=episodes_min)
    if episodes_max:
        serials = serials.filter(episodes__lte=episodes_max)
    
    if seasons_min:
        serials = serials.filter(seasons__gte=seasons_min)
    if seasons_max:
        serials = serials.filter(seasons__lte=seasons_max)
    
    if first_air_date_min:
        serials = serials.filter(first_air_date__gte=first_air_date_min)
    if first_air_date_max:
        serials = serials.filter(first_air_date__lte=first_air_date_max)
    
    if last_air_date_min:
        serials = serials.filter(last_air_date__gte=last_air_date_min)
    if last_air_date_max:
        serials = serials.filter(last_air_date__lte=last_air_date_max)
    
    if rating_min:
        serials = serials.filter(rating__gte=rating_min)
    if rating_max:
        serials = serials.filter(rating__lte=rating_max)
    
    if status_filter:
        serials = serials.filter(status=status_filter)
    
    if selected_genres:
        serials = serials.filter(genres__search_id__in=selected_genres).distinct()
    
    if is_parsed:
        serials = serials.filter(is_parsed=True)

    if is_not_parsed:
        serials = serials.filter(is_parsed=False)
    
    serials = set(list(serials))

    messages = Message.objects.all().order_by('-id')

    messages_type = {
        "success": 0,
        "warning": 0,
        "error": 0,
        "clear": 0
    }

    for message in messages:
        messages_type[message.message_type] += 1
    
    genres = Genre.objects.all()

    return render(request, "adminPanel/serials.html", context={
        "serials": serials,
        "messages": messages,
        "messages_type": messages_type,
        "genres": genres,
        "filter_values": {
            "title_search": title_search,
            "episodes_min": episodes_min,
            "episodes_max": episodes_max,
            "seasons_min": seasons_min,
            "seasons_max": seasons_max,
            "first_air_date_min": first_air_date_min,
            "first_air_date_max": first_air_date_max,
            "last_air_date_min": last_air_date_min,
            "last_air_date_max": last_air_date_max,
            "rating_min": rating_min,
            "rating_max": rating_max,
            "status": status_filter,
            "selected_genres": selected_genres,
            "is_parsed": is_parsed,
            "is_not_parsed": is_not_parsed
        }
    })

def actors_admin_panel(request):
    name_search = request.GET.get('name_search', '').strip()
    birthday_min = request.GET.get('birthday_min', '').strip()
    birthday_max = request.GET.get('birthday_max', '').strip()
    deathday_min = request.GET.get('deathday_min', '').strip()
    deathday_max = request.GET.get('deathday_max', '').strip()
    gender_filter = request.GET.get('gender', '').strip()
    project_search = request.GET.get('project_search', '').strip()
    is_parsed = request.GET.get('is_parsed', '').strip()
    is_not_parsed = request.GET.get('is_not_parsed', '').strip()

    actors = Actor.objects.all()
    
    if name_search:
        actors_with_default_search = actors.filter(
            name__icontains=name_search
        )
        actors_with_capitalize_search = actors.filter(
            name__icontains=name_search.capitalize()
        )
        actors = actors_with_default_search.union(actors_with_capitalize_search, all=True)
    
    if birthday_min:
        actors = actors.filter(birthday__gte=birthday_min)
    if birthday_max:
        actors = actors.filter(birthday__lte=birthday_max)
    
    if deathday_min:
        actors = actors.filter(deathday__gte=deathday_min)
    if deathday_max:
        actors = actors.filter(deathday__lte=deathday_max)
    
    if gender_filter:
        actors = actors.filter(gender=gender_filter)
    
    if is_parsed:
        actors = actors.filter(is_parsed=True)

    if is_not_parsed:
        actors = actors.filter(is_parsed=False)
    
    if project_search:
        actors_from_movies_default = actors.filter(
            movies__title__icontains=project_search
        )
        actors_from_movies_capitalize = actors.filter(
            movies__title__icontains=project_search.capitalize()
        )
        actors_in_film = actors_from_movies_default.union(actors_from_movies_capitalize, all=True)
        
        actors_from_serials_default = actors.filter(
            serials__title__icontains=project_search
        )
        actors_from_serials_capitalize = actors.filter(
            serials__title__icontains=project_search.capitalize()
        )

        actors_in_serial = actors_from_serials_default.union(actors_from_serials_capitalize, all=True)
        
        actors = actors_in_film.union(actors_in_serial, all=True)

    actors = list(set(actors))
    
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
        "messages_type": messages_type,
        "filter_values": {
            "name_search": name_search,
            "birthday_min": birthday_min,
            "birthday_max": birthday_max,
            "deathday_min": deathday_min,
            "deathday_max": deathday_max,
            "gender": gender_filter,
            "project_search": project_search,
            "is_parsed": is_parsed,
            "is_not_parsed": is_not_parsed
        }  
    })

def genres_admin_panel(request):
    all_genres = Genre.objects.all()
    genres = all_genres.order_by('-id')

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
        genres = genres.filter(
            Q(search_id__icontains=id_search)
        )

    return render(request, "adminPanel/genres.html", context={
        "genres": genres,
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