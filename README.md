## Foodgram (Продуктовый помощник)

![workflow](https://github.com/Zh-Andrew/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

Foodgram - данный сервис позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

[Адрес проекта](http://62.84.122.38/)

Логин, пароль администратора: admin

### Развернуть проект на удаленном сервере:

- Клонировать репозиторий:
```
https://github.com/Zh-Andrew/foodgram-project-react.git
```

- Установить на сервере Docker, Docker Compose:


- Скопировать на сервер файлы docker-compose.yml, nginx.conf из папки infra (команды выполнять находясь в папке infra):

```
scp docker-compose.yml nginx.conf username@IP:/home/username/   # username - имя пользователя на сервере
                                                                # IP - публичный IP сервера
```

- Для работы с GitHub Actions необходимо в репозитории в разделе Settings > Secrets > Actions создать переменные окружения:
```
SECRET_KEY                # секретный ключ Django
DOCKER_PASSWORD           # пароль DockerHub
DOCKER_USERNAME           # логин DockerHub
HOST                      # публичный IP сервера
USER                      # имя пользователя на сервере
PASSPHRASE                # *если ssh-ключ защищен паролем
SSH_KEY                   # приватный ssh-ключ
TELEGRAM_TO               # ID телеграм-аккаунта куда надо отправить сообщение
TELEGRAM_TOKEN            # токен бота, посылающего сообщение
DB_ENGINE                 # django.db.backends.postgresql
DB_NAME                   # postgres
POSTGRES_USER             # postgres
POSTGRES_PASSWORD         # postgres (или свой)
DB_HOST                   # db
DB_PORT                   # 5432 (порт по умолчанию)
```

- Создать и запустить контейнеры Docker, выполнить команду на сервере
```
sudo docker-compose up -d
```

- После успешной сборки выполнить миграции:
```
sudo docker compose exec backend python manage.py makemigrations foodgram
```
```
sudo docker compose exec backend python manage.py makemigrations users
```
```
sudo docker compose exec backend python manage.py migrate
```

- Создать суперпользователя:
```
sudo docker compose exec backend python manage.py createsuperuser
```

- Собрать статику:
```
sudo docker compose exec backend python manage.py collectstatic --noinput
```

- Импортировать данные по ингредиентам из CSV файла:
```
sudo docker compose exec backend python manage.py import_ingredients
```

- Для остановки контейнеров Docker:
```
sudo docker compose down -v      # с их удалением
sudo docker compose stop         # без удаления
```

### Развернуть проект на локальной машине:

- Клонировать репозиторий:
```
https://github.com/Zh-Andrew/foodgram-project-react.git
```

- В директории backend создать файл .env, для хранения конфиденциальных данных и заполнить своими данными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres #(лучше свой пароль)
DB_HOST=db
DB_PORT=5432
SECRET_KEY='секретный ключ Django'
```

- Создать и запустить контейнеры Docker, как указано выше.


- После запуска проект будут доступен по адресу: [http://localhost/](http://localhost/)


- Документация будет доступна по адресу: [http://localhost/api/docs/](http://localhost/api/docs/)


### Технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL, Yandex Cloud, Continuous Integration, Continuous Deployment

### Автор backend'а:

ZhAndrew
