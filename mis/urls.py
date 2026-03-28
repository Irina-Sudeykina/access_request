from django.urls import path

from mis.apps import MisConfig
from mis.views import (AccessRequestListView, AccessSuccessListView, ApprovedSupervisorView, RejectedSupervisorView,
                       ApprovedOwnerView, RejectedOwnerView, ApprovedIBView, RejectedIBView, AccessRequestCreateView)

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
]
