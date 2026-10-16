"""Тесты модели `User`."""
import pytest
from django.contrib.auth import get_user_model


User = get_user_model()


@pytest.mark.django_db
class TestUserModel:

    def test_create_user_with_password(self):
        user = User.objects.create_user(
            username='alice', password='secret123',
        )
        assert user.pk is not None
        assert user.check_password('secret123')
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username='root', password='rootpass123',
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.check_password('rootpass123')

    def test_str_returns_username(self):
        user = User.objects.create_user(username='bob', password='x')
        assert str(user) == 'bob'

    def test_description_defaults_to_none(self):
        user = User.objects.create_user(username='carl', password='x')
        assert user.description is None

    def test_description_can_be_set(self):
        user = User.objects.create_user(
            username='dave', password='x',
            description='Люблю кино',
        )
        user.refresh_from_db()
        assert user.description == 'Люблю кино'

    def test_avatar_defaults_to_empty(self):
        """ImageField без файла отдаёт пустую строку, не None."""
        user = User.objects.create_user(username='eve', password='x')
        assert user.avatar in ('', None)

    def test_username_unique(self):
        User.objects.create_user(username='frank', password='x')
        from django.db import IntegrityError, transaction
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(username='frank', password='y')

    def test_email_not_unique_by_default(self):
        """В `AbstractUser` email не unique — фиксируем текущее поведение."""
        User.objects.create_user(username='g1', email='same@x.com', password='x')
        User.objects.create_user(username='g2', email='same@x.com', password='x')
        assert User.objects.filter(email='same@x.com').count() == 2


@pytest.mark.django_db
class TestUserFactory:
    """Проверяем, что фабрика отдаёт валидного юзера."""

    def test_user_factory(self):
        from users.tests.factories import UserFactory
        user = UserFactory()
        assert user.pk is not None
        assert user.check_password('testpass123')

    def test_superuser_factory(self):
        from users.tests.factories import SuperUserFactory
        admin = SuperUserFactory()
        assert admin.is_superuser is True
        assert admin.is_staff is True

    def test_user_factory_unique_usernames(self):
        from users.tests.factories import UserFactory
        u1 = UserFactory()
        u2 = UserFactory()
        assert u1.username != u2.username