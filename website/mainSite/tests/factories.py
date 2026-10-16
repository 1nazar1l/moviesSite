"""Фабрики для тестов приложения `mainSite`."""

import factory
from django.contrib.auth import get_user_model

from mainSite.models import UserList

User = get_user_model()


class UserListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserList

    user = factory.SubFactory("users.tests.factories.UserFactory")
    title = factory.Sequence(lambda n: f"Список {n}")
    list_type = "custom"
    is_private = False
