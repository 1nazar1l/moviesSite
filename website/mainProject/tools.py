import requests
import os
import json
from environs import env
from .models import Film, Serial, Actor
import shutil
import os
from datetime import datetime


env.read_env()
api_key = env("API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
jsons_folder_path = "mainProject/templates/jsons"

def set_time():
    print(datetime.now().date())
    print(datetime.now().time())

def get_folder_path(media_type, jsons_folder_path):
    if media_type == "films":
        folder_path = f"{jsons_folder_path}/films"
    elif media_type == "serials":
        folder_path = f"{jsons_folder_path}/serials"
    elif media_type == "actors":
        folder_path = f"{jsons_folder_path}/actors"

    return folder_path

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

def collect_special_messages_block(messages, messages_block, request):
    messages.append("end")
    
    messages_block.append(messages)
    request.session['custom_messages'].extend(messages_block)
    request.session.modified = True

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

def get_media_items_id(media_type, start_page, end_page):
    if media_type == "films":
        url = f"{BASE_URL}/movie/popular"
    elif media_type == "serials":
        url = f"{BASE_URL}/tv/popular"
    elif media_type == "actors":
        url = f"{BASE_URL}/person/popular"

    media_items = []

    folder_path = get_folder_path(media_type, jsons_folder_path)
    os.makedirs(folder_path, exist_ok=True)

    for page_number in range(start_page, end_page + 1):
        params = {
            "api_key": api_key,
            "language": "en",
            "page": page_number,         
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        index = "title" if media_type == "films" else "name"
        
        data = response.json()
        for media_item in data["results"]:
            media_items.append({
                "id": media_item["id"],
                "name": media_item[index],
                "page_number": page_number
            })
        
    filename = f"{media_type}_id.json"
    filepath = os.path.join(folder_path, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(media_items, f, indent=4, ensure_ascii=False)

def parse_media_items(media_type):
    img_url = "https://media.themoviedb.org/t/p/w220_and_h330_face/"
    media_items = []

    folder_path = get_folder_path(media_type, jsons_folder_path)
    os.makedirs(folder_path, exist_ok=True)
    ids_json_filename = f"{media_type}_id.json"
    ids_json_filepath = os.path.join(folder_path, ids_json_filename)
    
    with open(ids_json_filepath, "r", encoding='utf-8') as f:
        media_items_data = json.load(f)

    for media_item_data in media_items_data:
        if media_type == "films":
            url = f"{BASE_URL}/movie/{media_item_data["id"]}"
        elif media_type == "serials":
            url = f"{BASE_URL}/tv/{media_item_data["id"]}"
        elif media_type == "actors":
            url = f"{BASE_URL}/person/{media_item_data["id"]}"

        
        if media_type != "actors":
            params = {
                "api_key": api_key,
                "language": "en",
            }
        else:
            params = {
                "api_key": api_key,
                "language": "en",
                "append_to_response": "movie_credits"
            }


        response = requests.get(url, params=params)
        response.raise_for_status()

        media_item = response.json()

        img_index = "profile_path" if media_type == "actors" else "poster_path"

        if media_item[img_index] is None:
            site_img_path = ""
            local_img_path = ""
        else:
            site_img_path = f"{img_url}/{media_item[img_index]}"
            local_img_path = f"images/{media_type}/{media_item["id"]}.jpg"


        if media_type == "films":
            media_item_object = {
                "id": media_item["id"],
                "title": media_item["title"],
                "budget": media_item["budget"],
                "revenue": media_item["revenue"],
                "genres": [{"id": genre["id"], "name": genre["name"]} for genre in media_item["genres"]],
                "overview": media_item["overview"],
                "site_img_path": site_img_path,
                "local_img_path": local_img_path,
                "release_date": media_item["release_date"],
                "runtime": media_item["runtime"],
                "status": media_item["status"],
                "vote_average": media_item["vote_average"],
            }
        elif media_type == "serials":
            media_item_object = {
                "created_by": [{
                    "id": author["id"], 
                    "name": author["name"]
                } for author in media_item["created_by"]],
                "first_air_date": media_item["first_air_date"],
                "genres": [{"id": genre["id"], "name": genre["name"]} for genre in media_item["genres"]],
                "id": media_item["id"],
                "last_air_date": media_item["last_air_date"],
                "name": media_item["name"],
                "networks": [{"id": network["id"], "name": network["name"]} for network in media_item["networks"]],
                "episodes": media_item["number_of_episodes"],
                "seasons": media_item["number_of_seasons"],
                "overview": media_item["overview"],
                "site_img_path": site_img_path,
                "local_img_path": local_img_path,
                "status": media_item["status"],
                "vote_average": media_item["vote_average"],
            }
        elif media_type == "actors":
            media_item_object = {
                "biography": media_item["biography"],
                "birthday": media_item["birthday"],
                "deathday": media_item["deathday"],
                "gender": media_item["gender"],
                "id": media_item["id"],
                "name": media_item["name"],
                "site_img_path": site_img_path,
                "local_img_path": local_img_path,
                "movies": [movie["id"] for movie in media_item["movie_credits"]["cast"]]
            }

        media_items.append(media_item_object)

    json_filename = f"{media_type}.json"
    json_filepath = os.path.join(folder_path, json_filename)

    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(media_items, f, indent=4, ensure_ascii=False)

def transfer_media_items_to_db(media_type):
    folder_path = get_folder_path(media_type, jsons_folder_path)
    os.makedirs(folder_path, exist_ok=True)

    json_filename = f"{media_type}.json"
    json_filepath = os.path.join(folder_path, json_filename)

    if os.path.exists(json_filepath):
        with open(json_filepath, "r", encoding='utf-8') as f:
            media_items = json.load(f)

    for media_item in media_items:
        if media_type == "films":
            defaults = {
                "id": media_item["id"],
                "title": media_item["title"],
                "budget": media_item["budget"],
                "revenue": media_item["revenue"],
                "overview": media_item["overview"],
                "site_img_path": media_item["site_img_path"],
                "local_img_path": media_item["local_img_path"],
                "release_date": media_item["release_date"],
                "runtime": media_item["runtime"],
                "status": media_item["status"],
                "rating": media_item["vote_average"],
            }
        elif media_type == "serials":
            defaults = {
                "id": media_item["id"],
                "first_air_date": media_item["first_air_date"],
                "last_air_date": media_item["last_air_date"],
                "title": media_item["name"],
                "episodes": media_item["episodes"],
                "seasons": media_item["seasons"],
                "overview": media_item["overview"],
                "site_img_path": media_item["site_img_path"],
                "local_img_path": media_item["local_img_path"],
                "status": media_item["status"],
                "rating": media_item["vote_average"],
            }
        elif media_type == "actors":
            defaults = {
                "id": media_item["id"],
                "name": media_item["name"],
                "biography": media_item["biography"],
                "birthday": media_item["birthday"],
                "deathday": media_item["deathday"],
                "gender": media_item["gender"],
                "site_img_path": media_item["site_img_path"],
                "local_img_path": media_item["local_img_path"],
            }

        if media_type == "films":
            media_item_obj, created = Film.objects.get_or_create(
                search_id=media_item["id"],
                defaults=defaults
            )
        elif media_type == "serials":
            media_item_obj, created = Serial.objects.get_or_create(
                search_id=media_item["id"],
                defaults=defaults
            )
        elif media_type == "actors":
            media_item_obj, created = Actor.objects.get_or_create(
                search_id=media_item["id"],
                defaults=defaults
            )

def start_parsing_media_items(request, media_type, messages, messages_block):
    vpn_is_connected = request.POST.get('vpn_is_connected')
    get_media_items_id_list = request.POST.get("get_media_items_id")
    start_page = request.POST.get('start_page')
    end_page = request.POST.get('end_page')
    get_media_items_data = request.POST.get("get_media_items_data")
    delete_jsons = request.POST.get('delete_jsons')
    update_db = request.POST.get('update_db')
    should_download_images = request.POST.get('download_images')
    
    if vpn_is_connected:
        try:
            start_page = int(start_page)
            end_page = int(end_page)

            if start_page < 0 or end_page < 0:
                messages.append(f"{media_type}Нельзя вводить числа меньше чем ноль")
                raise ValueError(f"Поддерживаются только положительные целочисленные типы данных")
            else:
                if start_page > end_page:
                    start_page, end_page = end_page, start_page
            try:
                if get_media_items_id_list:
                    get_media_items_id(media_type, start_page, end_page)
                    messages.append(f"{media_type}Id актеров получены")

                if get_media_items_data:
                    parse_media_items(media_type)
                    messages.append(f"{media_type}Данные актеров получены")

            except Exception as e:
                messages.append(f"{media_type}Возможно не включен VPN. Ошибка при запросе к TMDB API! {e}")

        except Exception as e:
            messages.append(f"{media_type}Можно вводить только целые числа: {e}")

    if update_db:
        transfer_media_items_to_db(media_type)
        messages.append(f"{media_type}Актеры занесены в бд")

    if delete_jsons:
        delete_everything_in_folder(media_type)
        messages.append(f"{media_type}Папка с json файлами очищена!")

    if vpn_is_connected and should_download_images:
        download_images(media_type)
        messages.append(f"{media_type}Фотографии актеров скачаны")

    collect_special_messages_block(messages, messages_block, request)