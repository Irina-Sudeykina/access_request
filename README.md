# Проект "access_request" - Веб-приложение подачи заявок на предоставление доступа к информационным системам (ИС) 

## Описание:
 Проект "access_request" - это проект на Python, 
 передставляющий собой веб-приложение подачи заявок на предоставление доступа к информационным системам
 
 
## Установка:
 1. Клонируйте репозиторий:
 ```
 git clone https://github.com/Irina-Sudeykina/access_request.git
 
 ```

 2. Установите зависимости:
 ```
 pip install -r requirements.txt
 ```

## Использование:

### Модель User: ###
Модель представляет пользователя платформы, и имеет следующие свойства:<br>
fullname - ФИО,<br>
email - Email,<br>
phone - Телефон,<br>
position - Должность<br>


### Контроллер CustomLoginView(AbstractUser) ###
Контроллер для входа в сервис

### Контроллер CustomLogoutView(LogoutView) ###
Контроллер для выхода из сервиса


### Контекстный процессор user_groups(request) ###
Контекстный процессор, добавляющий переменные о группах пользователя


### Модель InformationSystem: ###
Модель представляет информационную систему, и имеет следующие свойства:<br>
title - Наименование ИС<br>
owner - Пользователь - владелец ИС<br>


### Модель InformationSystemRole: ###
Модель представляет роль в информационной системе, и имеет следующие свойства:<br>
title - Наименование роли в ИС<br>
information_system - Наименование ИС<br>


### Модель AccessRequest: ###
Модель представляет заявку на доступ к информационной системе, и имеет следующие свойства:<br>
information_system - Наименование ИС<br>
owner - Пользователь подавший заявку<br>
supervisor - Непосредственный руководитель<br>
permission_level - Уровень доступа<br>
information_system_role - Наименование роли в ИС<br>
approved_status_supervisor_is - Статус согласования непосредственным руководителем<br>
approved_status_owner_is - Статус согласования владельцем ИС<br>
approved_status_ib_is - Статус согласования сотрудником ИБ<br>


### Контроллер AccessRequestListView(LoginRequiredMixin, ListView) ###
Контроллер для просмотра списка заявок на доступ, созданных пользователем и статистика

### Контроллер AccessSuccessListView(ListAPIView) ###
Контроллер для просмотра списка заявок на согласование


### Контроллер ApprovalActionView(ApprovalPermissionMixin, SingleObjectMixin, View) ###
Базовый контроллер для действий согласования

### Контроллер ApprovedSupervisorView(ApprovalActionView) ###
Контроллер для согласования заявки непосредственным руководителем

### Контроллер RejectedSupervisorView(ApprovalActionView) ###
Контроллер для отклонения заявки непосредственным руководителем

### Контроллер ApprovedOwnerView(ApprovalActionView) ###
Контроллер для согласования заявки владельцем ИС

### Контроллер RejectedOwnerView(ApprovalActionView) ###
Контроллер для отклонения заявки владельцем ИС

### Контроллер ApprovedIBView(ApprovalActionView) ###
Контроллер для согласования заявки сотрудником ИБ

### Контроллер RejectedIBView(ApprovalActionView) ###
Контроллер для отклонения заявки сотрудником ИБ


### Контроллер AccessRequestCreateView(CreateView) ###
Контроллер для создания заявки на предоставление доступа


### Контроллер InformationSystemListView(ListView) ###
Контроллер для просмотра списка информационных систем

### Контроллер InformationSystemCreateView(CreateView) ###
Контроллер для создания информационной системы

### Контроллер InformationSystemUpdateView(UpdateView) ###
Контроллер для редактирования информационной системы

### Контроллер InformationSystemDeleteView(DeleteView) ###
Контроллер для удаления информационной системы


### Контроллер InformationSystemRoleListView(ListView) ###
Контроллер для просмотра списка ролей в информационных системах

### Контроллер InformationSystemRoleCreateView(CreateView) ###
Контроллер для создания роли в информационной системе

### Контроллер InformationSystemRoleUpdateView(UpdateView) ###
Контроллер для редактирования роли в информационной системе

### Контроллер InformationSystemRoleDeleteView(DeleteView) ###
Контроллер для удаления роли в информационной системе


## Миксины:

### Миксин ApprovalPermissionMixin(AccessMixin) ###
Миксин для проверки прав на согласование заявки


## Сервисы:

### Сервис AccessRequestService ###
Класс для получения статистики по заявкам

 get_access_request_count() - Общее количество заявок<br>
 get_active_access_request_count() - Количество активных заявок (теребующих согласования)<br>
 get_approved_access_request_count() - Количество согласованных заявок<br>
 get_rejected_access_request_count() - Количество отклоненных заявок<br>


## Формы:

### Форма StyleFormMixin ###
Форма для красивого отображения

### Форма AccessRequestForm(StyleFormMixin, forms.ModelForm) ###
Форма для создания новой заявки на предоставления доступа

### Форма InformationSystemForm(StyleFormMixin, forms.ModelForm) ###
Форма для создания новой ИС

### Форма InformationSystemRoleForm(StyleFormMixin, forms.ModelForm) ###
Форма для создания новой роли в ИС


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

## Создание и запуск проекта

### 1. Склонируйте репозиторий проекта:
```
git clone https://github.com/Irina-Sudeykina/access_request.git
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
Убедитесь, что все сервисы (web, db) успешно запущены.

### 4. Проверка работоспособности каждого сервиса:

- **Web-сервер (Django):**
Проект доступен по адресу: http://localhost:8000/. Проверьте страницу, открыв браузер.

- **PostgreSQL:**
Убедитесь, что база данных доступна. Можно использовать команду:
```
docker-compose exec db psql -U postgres
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
```

### Загрузка данных из фикстур:
```
docker-compose exec web python manage.py loaddata groups_fixture.json --format json
docker-compose exec web python manage.py loaddata users_fixture.json --format json
docker-compose exec web python manage.py loaddata mis_fixture.json --format json
```

### Выполнение кастомной команды - создание суперпользователя:
```
docker-compose exec web python manage.py csu
```

### Полезные команды:
Команда	Описание
docker-compose up -d	Запустить контейнеры в фоновом режиме
docker-compose ps	Показать список запущенных контейнеров
docker-compose stop	Остановить работающие контейнеры
docker-compose restart	Перезапустить контейнеры
docker-compose logs service-name	Получить журналы выбранного сервиса
docker-compose exec container cmd	Выполнить команду внутри указанного контейнера


 ## Тестирование:
Проект покрыт тестами. Для их запуска выполните команду:
```
python manage.py test
или
pytest
```

Для просмотра отчета откройте файл htmlcov\index.html



## Лицензия:
Проект распространяется под [лицензией MIT](LICENSE).
