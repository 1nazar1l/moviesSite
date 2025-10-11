from django.urls import path, include
from . import views
from mainProject.views import films_admin_panel

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.mainPage, name='mainPage'),
    path('auth/', views.authPage, name='authPage'),
    path('reg/', views.regPage, name='regPage'),
    path('films/', views.filmsPage, name='filmsPage'),
    path('search/', views.searchPage, name='searchPage'),
    path('profile/', views.profilePage, name='profilePage'),
    path('item/', views.itemPage, name='itemPage'),
    path('profile/signOut', views.signOut, name='signOut'),
    path('adminPanel/films', films_admin_panel, name='adminPanel'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)