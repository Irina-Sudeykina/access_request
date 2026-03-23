from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import Group

class ApprovalPermissionMixin(AccessMixin):
    """
    Миксин для проверки прав на согласование заявки.
    """
    def dispatch(self, request, *args, **kwargs):
        # Получаем объект заявки (он должен быть у view)
        # Для этого view должен наследовать SingleObjectMixin или получать объект другим способом
        obj = self.get_object()
        user = request.user

        # Проверяем права руководителя
        is_supervisor = obj.supervisor == user

        # Проверяем права владельца ИС
        is_owner = obj.information_system.owner == user

        # Проверяем права специалиста ИБ (членство в группе)
        try:
            ib_group = Group.objects.get(name="InformationSecurity")
            is_ib = ib_group in user.groups.all()
        except Group.DoesNotExist:
            is_ib = False

        # Если ни одно из условий не выполнено - запрещаем доступ
        if not (is_supervisor or is_owner or is_ib):
            return self.handle_no_permission() # Вызывает 403 Forbidden

        return super().dispatch(request, *args, **kwargs)
