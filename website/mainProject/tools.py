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


def measure_time(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        func(*args, **kwargs)
        end = datetime.now()
        lead_time = end - start

        return start.replace(microsecond=0), lead_time.total_seconds()
    
    return wrapper

def create_error_message(messages, media_type, text):
    messages.append({
        "message_type": "error",
        "media_type": media_type,
        "text": text,
        "when_happened": str(datetime.now().replace(microsecond=0)),
        "time_to_complete": 0.0,
        "admin": "People"
    })

def create_warning_message(messages, media_type, text):
    messages.append({
        "message_type": "warning",
        "media_type": media_type,
        "text": text,
        "when_happened": str(datetime.now().replace(microsecond=0)),
        "time_to_complete": 0.0,
        "admin": "People"
    })

def create_success_message(messages, media_type, start_time, lead_time, text):
    messages.append({
        "message_type": "success",
        "media_type": media_type,
        "text": text,
        "when_happened": str(start_time),
        "time_to_complete": str(lead_time),
        "admin": "People"
    })

def get_folder_path(media_type, jsons_folder_path):
    return f"{jsons_folder_path}/{media_type}"

def collect_special_messages_block(messages, messages_block, request):
    messages_block.append(messages)
    request.session['custom_messages'].extend(messages_block)
    request.session.modified = True

@measure_time
def delete_everything_in_folder(folder_path):
    shutil.rmtree(folder_path)
    os.mkdir(folder_path)    

@measure_time
def download_images(model):
    for media_item in model.objects.all():
        img_filepath = os.path.join("mainProject/static", media_item.local_img_path)

        if not os.path.exists(img_filepath):
            if media_item.site_img_path != "":
                p = requests.get(media_item.site_img_path)
            
                with open(img_filepath, "wb") as out:
                    out.write(p.content)

@measure_time
def get_media_items_id(media_type, start_page, end_page, url, ids_filepath):
    media_items = []

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

    with open(ids_filepath, "w", encoding="utf-8") as f:
        json.dump(media_items, f, indent=4, ensure_ascii=False)

@measure_time
def parse_media_items(media_type, root_url, ids_json_filepath, media_datasets_filepath, img_url):
    media_items = []

    with open(ids_json_filepath, "r", encoding='utf-8') as f:
        media_items_data = json.load(f)

    for media_item_data in media_items_data:
        url = f"{root_url}/{media_item_data["id"]}"

        if media_type != "actors":
            params = {
                "api_key": api_key,
                "language": "en",
            }

            img_index = "poster_path"
        else:
            params = {
                "api_key": api_key,
                "language": "en",
                "append_to_response": "movie_credits"
            }

            img_index = "profile_path"

        response = requests.get(url, params=params)
        response.raise_for_status()

        media_item = response.json()

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

    with open(media_datasets_filepath, "w", encoding="utf-8") as f:
        json.dump(media_items, f, indent=4, ensure_ascii=False)

@measure_time
def transfer_media_items_to_db(messages, media_type, media_datasets_filepath, model):
    if os.path.exists(media_datasets_filepath):
        with open(media_datasets_filepath, "r", encoding='utf-8') as f:
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
                    "movies": media_item["movies"]
                }

            media_item_obj, created = model.objects.get_or_create(
                search_id=media_item["id"],
                defaults=defaults
            )

    else:
        create_error_message(messages, media_type, "Json файл с данными не был найден, либо был очищен")


def delete_selected_media_items(request, media_type, messages, messages_block):
    media_ids = request.POST.getlist('media_ids')

    if not media_ids:
        create_error_message(messages, media_type, "Не выбрано ни одного объекта для удаления")
        collect_special_messages_block(messages, messages_block, request)
        return

    try:
        models = {
            "films": Film,
            "serials": Serial,
            "actors": Actor,
        }

        model = models.get(media_type)
        
        if not model:
            create_error_message(messages, media_type, "Модель не найдена(delete_selected_media_items)")
            collect_special_messages_block(messages, messages_block, request)
            return

        start_time = datetime.now()
        media_items_to_delete = model.objects.filter(id__in=media_ids)

        if media_type != "actors":
            deleted_media_items = [[media_item.title, media_item.search_id] for media_item in media_items_to_delete]
        else:
            deleted_media_items = [[media_item.name, media_item.search_id] for media_item in media_items_to_delete]

        deleted_count = media_items_to_delete.delete()[0]

        end = datetime.now()
        lead_time = end - start_time

        create_success_message(
            messages, 
            media_type, 
            str(start_time.replace(microsecond=0)),
            str(lead_time.total_seconds()),
            f"Успешно удалено {deleted_count} объектов!"
        )


        for media_item in deleted_media_items:
            create_success_message(
                messages, 
                media_type, 
                str(start_time.replace(microsecond=0)),
                "0.000000",
                f"Объект {media_item[0]}(id {media_item[1]}) успешно удалён!"
            )

    except Exception as e:
        create_error_message(messages, media_type, f"Ошибка при удалении: {str(e)}")

    collect_special_messages_block(messages, messages_block, request)

