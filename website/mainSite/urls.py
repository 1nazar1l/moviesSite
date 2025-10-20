from django.urls import path, include, re_path
from . import views
from mainProject.views import films_admin_panel

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.mainPage, name='mainPage'),
    path('auth/', views.authPage, name='authPage'),
    path('reg/', views.regPage, name='regPage'),
    path('films/', views.filmsPage, name='filmsPage'),
    path('serials/', views.serialsPage, name='serialsPage'),
    path('actors/', views.actorsPage, name='actorsPage'),
    path('search/', views.searchPage, name='searchPage'),
    path('profile/', views.profilePage, name='profilePage'),
    path('profile/signOut', views.signOut, name='signOut'),
    path('adminPanel/films', films_admin_panel, name='adminPanel'),
    path('<str:media_type>/<int:search_id>', views.itemPage, name='itemPage'),
    path('<str:media_type>/', views.errorPage, name='errorPage'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)