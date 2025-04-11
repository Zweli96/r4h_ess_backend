from django.contrib import admin
from .models import Staff, Department, District,Activity

# Register your models here.
admin.site.register(Staff)
admin.site.register(Department)
admin.site.register(District)
admin.site.register(Activity)
