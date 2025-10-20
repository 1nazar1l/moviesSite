from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Film(models.Model):
    search_id = models.IntegerField(null=True, blank=True)
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
    genres = models.JSONField(null=True, blank=True)
    actors = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return f"{self.search_id}, {self.title}"

class Serial(models.Model):
    search_id = models.IntegerField(null=True, blank=True)
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
    genres = models.JSONField(null=True, blank=True)
    actors = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = "Сериал"
        verbose_name_plural = "Сериалы"

    def __str__(self):
        return f"{self.search_id}, {self.title}"
    
class Actor(models.Model):
    search_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    biography = models.TextField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True, default=None)
    deathday = models.DateField(null=True, blank=True, default=None)
    gender = models.IntegerField(null=True, blank=True)
    site_img_path = models.URLField(null=True, blank=True)
    local_img_path = models.ImageField(upload_to='actors', null=True, blank=True)
    movies = models.JSONField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Актер"
        verbose_name_plural = "Актеры"

    def __str__(self):
        return f"{self.search_id}, {self.name}"
    
class Message(models.Model):
    from_page = models.TextField()
    admin = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    date = models.DateTimeField()
    time = models.FloatField()
    message_type = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return f"{self.id}, {self.admin}, {self.text}"