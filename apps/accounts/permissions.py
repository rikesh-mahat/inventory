from rest_framework.permissions import BasePermission

class SupplierPermission(BasePermission):
    def has_permission(self, request):
        if request.user.role == "Supplier":
            return True
        return False