import requests
import os
import json
from environs import env
from .models import Film
import time
import shutil
import os

env.read_env()
api_key = env("API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
jsons_folder_path = "mainProject/templates/jsons/pages"

def parse_page(page, movies, img_url):
    for movie in page["results"]:

        overview = movie["overview"]

        movies.append({
            "id": movie["id"],
            "title": movie["title"],
            "overview": overview,
            "img_path": os.path.join(f"{img_url}{movie["poster_path"]}"),
            "release_date": movie["release_date"],
            "genre_ids": movie["genre_ids"],
            "rating": movie["vote_average"],
            "title_lang": movie["original_language"],
            "is_adult": movie["adult"]
        })
    
    return movies

def download_movies(start_page=1, end_page=2, language="en"):
    movies = []

    os.makedirs(jsons_folder_path, exist_ok=True)
    
    url = f"{BASE_URL}/movie/popular"
    img_url = "https://media.themoviedb.org/t/p/w220_and_h330_face/"

    for page_number in range(start_page, end_page+1):
        params = {
            "api_key": api_key,
            "language": language,
            "page": page_number,         
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            movies = parse_page(data, movies, img_url)
            time.sleep(0.1)

            filepath = f"page{page_number}.json"
            filepath = os.path.join(jsons_folder_path, filepath)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(movies, f, indent=4, ensure_ascii=False)

            movies = []
            
        except requests.exceptions.RequestException as e:
            print("Ошибка при запросе к TMDB API:", e)

def get_file_numbers():
    files = os.listdir(jsons_folder_path)
    file_numbers = []

    for file in files:
        file_name, file_type = file.split(".")
        
        if file_type == "json":
            file_number = file_name[4:]
            file_numbers.append(int(file_number))

    file_numbers.sort()
    return file_numbers

def json_to_db(upgraded_field):
    file_numbers = get_file_numbers()
    for num in file_numbers:
        filename = f"page{num}.json"
        path = os.path.join(jsons_folder_path, filename)
        print(path)

        if os.path.exists(path):
            with open(path, "r", encoding='utf-8') as f:
                films_data = json.load(f)

            for film_data in films_data:
                film_obj, created = Film.objects.get_or_create(
                    search_id=film_data["id"],
                    defaults={
                        'title': film_data["title"],
                        'overview': film_data["overview"],
                        'img_path': film_data["img_path"],
                        'release_date': film_data["release_date"],
                        'rating': film_data["rating"],
                        'title_lang': film_data["title_lang"],
                        'is_adult': film_data["is_adult"]
                    }
                )
                
                if not created and upgraded_field:
                    film_obj.title = film_data[upgraded_field]
                    film_obj.save()

def delete_everything_in_folder():
    shutil.rmtree(jsons_folder_path)
    os.mkdir(jsons_folder_path)    