Проект «Продуктовый помощник» - Foodgram

Foodgram - Продуктовый помощник. Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

---
Инструкция по запуску проекта:

Клонируйте репозиторий
```
git clone git@github.com:Fr0stFree/foodgram-project-react.git
```
Перейдите в директорию проекта
```
cd foodgram-project-react/
```
Создайте и активируйте виртуальное окружение, обновите pip, установите зависимости
```
python3 -m venv venv
. venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Перейдите в директорию с бекендом и примените миграции
```
cd backend/
python manage.py makemigrations
python manage.py migrate
```
Запустите проект
```
python manage.py runserver
```
Проект будет развернут по адресу localhost на порту 8000
