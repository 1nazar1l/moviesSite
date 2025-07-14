from django.urls import path, include
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('delete-film/', views.delete_film, name='delete_film'),
    path('parse_films/', views.parse_films, name='parse_films'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)