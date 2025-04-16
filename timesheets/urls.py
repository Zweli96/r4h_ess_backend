# todo/todo_api/urls.py : API urls.py
from django.urls import path, include, re_path
from .views import (
    TimesheetListApiView,
    TimesheetDetailApiView,
    ApproveListApiView,
    ApproveDetailApiView,
    PeriodListApiView,
    EmployeePeriodListApiView, ActivityListApiView, ActivityDetailApiView, TimesheetReportView
)

urlpatterns = [
    path('timesheets', TimesheetListApiView.as_view()),
    path('<int:timesheet_id>/', TimesheetDetailApiView.as_view()),
    path('approvals', ApproveListApiView.as_view()),
    #     path('approvals/<int:timesheet_id>',
    #          ApproveDetailApiView.as_view()),
    path(
        "approvals/approve/<int:timesheet_id>",
        ApproveDetailApiView.as_view(),
        name="approve-timesheet",
        kwargs={"action": "approve"},  # Pass action as 'approve'
    ),
    path(
        "approvals/reject/<int:timesheet_id>",
        ApproveDetailApiView.as_view(),
        name="reject-timesheet",
        kwargs={"action": "reject"},  # Pass action as 'reject'
    ),
    path('periods', PeriodListApiView.as_view()),
    path('periods/employee/<int:period_id>',
         EmployeePeriodListApiView.as_view()),
    path('activities/', ActivityListApiView.as_view()),
    path('activities/<int:activity_id>/', ActivityDetailApiView.as_view()),
    path('timesheetReport/', TimesheetReportView.as_view()),
]
