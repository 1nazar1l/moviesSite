from django.contrib import admin
from .models import Film, Serial, Actor, Message, Comment, Favorite, Genre

admin.site.register(Film)
admin.site.register(Serial)
admin.site.register(Actor)
admin.site.register(Message)
admin.site.register(Comment)
admin.site.register(Favorite)
admin.site.register(Genre)
