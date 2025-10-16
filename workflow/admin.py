from django.contrib import admin
from .models import ProductionPhase, BatchPhaseExecution, Machine

@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ['name', 'machine_type', 'is_active', 'created_date']
    list_filter = ['machine_type', 'is_active', 'created_date']
    search_fields = ['name']
    ordering = ['machine_type', 'name']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'machine_type', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_date',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_date']

@admin.register(ProductionPhase)
class ProductionPhaseAdmin(admin.ModelAdmin):
    list_display = ['phase_name', 'product_type', 'phase_order', 'is_mandatory', 'requires_approval']
    list_filter = ['product_type', 'is_mandatory', 'requires_approval']
    search_fields = ['phase_name', 'description']
    ordering = ['product_type', 'phase_order']

@admin.register(BatchPhaseExecution)
class BatchPhaseExecutionAdmin(admin.ModelAdmin):
    list_display = ['bmr', 'phase', 'status', 'machine_used', 'started_by', 'completed_by', 'started_date', 'completed_date']
    list_filter = ['status', 'phase__product_type', 'phase__phase_name', 'machine_used', 'breakdown_occurred', 'changeover_occurred', 'started_date', 'completed_date']
    search_fields = ['bmr__batch_number', 'phase__phase_name', 'operator_comments', 'machine_used__name']
    readonly_fields = ['created_date']
    ordering = ['-started_date']
    
    fieldsets = (
        (None, {
            'fields': ('bmr', 'phase', 'status', 'machine_used')
        }),
        ('Execution Details', {
            'fields': ('started_by', 'completed_by', 'started_date', 'completed_date', 'created_date')
        }),
        ('Comments', {
            'fields': ('operator_comments', 'qa_comments')
        }),
        ('Breakdown Information', {
            'fields': ('breakdown_occurred', 'breakdown_start_time', 'breakdown_end_time'),
            'classes': ('collapse',)
        }),
        ('Changeover Information', {
            'fields': ('changeover_occurred', 'changeover_start_time', 'changeover_end_time'),
            'classes': ('collapse',)
        }),
        ('Quality Control', {
            'fields': ('qc_approved', 'qc_approved_by', 'qc_approval_date', 'rejection_reason'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bmr', 'phase', 'started_by', 'completed_by', 'machine_used')
