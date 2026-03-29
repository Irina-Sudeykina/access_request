from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.test import RequestFactory, TestCase
from django.urls import reverse

from users.context_processors import user_groups

User = get_user_model()


class UserModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем тестового пользователя, который будет использоваться во всех методах теста
        cls.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="StrongPass123",
            fullname="Иванов Иван",
            position="Инженер",
        )
        # Создаем суперпользователя
        cls.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
            fullname="Админ Супер",
            position="Системный администратор",
        )

    def test_user_creation(self):
        """Пользователь создается с правильными полями"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertTrue(self.user.check_password("StrongPass123"))
        self.assertEqual(self.user.fullname, "Иванов Иван")

    def test_email_uniqueness(self):
        """Проверка на уникальность email"""
        with self.assertRaises(Exception):  # IntegrityError или ValidationError
            User.objects.create_user(
                username="anotheruser", email="test@example.com", password="password"  # Тот же email!
            )

    def test_str_representation(self):
        """Проверка метода __str__"""
        # Тест для обычного пользователя
        expected_str = "Иванов Иван - Инженер"
        self.assertEqual(str(self.user), expected_str)

        # Проверяем, что строка суперпользователя ТОЧНО соответствует тому,
        # что мы задали при его создании в setUpTestData
        expected_superuser_str = "Админ Супер - Системный администратор"
        self.assertEqual(str(self.superuser), expected_superuser_str)

    def test_required_fields(self):
        """Проверка, что USERNAME_FIELD (username) обязателен"""
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", email="a@a.com", password="pass")


class ContextProcessorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        # Создаем группу Admins
        self.admins_group, created = Group.objects.get_or_create(name="Admins")

        # Создаем обычного пользователя и добавляем его в группу
        self.user = User.objects.create_user(username="test", password="123")
        self.user.groups.add(self.admins_group)

    def test_user_is_admin(self):
        """Если пользователь в группе Admins, переменная is_admin должна быть True"""
        request = self.factory.get("/")
        request.user = self.user

        context = user_groups(request)
        self.assertTrue(context["is_admin"])

    def test_anonymous_user(self):
        """Для анонимного пользователя is_admin должен быть False"""
        request = self.factory.get("/")
        request.user = AnonymousUser()

        context = user_groups(request)
        self.assertFalse(context["is_admin"])

    def test_superuser_is_admin(self):
        """Суперпользователь должен считаться админом"""
        superuser = User.objects.create_superuser(username="super", email="s@s.com", password="123")
        request = self.factory.get("/")
        request.user = superuser

        context = user_groups(request)
        self.assertTrue(context["is_admin"])


class AuthViewsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="password123")

    def test_login_view_url_exists_at_desired_location(self):
        """Страница входа доступна по адресу /users/login/"""
        response = self.client.get("/users/login/")
        self.assertEqual(response.status_code, 200)

    def test_login_view_url_by_name(self):
        """Страница входа доступна по имени URL"""
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        """POST-запрос на страницу входа с верными данными должен редиректить"""
        # Используем self.client.post для имитации отправки формы
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "testuser",
                "password": "password123",
            },
        )

        # Проверяем, что статус ответа - редирект (302)
        self.assertEqual(response.status_code, 302)

        # Проверяем, что редирект ведет на правильный URL
        self.assertRedirects(response, reverse("mis:accessrequest_list"))

    def test_logout_view(self):
        """После выхода пользователь разлогинен"""
        self.client.login(username="testuser", password="password123")

        response = self.client.post(reverse("users:logout"))

        # Проверяем, что статус ответа - редирект (302)
        self.assertEqual(response.status_code, 302)

        # Проверяем, что редирект ведет на URL, указанный в next_page="/"
        # Обратите внимание: мы сравниваем с '/', а не делаем запрос по этому адресу
        self.assertRedirects(response, "/", fetch_redirect_response=False)
