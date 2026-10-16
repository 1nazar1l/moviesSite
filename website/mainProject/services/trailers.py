"""Поиск ссылки на трейлер: TMDB API → fallback на YouTube через BS4."""

import logging
import re

import requests
from bs4 import BeautifulSoup

from .tmdb import BASE_URL

logger = logging.getLogger(__name__)


def get_trailer_url(search_id, media_type, title=None, release_date=None):
    """
    Получение ссылки на трейлер фильма/сериала.
    Сначала пытается через API TMDB, затем через BeautifulSoup на YouTube.
    """
    if media_type in ["films", "serials"]:
        url_part = "movie" if media_type == "films" else "tv"
        videos_url = f"{BASE_URL}/{url_part}/{search_id}/videos"

        from django.conf import settings

        params = {
            "api_key": settings.TMDB_API_KEY,
            "language": "ru",
        }

        try:
            response = requests.get(videos_url, params=params)
            response.raise_for_status()
            videos_data = response.json()

            if videos_data and "results" in videos_data:
                trailers = [
                    video
                    for video in videos_data["results"]
                    if video["site"] == "YouTube" and video["type"] in ["Trailer", "Teaser"]
                ]

                if trailers:
                    trailers.sort(
                        key=lambda x: (
                            x.get("official", False),
                            x.get("published_at", ""),
                        ),
                        reverse=True,
                    )
                    trailer = trailers[0]
                    return f"https://www.youtube.com/watch?v={trailer['key']}"

        except requests.exceptions.RequestException:
            pass

    if title:
        return get_trailer_url_bs4(title, release_date)

    return None


def get_trailer_url_bs4(title, release_date=None):
    """Получение ссылки на трейлер через YouTube и BeautifulSoup."""
    search_query = f"{title} {release_date[:4] if release_date else ''} официальный трейлер"
    search_query = search_query.replace(" ", "+")

    youtube_url = f"https://www.youtube.com/results?search_query={search_query}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.124 Safari/537.36"
        )
    }

    try:
        response = requests.get(youtube_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        video_links = []
        script_tags = soup.find_all("script")

        for script in script_tags:
            script_text = script.string
            if script_text and "videoId" in script_text:
                video_ids = re.findall(r'"videoId":"([^"]+)"', script_text)
                video_links.extend(video_ids)

        if not video_links:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "/watch?v=" in href and href not in video_links:
                    video_links.append(href)

        processed_links = []
        for link in video_links:
            if link.startswith("/watch?v="):
                video_id = link.split("watch?v=")[1].split("&")[0]
                processed_links.append(video_id)
            elif len(link) == 11:
                processed_links.append(link)

        if processed_links:
            return f"https://www.youtube.com/watch?v={processed_links[0]}"

        return None

    except Exception:
        logger.exception("Ошибка при поиске трейлера через BeautifulSoup: title=%r", title)
        return None
