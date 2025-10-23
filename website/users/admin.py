from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # Поля, которые показываются в списке пользователей
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    
    # Поля, которые можно редактировать в списке
    list_editable = ('is_staff',)
    
    # Поля для фильтрации
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # Поля для поиска
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    # Группировка полей в форме редактирования
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('description', 'avatar')
        }),
    )
    
    # Поля в форме создания пользователя
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'first_name', 'last_name', 'description', 'avatar', 'registration_date')
        }),
    )

# Регистрируем кастомную модель и админ-класс
admin.site.register(User, CustomUserAdmin)