from django.contrib import admin
from .models import FGSInventory, ProductRelease, FGSAlert

@admin.register(FGSInventory)
class FGSInventoryAdmin(admin.ModelAdmin):
    list_display = [
        'batch_number', 'product', 'quantity_available', 'status', 
        'created_at'
    ]
    list_filter = ['status', 'product', 'created_at']
    search_fields = ['batch_number', 'product__product_name']
    readonly_fields = ['created_at', 'updated_at', 'quantity_produced', 'unit_of_measure']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('bmr', 'product', 'batch_number')
        }),
        ('Quantity Details', {
            'fields': ('quantity_produced', 'quantity_available', 'unit_of_measure')
        }),
        ('Status & Quality', {
            'fields': ('status', 'release_certificate_number', 'qa_approved_by', 'qa_approval_date')
        }),
        ('Tracking', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductRelease)
class ProductReleaseAdmin(admin.ModelAdmin):
    list_display = [
        'release_reference', 'inventory', 'release_type', 'quantity_released',
        'customer_name', 'release_date', 'total_value'
    ]
    list_filter = ['release_type', 'release_date', 'inventory__product']
    search_fields = ['release_reference', 'customer_name', 'inventory__batch_number']
    readonly_fields = ['release_date', 'total_value']
    
    fieldsets = (
        ('Release Information', {
            'fields': ('inventory', 'release_type', 'quantity_released', 'release_reference')
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_contact', 'delivery_address')
        }),
        ('Financial Information', {
            'fields': ('unit_price', 'total_value')
        }),
        ('Authorization', {
            'fields': ('authorized_by', 'created_by', 'notes')
        }),
    )

@admin.register(FGSAlert)
class FGSAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'alert_type', 'priority', 'inventory', 'is_resolved', 'created_at']
    list_filter = ['alert_type', 'priority', 'is_resolved', 'created_at']
    search_fields = ['title', 'message', 'inventory__batch_number']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'priority', 'title', 'message')
        }),
        ('Related Data', {
            'fields': ('inventory',)
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_by', 'resolved_at')
        }),
    )
