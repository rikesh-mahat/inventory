from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from apps.accounts.models import (
    User,
    Customer,
    Supplier,
    Biller,
    Warehouse,
)
from apps.accounts.serializers import (
    UserSerializer,
    SupplierSerializer,
    CustomerSerializer,
    BillerSerializer,
    WarehouseSerializer,
    GetSupplierSerializer,
    GetCustomerSerializer,
    GetBillerSerializer,
)
from apps.accounts.pagination import MyPagination
from utils.permissions import SupplierPermission


class CommonModelViewset(ModelViewSet):
    pagination_class = MyPagination


class UserViewSet(CommonModelViewset):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["full_name", ]
    permission_classes = [IsAdminUser]


class CustomerViewSet(CommonModelViewset):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return GetCustomerSerializer
        return super().get_serializer_class()


class SupplierViewSet(CommonModelViewset):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [SupplierPermission]

    def get_serializer_class(self):
        if self.action == "list":
            return GetSupplierSerializer
        return super().get_serializer_class()


class BillerViewSet(CommonModelViewset):
    queryset = Biller.objects.all()
    serializer_class = BillerSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GetBillerSerializer
        return super().get_serializer_class()

    def create(self, request):
        request.data["biller_code"] = f"BC-{Biller.objects.count()}"
        serializers = BillerSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(created_by=request.user)
        return Response(serializers.data, status=status.HTTP_201_CREATED)


class WarehouseViewSet(CommonModelViewset):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['^name']
    ordering_fields = ['name', 'email']

    def validation(self, data):
        if len(data.get('name')) < 3:
            error_message = {
                'name': 'This field should have more than 3 chars.'}
            raise serializers.ValidationError(error_message)
        return True

    def perform_create(self, serializer):
        if self.validation(serializer.validated_data):
            serializer.save()
