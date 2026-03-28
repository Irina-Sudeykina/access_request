from smart_selects.db_fields import ChainedForeignKey

from django.db import models
from users.models import User


class InformationSystem(models.Model):
    title = models.CharField(max_length=150, verbose_name="Наименование ИС", help_text="Введите наименование ИС")

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="owned_is",
        verbose_name="Пользователь",
        help_text="Укажите пользователя - владельца ИС",
    )

    class Meta:
        verbose_name = "Информационная система"
        verbose_name_plural = "Информационные системы"
        ordering = [
            "title",
        ]

    def __str__(self):
        return f"{self.title}"


class InformationSystemRole(models.Model):
    title = models.CharField(
        max_length=150, 
        verbose_name="Наименование роли в ИС", 
        help_text="Введите наименование роли в ИС"
    )

    information_system = models.ForeignKey(
        InformationSystem,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="role_is",
        verbose_name="Наименование ИС",
        help_text="Укажите наименование ИС",
    )

    class Meta:
        verbose_name = "Роль информационной системы"
        verbose_name_plural = "Роли информационных систем"
        ordering = [
            "information_system",
            "title",
        ]

    def __str__(self):
        return f"{self.information_system} - {self.title}"


class AccessRequest(models.Model):
    PERMISSION_LEVELS = [
        ("READ", 'Чтение'),
        ("WRITE", 'Запись'),
    ]

    APPROVAL_STATUS_CHOICES = [
        ("pending", "На согласовании"),
        ("approved", "Согласовано"),
        ("rejected", "Отклонено"),
    ]
    
    created_at = models.DateField(
        blank=True, auto_now_add=True, verbose_name="Дата создания", help_text="Укажите дату создания"
    )

    information_system = models.ForeignKey(
        InformationSystem,
        on_delete=models.CASCADE,
        related_name="access_request_is",
        verbose_name="Наименование ИС",
        help_text="Укажите наименование ИС",
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="owned_access_request",
        verbose_name="Пользователь",
        help_text="Укажите пользователя - подающего заявку",
    )

    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name="supervisor_access_request",
        verbose_name="Непосредственный руководитель",
        help_text="Укажите непосредственного руководителя",
    )

    permission_level = models.CharField(
        max_length=10,
        choices=PERMISSION_LEVELS,
        default="READ",
        verbose_name="Уровень доступа",
        help_text="Укажите уровень доступа",
    )
    
    information_system_role = ChainedForeignKey(
        InformationSystemRole,
        on_delete=models.CASCADE,
        chained_field="information_system",  # Имя поля в ЭТОЙ модели
        chained_model_field="information_system",  # Имя поля в модели Role
        show_all=False,
        auto_choose=True,
        sort=True,
        verbose_name="Наименование роли в ИС",
        help_text="Укажите наименование роли в ИС",
    )

    approved_status_supervisor_is = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default="pending",
        editable=False,
        verbose_name="Статус согласования непосредственным руководителем",
        help_text="Укажите статус согласования непосредственным руководителем",
    )

    approved_status_owner_is = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default="pending",
        editable=False,
        verbose_name="Статус согласования владельцем ИС",
        help_text="Укажите статус согласования владельцем ИС",
    )

    approved_status_ib_is = models.CharField(
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default="pending",
        editable=False,
        verbose_name="Статус согласования сотрудником ИБ",
        help_text="Укажите статус согласования сотрудником ИБ",
    )

    class Meta:
        verbose_name = "Заявка на доступ к ИС"
        verbose_name_plural = "Заявки на доступ к ИС"
        ordering = [
            "created_at",
        ]
        permissions = [
            ("can_status_supervisor", "Может согласовывать как руководитель"),
            ("can_status_owner_is", "Может согласовывать как владелец ИС"),
            ("can_status_ib", "Может согласовывать как сотрудник ИБ"),
        ]

    def __str__(self):
        return f"{self.created_at} - {self.information_system} - {self.owner}"
