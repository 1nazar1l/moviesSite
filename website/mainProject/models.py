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
        return f"{self.title}, {self.is_adult}"