def delete_all_media_items(request, media_type, messages, messages_block):
    models = {
        "films": Film,
        "serials": Serial,
        "actors": Actor,
    }

    model = models.get(media_type)

    if not model:
        create_error_message(messages, media_type, "Модель не найдена(delete_all_media_items)")
        collect_special_messages_block(messages, messages_block, request)
        return
    
    start_time = datetime.now()
    model.objects.all().delete()
    end = datetime.now()
    lead_time = end - start_time

    create_success_message(
        messages,
        media_type,
        str(start_time.replace(microsecond=0)),
        str(lead_time.total_seconds()),
        "Все объекты успешно удалены!"
    )

    collect_special_messages_block(messages, messages_block, request)

def start_parsing_media_items(request, media_type, messages, messages_block):
    vpn_is_connected = request.POST.get('vpn_is_connected')
    get_media_items_id_list = request.POST.get("get_media_items_id")
    start_page = request.POST.get('start_page')
    end_page = request.POST.get('end_page')
    get_media_items_data = request.POST.get("get_media_items_data")
    delete_jsons = request.POST.get('delete_jsons')
    update_db = request.POST.get('update_db')
    should_download_images = request.POST.get('download_images')

    models = {
        "films": Film,
        "serials": Serial,
        "actors": Actor,
    }

    model = models.get(media_type)

    if media_type == "films":
        media_items_ids_root_url = f"{BASE_URL}/movie/popular"
        media_item_data_root_url = f"{BASE_URL}/movie"
    elif media_type == "serials":
        media_items_ids_root_url = f"{BASE_URL}/tv/popular"
        media_item_data_root_url = f"{BASE_URL}/tv"
    elif media_type == "actors":
        media_items_ids_root_url = f"{BASE_URL}/person/popular"
        media_item_data_root_url = f"{BASE_URL}/person"

    folder_path = get_folder_path(media_type, jsons_folder_path)
    os.makedirs(folder_path, exist_ok=True)

    url_for_download_images = "https://media.themoviedb.org/t/p/w220_and_h330_face/"
    
    imgs_folder = f"mainProject/static/images/{media_type}"
    os.makedirs(imgs_folder, exist_ok=True)

    ids_json_filename = f"{media_type}_id.json"
    ids_json_filepath = os.path.join(folder_path, ids_json_filename)

    media_datasets_json_filename = f"{media_type}.json"
    media_datasets_json_filepath = os.path.join(folder_path, media_datasets_json_filename)

    if not model:
        create_error_message(messages, media_type, "Модель не найдена")
        collect_special_messages_block(messages, messages_block, request)
        return

    if vpn_is_connected and get_media_items_id_list:
        try:
            start_time, lead_time = get_media_items_id(media_type, start_page, end_page, media_items_ids_root_url, ids_json_filepath)
            create_success_message(messages, media_type, start_time, lead_time, "Id объектов получены")

        except requests.exceptions.ConnectionError:
            create_error_message(messages, media_type, "VPN не включен!")

    if vpn_is_connected and get_media_items_data:
        try:
            start_time, lead_time = parse_media_items(media_type, media_item_data_root_url, ids_json_filepath, media_datasets_json_filepath, url_for_download_images)
            create_success_message(messages, media_type, start_time, lead_time, "Данные объектов получены")

        except Exception as e:
            create_error_message(messages, media_type, f"Возможно не включен VPN. Ошибка при запросе к TMDB API! {e}")

    if update_db:
        start_time, lead_time = transfer_media_items_to_db(messages, media_type, media_datasets_json_filepath, model)
        create_success_message(messages, media_type, start_time, lead_time, "Объекты занесены в бд")

    if delete_jsons:
        start_time, lead_time = delete_everything_in_folder(folder_path)
        create_success_message(messages, media_type, start_time, lead_time, "Папка с json файлами очищена!")

    if vpn_is_connected and should_download_images:
        start_time, lead_time = download_images(model)

        create_success_message(
            messages, 
            media_type, 
            start_time, 
            lead_time, 
            "Фотографии актеров скачаны" if media_type == "actors" else "Постеры скачаны"
        )

    collect_special_messages_block(messages, messages_block, request)
