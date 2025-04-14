from django.contrib import admin
from .models import Timesheet, Period, PublicHoliday
# Register your models here.
admin.site.register(Timesheet)
admin.site.register(Period)

admin.site.register(PublicHoliday)
