import requests
import os
import json
from environs import env
from .models import Film, Serial, Actor
import time
import shutil
import os

env.read_env()
api_key = env("API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
jsons_folder_path = "mainProject/templates/jsons"

def parse_page(media_type, page, media_items, img_url):
    for media_item in page["results"]:

        id = media_item["id"]
        title = media_item["title"] if media_type == "films" else media_item["name"]
        overview = media_item["overview"]

        if media_item["poster_path"] is None:
            site_img_path = ""
            local_img_path = ""
        else:
            site_img_path = f"{img_url}/{media_item["poster_path"]}"
            local_img_path = f"images/{media_type}/{media_item["id"]}.jpg"

        release_date = media_item["release_date"] if media_type == "films" else media_item["first_air_date"]
        genre_ids =  media_item["genre_ids"]
        rating = media_item["vote_average"]
        title_lang = media_item["original_language"]
        is_adult = media_item["adult"]

        media_items.append({
            "id": id,
            "title": title,
            "overview": overview,
            "site_img_path": site_img_path,
            "local_img_path": local_img_path,
            "release_date": release_date,
            "genre_ids": genre_ids,
            "rating": rating,
            "title_lang": title_lang,
            "is_adult": is_adult
        })
    
    return media_items

def get_folder_path(media_type, jsons_folder_path):
    if media_type == "films":
        folder_path = f"{jsons_folder_path}/films"
    elif media_type == "serials":
        folder_path = f"{jsons_folder_path}/serials"
    elif media_type == "actors":
        folder_path = f"{jsons_folder_path}/actors"

    return folder_path

def download_media_items(media_type, start_page=1, end_page=2, language="en"):
    media_items = []
    url = ""    
    folder_path = get_folder_path(media_type, jsons_folder_path)
    os.makedirs(folder_path, exist_ok=True)

    if media_type == "films":
        url = f"{BASE_URL}/movie/popular"

    elif media_type == "serials":
        url = f"{BASE_URL}/tv/popular"

    img_url = "https://media.themoviedb.org/t/p/w220_and_h330_face/"

    for page_number in range(start_page, end_page+1):
        params = {
            "api_key": api_key,
            "language": language,
            "page": page_number,         
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        print(response.url)
        
        data = response.json()
        media_items = parse_page(media_type, data, media_items, img_url)
        time.sleep(0.1)

        filepath = f"page{page_number}.json"
        filepath = os.path.join(folder_path, filepath)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(media_items, f, indent=4, ensure_ascii=False)

        media_items = []

def get_file_numbers(folder_path):
    files = os.listdir(folder_path)
    file_numbers = []

    for file in files:
        file_name, file_type = file.split(".")
        
        if file_type == "json":
            file_number = file_name[4:]
            file_numbers.append(int(file_number))

    file_numbers.sort()
    return file_numbers

def json_to_db(media_type, upgraded_field, operation_messages):
    folder_path = get_folder_path(media_type, jsons_folder_path)
    file_numbers = get_file_numbers(folder_path)

    for num in file_numbers:
        filename = f"page{num}.json"
        path = os.path.join(folder_path, filename)

        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as f:
                media_items = json.load(f)

            for media_item in media_items:
                if media_type == "films":
                    media_obj, created = Film.objects.get_or_create(
                        search_id=media_item["id"],
                        defaults={
                            'title': media_item["title"],
                            'overview': media_item["overview"],
                            'site_img_path': media_item["site_img_path"],
                            'local_img_path': media_item["local_img_path"],
                            'release_date': media_item["release_date"],
                            'rating': media_item["rating"],
                            'title_lang': media_item["title_lang"],
                            'is_adult': media_item["is_adult"]
                        }
                    )
                elif media_type == "serials":
                    media_obj, created = Serial.objects.get_or_create(
                        search_id=media_item["id"],
                        defaults={
                            'title': media_item["title"],
                            'overview': media_item["overview"],
                            'site_img_path': media_item["site_img_path"],
                            'local_img_path': media_item["local_img_path"],
                            'release_date': media_item["release_date"],
                            'rating': media_item["rating"],
                            'title_lang': media_item["title_lang"],
                            'is_adult': media_item["is_adult"]
                        }
                    )

        else:
            operation_messages.append(f"Путь {path} не существует")

def delete_everything_in_folder(media_type):
    folder_path = get_folder_path(media_type, jsons_folder_path)

    shutil.rmtree(folder_path)
    os.mkdir(folder_path)    

def download_images(media_type):
    imgs_folder = f"mainProject/static/images/{media_type}"
    os.makedirs(imgs_folder, exist_ok=True)

    if media_type == "films":
        media_items = Film.objects.all()
    elif media_type == "serials":
        media_items = Serial.objects.all()
    if media_type == "actors":
        media_items = Actor.objects.all()

    for media_item in media_items:
        img_filepath = os.path.join("mainProject/static", media_item.local_img_path)

        if not os.path.exists(img_filepath):
            if media_item.site_img_path != "":
                p = requests.get(media_item.site_img_path)
            
                with open(img_filepath, "wb") as out:
                    out.write(p.content)

    # folder_path = get_folder_path(media_type, jsons_folder_path)

    # file_numbers = get_file_numbers(folder_path)

    # for num in file_numbers:
    #     json_filename = f"page{num}.json"
    #     json_path = os.path.join(folder_path, json_filename)

    #     if os.path.exists(json_path):
    #         with open(json_path, "r", encoding='utf-8') as f:
    #             media_items_data = json.load(f)

    #         for media_item in media_items_data:
    #             img_filepath = os.path.join("mainProject/static", media_item["local_img_path"])

    #             if not os.path.exists(img_filepath):
    #                 if media_item["site_img_path"] != "":
    #                     p = requests.get(media_item["site_img_path"])
                    
    #                     with open(img_filepath, "wb") as out:
    #                         out.write(p.content)

def collect_special_messages_block(messages, messages_block, request):
    messages.append("end")
    
    messages_block.append(messages)
    request.session['custom_messages'].extend(messages_block)
    request.session.modified = True

def parse_media_items(request, media_type, messages, messages_block):
    start_page = request.POST.get('start_page')
    end_page = request.POST.get('end_page')
    delete_jsons = request.POST.get('delete_jsons')
    update_db = request.POST.get('update_db')
    vpn_is_connected = request.POST.get('vpn_is_connected')
    upgraded_field = request.POST.get('upgraded_field')
    should_download_images = request.POST.get("should_download_images")

    if vpn_is_connected:
        try:
            start_page = int(start_page)
            end_page = int(end_page)

            if start_page < 0 or end_page < 0:
                messages.append("Нельзя вводить числа меньше чем ноль")
                raise ValueError("Поддерживаются только положительные целочисленные типы данных")
            else:
                if start_page > end_page:
                    start_page, end_page = end_page, start_page
            try:
                download_media_items(media_type, start_page, end_page)
                if media_type == "films":
                    messages.append("Фильмы скачаны!")
                elif media_type == "serials":
                    messages.append("Сериалы скачаны!")

            except Exception as e:
                messages.append(f"Возможно не включен VPN. Ошибка при запросе к TMDB API! {e}")

        except Exception as e:
            messages.append(f"Можно вводить только целые числа: {e}")
        
    if update_db:
        json_to_db(media_type, upgraded_field, messages)
        if media_type == "films":
            messages.append("Фильмы перенесены в базу данных!")
        elif media_type == "serials":
            messages.append("Сериалы перенесены в базу данных!")
        if upgraded_field:
            messages.append(f"Обновленно поле {upgraded_field}!")

    if delete_jsons:
        delete_everything_in_folder(media_type)
        messages.append("Папка с json файлами очищена!")

    if vpn_is_connected and should_download_images:
        download_images(media_type)

        if media_type == "films":
                messages.append("Постеры к фильмам скачаны!")
        elif media_type == "serials":
            messages.append("Постеры к сериалам скачаны!")

    collect_special_messages_block(messages, messages_block, request)

def delete_selected_media_items(request, media_type, messages, messages_block):
    media_ids = request.POST.getlist('media_ids')

    if not media_ids:
        if media_type == "films":
            messages.append("Не выбрано ни одного фильма для удаления")
        elif media_type == "serials":
            messages.append("Не выбрано ни одного сериала для удаления")
        elif media_type == "actors":
            messages.append("Не выбрано ни одного актера для удаления")
    else:
        try:
            if media_type == "films":
                media_items_to_delete = Film.objects.filter(id__in=media_ids)
            elif media_type == "serials":
                media_items_to_delete = Serial.objects.filter(id__in=media_ids)
            elif media_type == "actors":
                media_items_to_delete = Actor.objects.filter(id__in=media_ids)

            if media_type != "actors":
                deleted_media_items = [[media_item.title, media_item.search_id] for media_item in media_items_to_delete]
            else:
                deleted_media_items = [[media_item.name, media_item.search_id] for media_item in media_items_to_delete]

            deleted_count = media_items_to_delete.delete()[0]

            if media_type == "films":
                messages.append(f"Успешно удалено {deleted_count} фильмов!")
            elif media_type == "serials":
                messages.append(f"Успешно удалено {deleted_count} сериалов!")
            elif media_type == "actors":
                messages.append(f"Успешно удалено {deleted_count} актеров!")

            for media_item in deleted_media_items:
                if media_type == "films":
                    messages.append(f"Фильм {media_item[0]}(id {media_item[1]}) успешно удалён!")
                elif media_type == "serials":
                    messages.append(f"Сериал {media_item[0]}(id {media_item[1]}) успешно удалён!")
                elif media_type == "actors":
                    messages.append(f"Актер {media_item[0]}(id {media_item[1]}) успешно удалён!")
                    

        except Exception as e:
            messages.append(f"Ошибка при удалении: {str(e)}")

    collect_special_messages_block(messages, messages_block, request)

def delete_all_media_items(request, media_type, messages, messages_block):
    if media_type == "films":
        films = Film.objects.all().delete()
        messages.append(f"Все фильмы успешно удалены!")
    elif media_type == "serials":
        serials = Serial.objects.all().delete()
        messages.append(f"Все сериалы успешно удалены!")
    elif media_type == "actors":
        actors = Actor.objects.all().delete()
        messages.append(f"Все актеры успешно удалены!")
        
    collect_special_messages_block(messages, messages_block, request)

def get_actors_id(start_page, end_page):
    url = f"{BASE_URL}/person/popular"
    actors = []

    folder_path = get_folder_path("actors", jsons_folder_path)
    os.makedirs(folder_path, exist_ok=True)

    for page_number in range(start_page, end_page + 1):
        params = {
            "api_key": api_key,
            "language": "en",
            "page": page_number,         
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        for actor in data["results"]:
            actors.append({
                "id": actor["id"],
                "name": actor["name"],
                "page_number": page_number
            })
        
    filepath = "actors_id.json"
    filepath = os.path.join(folder_path, filepath)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(actors, f, indent=4, ensure_ascii=False)

def parse_actors():
    img_url = "https://media.themoviedb.org/t/p/w220_and_h330_face/"
    actors = []

    path = f"{jsons_folder_path}/actors/actors_id.json"

    folder_path = get_folder_path("actors", jsons_folder_path)
    os.makedirs(folder_path, exist_ok=True)

    with open(path, "r", encoding='utf-8') as f:
        actors_data = json.load(f)

    for actor in actors_data:

        url = f"{BASE_URL}/person/{actor["id"]}"

        params = {
            "api_key": api_key,
            "language": "en",
            "append_to_response": "movie_credits"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if data["profile_path"] is None:
            site_img_path = ""
            local_img_path = ""
        else:
            site_img_path = f"{img_url}/{data["profile_path"]}"
            local_img_path = f"images/actors/{data["id"]}.jpg"

        actors.append({
            "biography": data["biography"],
            "birthday": data["birthday"],
            "deathday": data["deathday"],
            "gender": data["gender"],
            "id": data["id"],
            "name": data["name"],
            "site_img_path": site_img_path,
            "local_img_path": local_img_path,
            "movies": [movie["id"] for movie in data["movie_credits"]["cast"]]
        })

    filepath = "actors.json"
    filepath = os.path.join(folder_path, filepath)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(actors, f, indent=4, ensure_ascii=False)
    
def transfer_actors_to_db():
    path = f"{jsons_folder_path}/actors/actors.json"

    folder_path = get_folder_path("actors", jsons_folder_path)
    os.makedirs(folder_path, exist_ok=True)

    if os.path.exists(path):
        with open(path, "r", encoding='utf-8') as f:
            actors_data = json.load(f)

    for actor in actors_data:
        actor_obj, created = Actor.objects.get_or_create(
            search_id=actor["id"],
            defaults={
                "name": actor["name"],
                "biography": actor["biography"],
                "birthday": actor["birthday"],
                "deathday": actor["deathday"],
                "gender": actor["gender"],
                "site_img_path": actor["site_img_path"],
                "local_img_path": actor["local_img_path"],
            }
        )

def parse_actors_item(request, media_type, messages, messages_block):
    vpn_is_connected = request.POST.get('vpn_is_connected')
    get_actors_id_list = request.POST.get("get_actors_id")
    start_page = request.POST.get('start_page')
    end_page = request.POST.get('end_page')
    get_actors_data = request.POST.get("get_actors_data")
    delete_jsons = request.POST.get('delete_jsons')
    update_db = request.POST.get('update_db')
    checkbox_download_images = request.POST.get('download_images')
    
    if vpn_is_connected:
        try:
            start_page = int(start_page)
            end_page = int(end_page)

            if start_page < 0 or end_page < 0:
                messages.append("Нельзя вводить числа меньше чем ноль")
                raise ValueError("Поддерживаются только положительные целочисленные типы данных")
            else:
                if start_page > end_page:
                    start_page, end_page = end_page, start_page
            try:
                if get_actors_id_list:
                    get_actors_id(start_page, end_page)
                    messages.append("Id актеров получены")

                if get_actors_data:
                    parse_actors()
                    messages.append("Данные актеров получены")

            except Exception as e:
                messages.append(f"Возможно не включен VPN. Ошибка при запросе к TMDB API! {e}")

        except Exception as e:
            messages.append(f"Можно вводить только целые числа: {e}")

    if update_db:
        transfer_actors_to_db()
        messages.append("Актеры занесены в бд")

    if delete_jsons:
        delete_everything_in_folder(media_type)
        messages.append("Папка с json файлами очищена!")

    if vpn_is_connected and checkbox_download_images:
        download_images(media_type)
        messages.append("Фотографии актеров скачаны")

    collect_special_messages_block(messages, messages_block, request)