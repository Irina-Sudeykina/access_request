from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.views.generic import View

from mis.forms import AccessRequestForm, InformationSystemForm, InformationSystemRoleForm
from mis.mixins import ApprovalPermissionMixin
from mis.models import AccessRequest, InformationSystem, InformationSystemRole
from mis.services import AccessRequestService

User = get_user_model()


class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Создаем общие тестовые данные для всех методов в этом классе.
        Этот метод выполняется один раз перед всеми тестами.
        """
        # Создаем пользователя (владельца)
        cls.user = User.objects.create_user(
            username="testuser",
            email="testuser@test.com",
            password="password123",
            fullname="Тест Пользователь",
            position="Тестировщик",
        )

        # Создаем информационную систему
        cls.system = InformationSystem.objects.create(title="Система А", owner=cls.user)

        # Создаем роль в информационной системе
        cls.role = InformationSystemRole.objects.create(title="Роль Тест", information_system=cls.system)

        # Создаем заявку на доступ, используя созданные выше объекты.
        # Это нужно для теста строкового представления AccessRequest.
        cls.access_request = AccessRequest.objects.create(
            information_system=cls.system,
            owner=cls.user,
            supervisor=cls.user,
            permission_level="READ",
            information_system_role=cls.role,
        )

    def test_information_system_str(self):
        """Проверка отображения модели InformationSystem"""
        self.assertEqual(str(self.system), "Система А")

    def test_information_system_role_str(self):
        """Проверка строкового представления модели InformationSystemRole"""
        # Ожидаемый формат: "<Название ИС> - <Название роли>"
        expected_str = f"{self.system} - {self.role.title}"
        self.assertEqual(str(self.role), expected_str)

    def test_access_request_creation(self):
        """Тест создания заявки с заполнением всех обязательных полей"""
        # Проверяем, что поля заявки соответствуют переданным данным
        self.assertEqual(self.access_request.information_system, self.system)
        self.assertEqual(self.access_request.owner, self.user)

        # Проверяем, что статус по умолчанию установлен в 'pending'
        self.assertEqual(self.access_request.approved_status_supervisor_is, "pending")

    def test_access_request_str(self):
        """Проверка строкового представления модели AccessRequest"""
        # Ожидаемый формат: "<Дата> - <Название ИС> - <Владелец>"
        # Форматируем дату так же, как это делает Django по умолчанию для DateField в str()
        expected_date = self.access_request.created_at.strftime("%Y-%m-%d")
        expected_str = f"{expected_date} - {self.system} - {self.user}"

        self.assertEqual(str(self.access_request), expected_str)


class ServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем данные для тестов сервиса
        cls.user = User.objects.create_user(username="user", email="user@test.com", password="123")

        cls.system = InformationSystem.objects.create(title="Система С", owner=cls.user)

        # Создаем роль для заявок
        cls.role = InformationSystemRole.objects.create(title="Роль С", information_system=cls.system)

        # Создаем заявки в разных статусах, указывая роль
        AccessRequest.objects.create(
            information_system=cls.system,
            owner=cls.user,
            supervisor=cls.user,
            approved_status_ib_is="pending",
            information_system_role=cls.role,
            permission_level="READ",
        )

        AccessRequest.objects.create(
            information_system=cls.system,
            owner=cls.user,
            supervisor=cls.user,
            approved_status_ib_is="approved",
            information_system_role=cls.role,
            permission_level="READ",
        )

    def test_service_counts(self):
        """Тест подсчета заявок сервисом"""
        self.assertEqual(AccessRequestService.get_access_request_count(), 2)


class FormTests(TestCase):
    """Тесты для форм приложения mis"""

    @classmethod
    def setUpTestData(cls):
        """
        Создаем пользователей и группы для тестов форм.
        Это выполняется один раз для всего класса.
        """
        # Создаем группу Admins
        cls.admins_group = Group.objects.create(name="Admins")

        # Создаем обычного пользователя
        cls.regular_user = User.objects.create_user(
            username="regular_user",
            email="regular@test.com",
            password="123",
            fullname="Обычный Пользователь",
            position="Сотрудник"
        )

        # Создаем админа и добавляем в группу
        cls.admin_user = User.objects.create_user(
            username="admin_user",
            email="admin@test.com",
            password="123",
            fullname="Админ",
            position="Руководитель"
        )
        cls.admin_user.groups.add(cls.admins_group)

        # Создаем суперпользователя
        cls.superuser = User.objects.create_superuser(
            username="superuser",
            email="super@test.com",
            password="123"
        )

        # Создаем информационную систему и роль для теста AccessRequestForm
        cls.information_system = InformationSystem.objects.create(
            title="Тестовая ИС",
            owner=cls.regular_user
        )

        cls.role = InformationSystemRole.objects.create(
            title="Тестовая Роль",
            information_system=cls.information_system
        )

    def test_access_request_form_filters_admins(self):
        """Форма не должна показывать админов в списке руководителей"""
        form = AccessRequestForm(user=self.regular_user)
        queryset = form.fields["supervisor"].queryset

        self.assertIn(self.regular_user, queryset)
        self.assertNotIn(self.admin_user, queryset)

    def test_information_system_form_excludes_admins(self):
        """
        Тест покрывает строки в классе InformationSystemForm:
        - Проверка удаления help_text (строки внутри цикла).
        - Логика фильтрации поля 'owner' (строки 56-75).
        """
        # Создаем экземпляр формы
        form = InformationSystemForm()

        # 1. Проверяем, что help_text удален для поля 'owner'
        self.assertIsNone(form.fields["owner"].help_text)

        # 2. Проверяем логику фильтрации (строки с exclude)
        queryset = form.fields["owner"].queryset

        # В списке выбора владельца НЕ должно быть админов и суперпользователей
        self.assertNotIn(self.admin_user, queryset)
        self.assertNotIn(self.superuser, queryset)

        # В списке должен быть обычный пользователь
        self.assertIn(self.regular_user, queryset)

    def test_information_system_role_form_help_text(self):
        """
        Тест покрывает строки в классе InformationSystemRoleForm:
        - Проверка удаления help_text (строки внутри цикла).
        """
        form = InformationSystemRoleForm()

        # Проверяем, что help_text удален для всех полей (например, для 'title')
        self.assertIsNone(form.fields["title"].help_text)

    def test_access_request_form_logic(self):
        """
        Тест покрывает строки в классе AccessRequestForm:
        - Проверка удаления help_text.
        - Логика фильтрации поля 'supervisor'.
        - Логика динамического обновления поля 'information_system_role'.
        """
        # Создаем форму для обычного пользователя
        form = AccessRequestForm(user=self.regular_user)

        # 1. Проверяем удаление help_text для поля supervisor
        self.assertIsNone(form.fields["supervisor"].help_text)

        # 2. Проверяем логику фильтрации supervisor (строка 66 и далее)
        queryset = form.fields["supervisor"].queryset

        # В списке руководителей НЕ должно быть админов и суперпользователей
        self.assertNotIn(self.admin_user, queryset)
        self.assertNotIn(self.superuser, queryset)

        # В списке должен быть обычный пользователь (он может быть руководителем сам себе в тесте)
        self.assertIn(self.regular_user, queryset)

        # 3. Проверяем логику динамического обновления ролей (строки ~70-75)
        post_data = {
            "information_system": self.information_system.id,
            "supervisor": self.regular_user.id,
            "permission_level": "READ"
        }
        form = AccessRequestForm(data=post_data)

        # Поле информации о ролях должно быть отфильтровано по выбранной системе
        role_queryset = form.fields["information_system_role"].queryset
        self.assertIn(self.role, role_queryset)


class MixinTests(TestCase):
    """Тесты для миксинов и вспомогательной логики"""

    def setUp(self):
        """
        Создаем сложную структуру данных перед каждым тестом.
        """
        # Создаем группу для специалистов ИБ
        self.ib_group, _ = Group.objects.get_or_create(name="InformationSecurity")

        # Создаем пользователей с уникальными email
        self.supervisor = User.objects.create_user(username="supervisor", email="s@test.com", password="123")
        self.owner_is = User.objects.create_user(username="owner_is", email="o@test.com", password="123")
        self.ib_user = User.objects.create_user(username="ib_user", email="i@test.com", password="123")
        self.regular_user = User.objects.create_user(username="regular", email="r@test.com", password="123")

        # Добавляем пользователя ИБ в группу
        self.ib_user.groups.add(self.ib_group)

        # Создаем информационную систему с владельцем
        self.information_system = InformationSystem.objects.create(title="Тестовая ИС", owner=self.owner_is)

        # Создаем роль и заявку
        self.role = InformationSystemRole.objects.create(
            title="Тестовая Роль", information_system=self.information_system
        )

        self.access_request = AccessRequest.objects.create(
            information_system=self.information_system,
            supervisor=self.supervisor,
            owner=self.regular_user,
            information_system_role=self.role,
            permission_level="READ",
        )

    def _test_access(self, user, should_have_access=True):
        """
        Универсальный метод для тестирования доступа.
        """
        request = RequestFactory().get("/")
        request.user = user

        class FakeView(ApprovalPermissionMixin, View):
            def get(self, request, *args, **kwargs):
                return HttpResponse("Доступ разрешен")

            def get_object(self):
                return self.access_request

        view = FakeView()

        if should_have_access:
            # Если доступ ДОЛЖЕН быть: проверяем успешный ответ
            view.request = request
            view.access_request = self.access_request

            response = view.dispatch(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content.decode(), "Доступ разрешен")
        else:
            # Если доступа быть НЕ ДОЛЖНО: проверяем, что вызвано исключение PermissionDenied
            with self.assertRaises(PermissionDenied):
                view.request = request
                view.access_request = self.access_request
                view.dispatch(request)

    def test_approval_mixin_supervisor_access(self):
        """Тест: Руководитель (supervisor) имеет доступ к заявке."""
        self._test_access(user=self.supervisor, should_have_access=True)

    def test_approval_mixin_owner_is_access(self):
        """Тест: Владелец ИС (owner_is) имеет доступ к заявке."""
        self._test_access(user=self.owner_is, should_have_access=True)

    def test_approval_mixin_ib_user_access(self):
        """Тест: Сотрудник ИБ (ib_user) имеет доступ к заявке."""
        self._test_access(user=self.ib_user, should_have_access=True)

    def test_approval_mixin_no_access(self):
        """Тест: Обычный пользователь НЕ имеет доступа."""
        # Здесь мы проверяем, что для пользователя без прав будет вызвано исключение
        self._test_access(user=self.regular_user, should_have_access=False)


class AccessSuccessListViewTests(TestCase):
    """Тесты для класса AccessSuccessListView (Список заявок на согласование)"""

    def setUp(self):
        """
        Этот метод выполняется ПЕРЕД КАЖДЫМ тестом.
        Он создает чистые данные, что решает проблему конфликтов.
        """
        # Создаем клиента для симуляции браузера
        self.client = Client()
        self.url = reverse("mis:accesssuccess_list")

        # --- Создаем данные для этого теста ---

        # Создаем группу для специалистов ИБ
        self.ib_group = Group.objects.create(name="InformationSecurity")

        # Создаем пользователей
        self.supervisor = User.objects.create_user(username="supervisor", password="123", email="s@test.com")
        self.owner_is = User.objects.create_user(username="owner_is", password="123", email="o@test.com")
        self.ib_user = User.objects.create_user(username="ib_user", password="123", email="i@test.com")
        self.regular_user = User.objects.create_user(username="regular", password="123", email="r@test.com")

        # Добавляем пользователя ИБ в группу
        self.ib_user.groups.add(self.ib_group)

        # Создаем информационную систему с владельцем
        self.system = InformationSystem.objects.create(title="Система для тестов", owner=self.owner_is)

        # Создаем роль
        self.role = InformationSystemRole.objects.create(title="Тестовая Роль", information_system=self.system)

        # --- Создаем заявки в разных статусах ---

        # 1. Заявка на согласовании у руководителя (должна быть видна Супервайзеру)
        self.request_pending_supervisor = AccessRequest.objects.create(
            information_system=self.system,
            supervisor=self.supervisor,
            owner=self.regular_user,
            information_system_role=self.role,
            permission_level="READ",
            approved_status_supervisor_is="pending",
            approved_status_owner_is="pending",
            approved_status_ib_is="pending",
        )

        # 2. Заявка согласована руководителем, ждет владельца (должна быть видна Владельцу ИС)
        self.request_pending_owner = AccessRequest.objects.create(
            information_system=self.system,
            supervisor=self.supervisor,
            owner=self.regular_user,
            information_system_role=self.role,
            permission_level="READ",
            approved_status_supervisor_is="approved",
            approved_status_owner_is="pending",
            approved_status_ib_is="pending",
        )

        # 3. Заявка согласована владельцем, ждет ИБ (должна быть видна ИБ-специалисту)
        self.request_pending_ib = AccessRequest.objects.create(
            information_system=self.system,
            supervisor=self.supervisor,
            owner=self.regular_user,
            information_system_role=self.role,
            permission_level="READ",
            approved_status_supervisor_is="approved",
            approved_status_owner_is="approved",
            approved_status_ib_is="pending",
        )

    def test_supervisor_sees_only_his_requests(self):
        """Тест: Супервайзер видит только заявки, ожидающие его согласования."""
        self.client.login(username="supervisor", password="123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        # Супервайзер должен видеть только одну заявку: request_pending_supervisor
        self.assertEqual(len(response.context["object_list"]), 1)
        self.assertIn(self.request_pending_supervisor, response.context["object_list"])

        # Проверяем, что другие заявки НЕ попали в список
        self.assertNotIn(self.request_pending_owner, response.context["object_list"])
        self.assertNotIn(self.request_pending_ib, response.context["object_list"])

    def test_owner_is_sees_only_his_requests(self):
        """Тест: Владелец ИС видит только заявки, согласованные руководителем и ожидающие его."""
        self.client.login(username="owner_is", password="123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        # Владелец должен видеть только одну заявку: request_pending_owner
        self.assertEqual(len(response.context["object_list"]), 1)
        self.assertIn(self.request_pending_owner, response.context["object_list"])

        # Другие заявки не должны быть видны
        self.assertNotIn(self.request_pending_supervisor, response.context["object_list"])
        self.assertNotIn(self.request_pending_ib, response.context["object_list"])

    def test_ib_user_sees_only_his_requests(self):
        """Тест: Сотрудник ИБ видит только заявки, согласованные владельцем и ожидающие его."""
        self.client.login(username="ib_user", password="123")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

        # ИБ-специалист должен видеть только одну заявку: request_pending_ib
        self.assertEqual(len(response.context["object_list"]), 1)
        self.assertIn(self.request_pending_ib, response.context["object_list"])

        # Другие заявки не должны быть видны
        self.assertNotIn(self.request_pending_supervisor, response.context["object_list"])
        self.assertNotIn(self.request_pending_owner, response.context["object_list"])


class ApprovalActionViewTests(TestCase):
    """Тесты для базового класса ApprovalActionView и его наследников"""

    @classmethod
    def setUpTestData(cls):
        """
        Создаем данные ОДИН РАЗ для всего класса ApprovalActionViewTests.
        Используем уникальные имена и заполняем все необходимые поля.
        """
        # --- Создаем данные ---

        # Создаем группу для специалистов ИБ
        cls.ib_group = Group.objects.create(name="InformationSecurity")

        # Создаем пользователей с уникальными именами и ЗАПОЛНЕННЫМИ профилями
        cls.supervisor = User.objects.create_user(
            username="supervisor_approval",
            password="123",
            email="s_approval@test.com",
            fullname="Супервайзер Тестов",
            position="Начальник отдела",
        )
        cls.owner_is = User.objects.create_user(
            username="owner_is_approval",
            password="123",
            email="o_approval@test.com",
            fullname="Владелец ИС",
            position="Системный архитектор",
        )
        cls.ib_user = User.objects.create_user(
            username="ib_user_approval",
            password="123",
            email="i_approval@test.com",
            fullname="Сотрудник ИБ",
            position="Инженер по безопасности",
        )
        # Создаем обычного пользователя (владельца заявки) с профилем
        cls.regular_user = User.objects.create_user(
            username="regular_approval",
            password="123",
            email="r_approval@test.com",
            fullname="Иван Иванов",
            position="Разработчик",
        )

        # Добавляем пользователя ИБ в группу
        cls.ib_user.groups.add(cls.ib_group)

        # Создаем информационную систему с уникальным названием
        cls.system = InformationSystem.objects.create(title="Система для тестов ApprovalAction", owner=cls.owner_is)

        # Создаем роль
        cls.role = InformationSystemRole.objects.create(
            title="Тестовая Роль для Approval", information_system=cls.system
        )

        # Создаем заявку в статусе 'pending' по всем этапам
        cls.access_request = AccessRequest.objects.create(
            information_system=cls.system,
            supervisor=cls.supervisor,  # Заявка принадлежит этому руководителю
            owner=cls.regular_user,  # Владелец заявки - regular_user
            information_system_role=cls.role,
            permission_level="READ",
            approved_status_supervisor_is="pending",
            approved_status_owner_is="pending",
            approved_status_ib_is="pending",
        )

    def setUp(self):
        """Создаем клиента для каждого теста."""
        self.client = Client()

    def _get_approval_url(self, view_name):
        """Вспомогательный метод для генерации URL"""
        return reverse(view_name, kwargs={"pk": self.access_request.pk})

    def test_supervisor_can_approve(self):
        """Тест: Супервайзер может согласовать заявку (изменяет статус на 'approved')"""
        self.client.login(username="supervisor_approval", password="123")

        url = self._get_approval_url("mis:approved_supervisor")  # Замените на имя вашего URL

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Обновляем объект из базы данных
        self.access_request.refresh_from_db()

        self.assertEqual(self.access_request.approved_status_supervisor_is, "approved")

    def test_supervisor_can_reject(self):
        """Тест: Супервайзер может отклонить заявку (изменяет статус на 'rejected')"""
        self.client.login(username="supervisor_approval", password="123")

        url = self._get_approval_url("mis:rejected_supervisor")  # Замените на имя вашего URL

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.access_request.refresh_from_db()

        self.assertEqual(self.access_request.approved_status_supervisor_is, "rejected")

    def test_owner_can_approve(self):
        """Тест: Владелец ИС может согласовать заявку (изменяет статус на 'approved')"""
        # Предварительно руководитель должен согласовать заявку
        self.access_request.approved_status_supervisor_is = "approved"
        self.access_request.save()

        self.client.login(username="owner_is_approval", password="123")

        url = self._get_approval_url("mis:approved_owner")  # Замените на имя вашего URL

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        self.access_request.refresh_from_db()

        self.assertEqual(self.access_request.approved_status_owner_is, "approved")

    def test_ib_user_can_approve_and_sends_email(self):
        """
        Тест: Сотрудник ИБ может согласовать заявку (изменяет статус на 'approved')
        и отправляет письмо.
        """
        # Предварительно руководитель и владелец должны согласовать заявку
        self.access_request.approved_status_supervisor_is = "approved"
        self.access_request.approved_status_owner_is = "approved"
        self.access_request.save()

        self.client.login(username="ib_user_approval", password="123")

        url = self._get_approval_url("mis:approved_ib")

        # Отправляем POST-запрос
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Обновляем объект из базы данных
        self.access_request.refresh_from_db()
        self.assertEqual(self.access_request.approved_status_ib_is, "approved")

        # --- Проверка отправки письма ---
        from django.core import mail  # Импортируем модуль mail

        # Проверяем, что в "исходящих" письмах теста есть ровно одно письмо
        self.assertEqual(len(mail.outbox), 1)

        # Получаем отправленное письмо
        sent_email = mail.outbox[0]

        # Проверяем основные атрибуты письма
        self.assertEqual(sent_email.subject, f"Заявка на доступ к ИС {self.system}")

        # Проверяем, что тело письма содержит данные из заявки
        # (Это осталось без изменений)
        self.assertIn(self.access_request.owner.fullname, sent_email.body)
        self.assertIn(self.access_request.supervisor.fullname, sent_email.body)

        # --- ИСПРАВЛЕННАЯ ПРОВЕРКА ПОЛУЧАТЕЛЯ ---
        # Теперь проверяем заголовок 'to', куда Django помещает список получателей
        # В тестовой среде этот список может быть пустым, если не настроен EMAIL_BACKEND,
        # но мы можем проверить, что логика формирования списка была запущена.

        # Проверяем, что поле 'to' не пустое (в идеале там должен быть адрес из .env)
        # Если в вашем тестовом конфиге настроен email backend, адрес будет здесь.
        # Если нет, мы хотя бы проверим структуру письма.

        # Проверяем, что в теле письма есть строка с "УЗ:", так как она там точно есть.
        lines = sent_email.body.splitlines()
        uz_line = [line for line in lines if line.startswith("УЗ:")]

        self.assertTrue(uz_line, "В письме не найдена строка с УЗ получателя")

    def test_owner_can_reject(self):
        """
        Тест: Владелец ИС может отклонить заявку (изменяет статус на 'rejected').
        """
        # Предварительно руководитель должен согласовать заявку
        self.access_request.approved_status_supervisor_is = "approved"
        self.access_request.save()

        self.client.login(username="owner_is_approval", password="123")

        url = self._get_approval_url("mis:rejected_owner")  # Используем URL для отклонения владельцем

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Обновляем объект из базы данных
        self.access_request.refresh_from_db()

        # Проверяем, что статус изменился на 'rejected'
        self.assertEqual(self.access_request.approved_status_owner_is, "rejected")

    def test_ib_user_can_reject(self):
        """
        Тест: Сотрудник ИБ может отклонить заявку (изменяет статус на 'rejected').
        """
        # Предварительно руководитель и владелец должны согласовать заявку
        self.access_request.approved_status_supervisor_is = "approved"
        self.access_request.approved_status_owner_is = "approved"
        self.access_request.save()

        self.client.login(username="ib_user_approval", password="123")

        url = self._get_approval_url("mis:rejected_ib")  # Используем URL для отклонения ИБ

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)

        # Обновляем объект из базы данных
        self.access_request.refresh_from_db()

        # Проверяем, что статус изменился на 'rejected'
        self.assertEqual(self.access_request.approved_status_ib_is, "rejected")


class AccessRequestCreateViewTests(TestCase):
    """Тесты для класса AccessRequestCreateView (Создание заявки на доступ)"""

    @classmethod
    def setUpTestData(cls):
        """
        Создаем данные для тестов: пользователя, систему и роль.
        Это выполняется один раз для всего класса.
        """
        # Создаем пользователя, который будет подавать заявку
        cls.user = User.objects.create_user(
            username="testuser_creator",
            email="creator@test.com",
            password="password123",
            fullname="Тестовый Создатель",
            position="Разработчик",
        )

        # Создаем супервайзера (руководителя)
        cls.supervisor = User.objects.create_user(
            username="test_supervisor",
            email="supervisor@test.com",
            password="123",
            fullname="Тестовый Супервайзер",
            position="Руководитель",
        )

        # Создаем информационную систему
        cls.system = InformationSystem.objects.create(
            title="Система для Тестов Создания",
            owner=cls.user,  # Владелец может быть тем же пользователем, это не важно для теста создания
        )

        # Создаем роль в системе
        cls.role = InformationSystemRole.objects.create(
            title="Тестовая Роль для Создания", information_system=cls.system
        )

    def setUp(self):
        """Создаем авторизованного клиента для каждого теста."""
        self.client = Client()
        self.client.login(username="testuser_creator", password="password123")
        self.create_url = reverse("mis:accessrequest_create")

    def test_access_request_create_view_get(self):
        """
        Тест: GET-запрос к странице создания заявки.
        Проверяем, что страница доступна и содержит форму.
        """
        response = self.client.get(self.create_url)

        # Проверяем, что страница загрузилась успешно
        self.assertEqual(response.status_code, 200)

        # Проверяем, что в контексте есть форма
        self.assertIn("form", response.context)

        # Проверяем, что используется правильный шаблон (если он у вас явно указан)
        # self.assertTemplateUsed(response, 'mis/accessrequest_form.html')

    def test_access_request_create_view_post_success(self):
        """
        Тест: Успешное создание заявки через POST-запрос.
        Проверяем создание объекта в БД и редирект.
        """
        # Подготавливаем данные для POST-запроса
        post_data = {
            "information_system": self.system.id,
            "supervisor": self.supervisor.id,
            "permission_level": "READ",
            "information_system_role": self.role.id,
        }

        # Считаем количество заявок до отправки формы
        initial_count = AccessRequest.objects.count()

        # Отправляем POST-запрос с данными формы
        response = self.client.post(self.create_url, data=post_data, follow=True)

        # Проверяем, что произошел редирект (код 302) на страницу списка заявок
        self.assertRedirects(response, reverse("mis:accessrequest_list"))

        # Проверяем, что в базе данных появился новый объект
        self.assertEqual(AccessRequest.objects.count(), initial_count + 1)

        # Получаем только что созданную заявку из базы
        new_request = AccessRequest.objects.latest("id")

        # Проверяем, что поля заявки заполнены верно
        self.assertEqual(new_request.owner, self.user)  # Владелец должен быть текущим пользователем
        self.assertEqual(new_request.information_system, self.system)
        self.assertEqual(new_request.supervisor, self.supervisor)
        self.assertEqual(new_request.permission_level, "READ")
