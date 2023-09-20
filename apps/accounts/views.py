from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from rest_framework.exceptions import ValidationError
from utils.emails import send_otp_email
from django.shortcuts import get_object_or_404
from apps.accounts.models import (
    User,
    Customer,
    Supplier,
    Biller,
    Warehouse,
    OTP,
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
from apps.accounts.utils import generate_otp

from utils.paginations import MyPagination
from utils.permissions import SupplierPermission


class CommonModelViewset(ModelViewSet):
    pagination_class = MyPagination


class UserViewSet(CommonModelViewset):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    
    search_fields = ['full_name', 'phone']
    ordering_fields = ['full_name']
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

    @action(methods = ['POST'], url_path = 'forgot-password', detail=False)
    def forgot_password(self, request):
        # using email serializer to validate the user password
        email_serializer = EmailSerializer(data=request.data)
        email_serializer.is_valid(raise_exception=True)
        email = email_serializer.validated_data['email']
        
        # getting the user after validating email 
        user = get_object_or_404(User, email=email)
        otp_for_user = generate_otp()
        
        # create user and add otp for the user else update the otp for user
        try:
            user_otp = OTP.objects.get(user=user)
            user_otp.otp = otp_for_user
            user_otp.save()
        except OTP.DoesNotExist:
            user_otp = OTP.objects.create(user=user, otp=otp_for_user)
        send_otp_email(user.email, otp_for_user)
        
        return Response({"success"  : "Email has been sent successfully", "data" : {"otp" : otp_for_user}}, status= status.HTTP_201_CREATED)
    
    @action(methods = ['POST'], detail=False, url_path = 'change-password', permission_classes=[AllowAny])
    def change_password(self, request):
        
        # getting the otp and its user
        pk = request.data.get('otp')
        user_otp = OTP.objects.filter(otp=pk).first()
        if user_otp is None:
            raise ValidationError({'otp': 'Sorry, the OTP you have entered is incorrect'})
        user = user_otp.user
        
        # validating otp, password and getting the new password from the user
        forgot_password_serializer = ForgotPasswordSerializer(data = request.data, context={'OTP': user_otp})
        forgot_password_serializer.is_valid(raise_exception=True)
        password = forgot_password_serializer.validated_data['password']
        
        
        # updating the user password
        user.set_password(password)
        user.save()
        
        # return success response after updating the password
        return Response({"success" : "Password reset successful"}, status=status.HTTP_202_ACCEPTED)

class CustomerViewSet(CommonModelViewset):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def create(self, request):
        
        # getting the user data
        user_data = request.data.pop('user')
        user_serializer = UserSerializer(data = user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        
        
        # # getting the remaining customer info
        customer_data = request.data
        customer_serializer = CustomerSerializer(data = customer_data)
        
        # validate customer data
        if customer_serializer.is_valid():
            customer_serializer.save(user = user)
            return Response({'data': customer_serializer.data}, status=status.HTTP_201_CREATED)
        else:
            user.delete()  # Delete the user if customer serializer is not valid
            return Response({'errors': customer_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def get_serializer_class(self):
        if self.action == "list":
            return GetCustomerSerializer
        return super().get_serializer_class()

    
    

class SupplierViewSet(CommonModelViewset):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

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

    
    

         
