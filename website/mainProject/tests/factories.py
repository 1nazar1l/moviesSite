"""Фабрики для тестов приложения `mainProject`."""

import factory
from django.utils import timezone

from mainProject.models import Actor, Film, Genre, Serial


class GenreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Genre

    search_id = factory.Sequence(lambda n: 1000 + n)
    name = factory.Sequence(lambda n: f"Жанр {n}")


class FilmFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Film

    search_id = factory.Sequence(lambda n: 2000 + n)
    is_parsed = True
    title = factory.Sequence(lambda n: f"Фильм {n}")
    release_date = factory.LazyFunction(lambda: timezone.now().date())
    rating = 7.5


class SerialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Serial

    search_id = factory.Sequence(lambda n: 3000 + n)
    is_parsed = True
    title = factory.Sequence(lambda n: f"Сериал {n}")
    first_air_date = factory.LazyFunction(lambda: timezone.now().date())
    rating = 8.0


class ActorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Actor

    search_id = factory.Sequence(lambda n: 4000 + n)
    is_parsed = True
    name = factory.Sequence(lambda n: f"Актёр {n}")
