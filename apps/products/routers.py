from rest_framework.routers import DefaultRouter
from apps.products.views import (
    ProductViewSet,
    BrandViewSet,
    CategoryViewSet,
    UnitViewSet,
    BarcodeViewset,
    PurchaseViewSet,
    SalesViewSet,
    PurchaseInvoiceViewSet,
    SalesInvoiceViewSet,
    AdjustmentViewSet,
    AdjustmentItemsViewSet
)

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("brands", BrandViewSet)
router.register("category", CategoryViewSet)
router.register("units", UnitViewSet)
router.register("barcodes",  BarcodeViewset)
router.register('purchases', PurchaseViewSet)
router.register("sales", SalesViewSet)
router.register('purchase-invoice', PurchaseInvoiceViewSet)
router.register('sales-invoice', SalesInvoiceViewSet)
router.register('adjustment', AdjustmentViewSet)
router.register('adjustment-items', AdjustmentItemsViewSet)