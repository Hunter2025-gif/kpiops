from django.contrib import admin
from .models import QuarantineBatch, SampleRequest

@admin.register(QuarantineBatch)
class QuarantineBatchAdmin(admin.ModelAdmin):
    list_display = ['bmr', 'current_phase', 'status', 'quarantine_date', 'sample_count']
    list_filter = ['status', 'current_phase', 'quarantine_date']
    search_fields = ['bmr__batch_number', 'bmr__product__product_name']
    readonly_fields = ['quarantine_date', 'quarantine_duration_hours']

@admin.register(SampleRequest)
class SampleRequestAdmin(admin.ModelAdmin):
    list_display = ['quarantine_batch', 'sample_number', 'qc_status', 'request_date', 'approved_date']
    list_filter = ['qc_status', 'request_date', 'approved_date']
    search_fields = ['quarantine_batch__bmr__batch_number']
    readonly_fields = ['request_date', 'sample_date', 'received_date', 'approved_date']