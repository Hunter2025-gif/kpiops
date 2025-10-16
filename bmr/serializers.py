from rest_framework import serializers
from .models import BMR, BMRMaterial, BMRSignature
from products.models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product details when creating BMR"""
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_code', 'product_name', 'product_type', 
            'dosage_form', 'strength', 'pack_size', 'is_coated',
            'tablet_subtype', 'manufacturing_method', 'storage_conditions',
            'shelf_life_months', 'standard_batch_size', 'batch_size_unit'
        ]
        read_only_fields = ['id']

class BMRMaterialSerializer(serializers.ModelSerializer):
    """Serializer for BMR materials"""
    
    class Meta:
        model = BMRMaterial
        fields = [
            'id', 'material_name', 'material_code', 'required_quantity',
            'unit_of_measure', 'batch_lot_number', 'expiry_date', 'supplier',
            'dispensed_quantity', 'dispensed_by', 'dispensed_date', 'is_dispensed'
        ]
        read_only_fields = ['id', 'dispensed_by', 'dispensed_date']

class BMRSignatureSerializer(serializers.ModelSerializer):
    """Serializer for BMR signatures"""
    signed_by_name = serializers.CharField(source='signed_by.get_full_name', read_only=True)
    signed_by_role = serializers.CharField(source='signed_by.role', read_only=True)
    
    class Meta:
        model = BMRSignature
        fields = [
            'id', 'signature_type', 'signed_by', 'signed_by_name', 
            'signed_by_role', 'signed_date', 'comments'
        ]
        read_only_fields = ['id', 'signed_by', 'signed_date']

class BMRCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new BMR"""
    materials = BMRMaterialSerializer(many=True, required=False)
    
    class Meta:
        model = BMR
        fields = [
            'product', 'batch_number', 'batch_size', 'batch_size_unit', 
            'planned_start_date', 'planned_completion_date', 'manufacturing_instructions',
            'special_instructions', 'in_process_controls', 
            'quality_checks_required', 'materials'
        ]
    
    def validate_batch_number(self, value):
        """Validate batch number format and uniqueness"""
        import re
        pattern = r'^\d{7}$'  # 7 digits total (e.g., 0012025)
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                'Batch number must be in format XXXYYYY (e.g., 0012025)'
            )
        return value
    
    def create(self, validated_data):
        materials_data = validated_data.pop('materials', [])
        bmr = BMR.objects.create(
            created_by=self.context['request'].user,
            **validated_data
        )
        
        # Create materials
        for material_data in materials_data:
            BMRMaterial.objects.create(bmr=bmr, **material_data)
        
        return bmr

class BMRDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for BMR with all related data"""
    product = ProductSerializer(read_only=True)
    materials = BMRMaterialSerializer(many=True, read_only=True)
    signatures = BMRSignatureSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = BMR
        fields = [
            'id', 'bmr_number', 'batch_number', 'product', 'batch_size',
            'batch_size_unit', 'created_date', 'planned_start_date',
            'planned_completion_date', 'actual_start_date', 'actual_completion_date',
            'status', 'created_by', 'created_by_name', 'approved_by', 
            'approved_by_name', 'approved_date', 'manufacturing_instructions',
            'special_instructions', 'in_process_controls', 'quality_checks_required',
            'qa_comments', 'regulatory_comments', 'materials', 'signatures'
        ]
        read_only_fields = [
            'id', 'bmr_number', 'batch_number', 'created_date', 'created_by',
            'approved_by', 'approved_date'
        ]

class BMRListSerializer(serializers.ModelSerializer):
    """Simple serializer for BMR list view"""
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = BMR
        fields = [
            'id', 'bmr_number', 'batch_number', 'product_name', 'product_code',
            'batch_size', 'status', 'created_date', 'planned_start_date',
            'created_by_name'
        ]
        read_only_fields = fields
