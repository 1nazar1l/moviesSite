"""Тесты Comment и Favorite — универсальные связи через ContentType."""
import pytest
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from mainProject.models import Actor, Comment, Favorite, Film, Serial
from mainProject.tests.factories import ActorFactory, FilmFactory, SerialFactory


@pytest.mark.django_db
class TestComment:

    def test_create_for_film(self, user):
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        comment = Comment.objects.create(
            content_type=ct, object_id=film.pk,
            user=user, text='Отличный фильм', rating=9,
        )
        assert comment.pk is not None
        assert comment.content_object == film
        assert comment.rating == 9

    def test_create_for_serial(self, user):
        serial = SerialFactory()
        ct = ContentType.objects.get_for_model(Serial)
        comment = Comment.objects.create(
            content_type=ct, object_id=serial.pk,
            user=user, text='Топ', rating=10,
        )
        assert comment.content_object == serial

    def test_create_for_actor(self, user):
        actor = ActorFactory()
        ct = ContentType.objects.get_for_model(Actor)
        comment = Comment.objects.create(
            content_type=ct, object_id=actor.pk,
            user=user, text='Хороший актёр',
        )
        assert comment.content_object == actor

    def test_str(self, user):
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        comment = Comment.objects.create(
            content_type=ct, object_id=film.pk,
            user=user, text='x',
        )
        assert str(user) in str(comment)
        assert comment.writing_date.strftime('%d.%m.%Y') in str(comment)

    def test_likes_dislikes_m2m(self, user):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other = User.objects.create_user(username='other', password='x')

        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        comment = Comment.objects.create(
            content_type=ct, object_id=film.pk, user=user, text='x',
        )
        comment.likes.add(other)
        assert other in comment.likes.all()
        assert comment.dislikes.count() == 0

    def test_ordering_newest_first(self, user):
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        c1 = Comment.objects.create(
            content_type=ct, object_id=film.pk, user=user, text='1',
            writing_date=timezone.now() - timezone.timedelta(days=1),
        )
        c2 = Comment.objects.create(
            content_type=ct, object_id=film.pk, user=user, text='2',
            writing_date=timezone.now(),
        )
        comments = list(Comment.objects.filter(
            content_type=ct, object_id=film.pk,
        ))
        assert comments[0].pk == c2.pk
        assert comments[1].pk == c1.pk

    def test_is_private_default_none(self, user):
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        comment = Comment.objects.create(
            content_type=ct, object_id=film.pk, user=user, text='x',
        )
        assert comment.is_private is None

    def test_rating_choices_1_to_10(self, user):
        from django.core.exceptions import ValidationError
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        comment = Comment(
            content_type=ct, object_id=film.pk, user=user,
            text='x', rating=11,
        )
        with pytest.raises(ValidationError):
            comment.full_clean()


@pytest.mark.django_db
class TestFavorite:

    def test_create(self, user):
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        fav = Favorite.objects.create(
            content_type=ct, object_id=film.pk, user=user,
        )
        assert fav.pk is not None
        assert fav.content_object == film
        assert fav.added_date is not None

    def test_unique_together_user_content(self, user):
        """Нельзя добавить один и тот же объект дважды."""
        from django.db import IntegrityError, transaction
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        Favorite.objects.create(
            content_type=ct, object_id=film.pk, user=user,
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Favorite.objects.create(
                    content_type=ct, object_id=film.pk, user=user,
                )

    def test_different_users_can_favorite_same_film(self, user):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        other = User.objects.create_user(username='u2', password='x')

        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        Favorite.objects.create(content_type=ct, object_id=film.pk, user=user)
        Favorite.objects.create(content_type=ct, object_id=film.pk, user=other)
        assert Favorite.objects.filter(
            content_type=ct, object_id=film.pk,
        ).count() == 2

    def test_str(self, user):
        film = FilmFactory(title='Матрица')
        ct = ContentType.objects.get_for_model(Film)
        fav = Favorite.objects.create(
            content_type=ct, object_id=film.pk, user=user,
        )
        assert user.username in str(fav)

    def test_related_name_favorites_on_user(self, user):
        film = FilmFactory()
        ct = ContentType.objects.get_for_model(Film)
        Favorite.objects.create(content_type=ct, object_id=film.pk, user=user)
        assert user.favorites.count() == 1