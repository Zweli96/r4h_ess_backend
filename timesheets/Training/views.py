from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Course, UserProgress
from .serializers import CourseSerializer, UserProgressSerializer

class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class UserProgressView(generics.RetrieveUpdateAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = UserProgressSerializer

    def get_object(self):
        course_id = self.kwargs['course_id']
        return UserProgress.objects.get_or_create(
            user=self.request.user,
            course_id=course_id,
            defaults={'is_completed': False}
        )[0]

class UserProgressListView(generics.ListAPIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = UserProgressSerializer

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)