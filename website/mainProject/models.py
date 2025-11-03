from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


    
class Actor(models.Model):
    search_id = models.IntegerField(null=True, blank=True)
    is_parsed = models.BooleanField(null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True, default=None)
    deathday = models.DateField(null=True, blank=True, default=None)
    gender = models.IntegerField(null=True, blank=True)
    site_img_path = models.URLField(null=True, blank=True)
    local_img_path = models.ImageField(upload_to='actors/', null=True, blank=True)
    movies = models.ManyToManyField('Film', blank=True)
    serials = models.ManyToManyField('Serial', blank=True)
    
    class Meta:
        verbose_name = "Актер"
        verbose_name_plural = "Актеры"

    def __str__(self):
        return f"{self.search_id}, {self.name}"

class Film(models.Model):
    search_id = models.IntegerField(null=True, blank=True)
    is_parsed = models.BooleanField(null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    budget = models.IntegerField(null=True, blank=True)
    revenue = models.IntegerField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    site_img_path = models.URLField(null=True, blank=True)
    local_img_path = models.ImageField(upload_to='films/', null=True, blank=True)
    release_date = models.DateField(null=True, blank=True, default=timezone.now)
    runtime = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    genres = models.ManyToManyField('Genre', blank=True, related_name='films')
    actors = models.ManyToManyField(Actor, blank=True)

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return f"{self.search_id}, {self.title}, is_parsed: {self.is_parsed}"

class Serial(models.Model):
    search_id = models.IntegerField(null=True, blank=True)
    is_parsed = models.BooleanField(null=True, blank=True)
    first_air_date = models.DateField(null=True, blank=True, default=timezone.now)
    last_air_date = models.DateField(null=True, blank=True, default=timezone.now)
    title = models.CharField(max_length=100, null=True, blank=True)
    episodes = models.IntegerField(null=True, blank=True)
    seasons = models.IntegerField(null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    site_img_path = models.URLField(null=True, blank=True)
    local_img_path = models.ImageField(upload_to='serials/', null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    genres = models.ManyToManyField('Genre', blank=True, related_name='serials')
    actors = models.ManyToManyField(Actor, blank=True)

    class Meta:
        verbose_name = "Сериал"
        verbose_name_plural = "Сериалы"

    def __str__(self):
        return f"{self.search_id}, {self.title}"

    
class Message(models.Model):
    from_page = models.TextField()
    admin = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    date = models.DateTimeField()
    time = models.FloatField()
    message_type = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"{self.id}, {self.admin}, {self.text}"
    

class Comment(models.Model):
    # Универсальная связь с любым объектом (Film, Serial, Actor)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Пользователь, который оставил комментарий
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    text = models.TextField(verbose_name="Текст комментария")
    writing_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Дата написания"
    )
    
    # Для лайков и дизлайков лучше использовать ManyToMany
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comment_likes',
        blank=True
    )
    dislikes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='comment_dislikes',
        blank=True
    )

    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Неудовлетворительно'),
        (4, '4 - Ниже среднего'),
        (5, '5 - Средне'),
        (6, '6 - Выше среднего'),
        (7, '7 - Хорошо'),
        (8, '8 - Очень хорошо'),
        (9, '9 - Отлично'),
        (10, '10 - Шедевр'),
    ]
    
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        verbose_name="Оценка"
    )
    
    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['-writing_date']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"Комментарий {self.user} от {self.writing_date.strftime('%d.%m.%Y')}"


class Favorite(models.Model):
    # Универсальная связь с любым объектом (Film, Serial, Actor)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Пользователь, который добавил в избранное
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    
    # Дата добавления в избранное
    added_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    
    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        ordering = ['-added_date']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['user']),
        ]
        # Уникальность - пользователь не может добавить один объект дважды
        unique_together = ['user', 'content_type', 'object_id']

    def __str__(self):
        return f"{self.user.username} - {self.content_object}"


class Genre(models.Model):
    search_id = models.IntegerField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
    
    def __str__(self):
        return f"{self.search_id} - {self.name}"