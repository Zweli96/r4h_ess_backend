from django.contrib import admin
from .models import Timesheet, Period, PublicHoliday
from timesheets.Training.models import Course, Chapter, AssessmentQuestion, UserProgress
# Register your models here.
admin.site.register(Course)
admin.site.register(Chapter)

admin.site.register(AssessmentQuestion)
admin.site.register(UserProgress)
admin.site.register(Timesheet)
admin.site.register(Period)

admin.site.register(PublicHoliday)