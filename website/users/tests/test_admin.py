"""Тесты кастомной админки `User`.

Здесь мы проверяем регресс: страница создания пользователя в админке
должна отдавать 200. Сейчас в `CustomUserAdmin.add_fieldsets` указано
поле `registration_date`, которого нет в модели `User` — это ошибка,
унаследованная от старой версии модели. Тест её фиксирует.
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestUserAdmin:

    def test_add_form_renders(self, client, admin_user):
        """Страница /admin/users/user/add/ должна открываться без ошибок."""
        client.force_login(admin_user)
        url = reverse('admin:users_user_add')
        response = client.get(url)
        assert response.status_code == 200

    def test_change_form_renders(self, client, admin_user, user):
        """Страница редактирования юзера тоже должна открываться."""
        client.force_login(admin_user)
        url = reverse('admin:users_user_change', args=[user.pk])
        response = client.get(url)
        assert response.status_code == 200

    def test_changelist_renders(self, client, admin_user):
        client.force_login(admin_user)
        url = reverse('admin:users_user_changelist')
        response = client.get(url)
        assert response.status_code == 200