from django.urls import path, include
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('films/clear_messages/', views.clear_messages, name='clear_messages'),

    path('films/', views.films_admin_panel, name='films'),
    path('films/parse_films/', views.parse_films, name='parse_films'),
    path('films/update_films_info/', views.update_films_info, name='update_films_info'),
    path('films/delete_films/', views.delete_films, name='delete_films'),
    path('films/delete_all_films/', views.delete_all_films, name='delete_all_films'),

    path('serials/', views.serials_admin_panel, name='serials'),
    path('serials/parse_serials/', views.parse_serials, name='parse_serials'),
    path('serials/update_serials_info/', views.update_serials_info, name='update_serials_info'),
    path('serials/delete_serials/', views.delete_serials, name='delete_serials'),
    path('serials/delete_all_serials/', views.delete_all_serials, name='delete_all_serials'),

    path('actors/', views.actors_admin_panel, name='actors'),
    path('actors/parse_actors/', views.parse_actors, name='parse_actors'),
    path('actors/delete_actors/', views.delete_actors, name='delete_actors'),
    path('actors/delete_all_actors/', views.delete_all_actors, name='delete_all_actors'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)