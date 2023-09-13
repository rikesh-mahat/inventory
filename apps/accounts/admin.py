from django.contrib import admin
from apps.accounts.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'phone', 'otp']