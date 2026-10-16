"""Smoke-тест: Django загружается, БД работает."""

import pytest


@pytest.mark.django_db
def test_db_works():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    User.objects.create_user(username="smoke", password="x")
    assert User.objects.filter(username="smoke").exists()
