"""Избранное: добавление и удаление."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect

from mainProject.models import Favorite


@login_required
def add_to_favorite(request):
    if request.method == 'POST':
        try:
            content_type_name = request.POST.get('content_type')
            object_id = request.POST.get('object_id')

            if not all([content_type_name, object_id]):
                messages.error(request, 'Ошибка: не указан объект')
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            content_type = ContentType.objects.get(model=content_type_name.lower())
            model_class = content_type.model_class()
            content_object = model_class.objects.get(id=object_id)

            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=object_id,
            )
            if created:
                messages.success(request, f'{content_object} добавлен в избранное!')
            else:
                messages.info(request, f'{content_object} уже в избранном')

        except ContentType.DoesNotExist:
            messages.error(request, 'Ошибка: тип объекта не найден')
        except Exception as e:
            messages.error(request, f'Ошибка при добавлении в избранное: {str(e)}')

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def remove_from_favorite(request):
    if request.method == 'POST':
        try:
            content_type_name = request.POST.get('content_type')
            object_id = request.POST.get('object_id')

            if not all([content_type_name, object_id]):
                messages.error(request, 'Ошибка: не указан объект')
                return redirect(request.META.get('HTTP_REFERER', 'home'))

            content_type = ContentType.objects.get(model=content_type_name.lower())
            Favorite.objects.get(
                user=request.user, content_type=content_type, object_id=object_id,
            ).delete()

        except ContentType.DoesNotExist:
            messages.error(request, 'Ошибка: тип объекта не найден')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении из избранного: {str(e)}')

    return redirect(request.META.get('HTTP_REFERER', 'home'))