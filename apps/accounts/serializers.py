from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from decouple import config
import pyotp

from apps.accounts.models import (
    User,
    Customer,
    Biller,
    Supplier,
    OTP,
)

from apps.store.models import Warehouse

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
        required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "phone",
            "email",
            "password",
            "password2",
            "gender",
            "username",
            "role",
        )
        

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {
                    "password": "The two password fields did not match"
                }
            )
        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        validated_data.pop('password2')
        user = User.objects.create(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = (
            "supplier_code",
            "company",
        )


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            "supplier_name",
            "customer_group",
            "reward_point",
        )


class BillerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biller
        fields = (
            "id",
            "NID",
            "warehouse",
            "biller_code"
        )


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = fields = (
            "id",
            "name",
            "email",
            "phone",
        )


class GetSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = (
            "supplier_code",
            "company",
        )


class GetBillerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    warehouse = WarehouseSerializer()

    class Meta:
        model = Biller
        fields = (
            "id",
            "biller_code",
            "user",
            "NID",
            "warehouse",
        )

class GetCustomerSerializer(serializers.ModelSerializer):
    supplier_name = GetSupplierSerializer()

    class Meta:
        model = Customer
        fields = (
            "supplier_name",
            "customer_group",
            "reward_point",
        )
        



class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=255, write_only =True)
    password = serializers.CharField(max_length=255, write_only=True)
    password1 = serializers.CharField(max_length = 255, write_only= True)
    
    class Meta:
        model = User
        fields = ['old_password', 'password', 'password1']
        
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old password" : "Sorry your old password doesn't match"})
        return value
    
    def validate(self, data):
        if data.get('password') != data.get('password1'):
            raise serializers.ValidationError({"password" : "Your password donot match"})
        return data
   
    def update(self, instance, validated_data):
        instance.set_password(validated_data.get("password"))
        instance.save()
        return instance



class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True)
    
    class Meta:
        fields = ['email']
    
class ForgotPasswordSerializer(serializers.ModelSerializer):
    otp = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    
    class Meta:
        model = OTP
        fields = ['otp', 'password', 'password1']
        
    def validate_otp(self, value):
        otp = self.context['otp']
        totp = pyotp.TOTP(config('TOTP_SECRET_KEY'))
        
        if not totp.verify(otp):
            raise serializers.ValidationError("The otp has expired")
        if  otp.otp!= value:
            raise serializers.ValidationError("otp doesn't match")
        return value
    
    def validate(self, data):
        if data.get('password') != data.get('password1'):
            raise serializers.ValidationError('password do not match')
        return data
    
    
# class OTPSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OTP
#         fields = ['user', 'otp', 'created_at']