from django.contrib import admin
from .models import BMR, BMRMaterial, BMRSignature, BMRRequest

@admin.register(BMR)
class BMRAdmin(admin.ModelAdmin):
    list_display = [
        'bmr_number', 'batch_number', 'product', 'status', 
        'created_by', 'created_date', 'get_batch_size'
    ]
    list_filter = ['status', 'product__product_type', 'created_date']
    search_fields = ['bmr_number', 'batch_number', 'product__product_name']
    readonly_fields = ['bmr_number', 'created_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('product', 'batch_number', 'bmr_number', 'actual_batch_size', 'actual_batch_size_unit'),
            'description': 'Enter batch number manually in format XXXYYYY (e.g., 0012025)'
        }),
        ('Dates', {
            'fields': ('created_date', 'planned_start_date', 'planned_completion_date', 
                      'actual_start_date', 'actual_completion_date')
        }),
        ('Status & Approval', {
            'fields': ('status', 'created_by', 'approved_by', 'approved_date')
        }),
        ('Instructions', {
            'fields': ('manufacturing_instructions', 'special_instructions', 
                      'in_process_controls', 'quality_checks_required')
        }),
        ('Comments', {
            'fields': ('qa_comments', 'regulatory_comments')
        }),
    )
    
    def get_batch_size(self, obj):
        return f"{obj.batch_size} {obj.batch_size_unit}"
    get_batch_size.short_description = "Batch Size"

@admin.register(BMRMaterial)
class BMRMaterialAdmin(admin.ModelAdmin):
    list_display = [
        'bmr', 'material_name', 'material_code', 'required_quantity', 
        'unit_of_measure', 'is_dispensed'
    ]
    list_filter = ['is_dispensed', 'unit_of_measure']
    search_fields = ['material_name', 'material_code', 'bmr__batch_number']

@admin.register(BMRSignature)
class BMRSignatureAdmin(admin.ModelAdmin):
    list_display = ['bmr', 'signature_type', 'signed_by', 'signed_date']
    list_filter = ['signature_type', 'signed_date']
    search_fields = ['bmr__batch_number', 'signed_by__username']

@admin.register(BMRRequest)
class BMRRequestAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'requested_by', 'request_date', 'required_date', 
        'status', 'priority', 'approved_by'
    ]
    list_filter = ['status', 'priority', 'request_date', 'required_date']
    search_fields = ['product__product_name', 'requested_by__username', 'reason']
    readonly_fields = ['request_date']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('product', 'requested_by', 'request_date', 'required_date', 'quantity_required', 'quantity_unit')
        }),
        ('Request Details', {
            'fields': ('priority', 'reason', 'status')
        }),
        ('Approval Information', {
            'fields': ('approved_by', 'bmr')
        }),
    )
