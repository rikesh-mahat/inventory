from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from apps.products.models import (
    Brand,
    Sales,
    Category,
    Product,
    Purchase,
    Unit,
    PurchaseInvoice,
    SalesInvoice,
    Adjustment,
    AdjustmentItems,
)

from apps.products.serializers import (
    BrandSerializers,
    CategorySerializer,
    ProductSerializer,
    GETProductSerializer,
    UnitSerializer,
    BarcodeSerializer,
    GETBarcodeSerializer,
    GetCategorySeralizer,
    GetUnitSeralizer,
    GetBrandSeralizer,
    PurchaseSerializer,
    SalesSerializer,
    GetPurchaseSerializer,
    PurchaseInvoiceSerializer,
    SalesInvoiceSerializer,
    AdjustmentSerializer,
    AdjustmentItemsSerializer,
)
from apps.accounts.serializers import UserSerializer
from rest_framework import serializers
from utils.paginations import MyPagination
from rest_framework.permissions import BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.response import Response
from rest_framework import status
from utils.permissions import SupplierPermission
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)
from django.shortcuts import get_object_or_404

from apps.store.models import Warehouse
from apps.products.models import Barcode

import barcode
from PIL import Image
from io import BytesIO
import uuid
import os
from barcode.writer import ImageWriter

# Create your views here.


class MyPagination(ModelViewSet):
    pagination_class = MyPagination


class BrandViewSet(MyPagination):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializers
    http_method_names = ["get", "post", "put", "delete"]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["brand_name"]

    def create(self, request, *args, **kwargs):
        serializers = BrandSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(created_by=request.user, modified_by=None)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializers = BrandSerializers(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(modified_by=request.user)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetBrandSeralizer
        return super().get_serializer_class()


class CategoryViewSet(MyPagination):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    http_method_names = ["get", "post", "delete"]

    def create(self, request, *args, **kwargs):
        serializers = CategorySerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(created_by=request.user, modified_by=None)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetCategorySeralizer
        return super().get_serializer_class()


class UnitViewSet(ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]
    # permission_classes = [IsUserAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["=short_name"]
    ordering_fields = ["short_name"]

    def create(self, request, *args, **kwargs):
        serializers = UnitSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(created_by=request.user)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetUnitSeralizer
        return super().get_serializer_class()


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["created_by"]
    search_fields = ["product_name"]
    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [IsAuthenticated],
        "create": [IsAdminUser | SupplierPermission],
        "update": [IsAuthenticated | SupplierPermission],
    }

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except:
            return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GETProductSerializer
        return super().get_serializer_class()


class BarcodeViewset(ModelViewSet):
    queryset = Barcode.objects.all()
    serializer_class = BarcodeSerializer

    def create(self, request, *args, **kwargs):
        product_infromation = request.data.get("information")
        get_current_product = Product.objects.get(id=product_infromation)
        get_current_product_code = str(get_current_product.product_code)
        if not get_current_product_code:
            # print(product_infromation.product_code)
            return Response(
                {"error": "Product code is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        barcode_class = barcode.get_barcode_class("code128")
        code = barcode_class(get_current_product_code, writer=ImageWriter())

        unique_filename = f"barcode_{uuid.uuid4()}"

        directory_path = "barcode-image/"
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        barcode_image = code.save(f"barcode-image/{unique_filename}")

        serializer = BarcodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(barcode_image=barcode_image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GETBarcodeSerializer
        return super().get_serializer_class()


class PurchaseViewSet(ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [SupplierPermission],
        "create": [SupplierPermission],
        "update": [SupplierPermission],
        "destroy": [SupplierPermission],
    }

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except:
            return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetPurchaseSerializer
        return super().get_serializer_class()


class SalesViewSet(ModelViewSet):
    queryset = Sales.objects.all()
    serializer_class = SalesSerializer
    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [IsAuthenticated],
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "destroy": [IsAdminUser],
    }

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except:
            return [permission() for permission in self.permission_classes]


class PurchaseInvoiceViewSet(ModelViewSet):
    queryset = PurchaseInvoice.objects.all()
    serializer_class = PurchaseInvoiceSerializer

    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [IsAuthenticated],
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "destroy": [IsAdminUser],
    }

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except:
            return [permission() for permission in self.permission_classes]


class SalesInvoiceViewSet(ModelViewSet):
    queryset = SalesInvoice.objects.all()
    serializer_class = SalesInvoiceSerializer

    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [IsAuthenticated],
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "destroy": [IsAdminUser],
    }

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except:
            return [permission() for permission in self.permission_classes]


class AdjustmentViewSet(ModelViewSet):
    queryset = Adjustment.objects.all()
    serializer_class = AdjustmentSerializer
    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [IsAuthenticated],
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "destroy": [IsAdminUser],
    }

    def create(self, request):
        serializer = AdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        warehouse = serializer.validated_data.pop("warehouse")
        adjustment = Adjustment.objects.create(
            warehouse=warehouse, **serializer.validated_data
        )
        serializer = AdjustmentSerializer(adjustment)
        return Response({"success": "ok", "data": serializer.data})

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except:
            return [permission() for permission in self.permission_classes]


class AdjustmentItemsViewSet(ModelViewSet):
    queryset = AdjustmentItems.objects.all()
    serializer_class = AdjustmentItemsSerializer
    permission_classes_by_action = {
        "list": [AllowAny],
        "retrieve": [IsAuthenticated],
        "create": [IsAdminUser],
        "update": [IsAdminUser],
        "destroy": [IsAdminUser],
    }

    def create(self, request):
        serializer = AdjustmentItemsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        adjustment = AdjustmentItems.objects.create(**serializer.validated_data)
        serializer = AdjustmentItemsSerializer(adjustment)
        return Response({"data": serializer.data})

    def get_permissions(self):
        try:
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except:
            return [permission() for permission in self.permission_classes]
