"""Пользовательские списки: CRUD списков и элементов."""

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect, render

from badwords import ProfanityFilter
from mainProject.models import Actor, Film, Serial
from mainSite.models import ListItem, UserList


def add_list(request):
    _filter = ProfanityFilter()
    _filter.init(["ru", "en"])

    request.session.modified = True
    request.session["list_error_messages"] = []

    if request.POST:
        list_name = request.POST.get("list_name")
        list_description = request.POST.get("list_description")
        list_type = request.POST.get("list_type")
        list_is_private = request.POST.get("list_is_private")

        cleaned_words = []
        for word in list_name.split(" "):
            if _filter.filter_text(word, match_threshold=0.5):
                word = "*" * len(word)
            cleaned_words.append(word)
        list_name = " ".join(cleaned_words) + " "

        user = request.user
        user_lists = user.user_lists.all()
        if user_lists.filter(title=list_name):
            request.session["list_error_messages"].append(
                f"Лист с названием {list_name} уже существует в вашем списке"
            )
        else:
            UserList.objects.create(
                user=request.user,
                title=list_name,
                description=list_description,
                list_type=list_type,
                is_private=(list_is_private == "on"),
            )

    return redirect("profilePage")


def delete_list(request):
    list_id = request.POST.get("list_id")
    UserList.objects.get(id=list_id).delete()
    return redirect("profilePage")


def add_item_to_list(request):
    if request.method == "POST":
        item_id = request.POST.get("item_id")
        item_media_type = request.POST.get("item_media_type")
        list_id = request.POST.get("list_id")

        user_list = get_object_or_404(UserList, id=list_id, user=request.user)

        model_class = {"films": Film, "serials": Serial, "actors": Actor}.get(item_media_type)
        content_object = get_object_or_404(model_class, id=item_id)
        content_type = ContentType.objects.get_for_model(model_class)

        if not ListItem.objects.filter(
            user_list=user_list,
            content_type=content_type,
            object_id=item_id,
        ).exists():
            ListItem.objects.create(
                user_list=user_list,
                content_type=content_type,
                object_id=item_id,
                content_object=content_object,
            )

    return redirect(request.META.get("HTTP_REFERER", "home"))


def listPage(request, list_id):
    errors = request.session.get("list_error_messages", [])
    user_list = UserList.objects.get(id=list_id)
    user = user_list.user
    user_is_author = user.username == request.user.username
    items = user_list.items.all()
    for item in items:
        item.media_type = item.content_type.model

    return render(
        request,
        "main/list.html",
        context={
            "username": user.username,
            "user_list": user_list,
            "user_is_author": user_is_author,
            "author": user,
            "items": items,
            "items_count": len(items),
            "errors": errors,
        },
    )


def userListPage(request, user_id, list_id):
    user_list = UserList.objects.get(id=list_id)
    if user_list.is_private:
        return redirect("userPage", user_id=user_id)

    user = user_list.user
    user_is_author = user.username == request.user.username
    items = user_list.items.all()
    for item in items:
        item.media_type = item.content_type.model

    return render(
        request,
        "main/list.html",
        context={
            "username": user.username,
            "user_list": user_list,
            "user_is_author": user_is_author,
            "author": user,
            "items": items,
            "items_count": len(items),
            "user_id": user_id,
        },
    )


def delete_item_from_list(request):
    if request.method == "POST":
        media_type = request.POST.get("content_type")
        object_id = request.POST.get("object_id")
        list_id = request.POST.get("list_id")

        content_type = ContentType.objects.get(model=media_type.lower())
        user_list = UserList.objects.get(id=list_id)
        user_list.items.get(
            content_type=content_type,
            object_id=object_id,
        ).delete()

    return redirect(request.META.get("HTTP_REFERER", "home"))


def edit_list(request):
    request.session.modified = True
    request.session["list_error_messages"] = []

    if request.POST:
        list_id = request.POST.get("list_id")
        list_name = request.POST.get("list_name")
        list_description = request.POST.get("list_description")
        list_type = request.POST.get("list_type")
        list_is_private = request.POST.get("list_is_private")

        user_lists = request.user.user_lists.all()
        user_list = user_lists.get(id=list_id)

        if user_list.title != list_name:
            if user_lists.filter(title=list_name):
                request.session["list_error_messages"].append(
                    f"Лист с названием {list_name} уже существует в вашем списке"
                )
            else:
                user_list.title = list_name

        user_list.description = list_description
        user_list.list_type = list_type
        user_list.is_private = list_is_private == "on"
        user_list.save()

    return redirect(request.META.get("HTTP_REFERER", "home"))
