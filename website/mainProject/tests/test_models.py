"""Тесты моделей Film, Serial, Actor, Genre, Message."""
import pytest

from mainProject.models import Actor, Film, Genre, Message, Serial
from mainProject.tests.factories import (
    ActorFactory, FilmFactory, GenreFactory, SerialFactory,
)


@pytest.mark.django_db
class TestGenre:

    def test_create(self):
        genre = Genre.objects.create(search_id=28, name='Боевик')
        assert genre.pk is not None
        assert genre.name == 'Боевик'

    def test_str(self):
        genre = Genre.objects.create(search_id=28, name='Боевик')
        assert str(genre) == '28 - Боевик'

    def test_defaults_allow_none(self):
        genre = Genre.objects.create()
        assert genre.search_id is None
        assert genre.name is None


@pytest.mark.django_db
class TestFilm:

    def test_create_minimal(self):
        film = Film.objects.create(search_id=550, title='Бойцовский клуб')
        assert film.pk is not None
        assert film.title == 'Бойцовский клуб'

    def test_str_includes_search_id_and_title(self):
        film = FilmFactory(search_id=999, title='Матрица')
        s = str(film)
        assert '999' in s
        assert 'Матрица' in s
        assert 'is_parsed' in s

    def test_genres_m2m(self):
        film = FilmFactory()
        g1 = GenreFactory(name='Драма')
        g2 = GenreFactory(name='Комедия')
        film.genres.add(g1, g2)
        assert film.genres.count() == 2
        assert g1 in film.genres.all()

    def test_related_name_films_on_genre(self):
        """Genre.films — обратная связь от Film.genres."""
        genre = GenreFactory()
        film = FilmFactory()
        film.genres.add(genre)
        assert film in genre.films.all()

    def test_actors_m2m(self):
        film = FilmFactory()
        actor = ActorFactory()
        film.actors.add(actor)
        assert actor in film.actors.all()

    def test_trailer_url_blank_by_default(self):
        film = Film.objects.create(search_id=1, title='X')
        assert film.trailer_url in ('', None)


@pytest.mark.django_db
class TestSerial:

    def test_create_minimal(self):
        serial = Serial.objects.create(search_id=1399, title='Игра престолов')
        assert serial.pk is not None

    def test_str(self):
        serial = SerialFactory(search_id=1399, title='Игра престолов')
        s = str(serial)
        assert '1399' in s
        assert 'Игра престолов' in s

    def test_genres_and_actors(self):
        serial = SerialFactory()
        genre = GenreFactory()
        actor = ActorFactory()
        serial.genres.add(genre)
        serial.actors.add(actor)
        assert genre in serial.genres.all()
        assert actor in serial.actors.all()

    def test_seasons_episodes_nullable(self):
        serial = Serial.objects.create(search_id=1, title='X')
        assert serial.seasons is None
        assert serial.episodes is None


@pytest.mark.django_db
class TestActor:

    def test_create_minimal(self):
        actor = Actor.objects.create(search_id=1, name='Брэд Питт')
        assert actor.pk is not None

    def test_str(self):
        actor = ActorFactory(search_id=287, name='Брэд Питт')
        s = str(actor)
        assert '287' in s
        assert 'Брэд Питт' in s

    def test_movies_m2m(self):
        """actor.movies.add(film) — фиксируем текущее поведение.

        ⚠️ В модели две отдельные M2M-таблицы (Actor.movies и Film.actors),
        они не синхронизируются автоматически. Регресс-тест на баг —
        ниже. См. TODO.md, этап 4.
        """
        actor = ActorFactory()
        film = FilmFactory()
        actor.movies.add(film)
        assert film in actor.movies.all()

    def test_movies_and_actors_m2m_are_not_synced(self):
        """⚠️ Известный баг: actor.movies и film.actors не синхронизируются.

        Регресс-тест — если кто-то починит, тест упадёт и мы узнаем.
        """
        actor = ActorFactory()
        film = FilmFactory()
        actor.movies.add(film)
        # film.actors.all() пуст, потому что это другая M2M-таблица
        assert actor not in film.actors.all()

    def test_actors_add_via_film(self):
        """film.actors.add(actor) — обратная сторона того же бага."""
        actor = ActorFactory()
        film = FilmFactory()
        film.actors.add(actor)
        assert actor in film.actors.all()
        # но в actor.movies его нет
        assert film not in actor.movies.all()

    def test_serials_m2m(self):
        actor = ActorFactory()
        serial = SerialFactory()
        actor.serials.add(serial)
        assert serial in actor.serials.all()

    def test_serials_and_actors_m2m_are_not_synced(self):
        actor = ActorFactory()
        serial = SerialFactory()
        actor.serials.add(serial)
        assert actor not in serial.actors.all()

    def test_birthday_optional(self):
        actor = Actor.objects.create(search_id=1, name='X')
        assert actor.birthday is None
        assert actor.deathday is None


@pytest.mark.django_db
class TestMessage:

    def test_create(self):
        msg = Message.objects.create(
            from_page='films',
            text='Готово',
            date='2026-01-01T00:00:00Z',
            time=1.5,
            message_type='success',
        )
        assert msg.pk is not None
        assert msg.message_type == 'success'

    def test_str_includes_id_and_text(self):
        msg = Message.objects.create(
            from_page='films', text='Ошибка X',
            date='2026-01-01T00:00:00Z', time=0.0,
        )
        s = str(msg)
        assert str(msg.pk) in s
        assert 'Ошибка X' in s

    def test_admin_nullable(self):
        msg = Message.objects.create(
            from_page='films', text='x',
            date='2026-01-01T00:00:00Z', time=0.0,
        )
        assert msg.admin is None