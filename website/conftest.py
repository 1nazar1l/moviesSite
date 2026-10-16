"""Общие фикстуры для тестов проекта."""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def user(db):
    """Обычный пользователь."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def admin_user(db):
    """Суперпользователь."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )


@pytest.fixture
def client_logged(client, user):
    """Django test client, залогиненный как user."""
    client.force_login(user)
    return client
