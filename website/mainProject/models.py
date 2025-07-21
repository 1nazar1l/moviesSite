from django.db import models
from django.utils import timezone

class Film(models.Model):
    search_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    local_img_path = models.URLField(null=True, blank=True)
    site_img_path = models.URLField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True, default=timezone.now)
    rating = models.FloatField(null=True, blank=True)
    title_lang = models.CharField(max_length=10, null=True, blank=True)
    is_adult = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"

    def __str__(self):
        return f"{self.search_id}, {self.title}"

class Serial(models.Model):
    search_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    overview = models.TextField(null=True, blank=True)
    local_img_path = models.URLField(null=True, blank=True)
    site_img_path = models.URLField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True, default=timezone.now)
    rating = models.FloatField(null=True, blank=True)
    title_lang = models.CharField(max_length=10, null=True, blank=True)
    is_adult = models.BooleanField(null=True, blank=True)

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
    local_img_path = models.URLField(null=True, blank=True)
    movies = models.ManyToManyField(Film, null=True, blank=True)
    
    class Meta:
        verbose_name = "Актер"
        verbose_name_plural = "Актеры"

    def __str__(self):
        return f"{self.search_id}, {self.name}"