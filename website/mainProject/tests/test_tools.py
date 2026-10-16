"""Тесты mainProject/tools.py — парсинг TMDB с моком requests."""
from unittest.mock import MagicMock, patch

import pytest
import requests

from mainProject.models import Actor, Film, Genre, Message, Serial
from mainProject.tools import (
    create_error_message,
    create_success_message,
    create_warning_message,
    download_media_item,
    get_trailer_url,
)
from mainProject.tests.factories import GenreFactory


def _mock_response(json_data, status_code=200):
    """Хелпер: сделать мок requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    if status_code >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(f'{status_code}')
    return resp


# ---------------------------------------------------------------------------
# Message helpers
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMessageHelpers:

    def _fake_request(self, user):
        req = MagicMock()
        req.user = user
        return req

    def test_create_error_message(self, user):
        req = self._fake_request(user)
        create_error_message(req, 'films', 'Ошибка X')
        msg = Message.objects.get()
        assert msg.message_type == 'error'
        assert msg.text == 'Ошибка X'
        assert msg.from_page == 'films'
        assert msg.admin == user

    def test_create_warning_message(self, user):
        req = self._fake_request(user)
        create_warning_message(req, 'serials', 'Внимание')
        msg = Message.objects.get()
        assert msg.message_type == 'warning'

    def test_create_success_message(self, user):
        from django.utils import timezone
        req = self._fake_request(user)
        create_success_message(
            req, 'films', timezone.now().replace(microsecond=0), '1.5', 'Успех',
        )
        msg = Message.objects.get()
        assert msg.message_type == 'success'
        assert msg.time == 1.5


# ---------------------------------------------------------------------------
# get_trailer_url — TMDB API
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestGetTrailerUrl:

    @patch('mainProject.tools.requests.get')
    def test_trailer_from_tmdb_api(self, mock_get):
        """TMDB API вернул официальный трейлер — берём его."""
        mock_get.return_value = _mock_response({
            'results': [
                {
                    'site': 'YouTube',
                    'type': 'Trailer',
                    'key': 'abc123',
                    'official': True,
                    'published_at': '2024-01-01T00:00:00Z',
                },
                {
                    'site': 'YouTube',
                    'type': 'Teaser',
                    'key': 'teaser1',
                    'official': False,
                    'published_at': '2024-01-02T00:00:00Z',
                },
            ],
        })
        url = get_trailer_url(search_id=550, media_type='films', title='Fight Club')
        assert url == 'https://www.youtube.com/watch?v=abc123'

    @patch('mainProject.tools.requests.get')
    def test_trailer_prefers_official(self, mock_get):
        """Если есть официальный — берём его, а не свежий неофициальный."""
        mock_get.return_value = _mock_response({
            'results': [
                {
                    'site': 'YouTube', 'type': 'Trailer', 'key': 'old_official',
                    'official': True, 'published_at': '2020-01-01T00:00:00Z',
                },
                {
                    'site': 'YouTube', 'type': 'Trailer', 'key': 'new_unofficial',
                    'official': False, 'published_at': '2025-01-01T00:00:00Z',
                },
            ],
        })
        url = get_trailer_url(search_id=550, media_type='films')
        assert url == 'https://www.youtube.com/watch?v=old_official'

    @patch('mainProject.tools.get_trailer_url_bs4')
    @patch('mainProject.tools.requests.get')
    def test_trailer_fallback_to_bs4(self, mock_get, mock_bs4):
        """Если TMDB API не дал трейлера — падаем в BS4."""
        mock_get.return_value = _mock_response({'results': []})
        mock_bs4.return_value = 'https://www.youtube.com/watch?v=frombs4'

        url = get_trailer_url(
            search_id=550, media_type='films',
            title='Fight Club', release_date='1999-10-15',
        )
        assert url == 'https://www.youtube.com/watch?v=frombs4'
        mock_bs4.assert_called_once()

    @patch('mainProject.tools.get_trailer_url_bs4')
    @patch('mainProject.tools.requests.get')
    def test_trailer_api_exception_falls_back(self, mock_get, mock_bs4):
        """Если API упал с RequestException — идём в BS4."""
        mock_get.side_effect = requests.exceptions.ConnectionError('нет VPN')
        mock_bs4.return_value = 'https://www.youtube.com/watch?v=fallback'

        url = get_trailer_url(
            search_id=550, media_type='films',
            title='Fight Club', release_date='1999-10-15',
        )
        assert url == 'https://www.youtube.com/watch?v=fallback'

    @patch('mainProject.tools.requests.get')
    def test_trailer_no_title_returns_none(self, mock_get):
        """Без title и без трейлера в API — None."""
        mock_get.return_value = _mock_response({'results': []})
        url = get_trailer_url(search_id=550, media_type='films')
        assert url is None

    @patch('mainProject.tools.requests.get')
    def test_trailer_ignores_non_youtube(self, mock_get):
        """Трейлеры не с YouTube игнорируются."""
        mock_get.return_value = _mock_response({
            'results': [
                {'site': 'Vimeo', 'type': 'Trailer', 'key': 'xyz',
                 'official': True, 'published_at': '2024-01-01'},
            ],
        })
        url = get_trailer_url(search_id=550, media_type='films')
        assert url is None

    @patch('mainProject.tools.requests.get')
    def test_trailer_ignores_non_trailer_type(self, mock_get):
        """Только Trailer и Teaser, а не Clip/Featurette."""
        mock_get.return_value = _mock_response({
            'results': [
                {'site': 'YouTube', 'type': 'Clip', 'key': 'clip',
                 'official': True, 'published_at': '2024-01-01'},
            ],
        })
        url = get_trailer_url(search_id=550, media_type='films')
        assert url is None

    @patch('mainProject.tools.requests.get')
    def test_trailer_for_serial(self, mock_get):
        """Для сериалов url_part = 'tv'."""
        mock_get.return_value = _mock_response({
            'results': [
                {'site': 'YouTube', 'type': 'Trailer', 'key': 'tv_trailer',
                 'official': True, 'published_at': '2024-01-01'},
            ],
        })
        url = get_trailer_url(search_id=1399, media_type='serials')
        assert url == 'https://www.youtube.com/watch?v=tv_trailer'


# ---------------------------------------------------------------------------
# download_media_item — создание фильма, жанров, M2M
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestDownloadMediaItem:

    @patch('mainProject.tools.get_trailer_url', return_value=None)
    def test_download_film_creates_object(self, mock_trailer):
        """Создаётся Film с переданными полями."""
        data = {
            'id': 550,
            'title': 'Бойцовский клуб',
            'budget': 63000000,
            'revenue': 100853753,
            'overview': 'Описание',
            'poster_path': None,
            'release_date': '1999-10-15',
            'runtime': 139,
            'status': 'Released',
            'vote_average': 8.4,
            'genres': [],
        }
        download_media_item(
            'films', 'poster_path', data,
            Film, 'https://img.tmdb.org/',
        )
        film = Film.objects.get(search_id=550)
        assert film.title == 'Бойцовский клуб'
        assert film.rating == 8.4
        assert film.is_parsed is True

    @patch('mainProject.tools.get_trailer_url', return_value='https://yt/x')
    def test_download_film_creates_genres(self, mock_trailer):
        """M2M genres создаются и связываются."""
        data = {
            'id': 551,
            'title': 'X',
            'budget': 0, 'revenue': 0, 'overview': '',
            'poster_path': None, 'release_date': '2020-01-01',
            'runtime': 100, 'status': 'Released', 'vote_average': 7.0,
            'genres': [
                {'id': 28, 'name': 'Боевик'},
                {'id': 18, 'name': 'Драма'},
            ],
        }
        download_media_item('films', 'poster_path', data, Film, 'https://img/')
        film = Film.objects.get(search_id=551)
        assert film.genres.count() == 2
        assert Genre.objects.filter(search_id=28, name='Боевик').exists()
        assert film.trailer_url == 'https://yt/x'

    @patch('mainProject.tools.get_trailer_url', return_value=None)
    def test_download_serial(self, mock_trailer):
        data = {
            'id': 1399,
            'name': 'Игра престолов',
            'first_air_date': '2011-04-17',
            'last_air_date': '2019-05-19',
            'number_of_episodes': 73,
            'number_of_seasons': 8,
            'overview': '',
            'poster_path': None,
            'status': 'Ended',
            'vote_average': 8.4,
            'genres': [],
        }
        download_media_item('serials', 'poster_path', data, Serial, 'https://img/')
        serial = Serial.objects.get(search_id=1399)
        assert serial.title == 'Игра престолов'
        assert serial.seasons == 8
        assert serial.episodes == 73

    @patch('mainProject.tools.get_trailer_url', return_value=None)
    def test_download_actor(self, mock_trailer):
        data = {
            'id': 287,
            'name': 'Брэд Питт',
            'biography': 'Актёр',
            'birthday': '1963-12-18',
            'deathday': None,
            'gender': 2,
            'profile_path': None,
        }
        download_media_item('actors', 'profile_path', data, Actor, 'https://img/')
        actor = Actor.objects.get(search_id=287)
        assert actor.name == 'Брэд Питт'
        assert actor.is_parsed is True

    @patch('mainProject.tools.get_trailer_url', return_value=None)
    def test_download_creates_only_once(self, mock_trailer):
        """Повторный вызов — get_or_create, объект не дублируется."""
        data = {
            'id': 552, 'title': 'A', 'budget': 0, 'revenue': 0, 'overview': '',
            'poster_path': None, 'release_date': '2020-01-01', 'runtime': 100,
            'status': 'Released', 'vote_average': 7.0, 'genres': [],
        }
        download_media_item('films', 'poster_path', data, Film, 'https://img/')
        download_media_item('films', 'poster_path', data, Film, 'https://img/')
        assert Film.objects.filter(search_id=552).count() == 1

    @patch('mainProject.tools.get_trailer_url', return_value=None)
    def test_existing_film_updates_trailer(self, mock_trailer):
        """Если фильм уже есть и получен трейлер — обновляем trailer_url."""
        mock_trailer.return_value = 'https://yt/new'
        film = Film.objects.create(search_id=553, title='Old', is_parsed=True)
        data = {
            'id': 553, 'title': 'Old', 'budget': 0, 'revenue': 0, 'overview': '',
            'poster_path': None, 'release_date': '2020-01-01', 'runtime': 100,
            'status': 'Released', 'vote_average': 7.0, 'genres': [],
        }
        download_media_item('films', 'poster_path', data, Film, 'https://img/')
        film.refresh_from_db()
        assert film.trailer_url == 'https://yt/new'