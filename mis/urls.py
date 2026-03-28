from django.urls import path

from mis.apps import MisConfig
from mis.views import (AccessRequestListView, AccessSuccessListView, ApprovedSupervisorView, RejectedSupervisorView,
                       ApprovedOwnerView, RejectedOwnerView, ApprovedIBView, RejectedIBView, AccessRequestCreateView,
                       InformationSystemListView, InformationSystemCreateView, InformationSystemUpdateView, 
                       InformationSystemDeleteView, InformationSystemRoleListView, InformationSystemRoleCreateView,
                       InformationSystemRoleUpdateView, InformationSystemRoleDeleteView)

app_name = MisConfig.name


urlpatterns = [
    path("", AccessRequestListView.as_view(), name="accessrequest_list"),
    path("success/", AccessSuccessListView.as_view(), name="accesssuccess_list"),
    path("approved_supervisor/<int:pk>/", ApprovedSupervisorView.as_view(), name="approved_supervisor"),
    path("rejected_supervisor/<int:pk>/", RejectedSupervisorView.as_view(), name="rejected_supervisor"),
    path("approved_owner/<int:pk>/", ApprovedOwnerView.as_view(), name="approved_owner"),
    path("rejected_owner/<int:pk>/", RejectedOwnerView.as_view(), name="rejected_owner"),
    path("approved_ib/<int:pk>/", ApprovedIBView.as_view(), name="approved_ib"),
    path("rejected_ib/<int:pk>/", RejectedIBView.as_view(), name="rejected_ib"),
    path("access_request/create/", AccessRequestCreateView.as_view(), name="accessrequest_create"),
    path("information_system/", InformationSystemListView.as_view(), name="informationsystem_list"),
    path("information_system/create/", InformationSystemCreateView.as_view(), name="informationsystem_create"),
    path("information_system/<int:pk>/update/", InformationSystemUpdateView.as_view(), name="informationsystem_update"),
    path("information_system/<int:pk>/delete/", InformationSystemDeleteView.as_view(), name="informationsystem_delete"),
    path("information_system_role/", InformationSystemRoleListView.as_view(), name="informationsystemrole_list"),
    path("information_system_role/create/", InformationSystemRoleCreateView.as_view(), name="informationsystemrole_create"),
    path("information_system_role/<int:pk>/update/", InformationSystemRoleUpdateView.as_view(), name="informationsystemrole_update"),
    path("information_system_role/<int:pk>/delete/", InformationSystemRoleDeleteView.as_view(), name="informationsystemrole_delete"),
]
