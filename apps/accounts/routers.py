from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    UserViewSet,
    CustomerViewSet,
    SupplierViewSet,
    BillerViewSet,
    WarehouseViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("customers", CustomerViewSet, basename="customers")
router.register("suppliers", SupplierViewSet, basename="suppliers")
router.register("billers", BillerViewSet, basename="billers")
router.register("warehouse", WarehouseViewSet, basename="warehouse")

urlpatterns = router.urls
