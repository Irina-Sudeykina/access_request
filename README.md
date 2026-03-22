# Проект "Habit_tracker" - Трекер привычек

## Описание:
 Проект "Habit_tracker" - это проект на Python, 
 передставляющи собой трекер привычек
 
 
## Установка:
 1. Клонируйте репозиторий:
 ```
 git clone https://github.com/Irina-Sudeykina/Habit_tracker.git
 
 ```

 2. Установите зависимости:
 ```
 pip install -r requirements.txt
 ```

## Использование:

### Модель User: ###
Модель представляет пользователя платформы, и имеет следующие свойства:<br>
email - Email,<br>
phone - Телефон,<br>
tg_nick - Ник телеграмма<br>
avatar - Аватар<br>
tg_chat_id - Телеграм chat-id<br>


### Контроллер UserCreateAPIView(CreateAPIView) ###
Контроллер для для добавления пользователей


### Модель Habit: ###
Модель представляет привычки, и имеет следующие свойства:<br>
owner - Пользователь<br>
location - Место<br>
time_habit - Время<br>
action_habit - Действие<br>
is_pleasant - Признак приятной привычки<br>
linked_habit - Связанная привычка<br>
frequency - Периодичность<br>
reward - Вознаграждение<br>
time_to_complete - Время на выполнение<br>
is_published - Признак публичности<br>


### Модель Reminder: ###
Модель представляет напоминания, и имеет следующие свойства:<br>
owner - Пользователь<br>
habit - Привычка<br>
date_reminder - Дата напоминания<br>


### Контроллер HabitCreateAPIView(CreateAPIView) ###
Контроллер для создания привычек

### Контроллер HabitListAPIView(ListAPIView) ###
Контроллер для просмотра списка привычек

### Контроллер HabitPublishedListAPIView(ListAPIView) ###
Контроллер для просмотра списка публичных привычек

### Контроллер HabitRetrieveAPIView(RetrieveAPIView) ###
Контроллер для просмотра конкретной привычки

### Контроллер HabitUpdateAPIView(UpdateAPIView) ###
Контроллер для редактирования привычки

### Контроллер HabitDestroyAPIView(DestroyAPIView) ###
Контроллер для удаления привычки


### Контроллер ReminderCreateAPIView(CreateAPIView) ###
Контроллер для создания напоминания

### Контроллер ReminderListAPIView(ListAPIView) ###
Контроллер для просмотра списка напоминаний

### Контроллер ReminderRetrieveAPIView(RetrieveAPIView) ###
Контроллер для просмотра конкретного напоминания

### Контроллер ReminderUpdateAPIView(UpdateAPIView) ###
Контроллер для редактирования напоминания

### Контроллер ReminderDestroyAPIView(DestroyAPIView) ###
Контроллер для удаления напоминания


## Функции:

### Функция send_telegram_message(chat_id, message) ###
Отправляет сообщение в телеграмм<br>
Принимает: <br>
 chat_id - чат id<br>
 message - текст сообщения<br>


## Задачи:

### Задача send_reminder() ###
Периодическая задача для рассылки напоминаний


## Запуск сервера:
В терминале выполните:
 ```
python manage.py runserver
 ```
Для остановки нажмите Ctrl + C


# Инструкция по запуску проекта с использованием Docker Compose

## Предварительные условия
- Установленная среда Docker и Docker Compose.<br>
- Наличие рабочего экземпляра базы данных PostgreSQL.<br>
- Установка необходимых инструментов для просмотра страниц API (например, Postman).<br>

## Создание и запуск проекта

### Запуск через виртуальную машину:
```
ssh -i .ssh\adminsia adminsia@158.160.178.115
cd ~/Habit_tracker
```
В браузере:
```
http://158.160.178.115/admin/
```

### 1. Склонируйте репозиторий проекта:
```
git clone https://github.com/Irina-Sudeykina/Habit_tracker.git
cd project
```

### 2. Соберите образы, запустите контейнеры и примените миграции:
```
docker-compose up -d --build
docker-compose exec web python manage.py migrate
```
Эта команда создаст контейнеры, определённые в файле `docker-compose.yml`, и запустит их в фоновом режиме.

### 3. Просмотр списка запущенных контейнеров:
```
docker-compose ps
```
Убедитесь, что все сервисы (web, db, redis, celery, beat) успешно запущены.

### 4. Проверка работоспособности каждого сервиса:

- **Web-сервер (Django/Django REST Framework):**
Проект доступен по адресу: http://localhost:8000/. Проверьте страницу API, открыв браузер или отправляя HTTP-запросы через Postman.

- **PostgreSQL:**
Убедитесь, что база данных доступна. Можно использовать команду:
```
docker-compose exec db psql -U postgres
```

- **Redis:**
Проверить, запущен ли Redis, можно командой:
```
docker-compose exec redis redis-cli ping
```
Ожидаемый ответ: `PONG`.

- **Celery/Celery Beat:**
Логика Celery доступна через просмотр журналов:
```
docker-compose logs celery
docker-compose logs beat
```

### 5. Прекращение работы и удаление контейнеров:

Чтобы остановить и удалить все контейнеры, выполните команду:
```
docker-compose down
```

## Дополнительные опции

### Сборка образов без запуска контейнеров:
```
docker-compose build
```

### Локальная сборка образа с кастомизацией:
Если нужно внести изменения в Dockerfile или создать собственный образ, выполните:
```
docker-compose build
```

### Получение статуса служб:
Просматривайте журнал служб, чтобы видеть происходящее
```
docker-compose logs
```
Или по-отдельности
```
docker-compose logs web
docker-compose logs db
docker-compose logs redis
docker-compose logs celery
docker-compose logs beat
```

### Загрузка данных из фикстур:
```
docker-compose exec web python manage.py loaddata users_fixture.json --format json
docker-compose exec web python manage.py loaddata habits_fixture.json --format json
```

### Выполнение кастомной команды - создание суперпользователя:
```
docker-compose exec web python manage.py csu
```


### Примеры запросов к API:
Используйте Postman или curl для отправки GET/POST-запросов на конечные точки API, доступные по адресу http://localhost:8000/.

### Полезные команды:
Команда	Описание
docker-compose up -d	Запустить контейнеры в фоновом режиме
docker-compose ps	Показать список запущенных контейнеров
docker-compose stop	Остановить работающие контейнеры
docker-compose restart	Перезапустить контейнеры
docker-compose logs service-name	Получить журналы выбранного сервиса
docker-compose exec container cmd	Выполнить команду внутри указанного контейнера


 ## Тестирование:
Проект покрыт тестами фреймворка DRF. Для их запуска выполните команду:
```
python manage.py test
или
coverage run manage.py test
```
Для выгрузки отчета о покрытии проекта тестами выполните команду:
```
coverage report
или
coverage html
```

## Документация:
http://localhost:8000/swagger/
или
http://localhost:8000/redoc/

## Лицензия:
Проект распространяется под [лицензией MIT](LICENSE).
