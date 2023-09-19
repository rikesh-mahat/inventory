from rest_framework.permissions import (BasePermission,)
from apps.accounts.models import Supplier

class SupplierPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role == "Supplier"
    
    def has_object_permission(self, request, view, obj):
        return obj.supplier == request.user.supplier
    

