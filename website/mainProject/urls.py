from django.urls import path, include
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('films/', views.films_admin_panel, name='films'),
    path('films/clear_messages/', views.clear_messages, name='clear_messages'),
    path('films/delete_films/', views.delete_films, name='delete_films'),
    path('films/delete_all_films/', views.delete_all_films, name='delete_all_films'),
    path('films/parse_films/', views.parse_films, name='parse_films'),
    path('films/update_films_info/', views.update_info, name='update_films_info')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)