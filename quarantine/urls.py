from django.urls import path
from . import views

app_name = 'quarantine'

urlpatterns = [
    # Quarantine Dashboard
    path('', views.quarantine_dashboard, name='dashboard'),
    path('details/<int:quarantine_id>/', views.quarantine_details, name='details'),
    path('request-sample/<int:quarantine_id>/', views.request_sample, name='request_sample'),
    path('proceed/<int:quarantine_id>/', views.proceed_to_next_phase, name='proceed_to_next_phase'),
    
    # QA Dashboard
    path('qa/', views.qa_dashboard, name='qa_dashboard'),
    path('qa/process-sample/<int:sample_id>/', views.process_qa_sample, name='process_qa_sample'),
    
    # QC Dashboard
    path('qc/', views.qc_dashboard, name='qc_dashboard'),
    path('qc/receive-sample/<int:sample_id>/', views.receive_qc_sample, name='receive_qc_sample'),
    path('qc/approve-sample/<int:sample_id>/', views.approve_qc_sample, name='approve_qc_sample'),
    path('qc/fail-sample/<int:sample_id>/', views.fail_qc_sample, name='fail_qc_sample'),
    path('qc/approve-reject/<int:sample_id>/', views.approve_reject_sample, name='approve_reject_sample'),
]