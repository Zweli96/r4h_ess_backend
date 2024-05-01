from django.contrib import admin
from .models import Timesheet, Period, Project, PublicHoliday
# Register your models here.
admin.site.register(Timesheet)
admin.site.register(Period)
admin.site.register(Project)
admin.site.register(PublicHoliday)
