## Описание проекта
Проект "Вопросы и ответы". Сервис позволяет пользователям задавать вопросы и получать на них ответы от других пользователей. Возможности комментирования и голосования формирует сообщество и позволяет пользователям активно помогать друг другу.

## Используемые технологии
- Python 3.10.11
- Django 5.0.3
- Bootstrap v5.2.3
- БД - MySQL

## Установка и запуск проекта
1. Создание виртуальной среды Python в директории проекта

python -m venv askme_venv

2. Активация виртуальной среды

source askme_venv/bin/activate

3. Загрузка требуемых зависимостей

pip install -r requirements.txt

4. Создание БД, настройка переменной DATABASES в файле setting.py

5. Выполнение миграций

python manage.py migrate

6. Наполнение БД

python manage.py fill_db ratio

7. Запуск сервера

python manage.py runserver
