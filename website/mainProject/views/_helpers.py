"""Хелперы для вьюх mainProject."""
from mainProject.models import Message


def count_messages_by_type():
    """Считает количество сообщений по типам (success/warning/error/clear)."""
    counts = {"success": 0, "warning": 0, "error": 0, "clear": 0}
    for message in Message.objects.all():
        if message.message_type in counts:
            counts[message.message_type] += 1
    return counts