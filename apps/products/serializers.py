from rest_framework import serializers
from apps.products.models import (
    Brand,
    Sales,
    Category,
    Product,
    Unit,
    Barcode,
    Purchase,
    Adjustment,
    AdjustmentItems,
    Invoice,
    PurchaseInvoice,
    SalesInvoice,
)
from apps.accounts.serializers import (
    UserSerializer,
    SupplierSerializer,
    BillerSerializer,
    CustomerSerializer,
)
from apps.store.serializers import WarehouseSerializer
from apps.store.models import Warehouse
from apps.accounts.models import Supplier


class BrandSerializers(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = (
            "id",
            "brand_name",
            "brand_image",
        )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "main_category", "sub_category")

    def validate(self, data):
        if data["sub_category"] == data["main_category"]:
            raise serializers.ValidationError(
                {"sub_category": "Sub category cannot be same as main category."}
            )
        return data


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ("id", "unit_name", "short_name")


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "product_name",
            "product_type",
            "category",
            "product_code",
            "brand",
            "barcode",
            "product_unit",
            "product_price",
            "expense",
            "unit_price",
            "product_tax",
            "tax_method",
            "discount",
            "warehouse",
            "stock_alert",
            "product_image",
            "featured",
            "price_difference_in_warehouse",
            "has_expiry_date",
            "add_promotional_sale",
            "has_multi_variant",
            "has_imie_code",
        )

    def create(self, validated_data):
        warehouse_data = validated_data.pop("warehouse", [])  # Extract warehouse data

        product = Product.objects.create(**validated_data)
        for warehouse_info in warehouse_data:
            warehouse_id = warehouse_info.id

            try:
                warehouse_obj = Warehouse.objects.get(id=warehouse_id)
                product.warehouse.add(warehouse_obj)
            except Warehouse.DoesNotExist:
                pass

        return product


class BarcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barcode
        fields = [ "id", "information", "papersize"]


class GETBarcodeSerializer(serializers.ModelSerializer):
    information = ProductSerializer()
    class Meta:
        model = Barcode
        fields = ['id', 'information', 'papersize']

class GETProductSerializer(serializers.ModelSerializer):
    brand = BrandSerializers()
    category = CategorySerializer()
    product_unit = UnitSerializer()
    created_by = UserSerializer()
    modified_by = UserSerializer()
    user = UserSerializer()
    warehouse = WarehouseSerializer(many=True)

    class Meta:
        model = Product
        fields = "__all__"


class GetCategorySeralizer(serializers.ModelSerializer):
    created_by = UserSerializer()
    modified_by = UserSerializer()

    class Meta:
        model = Category
        fields = (
            "created_by",
            "modified_by",
            "main_category",
            "sub_category",
        )


class GetUnitSeralizer(serializers.ModelSerializer):
    created_by = UserSerializer()
    modified_by = UserSerializer()

    class Meta:
        model = Unit
        fields = ("created_by", "modified_by", "unit_name", "short_name")


class GetBrandSeralizer(serializers.ModelSerializer):
    created_by = UserSerializer()
    modified_by = UserSerializer()

    class Meta:
        model = Brand
        fields = (
            "created_by",
            "modified_by",
            "brand_name",
            "brand_image",
        )


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = [
            "id",
            "warehouse",
            "supplier",
            "product",
            "order_tax",
            "order_discount",
            "shipping",
            "sales_status",
            "purchase_note",
        ]


class GetPurchaseSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer()
    supplier = SupplierSerializer()
    product = ProductSerializer(many=True)

    class Meta:
        model = Purchase
        fields = [
            "id",
            "warehouse",
            "supplier",
            "product",
            "order_tax",
            "order_discount",
            "shipping",
            "sales_status",
            "purchase_note",
        ]


class SalesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sales
        fields = [
            "id",
            "customer",
            "warehouse",
            "biller",
            "product",
            "sales_tax",
            "discount",
            "shipping",
            "sales_status",
            "payment_status",
            "sales_image",
            "sales_note",
            "staff_remark",
        ]


class PurchaseInvoiceSerializer(serializers.ModelSerializer):
    
    purchases = PurchaseSerializer(many=True)
    
    class Meta:
        model = PurchaseInvoice
        fields = ['id', 'purchases']
    
class SalesInvoiceSerializer(serializers.ModelSerializer):
    
    sales = SalesSerializer(many=True)
    
    class Meta:
        model = SalesInvoice
        fields = ['id', 'sales']
        
        
class AdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adjustment
        fields = ["id", "warehouse", "image"]


class AdjustmentItemsSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(write_only=True)

    class Meta:
        model = AdjustmentItems
        fields = ["id", "adjustment", "product", "quantity", "type"]

    def validate(self, data):
        product = data.get("product")
        type = data.get("type")
        quantity = data.pop("quantity")
        if type == "Subtraction" and product.stock_alert < quantity:
            raise serializers.ValidationError(
                {product.product_name: "Quantity is greater than stock"}
            )
        elif type == "Addition":
            product.stock_alert += int(quantity)
        else:
            product.stock_alert -= int(quantity)
        product.save()

        return data



