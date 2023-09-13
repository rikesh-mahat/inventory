from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.views import APIView
from utils.emails import send_otp_email
from django.shortcuts import get_object_or_404

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
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    EmailSerializer,
)
from apps.accounts.pagination import MyPagination
from utils.permissions import SupplierPermission


class CommonModelViewset(ModelViewSet):
    pagination_class = MyPagination


class UserViewSet(CommonModelViewset):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["full_name" ]
    permission_classes = [IsAdminUser]
    
    def get_serializer_class(self):
        if self.action == "reset_password":
            return ChangePasswordSerializer
        return super().get_serializer_class()
    
    @action(methods = ['POST'], detail=True, url_path='reset-password', permission_classes=[IsAuthenticated])
    def reset_password(self, request, pk=None):
        serializers = ChangePasswordSerializer(request.user, data=request.data, context={'request': request})
        if serializers.is_valid():
            serializers.save()
            return Response({"success" : "password changed successfully"}, status=status.HTTP_201_CREATED)
        return Response({"error": serializers.errors}, status=status.HTTP_400_BAD_REQUEST)


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
    search_fields = ['name']
    ordering_fields = ['name', 'email']

    
import random
def generate_otp():
    otp = random.randint(0, 999999)
    otp_str = str(otp).zfill(6)
    return otp_str
    
class ForgotPasswordView(ModelViewSet):
    permission_classes = [AllowAny]
    
    def create(self, request):
      
        # using email serializer to validate the user password
        email_serializer = EmailSerializer(data=request.data)
        email_serializer.is_valid(raise_exception=True)
        email = email_serializer.validated_data['email']
        
        # getting the user after validating email 
        user = get_object_or_404(User, email=email)
        otp = generate_otp()
        user.otp = otp
        user.save()
        send_otp_email(user.email, otp)
        
        
    
        return Response({"success"  : "Email has been sent successfully", "data" : {"email" : user.id}}, status= status.HTTP_201_CREATED)
       
    @action(methods = ['POST'], detail=True, url_path = 'change-password', permission_classes=[AllowAny])
    def change_password(self, request, pk=None):
        
        user = get_object_or_404(User, id = pk)
        # validating otp, password and getting the new password from the user
        forgot_password_serializer = ForgotPasswordSerializer(data = request.data, context={'user': user})
        forgot_password_serializer.is_valid(raise_exception=True)
        password = forgot_password_serializer.validated_data['password']
        
        
        # updating the user password
        user.set_password(password)
        user.save()
        
        # return success response after updating the password
        return Response({"success" : "Password reset successful"}, status=status.HTTP_202_ACCEPTED)
         
