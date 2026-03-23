from rest_framework.permissions import BasePermission


class isOwner(BasePermission):
    message = "Вы не являетесь владельцем."

    def has_object_permission(self, request, view, obj):
        if obj.owner == request.user:
            return True
        return False
