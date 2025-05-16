from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

class CustomUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  
            try:
                send_mail(
                    'Your account credentials',
                    f'Username: {obj.username}\nEmail: {obj.email}',
                    settings.DEFAULT_FROM_EMAIL,
                    [obj.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending email: {e}")

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)
