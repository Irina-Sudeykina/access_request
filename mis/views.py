import os
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.views.generic import ListView, View
from django.views.generic.detail import SingleObjectMixin
from rest_framework.permissions import AllowAny, IsAuthenticated

from mis.mixins import ApprovalPermissionMixin
from mis.models import InformationSystem, InformationSystemRole, AccessRequest
from mis.serializers import InformationSystemSerializer, InformationSystemRoleSerializer, AccessRequestSerializer
from users.permissions import isOwner
from dotenv import load_dotenv

load_dotenv(override=True)


class AccessRequestListView(LoginRequiredMixin, ListView):
    model = AccessRequest
    template_name = "mis/accessrequest_list.html"
    login_url = '/users/login/' # Укажите точный URL входа (или имя url)

    def get_queryset(self):
        # Возвращаем только заявки текущего пользователя
        return AccessRequest.objects.filter(owner=self.request.user).order_by('-created_at')


class AccessSuccessListView(ListView):
    model = AccessRequest
    template_name = "mis/accesssuccess_list.html"

    def get_queryset(self):
        user = self.request.user

        # Получаем группу "Специалисты по информационной безопасности"
        # Используем try/except на случай, если группы нет в базе
        try:
            ib_group = Group.objects.get(name="InformationSecurity")
            user_is_ib = ib_group in user.groups.all()
        except Group.DoesNotExist:
            user_is_ib = False

        # Собираем все условия в список для наглядности
        conditions = [
            Q(supervisor=user, approved_status_supervisor_is="pending"),
            Q(information_system__owner=user, 
              approved_status_supervisor_is="approved", 
              approved_status_owner_is="pending")
        ]

        # Добавляем условие для ИБ-специалиста, если он действительно в группе
        if user_is_ib:
            conditions.append(Q(approved_status_owner_is="approved", approved_status_ib_is="pending"))

        # Объединяем все условия оператором OR
        final_query = conditions.pop()
        for item in conditions:
            final_query |= item

        return AccessRequest.objects.filter(final_query)

    def get_context_data(self, **kwargs):
        # 1. Получаем стандартный контекст
        context = super().get_context_data(**kwargs)

        # 2. Добавляем в него нашу переменную
        user = self.request.user

        # Проверяем членство в группе ИБ
        try:
            ib_group = Group.objects.get(name="InformationSecurity")
            is_in_ib_group = ib_group in user.groups.all()
        except Group.DoesNotExist:
            is_in_ib_group = False

        context['is_in_ib_group'] = is_in_ib_group

        return context


class ApprovalActionView(ApprovalPermissionMixin, SingleObjectMixin, View):
    """
    Базовый класс для действий согласования.
    """
    model = AccessRequest

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() # Получаем заявку
        
        # Здесь будет логика изменения статуса
        self.update_status()
        self.object.save()
        
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('mis:accesssuccess_list')


class ApprovedSupervisorView(ApprovalActionView):
    def update_status(self):
        self.object.approved_status_supervisor_is = "approved"
        self.object.save()


class RejectedSupervisorView(ApprovalActionView):
    def update_status(self):
        self.object.approved_status_supervisor_is = "rejected"
        self.object.save()


class ApprovedOwnerView(ApprovalActionView):
    def update_status(self):
        self.object.approved_status_owner_is = "approved"
        self.object.save()


class RejectedOwnerView(ApprovalActionView):
    def update_status(self):
        self.object.approved_status_owner_is = "rejected"
        self.object.save()


class ApprovedIBView(ApprovalActionView):
    """
    Класс для согласования заявки сотрудником ИБ.
    Наследует всю логику из ApprovalActionView.
    """
    def update_status(self):
        """
        Изменяет статус заявки и отправляет письмо в IT поддержку.
        """
        # 1. Изменяем статус заявки
        self.object.approved_status_ib_is = "approved"
        
        # ВАЖНО: Не забудьте сохранить изменения в базе данных!
        self.object.save() 

        # 2. Формируем текст письма
        subject = f"Заявка на доступ к ИС {self.object.information_system}"

        # Собираем строки в список
        lines = [
            f"ФИО сотрудника: {self.object.owner.fullname}",
            f"Должность: {self.object.owner.position}",
            f"Телефон: {self.object.owner.phone}",
            f"УЗ: {self.object.owner.username}",
            f"ФИО руководителя: {self.object.supervisor.fullname}",
            f"Должность: {self.object.supervisor.position}",
            f"Телефон: {self.object.supervisor.phone}",
            f"Уровень доступа: {self.object.permission_level}",
            f"Роль в ИС: {self.object.information_system_role}"
        ]

        # Объединяем строки, используя правильный перенос для ОС (os.linesep)
        # На Windows это будет \r\n, на Linux/macOS - \n
        message = os.linesep.join(lines)

        recipient_list = [os.getenv("EMAIL_IT_USER")] 

        # 3. Отправляем письмо
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )


class RejectedIBView(ApprovalActionView):
    def update_status(self):
        self.object.approved_status_ib_is = "rejected"
