from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.exceptions import ValidationError


class UserList(models.Model):
    """Модель для пользовательских списков"""
    
    # Владелец списка
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_lists',
        verbose_name="Владелец списка"
    )
    
    # Название списка
    title = models.CharField(
        max_length=255,
        verbose_name="Название списка"
    )
    
    # Описание списка (необязательное)
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание списка"
    )
    
    # Тип списка
    LIST_TYPE_CHOICES = [
        ('favorite', 'Избранное'),
        ('watch_later', 'Смотреть позже'),
        ('watched', 'Просмотрено'),
        ('custom', 'Пользовательский список'),
    ]
    
    list_type = models.CharField(
        max_length=20,
        choices=LIST_TYPE_CHOICES,
        default='custom',
        verbose_name="Тип списка"
    )
    
    # Приватность списка
    is_private = models.BooleanField(
        default=False,
        verbose_name="Приватный список"
    )
    
    # Дата создания и обновления
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Пользовательский список"
        verbose_name_plural = "Пользовательские списки"
        ordering = ['-created_at']
        unique_together = ['user', 'title']
        indexes = [
            models.Index(fields=['user', 'list_type']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.user.username})"
    
    def get_items_count(self):
        """Количество элементов в списке"""
        return self.items.count()
    
    def get_preview_items(self, limit=4):
        """Первые несколько элементов для превью"""
        return self.items.all()[:limit]


class ListItem(models.Model):
    """Модель для элементов в пользовательских списках"""
    
    # Ссылка на список
    user_list = models.ForeignKey(
        UserList,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Список"
    )
    
    # Универсальная связь с любым объектом (Film, Serial, Actor)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name="Тип контента"
    )
    
    object_id = models.PositiveIntegerField(
        verbose_name="ID объекта"
    )
    
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )
    
    # Дата добавления в список
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    
    # Позиция в списке (для ручной сортировки)
    position = models.PositiveIntegerField(
        default=0,
        verbose_name="Позиция в списке"
    )
    
    # Дополнительные заметки пользователя
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Заметки пользователя"
    )

    class Meta:
        verbose_name = "Элемент списка"
        verbose_name_plural = "Элементы списков"
        ordering = ['position', '-added_at']
        unique_together = ['user_list', 'content_type', 'object_id']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user_list', 'position']),
        ]
    
    def __str__(self):
        return f"{self.content_object} в {self.user_list.title}"
    
    def save(self, *args, **kwargs):
        """Автоматически устанавливает позицию при создании"""
        if not self.pk:
            last_position = ListItem.objects.filter(
                user_list=self.user_list
            ).aggregate(models.Max('position'))['position__max'] or 0
            self.position = last_position + 1
        super().save(*args, **kwargs)