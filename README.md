# Foodgram


### Статус Workflow:

![Build Status](https://github.com/NikolayPetrow23/foodgram-project-react/workflows/Main%20Kfoodgram%20workflow/badge.svg)


### Ссылка для проверки проекта:

https://recipe-assistant.ddns.net

### Email и пароль для админки:
#### Username: admin
#### Пароль: admin


## Описание

Сервис Foodgram или «Продуктовый помощник». Сервис позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

### Как запустить проект:

Для начала убедитесь, что у вас установлен Docker командой:

```
docker -v
```

Клонируйте репозиторий и перейдите в него в командной строке:

```
https://github.com/AlinaVoskoboynikova/foodgram-project-react.git
```

Перейдите в папку с проектом и создайте и активируйте виртуальное окружение:

```
python3 -m venv env
```

```
source venv/Scripts/activate
```

```
python3 -m pip install --upgrade pip
```

Установите зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Перейдите в папку с файлом docker-compose.yaml:

```
cd infra
```

Разверните контейнеры:

```
docker-compose up -d --build
```

Выполните миграции, создайте суперпользователя, соберите статику:

```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

## Автор
Николай Петров - [GitHub](https://github.com/NikolayPetrow23)
