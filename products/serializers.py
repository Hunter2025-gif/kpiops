from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product details"""
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_code', 'product_name', 'product_type', 
            'dosage_form', 'strength', 'pack_size', 'is_coated',
            'standard_batch_size', 'batch_size_unit',
            'tablet_subtype', 'manufacturing_method', 'storage_conditions',
            'shelf_life_months'
        ]
        read_only_fields = ['id']