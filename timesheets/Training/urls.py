from django.urls import path, include


from django.urls import path
from .views import CourseListView, CourseDetailView, UserProgressView, UserProgressListView

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('user-progress/<int:course_id>/', UserProgressView.as_view(), name='user-progress'),
    path('user-progress/', UserProgressListView.as_view(), name='user-progress-list'),
]
