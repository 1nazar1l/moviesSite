from django.urls import path, include
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='home'),
    path('delete_films/', views.delete_films, name='delete_films'),
    path('delete_all_films/', views.delete_all_films, name='delete_all_films'),
    path('parse_films/', views.parse_films, name='parse_films'),
    path('clear_messages/', views.clear_messages, name='clear_messages')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)