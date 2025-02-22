# todo/todo_api/urls.py : API urls.py
from django.urls import path, include, re_path
from .views import (
    TimesheetListApiView,
    TimesheetDetailApiView,
    ApproveListApiView,
    ApproveDetailApiView,
    PeriodListApiView,
    EmployeePeriodListApiView
)

urlpatterns = [
    path('', TimesheetListApiView.as_view()),
    path('<int:timesheet_id>/', TimesheetDetailApiView.as_view()),
    path('approvals', ApproveListApiView.as_view()),
    path('approvals/<int:timesheet_id>',
         ApproveDetailApiView.as_view()),
    path('periods', PeriodListApiView.as_view()),
    path('periods/employee/<int:period_id>',
         EmployeePeriodListApiView.as_view()),
]
