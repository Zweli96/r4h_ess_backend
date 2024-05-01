# todo/todo_api/urls.py : API urls.py
from django.urls import path, include, re_path
from .views import (
    TimesheetListApiView,
    TimesheetDetailApiView,
    ApproveListApiView,
    ApproveDetailApiView
)

urlpatterns = [
    path('api', TimesheetListApiView.as_view()),
    path('api/<int:timesheet_id>/', TimesheetDetailApiView.as_view()),
    path('api/approvals', ApproveListApiView.as_view()),
    path('api/approvals/<int:timesheet_id>/',
         ApproveDetailApiView.as_view()),
]
