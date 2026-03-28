from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now as timezone_now

from mis.models import InformationSystem, InformationSystemRole, AccessRequest


class AccessRequestService:
    """
    Класс для получения статистики по заявкам
    """

    @staticmethod
    def get_access_request_count():
        """
        Общее количество заявок
        """
        return AccessRequest.objects.count()

    @staticmethod
    def get_active_access_request_count():
        """
        Количество активных заявок (теребующих согласования)
        """
        active_access_request = AccessRequest.objects.filter(approved_status_ib_is="pending")
        return active_access_request.count()

    @staticmethod
    def get_approved_access_request_count():
        """
        Количество согласованных заявок
        """
        approved_access_request = AccessRequest.objects.filter(approved_status_ib_is="approved")
        return approved_access_request.count()

    @staticmethod
    def get_rejected_access_request_count():
        """
        Количество отклоненных заявок
        """
        rejected_supervisor = AccessRequest.objects.filter(approved_status_supervisor_is="rejected")
        rejected_owner = AccessRequest.objects.filter(approved_status_owner_is="rejected")
        rejected_ib = AccessRequest.objects.filter(approved_status_ib_is="rejected")
        return rejected_supervisor.count() + rejected_owner.count() + rejected_ib.count()
