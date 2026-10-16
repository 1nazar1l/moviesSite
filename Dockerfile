FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /code/requirements/
RUN pip install --upgrade pip && pip install -r requirements/dev.txt

COPY ./website /code

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]