"""Запись сообщений о парсинге в модель `Message`."""
from django.utils import timezone

from mainProject.models import Message


def create_error_message(request, media_type, text):
    Message.objects.create(
        message_type="error",
        from_page=media_type,
        text=text,
        date=timezone.now().replace(microsecond=0),
        time=0.0,
        admin=request.user,
    )


def create_warning_message(request, media_type, text):
    Message.objects.create(
        message_type="warning",
        from_page=media_type,
        text=text,
        date=timezone.now().replace(microsecond=0),
        time=0.0,
        admin=request.user,
    )


def create_success_message(request, media_type, start_time, lead_time, text):
    Message.objects.create(
        message_type="success",
        from_page=media_type,
        text=text,
        date=start_time,
        time=lead_time,
        admin=request.user,
    )