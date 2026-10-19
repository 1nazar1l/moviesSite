# MoviesSite

Веб-приложение для каталогизации фильмов, сериалов и актёров, написанное на
Django. По функционалу напоминает упрощённую версию «Кинопоиска» или Letterboxd:
каталог с фильтрами, карточки актёров, комментарии с оценками, личные списки и
избранное. Данные о фильмах, сериалах и актёрах загружаются автоматически из
открытого API [The Movie Database (TMDB)](https://www.themoviedb.org/).

Проект создавался как курсовой и позже был доработан: переведён на PostgreSQL,
контейнеризирован в Docker, покрыт тестами, подключён CI на GitHub Actions.

## Возможности

### Для посетителей сайта
- Каталог фильмов и сериалов с фильтрами по жанру, рейтингу, датам выхода,
  бюджету и сборам.
- Страницы актёров с биографией и списком работ.
- Глобальный поиск по названиям фильмов, сериалов и именам актёров.
- Трейлеры фильмов и сериалов: сначала запрашиваются через API TMDB, при их
  отсутствии — через поиск на YouTube.
- Оценка фильмов и сериалов от 1 до 10 через систему комментариев.
- Просмотр публичных профилей других пользователей и их списков.

### Для зарегистрированных пользователей
- Личный профиль: аватар, никнейм, описание, статистика (сколько дней на сайте,
  сколько оценок, комментариев, избранного).
- Система комментариев с оценкой. Комментарии можно делать публичными или
  приватными (видны только автору). Для комментариев и названий списков
  реализована фильтрация нецензурной лексики на русском и английском.
- Лайки и дизлайки к комментариям.
- Избранное — универсальная сущность: можно добавить фильм, сериал или актёра.
- Пользовательские списки четырёх типов: избранное, «смотреть позже»,
  «просмотрено» и произвольные. Списки бывают публичными и приватными,
  элементы можно сортировать и снабжать заметками.

### Для администраторов
- Отдельная админ-панель (не путать со стандартным `/admin/`): таблицы фильмов,
  сериалов, актёров и жанров с расширенными фильтрами по всем полям.
- Парсинг популярного контента из TMDB постранично с автоматическим скачиванием
  постеров и фотографий.
- Ручной парсинг отдельного фильма/сериала/актёра по его TMDB ID. При парсинге
  актёра автоматически подтягиваются его работы, при парсинге фильма — главные
  актёры (до 10 человек).
- Массовое удаление выбранных записей или полная очистка раздела.
- Отдельный журнал операций (модель `Message`): какие действия выполнялись,
  сколько заняли, чем закончились.

## Технологический стек

| Слой | Что используется |
|---|---|
| Язык | Python 3.12 |
| Web-фреймворк | Django 5.2 |
| БД | PostgreSQL 16 (в Docker), SQLite (для локальной разработки без Docker) |
| Внешние API | TMDB (фильмы, сериалы, актёры), YouTube (fallback для трейлеров) |
| HTTP-клиент | `requests` |
| Парсинг HTML | `beautifulsoup4` |
| Работа с изображениями | Pillow |
| Фильтрация мата | `badwords` (вендорная библиотека в `website/badwords/`) |
| Конфигурация | `environs` + `.env` |
| Тесты | `pytest-django`, `factory_boy` (87 тестов) |
| Линт и форматирование | `ruff`, `black`, `isort` |
| CI | GitHub Actions: `lint` + `test` на PostgreSQL |
| Контейнеризация | Docker, docker-compose |

## Требования

- **Docker Desktop** (Windows/macOS) или Docker Engine + docker compose (Linux).
- **Ключ TMDB API** — получить можно бесплатно на
  [themoviedb.org/settings/api](https://www.themoviedb.org/settings/api). Без него
  не работает только парсинг, остальной сайт доступен.
- **Пароль приложения Яндекса** — нужен только если хотите, чтобы при регистрации
  отправлялось приветственное письмо. Можно оставить фиктивным, тогда письма
  будут падать молча (`fail_silently=True`).
- **VPN** — TMDB API периодически блокируется в РФ. Для парсинга нужен VPN
  на машине, где запущен Docker.

## Запуск через Docker

Самый простой способ — всё поднимается одной командой.

### 1. Клонировать репозиторий

```bash
git clone https://github.com/1nazar1l/moviesSite.git
cd moviesSite
```

### 2. Создать файл `.env`

В корне проекта лежит `.env.example` — это шаблон. Скопируйте его и заполните:

```bash
cp .env.example .env
```

Обязательные переменные:

- `SECRET_KEY` — 50+ случайных символов. Сгенерировать можно так:
  ```bash
  python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```
- `API_KEY` — ключ TMDB.
- `EMAIL_HOST_USER` и `EMAIL_HOST_PASSWORD` — адрес Яндекс-почты и пароль
  приложения (создаётся в настройках Яндекс ID, раздел «Пароли приложений»).

Опциональные:

- `DEBUG` — `True` для разработки, `False` для продакшена. По умолчанию `False`.
- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` — через запятую, если сайт
  будет доступен не только с `localhost`.

### 3. Поднять контейнеры

```bash
docker compose up -d --build
```

Будут запущены два сервиса: `db` (PostgreSQL 16) и `web` (Django на `runserver`).
Первый билд занимает 3–5 минут: скачивается `python:3.12-slim`, ставятся
системные зависимости для `psycopg` и Pillow.

### 4. Применить миграции

```bash
docker compose exec web python manage.py migrate
```

### 5. Создать администратора

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Открыть сайт

- Основной сайт: http://127.0.0.1:8000/
- Админ-панель проекта: http://127.0.0.1:8000/adminPanel/films/
- Стандартная админка Django: http://127.0.0.1:8000/admin/

Чтобы загрузить первый контент, зайдите в `/adminPanel/films/`, введите номер
страницы TMDB (например, `1` — `2`) и нажмите «Парсить». Понадобится VPN.

## Локальная разработка без Docker

Если Docker не нужен (например, для быстрой отладки шаблонов), можно поднять
проект на SQLite.

### 1. Виртуальное окружение

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Зависимости

```bash
pip install -r requirements/dev.txt
```

### 3. `.env`

Скопируйте `.env.example` в `.env` и заполните. **Не задавайте `DB_ENGINE`** —
тогда Django автоматически использует SQLite (`website/db.sqlite3`).

### 4. Миграции и запуск

```bash
cd website
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Конфигурация (.env)

| Переменная | Обязательна | Назначение |
|---|---|---|
| `SECRET_KEY` | да | Django secret key |
| `API_KEY` | да | TMDB API key |
| `DEBUG` | нет (по умолчанию `False`) | Режим отладки |
| `ALLOWED_HOSTS` | для прода | Список хостов через запятую |
| `CSRF_TRUSTED_ORIGINS` | для прода | Доверенные origin'ы |
| `EMAIL_HOST_USER` | нет | Адрес Яндекс-почты для писем |
| `EMAIL_HOST_PASSWORD` | нет | Пароль приложения Яндекса |
| `DB_ENGINE` | нет | `django.db.backends.postgresql`, если нужен Postgres |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | при Postgres | Параметры подключения |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | при Docker | Параметры контейнера Postgres |

Пример `.env` для Docker:

```env
SECRET_KEY=change-me-to-50-random-chars
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000

API_KEY=your_tmdb_api_key_here

EMAIL_HOST_USER=you@yandex.com
EMAIL_HOST_PASSWORD=your_app_password_here

DB_ENGINE=django.db.backends.postgresql
DB_NAME=movies
DB_USER=movies
DB_PASSWORD=movies_secret_change_me
DB_HOST=db
DB_PORT=5432

POSTGRES_DB=movies
POSTGRES_USER=movies
POSTGRES_PASSWORD=movies_secret_change_me
```

## Структура проекта

```
moviesSite/
├── .github/
│   └── workflows/
│       └── ci.yml                 # lint + test на push/PR
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml                 # конфиг ruff/black/isort
├── requirements/
│   ├── base.txt                   # прод-зависимости
│   └── dev.txt                    # + тесты, линтеры, debug toolbar
└── website/
    ├── manage.py
    ├── pytest.ini
    ├── conftest.py                # общие фикстуры (user, admin_user, client_logged)
    ├── badwords/                  # вендорная библиотека фильтрации мата
    ├── mainProject/               # контент: фильмы, сериалы, актёры
    │   ├── models.py
    │   ├── admin.py
    │   ├── middleware.py          # AdminAccessMiddleware (только для админов)
    │   ├── tools.py               # фасад над services/ (обратная совместимость)
    │   ├── services/
    │   │   ├── messages.py        # лог операций
    │   │   ├── tmdb.py            # клиент TMDB
    │   │   ├── trailers.py        # поиск трейлеров
    │   │   ├── media_download.py  # создание/обновление объекта + скачивание постера
    │   │   └── parsing.py         # постраничный и точечный парсинг
    │   ├── views/
    │   │   ├── panels.py          # 4 таблицы админки
    │   │   └── actions.py         # delete/parse/clear_messages
    │   ├── templates/adminPanel/
    │   ├── static/adminPanel/
    │   └── tests/                 # 42 теста
    ├── mainSite/                  # пользовательская часть
    │   ├── models.py              # UserList, ListItem
    │   ├── views/
    │   │   ├── _helpers.py
    │   │   ├── pages.py           # главная, каталоги, поиск, карточка
    │   │   ├── auth.py            # логин, регистрация, выход
    │   │   ├── profile.py         # профиль, аватар, редактирование
    │   │   ├── comments.py
    │   │   ├── favorites.py
    │   │   ├── lists.py
    │   │   └── admin_tools.py
    │   ├── templates/main/
    │   ├── static/main/
    │   └── tests/                 # 21 тест
    ├── users/                     # кастомный User
    │   ├── models.py
    │   ├── admin.py
    │   └── tests/                 # 15 тестов
    └── website/
        ├── settings.py
        ├── urls.py
        ├── wsgi.py
        └── asgi.py
```

## Основные модели

- **`Film`**, **`Serial`**, **`Actor`**, **`Genre`** — контент. У `Film` и `Serial`
  общие поля (`search_id` в TMDB, `title`, `overview`, `site_img_path`,
  `local_img_path`, `rating`, `trailer_url`), разные специфичные (у фильма —
  `budget`, `revenue`, `runtime`, у сериала — `seasons`, `episodes`,
  `first_air_date`, `last_air_date`). Связь «актёр — фильм/сериал»
  хранится через `Actor.movies` и `Actor.serials` (с `related_name='actors'`),
  обратное чтение — `film.actors.all()`.
- **`Comment`** — универсальный (через `GenericForeignKey`), работает для
  `Film`, `Serial` и `Actor`. Поля: `text`, `rating` (1–10), `is_private`,
  `likes` / `dislikes` (M2M на пользователей), `writing_date`.
- **`Favorite`** — универсальное избранное. `unique_together` по
  `(user, content_type, object_id)` — один и тот же объект нельзя добавить
  дважды.
- **`UserList`** — список пользователя: `title`, `description`, `list_type`
  (favorite / watch_later / watched / custom), `is_private`. У одного
  пользователя не может быть двух списков с одинаковым названием.
- **`ListItem`** — элемент списка. Позиция проставляется в `save()` как
  `max(position) + 1`. `unique_together` по `(user_list, content_type, object_id)`.
- **`User`** — кастомный (`AbstractUser` + `description` + `avatar`).
- **`Message`** — лог операций. Поля: `message_type` (success/warning/error),
  `from_page`, `text`, `date`, `time`, `admin`.

## Как работает парсинг

1. **Постраничный парсинг.** Администратор вводит диапазон страниц в
   `/adminPanel/films/`. Приложение запрашивает у TMDB `/movie/popular?page=N`,
   фильтрует результаты (рейтинг ≥ 5.2, у фильма бюджет > 0, у актёра указана
   дата рождения), создаёт или обновляет объекты, скачивает постеры в `media/`.
2. **Точечный парсинг.** В карточке фильма/сериала можно добавить недостающего
   актёра по его TMDB ID — актёр прикрепится и к текущему фильму, и к своим
   работам.
3. **Трейлеры.** Сначала запрос к `/movie/{id}/videos`, ищутся официальные
   трейлеры на YouTube. Если их нет — BeautifulSoup парсит страницу поиска
   YouTube по запросу «{название} {год} официальный трейлер».
4. **Логирование.** Каждая операция пишется в `Message` со статусом и временем
   выполнения. На страницах админки выводится счётчик по типам.

## Тесты

```bash
# все 87 тестов
docker compose exec web pytest -v

# только одно приложение
docker compose exec web pytest mainProject/tests/ -v

# с покрытием (нужен pytest-cov, уже в dev.txt)
docker compose exec web pytest --cov=mainProject --cov=mainSite --cov=users
```

Тесты используют `factory_boy` для генерации данных. Внешние вызовы TMDB
мокаются через `unittest.mock.patch`.

Отдельно покрыты регресс-баги, найденные при разработке:

- `users/admin.py::test_add_form_renders` — в `add_fieldsets` было указано
  удалённое поле `registration_date`. Форма создания пользователя в админке
  падала с `FieldError`.
- `mainProject/tests/test_models.py` — проверка, что `actor.movies` и
  `film.actors` теперь работают через одну и ту же M2M-таблицу (раньше это
  были две разные таблицы, они не синхронизировались).

## Линт и форматирование

Все три инструмента запускаются из `website/`, где лежит `pyproject.toml`:

```bash
docker compose exec web ruff check .
docker compose exec web black --check .
docker compose exec web isort --check-only .
```

Автофикс (порядок важен — `isort` перед `black`):

```bash
docker compose exec web ruff check . --fix
docker compose exec web isort .
docker compose exec web black .
```

## CI

На каждый push в `main` и на pull request запускается
`.github/workflows/ci.yml` — два job'а:

- **lint** — `ruff check`, `black --check`, `isort --check-only`.
- **test** — поднимается PostgreSQL 16 как service-контейнер, ставятся
  зависимости из `requirements/dev.txt`, применяются миграции
  (`makemigrations --check --dry-run`), прогоняются тесты.

PR не мержится, пока оба job'а не зелёные. Секреты в CI фиктивные — TMDB API и
SMTP не дёргаются, тесты работают с моками.

## Безопасность и продакшен

Для локальной разработки используется `runserver`, для продакшена — `gunicorn`.
`.env` в продакшене должен содержать:

- `DEBUG=False`
- `ALLOWED_HOSTS=<домен>`
- `CSRF_TRUSTED_ORIGINS=https://<домен>`
- уникальный `SECRET_KEY` (никогда не тот, что в `.env.example`)

Проверить конфигурацию перед деплоем:

```bash
docker compose exec web python manage.py check --deploy
```

При `DEBUG=False` статику раздаёт whitenoise (уже в `requirements/base.txt`),
медиа — через `nginx` или аналог (в docker-compose нет nginx-сервиса, это нужно
добавить перед публикацией).

## Известные ограничения

- **`badwords/`** — вендорная копия библиотеки. Не обновляется из PyPI,
  словари лежат в репозитории. Это осознанное решение для курсового проекта.
- **Парсинг требует VPN** на машине, где запущен Docker.

## Лицензия

Проект создан в образовательных целях. Сторонние библиотеки (`Django`,
`requests`, `beautifulsoup4`, `Pillow`, `environs`, `badwords`) распространяются
под своими лицензиями. Код самого проекта можно свободно использовать в учебных
целях.
