"""Публичные страницы: главная, каталоги, поиск, карточка объекта, ошибка."""
from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect, render

from mainProject.models import Actor, Comment, Film, Genre, Serial
from mainSite.models import ListItem

from ._helpers import check_path

from django.contrib.auth import get_user_model



def mainPage(request):
    request.session['profile_error_messages'] = []

    today = date.today()
    films = Film.objects.exclude(is_parsed=False)
    coming_soon_films = films.filter(release_date__year=today.year)[:10]
    films = films.exclude(release_date__year=today.year).order_by('-rating')[:20]
    serials = Serial.objects.exclude(is_parsed=False)
    coming_soon_serials = serials.filter(first_air_date__year=today.year)[:10]
    serials = serials.exclude(first_air_date__year=today.year).order_by('-first_air_date')[:20]

    for items in [films, coming_soon_films, serials, coming_soon_serials]:
        for item in items:
            check_path(item)
            item.first_genre = item.genres.first()

    return render(request, "main/index.html", context={
        "username": request.user,
        "films": films,
        "serials": serials,
        "coming_soon_films": coming_soon_films,
        "coming_soon_serials": coming_soon_serials,
        "types": {"film": "film", "serial": "serial", "actor": "actor"},
    })


def filmsPage(request):
    request.session['profile_error_messages'] = []

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

    films = Film.objects.exclude(is_parsed=False)

    if title_search:
        films = films.filter(title__icontains=title_search).union(
            films.filter(title__icontains=title_search.capitalize()), all=True,
        )
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

    for film in films:
        check_path(film)

    films = set(list(films))
    genres = Genre.objects.all()

    context = {
        "username": request.user,
        "items": films,
        "media_type": "films",
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
        },
    }
    return render(request, "main/items.html", context=context)


def serialsPage(request):
    request.session['profile_error_messages'] = []

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

    serials = Serial.objects.exclude(is_parsed=False)

    if title_search:
        serials = serials.filter(title__icontains=title_search).union(
            serials.filter(title__icontains=title_search.capitalize()), all=True,
        )
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

    serials = set(list(serials))
    for serial in serials:
        check_path(serial)

    genres = Genre.objects.all()

    context = {
        "username": request.user,
        "items": serials,
        "media_type": "serials",
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
        },
    }
    return render(request, "main/items.html", context=context)


def actorsPage(request):
    request.session['profile_error_messages'] = []

    name_search = request.GET.get('name_search', '').strip()
    birthday_min = request.GET.get('birthday_min', '').strip()
    birthday_max = request.GET.get('birthday_max', '').strip()
    deathday_min = request.GET.get('deathday_min', '').strip()
    deathday_max = request.GET.get('deathday_max', '').strip()
    gender_filter = request.GET.get('gender', '').strip()
    project_search = request.GET.get('project_search', '').strip()

    actors = Actor.objects.exclude(is_parsed=False)

    if name_search:
        actors = actors.filter(name__icontains=name_search).union(
            actors.filter(name__icontains=name_search.capitalize()), all=True,
        )
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

    if project_search:
        actors_in_film = actors.filter(
            movies__title__icontains=project_search,
        ).union(
            actors.filter(movies__title__icontains=project_search.capitalize()),
            all=True,
        )
        actors_in_serial = actors.filter(
            serials__title__icontains=project_search,
        ).union(
            actors.filter(serials__title__icontains=project_search.capitalize()),
            all=True,
        )
        actors = actors_in_film.union(actors_in_serial, all=True)
        actors = list(set(actors))

    for actor in actors:
        check_path(actor)

    actors = set(list(actors))

    context = {
        "username": request.user,
        "items": actors,
        "media_type": "actors",
        "filter_values": {
            "name_search": name_search,
            "birthday_min": birthday_min,
            "birthday_max": birthday_max,
            "deathday_min": deathday_min,
            "deathday_max": deathday_max,
            "gender": gender_filter,
            "project_search": project_search,
        },
    }
    return render(request, "main/items.html", context=context)


