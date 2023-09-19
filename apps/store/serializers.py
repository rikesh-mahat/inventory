from rest_framework import serializers
from apps.store.models import Warehouse
# from apps.accounts.serializers import UserSerializer

class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ('id',
                    'name',
                  'phone',
                  'email',
                  'country',
                  'city')
    
