from rest_framework.routers import DefaultRouter
from apps.products.views import (
    ProductViewSet,
    BrandViewSet,
    CategoryViewSet,
    UnitViewSet,
)

router = DefaultRouter()
router.register("products", ProductViewSet)
router.register("brands", BrandViewSet)
router.register("cateogry", CategoryViewSet)
router.register("units", UnitViewSet)