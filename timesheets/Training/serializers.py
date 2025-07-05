from rest_framework import serializers
from .models import Course, Chapter, AssessmentQuestion, UserProgress

class ChapterSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'content', 'order']

class AssessmentQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentQuestion
        fields = ['id', 'question', 'options', 'answer', 'order']

    def get_options(self, obj):
        return [obj.option1, obj.option2, obj.option3, obj.option4]

class UserProgressSerializer(serializers.ModelSerializer):
    completed_chapters = serializers.PrimaryKeyRelatedField(many=True, queryset=Chapter.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = UserProgress
        fields = ['id', 'course', 'completed_chapters', 'assessment_score', 'is_completed']

class CourseSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    totalChapters = serializers.IntegerField(source='total_chapters', read_only=True)
    assessment_questions = AssessmentQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'image', 'chapters', 'totalChapters', 'assessment_questions']