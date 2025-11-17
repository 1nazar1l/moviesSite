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
    path('films/add_item_to_list', views.add_item_to_list, name='add_item_to_list'),
    path('serials/', views.serialsPage, name='serialsPage'),
    path('serials/add_item_to_list', views.add_item_to_list, name='add_item_to_list'),
    path('actors/', views.actorsPage, name='actorsPage'),
    path('actors/add_item_to_list', views.add_item_to_list, name='add_item_to_list'),
    path('search/', views.searchPage, name='searchPage'),
    path('profile/', views.profilePage, name='profilePage'),
    path('profile/listPage/<int:list_id>', views.listPage, name='listPage'),
    path('edit_list/', views.edit_list, name='edit_list'),
    path('delete_item_form_list/', views.delete_item_from_list, name='delete_item_from_list'),
    path('profile/avatar/', views.add_avatar, name='add_avatar'),
    path('profile/update_user_info', views.update_user_info, name='update_user_info'),
    path('profile/add_list', views.add_list, name='add_list'),
    path('profile/delete_list', views.delete_list, name='delete_list'),
    path('profile/signOut', views.signOut, name='signOut'),
    path('users/<int:user_id>', views.userPage, name="userPage"),
    path('users/<int:user_id>/listPage/<int:list_id>', views.userListPage, name="userListPage"),
    path('favorite/add/', views.add_to_favorite, name='add_to_favorite'),
    path('favorite/remove/', views.remove_from_favorite, name='remove_from_favorite'),
    path('adminPanel/films', films_admin_panel, name='adminPanel'),
    path('add_item_to_list/', views.add_item_to_list, name='add_item_to_list'),
    path('<str:media_type>/<int:search_id>', views.itemPage, name='itemPage'),
    path('add_new_item/', views.add_new_item, name="add_new_item"),
    path('comment/create/', views.create_comment, name='create_comment'),
    path('<str:media_type>/', views.errorPage, name='errorPage'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)