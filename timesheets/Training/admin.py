from django.contrib import admin


from timesheets.Training.models import Course, Chapter, AssessmentQuestion, UserProgress

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'total_chapters']
    list_filter = ['created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['total_chapters']

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    search_fields = ['title', 'content']
    list_select_related = ['course']

@admin.register(AssessmentQuestion)
class AssessmentQuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'course', 'order', 'answer']
    list_filter = ['course']
    search_fields = ['question', 'option1', 'option2', 'option3', 'option4']
    list_select_related = ['course']

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'assessment_score', 'is_completed']
    list_filter = ['user', 'course', 'is_completed']
    search_fields = ['user__username', 'course__title']
    list_select_related = ['user', 'course']
    filter_horizontal = ['completed_chapters']