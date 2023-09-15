from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from apps.products.models import Brand, Category, Product, Unit
from apps.products.serializers import (
    BrandSerializers,
    CategorySerializer,
    ProductSerializer,
    GETProductSerializer,
    UnitSerializer,
    BarcodeSerializer,
    GetCategorySeralizer,
    GetUnitSeralizer,
    GetBrandSeralizer,
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
    BasePermission,
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
)

from apps.store.models import Warehouse
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["created_by"]
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
    
    
   
        
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # getting the warehouse from the request data
        warehouse_data = request.data.pop("warehouse")
        warehouse_ids_list = []  # for storing the id of the warehouses
        
        # loop throught the warehouses 
        for warehouse in warehouse_data:
            # create an warehouse if id isn't passed or update an warehouse if id is passed
            warehouse_instance, created = Warehouse.objects.update_or_create(id = warehouse.get('id'),defaults=warehouse)
            
            # append the created or updated warehouse id in our list
            warehouse_ids_list.append(warehouse_instance.id)
            
        # finally set the ids of the warehouse in our manytomany field relatioship
        instance.warehouse.set(warehouse_ids_list)
        serializer = ProductSerializer(instance)
        
        return Response({"updated data" : serializer.data})



class BarcodeViewset(ModelViewSet):
    pass