def searchPage(request):
    request.session['profile_error_messages'] = []

    search = request.POST.get('search')

    if search:
        from ._helpers import set_previous_page_values
        set_previous_page_values(request, search_page_value=search)
    else:
        from ._helpers import get_previous_page_values
        for item in get_previous_page_values(request):
            for key, value in item.items():
                if key == "search_page_value":
                    search = value

    films = Film.objects.exclude(is_parsed=False)
    serials = Serial.objects.exclude(is_parsed=False)
    actors = Actor.objects.exclude(is_parsed=False)

    films = films.filter(title__icontains=search).union(
        films.filter(title__icontains=search.capitalize()), all=True,
    )
    serials = serials.filter(title__icontains=search).union(
        serials.filter(title__icontains=search.capitalize()), all=True,
    )
    actors = actors.filter(name__icontains=search).union(
        actors.filter(name__icontains=search.capitalize()), all=True,
    )

    films = set(list(films))
    serials = set(list(serials))
    actors = set(list(actors))

    for objects in [films, serials, actors]:
        for obj in objects:
            check_path(obj)

    return render(request, "main/search.html", context={
        "username": request.user,
        "films": films,
        "serials": serials,
        "actors": actors,
        "search_title": search,
        "results_count": len(films) + len(serials) + len(actors),
        "types": {"film": "film", "serial": "serial", "actor": "actor"},
    })


def itemPage(request, media_type, search_id):
    request.session['profile_error_messages'] = []

    if media_type in ("film", "serial", "actor"):
        media_type = f"{media_type}s"

    models = {"films": Film, "serials": Serial, "actors": Actor}
    model = models.get(media_type)

    item = model.objects.get(search_id=search_id)

    if not item.is_parsed:
        return redirect("errorPage", media_type="actor")

    actors, films, serials = [], [], []
    if media_type != "actors":
        check_path(item)
        actors = list(item.actors.all())
    else:
        check_path(item)
        films = list(item.movies.all())
        serials = list(item.serials.all())

    content_type = ContentType.objects.get_for_model(item)

    comments = Comment.objects.filter(
        content_type=content_type, object_id=item.id,
    ).select_related('user').order_by()

    author_comments = Comment.objects.none()
    if request.user.is_authenticated:
        author_comments = comments.filter(user=request.user).order_by()

    public_comments = comments.filter(is_private=False).order_by()

    if request.user.is_authenticated:
        comments = author_comments | public_comments
    else:
        comments = public_comments

    comments_count = comments.count()

    user_lists_with_status = []
    is_favorite = False

    if request.user.is_authenticated:
        User = get_user_model()
        user = User.objects.get(id=request.user.id)

        is_favorite = user.favorites.filter(
            content_type=content_type, object_id=item.id,
        ).exists()

        for user_list in user.user_lists.all():
            has_item = ListItem.objects.filter(
                user_list=user_list,
                content_type=content_type,
                object_id=item.id,
            ).exists()
            user_lists_with_status.append({'list': user_list, 'has_item': has_item})

    return render(request, "main/item.html", context={
        "username": request.user,
        "item": item,
        "films": films,
        "films_count": len(films),
        "serials": serials,
        "serials_count": len(serials),
        "actors": actors,
        "actors_count": len(actors),
        "media_type": media_type,
        "comments": comments,
        "comments_count": comments_count,
        "content_type_id": content_type.id,
        "object_id": item.id,
        "is_favorite": is_favorite,
        'user_lists_with_status': user_lists_with_status,
        "is_vpn": False,
        "types": {"film": "film", "serial": "serial", "actor": "actor"},
    })


def errorPage(request, media_type=""):
    request.session['profile_error_messages'] = []
    return render(request, "main/error.html", context={
        "username": request.user,
    })