from django.contrib import admin

from mis.models import AccessRequest, InformationSystem, InformationSystemRole


@admin.register(InformationSystem)
class InformationSystemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner")
    list_filter = (
        "title",
        "owner",
    )
    search_fields = (
        "title",
        "owner",
    )


@admin.register(InformationSystemRole)
class InformationSystemRoleAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "information_system")
    list_filter = (
        "title",
        "information_system",
    )
    search_fields = (
        "title",
        "information_system",
    )


@admin.register(AccessRequest)
class AccessRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "information_system",
        "owner",
        "permission_level",
        "information_system_role",
        "approved_status_supervisor_is",
        "approved_status_owner_is",
        "approved_status_ib_is",
    )
    list_filter = (
        "created_at",
        "information_system",
        "owner",
        "permission_level",
        "information_system_role",
        "approved_status_supervisor_is",
        "approved_status_owner_is",
        "approved_status_ib_is",
    )
    search_fields = (
        "created_at",
        "information_system",
        "owner",
        "permission_level",
        "information_system_role",
        "approved_status_supervisor_is",
        "approved_status_owner_is",
        "approved_status_ib_is",
    )
