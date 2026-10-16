"""Тесты моделей UserList и ListItem."""
import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, transaction

from mainProject.models import Actor, Film, Serial
from mainProject.tests.factories import ActorFactory, FilmFactory, SerialFactory
from mainSite.models import ListItem, UserList
from mainSite.tests.factories import UserListFactory


# ---------------------------------------------------------------------------
# UserList
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUserList:

    def test_create_custom(self, user):
        lst = UserList.objects.create(user=user, title='Мой список')
        assert lst.pk is not None
        assert lst.list_type == 'custom'
        assert lst.is_private is False

    def test_str(self, user):
        lst = UserList.objects.create(user=user, title='Любимое')
        s = str(lst)
        assert 'Любимое' in s
        assert user.username in s

    def test_unique_together_user_title(self, user):
        """Нельзя два списка с одинаковым названием у одного юзера."""
        UserList.objects.create(user=user, title='Дубликат')
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                UserList.objects.create(user=user, title='Дубликат')

    def test_different_users_same_title_allowed(self, user):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other = User.objects.create_user(username='u2', password='x')

        UserList.objects.create(user=user, title='Одно имя')
        UserList.objects.create(user=other, title='Одно имя')
        assert UserList.objects.filter(title='Одно имя').count() == 2

    def test_all_list_types_valid(self, user):
        """Все 4 типа из LIST_TYPE_CHOICES создаются."""
        for i, (code, _) in enumerate(UserList.LIST_TYPE_CHOICES):
            UserList.objects.create(user=user, title=f'Список {i}', list_type=code)
        assert UserList.objects.filter(user=user).count() == 4

    def test_ordering_newest_first(self, user):
        lst1 = UserListFactory(user=user, title='Первый')
        lst2 = UserListFactory(user=user, title='Второй')
        lists = list(UserList.objects.filter(user=user))
        # ordering = ['-created_at'] → новые сверху
        assert lists[0].pk == lst2.pk
        assert lists[1].pk == lst1.pk

    def test_get_items_count_empty(self, user):
        lst = UserListFactory(user=user)
        assert lst.get_items_count() == 0

    def test_get_items_count(self, user):
        lst = UserListFactory(user=user)
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        ListItem.objects.create(user_list=lst, content_type=ct, object_id=film.pk)
        assert lst.get_items_count() == 1

    def test_get_preview_items_limit(self, user):
        lst = UserListFactory(user=user)
        ct = ContentType.objects.get_for_model(Film)
        for i in range(10):
            film = FilmFactory()
            ListItem.objects.create(
                user_list=lst, content_type=ct, object_id=film.pk,
            )
        preview = lst.get_preview_items(limit=4)
        assert len(preview) == 4


# ---------------------------------------------------------------------------
# ListItem
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestListItem:

    def test_create_for_film(self, user):
        lst = UserListFactory(user=user)
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        item = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=film.pk,
        )
        assert item.pk is not None
        assert item.content_object == film

    def test_create_for_serial(self, user):
        lst = UserListFactory(user=user)
        serial = SerialFactory()
        ct = ContentType.objects.get_for_model(Serial)
        item = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=serial.pk,
        )
        assert item.content_object == serial

    def test_create_for_actor(self, user):
        lst = UserListFactory(user=user)
        actor = ActorFactory()
        ct = ContentType.objects.get_for_model(Actor)
        item = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=actor.pk,
        )
        assert item.content_object == actor

    def test_str(self, user):
        lst = UserListFactory(user=user, title='Топ')
        film = FilmFactory(title='Матрица')
        ct = ContentType.objects.get_for_model(Film)
        item = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=film.pk,
        )
        s = str(item)
        assert 'Матрица' in s or str(film.pk) in s
        assert 'Топ' in s

    def test_position_auto_increment(self, user):
        """ListItem.save() ставит position = max+1."""
        lst = UserListFactory(user=user)
        ct = ContentType.objects.get_for_model(Film)
        i1 = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=FilmFactory().pk,
        )
        i2 = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=FilmFactory().pk,
        )
        i3 = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=FilmFactory().pk,
        )
        assert i1.position == 1
        assert i2.position == 2
        assert i3.position == 3

    def test_position_isolated_per_list(self, user):
        """Позиция считается в рамках своего списка."""
        lst1 = UserListFactory(user=user, title='A')
        lst2 = UserListFactory(user=user, title='B')
        ct = ContentType.objects.get_for_model(Film)
        i1 = ListItem.objects.create(
            user_list=lst1, content_type=ct, object_id=FilmFactory().pk,
        )
        i2 = ListItem.objects.create(
            user_list=lst2, content_type=ct, object_id=FilmFactory().pk,
        )
        assert i1.position == 1
        assert i2.position == 1

    def test_unique_together_list_content(self, user):
        """Нельзя добавить один объект в один список дважды."""
        lst = UserListFactory(user=user)
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=film.pk,
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                ListItem.objects.create(
                    user_list=lst, content_type=ct, object_id=film.pk,
                )

    def test_same_object_different_lists_allowed(self, user):
        lst1 = UserListFactory(user=user, title='A')
        lst2 = UserListFactory(user=user, title='B')
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        ListItem.objects.create(user_list=lst1, content_type=ct, object_id=film.pk)
        ListItem.objects.create(user_list=lst2, content_type=ct, object_id=film.pk)
        assert ListItem.objects.filter(content_type=ct, object_id=film.pk).count() == 2

    def test_ordering_by_position(self, user):
        lst = UserListFactory(user=user)
        ct = ContentType.objects.get_for_model(Film)
        i1 = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=FilmFactory().pk,
        )
        i2 = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=FilmFactory().pk,
        )
        items = list(ListItem.objects.filter(user_list=lst))
        # ordering = ['position', '-added_at']
        assert items[0].pk == i1.pk
        assert items[1].pk == i2.pk

    def test_notes_optional(self, user):
        lst = UserListFactory(user=user)
        ct = ContentType.objects.get_for_model(Film)
        item = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=FilmFactory().pk,
        )
        assert item.notes is None

    def test_notes_can_be_set(self, user):
        lst = UserListFactory(user=user)
        ct = ContentType.objects.get_for_model(Film)
        item = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=FilmFactory().pk,
            notes='Посмотреть на выходных',
        )
        item.refresh_from_db()
        assert item.notes == 'Посмотреть на выходных'

    def test_cascade_on_list_delete(self, user):
        """Удаление списка удаляет его элементы."""
        lst = UserListFactory(user=user)
        ct = ContentType.objects.get_for_model(Film)
        item = ListItem.objects.create(
            user_list=lst, content_type=ct, object_id=FilmFactory().pk,
        )
        item_pk = item.pk
        lst.delete()
        assert ListItem.objects.filter(pk=item_pk).count() == 0