# Cоциальная сеть для публикации рецептов

## Описание проекта

Проект представляет собой [сайт](https://foodgramoksiasti.ddns.net/), на котором пользователи могут зарегистрироваться и авторизоваться, публиковать, редактировать и удалять собственные рецепты, а также просмотреть записи и страницы других пользователей, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Проект состоит из бэкенд-приложения на Django(API-приложение) и фронтенд-приложения на React(SPA-приложение). 
В рамках проекта настроено автоматическое тестирование и деплой проекта на удалённый сервер. Автоматизация настроена с помощью сервиса GitHub Actions: при пуше в ветку main проект тестируется, в случае успешного прохождения тестов образы обновлятся на Docker Hub, на удаленном сервере запускаются контейнеры из обновлённых образов.
После успешного деплоя приходит сообщение в Телеграм.

Полная документация к API находится в файле [docs/openapi-schema.yml](docs/openapi-schema.yml) и доступна по эндпоинту `/api/docs/`.

## Технологии

 - Python 3.11
 - Django==4.2.4
 - djangorestframework==3.14.0
 - djoser==2.2.0
 - React
 - Node.js
 - PostgreSQL
 - Gunicorn
 - Nginx


## Запуск проекта из образов с Docker hub

Для запуска d домашней директории сервера необходимо создать папку проекта, например foodgram, и перейти в нее; в папке foodgram создать файл `.env`, заполненный по образцу [.env.example](infra/.env.example):
    ```bash
    cd ~
    mkdir foodgram
    cd foodgram
    nano .env
    ```

Далее настроить в nginx перенаправление запросов на порт 10000:
    ```nginx
    server {
        server_name <...>;
        server_tokens off;

        location / {
            proxy_pass http://127.0.0.1:10000;
        }
    }
    ```

Затем получить HTTPS-сертификат для доменного имени:
    ```nginx
    sudo certbot --nginx
    ```

И добавить в GitHub Actions следующие секреты:
    - DOCKER_USERNAME - логин от Docker Hub
    - DOCKER_PASSWORD - пароль от Docker Hub
    - SSH_KEY - закрытый ssh-ключ для подключения к серверу
    - SSH_PASSPHRASE - passphrase от этого ключа
    - USER - имя пользователя на сервере
    - HOST - IP-адрес сервера
    - TELEGRAM_TO - ID телеграм-аккаунта для оповещения об успешном деплое
    - TELEGRAM_TOKEN - токен телеграм-бота

При первом коммите в ветку master будет выполнен полный деплой проекта (произойдет копирование файла docker-compose.production.yml, nginx.conf и папки docs, скачивание образов, создание и включение контейнеров, создание томов и сети). Подробнее см. [main.yml](.github/workflows/main.yml).

Создать суперюзера, а также загрузить в БД список ингридиентов, можно следующими командами из папки foodgram:
    ```bash
    docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
    docker compose -f docker-compose.production.yml exec backend python manage.py import_db_csv
    ```

И далее проект доступен на:
https://foodgramoksiasti.ddns.net/


## Запуск проекта из репозитория GitHub

Клонируем себе репозиторий и переходим в папку infra:
    ```bash
    git clone git@github.com:OksanaAstashkina/foodgram-project-react.git
    cd foodgram-project-react/infra/
    ```

Создаем в папке infra/ файл `.env` с переменными окружения, заполненный по образцу [.env.example](infra/.env.example).
    ```bash
    touch .env
    ```

Из директории проекта infra выполняем запуск проекта: собираем и запускаем докер-контейнеры через Docker Compose (при работе в Linux вначале команды поставить sudo):
    ```bash
    docker compose -f docker-compose.yml up
    ```

После запуска необходимо выполнить сбор статистики и миграции бэкенда, создание суперюзера, а также загрузку ингридиентов в БД (при работе в Linux вначале команды поставить sudo). Статистика фронтенда собирается во время запуска контейнера, после чего он останавливается.

    ```
    docker compose -f docker-compose.yml exec backend python manage.py migrate
    docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
    docker compose -f docker-compose.yml exec backend python manage.py collectstatic
    docker compose -f docker-compose.yml exec backend cp -r /app/collected_static/. /backend_static/static/
    docker compose -f docker-compose.yml exec backend python manage.py import_db_csv
    ```

И далее проект доступен на:
http://localhost:10000/

## Остановка оркестра контейнеров
В окне, где был запуск - Ctrl+С, или в другом окне (при работе в Linux вначале команды поставить sudo):
`docker compose -f [имя-файла-docker-compose.yml] down`

***
## *Автор*
Оксана Асташкина - [GitHub](https://github.com/OksanaAstashkina)

### *Дата создания*
Сентябрь, 2023 г.
