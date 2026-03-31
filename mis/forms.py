from django import forms
from django.contrib.auth.models import Group
from django.db.models import Q

from mis.models import AccessRequest, InformationSystem, InformationSystemRole


class StyleFormMixin:
    """
    Форма для красивого отображения
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class AccessRequestForm(StyleFormMixin, forms.ModelForm):
    """
    Форма для создания новой заявки на предоставления доступа
    """

    class Meta:
        model = AccessRequest
        exclude = ("owner",)

    def __init__(self, *args, **kwargs):
        # Извлекаем пользователя (если нужно для фильтрации систем)
        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # Проходим по всем полям формы и удаляем их подсказки
        for field in self.fields.values():
            field.help_text = None

        # --- Фильтр для поля 'supervisor' ---
        try:
            # 1. Находим группу "Admins"
            admins_group = Group.objects.get(name="Admins")

            # 2. Получаем базовый QuerySet для поля supervisor
            queryset = self.fields["supervisor"].queryset

            # 3. Исключаем пользователей, которые ИЛИ в группе Admins, ИЛИ являются суперпользователями
            # Q-объекты позволяют использовать логическое ИЛИ (|) в фильтре
            queryset = queryset.exclude(Q(groups=admins_group) | Q(is_superuser=True))

            # 4. Заменяем стандартный список пользователей на отфильтрованный
            self.fields["supervisor"].queryset = queryset

        except Group.DoesNotExist:
            # Если группы "Admins" нет, исключаем только суперпользователей
            self.fields["supervisor"].queryset = self.fields["supervisor"].queryset.exclude(is_superuser=True)

        # Этот блок отвечает за то, чтобы роли фильтровались при выборе системы
        # и чтобы форма работала при редактировании.

        # Если форма уже связана с сохраненным объектом (редактирование)
        if self.instance and self.instance.information_system_id:
            # Устанавливаем роли для текущей системы заявки
            self.fields["information_system_role"].queryset = self.instance.information_system.role_is.all()

        # Если в данных POST-запроса есть ID выбранной системы
        if "information_system" in self.data:
            try:
                system_id = int(self.data.get("information_system"))
                self.fields["information_system_role"].queryset = InformationSystemRole.objects.filter(
                    information_system_id=system_id
                )
            except (ValueError, TypeError):
                # Если ID невалидный, оставляем поле пустым
                pass


class InformationSystemForm(StyleFormMixin, forms.ModelForm):
    """
    Форма для создания новой ИС
    """

    class Meta:
        model = InformationSystem
        fields = ["title", "owner"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Проходим по всем полям формы и удаляем их подсказки
        for field in self.fields.values():
            field.help_text = None

        # --- Фильтр для поля 'owner' ---
        try:
            # 1. Находим группу "Admins"
            admins_group = Group.objects.get(name="Admins")

            # 2. Получаем базовый QuerySet для поля owner
            queryset = self.fields["owner"].queryset

            # 3. Исключаем пользователей, которые ИЛИ в группе Admins, ИЛИ являются суперпользователями
            # Q-объекты позволяют использовать логическое ИЛИ (|) в фильтре
            queryset = queryset.exclude(Q(groups=admins_group) | Q(is_superuser=True))

            # 4. Заменяем стандартный список пользователей на отфильтрованный
            self.fields["owner"].queryset = queryset

        except Group.DoesNotExist:
            # Если группы "Admins" нет, исключаем только суперпользователей
            self.fields["owner"].queryset = self.fields["owner"].queryset.exclude(is_superuser=True)


class InformationSystemRoleForm(StyleFormMixin, forms.ModelForm):
    """
    Форма для создания новой роли в ИС
    """

    class Meta:
        model = InformationSystemRole
        fields = ["title", "information_system"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Проходим по всем полям формы и удаляем их подсказки
        for field in self.fields.values():
            field.help_text = None
