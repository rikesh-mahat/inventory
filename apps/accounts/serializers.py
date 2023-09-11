from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import (
    User,
    Customer,
    Biller,
    Supplier,
    Warehouse,
)


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
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
        user = User.objects.create(**validated_data)
        if password is not None:
            user.set_password(validated_data['password'])
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
