from django.contrib import admin

from .models import ListItem, UserList

admin.site.register(UserList)
admin.site.register(ListItem)
