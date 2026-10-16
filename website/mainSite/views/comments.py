"""Создание комментариев с фильтрацией нецензурной лексики."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect

from badwords import ProfanityFilter
from mainProject.models import Actor, Comment, Film, Serial


@login_required
def create_comment(request):
    _filter = ProfanityFilter()
    _filter.init(["ru", "en"])

    if request.method == "POST":
        try:
            content_type_id = request.POST.get("content_type_id")
            object_id = request.POST.get("object_id")
            text = request.POST.get("text")
            rating = request.POST.get("rating")
            comment_is_private = request.POST.get("comment_is_private")

            if not all([content_type_id, object_id, text]):
                messages.error(request, "Заполните все обязательные поля.")
                return redirect(request.META.get("HTTP_REFERER", "profilePage"))

            cleaned_words = []
            for word in text.split(" "):
                if _filter.filter_text(word, match_threshold=0.5):
                    word = "*" * len(word)
                cleaned_words.append(word)
            text = " ".join(cleaned_words) + " "

            content_type = get_object_or_404(ContentType, id=content_type_id)
            model_class = content_type.model_class()
            content_object = get_object_or_404(model_class, id=object_id)

            Comment.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=object_id,
                text=text,
                rating=rating if rating else None,
                is_private=(comment_is_private == "on"),
            )

            messages.success(request, "Ваш комментарий успешно добавлен!")

            if hasattr(content_object, "search_id"):
                if model_class == Film:
                    return redirect(
                        "itemPage",
                        media_type="film",
                        search_id=content_object.search_id,
                    )
                if model_class == Serial:
                    return redirect(
                        "itemPage",
                        media_type="serial",
                        search_id=content_object.search_id,
                    )
                if model_class == Actor:
                    return redirect(
                        "itemPage",
                        media_type="actor",
                        search_id=content_object.search_id,
                    )

        except Exception as e:
            messages.error(request, f"Ошибка при добавлении комментария: {str(e)}")

    return redirect(request.META.get("HTTP_REFERER", "profilePage"))
