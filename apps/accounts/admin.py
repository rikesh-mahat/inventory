from django.contrib import admin
from apps.accounts.models import (User, OTP, Customer, Supplier)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'username', 'phone']
    
    
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['otp', 'user']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id']
    
    
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id']