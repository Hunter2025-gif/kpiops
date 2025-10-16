from django.urls import path
from . import views
from django.views.generic.base import RedirectView

app_name = 'dashboards'

urlpatterns = [
    path('export-wip/', views.export_wip, name='export_wip'),
    path('', views.dashboard_home, name='dashboard_home'),
    
    # QA Dashboard
    path('qa/', views.qa_dashboard, name='qa_dashboard'),
    
    # Regulatory Dashboard
    path('regulatory/', views.regulatory_dashboard, name='regulatory_dashboard'),
    
    # Production Manager Dashboard
    path('production-manager/', views.production_manager_dashboard, name='production_manager_dashboard'),
    
    # Store Manager Dashboard (Raw Material Release)
    path('store/', views.store_dashboard, name='store_dashboard'),
    
    # Generic Operator Dashboard
    path('operator/', views.operator_dashboard, name='operator_dashboard'),
    
    # Production Operator Dashboards
    path('mixing/', views.mixing_dashboard, name='mixing_dashboard'),
    path('granulation/', views.granulation_dashboard, name='granulation_dashboard'),
    path('blending/', views.blending_dashboard, name='blending_dashboard'),
    path('compression/', views.compression_dashboard, name='compression_dashboard'),
    path('coating/', views.coating_dashboard, name='coating_dashboard'),
    path('drying/', views.drying_dashboard, name='drying_dashboard'),
    path('filling/', views.filling_dashboard, name='filling_dashboard'),
    path('tube-filling/', views.tube_filling_dashboard, name='tube_filling_dashboard'),
    path('sorting/', views.sorting_dashboard, name='sorting_dashboard'),
    
    # Quality Control Dashboard
    path('qc/', views.qc_dashboard, name='qc_dashboard'),
    
    # Packaging Dashboards
    path('packaging/', views.packaging_dashboard, name='packaging_dashboard'),
    path('packing/', views.packing_dashboard, name='packing_dashboard'),
    path('finished-goods/', views.finished_goods_dashboard, name='finished_goods_dashboard'),
    
    # Admin Dashboard
        # Redirect for old URL pattern
    path('admin/', views.admin_redirect, name='admin_redirect'),
    path('admin-overview/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/timeline/', views.admin_timeline_view, name='admin_timeline'),
    path('admin/fgs-monitor/', views.admin_fgs_monitor, name='admin_fgs_monitor'),
    path('admin/quarantine-monitor/', views.quarantine_monitor_view, name='quarantine_monitor'),
    path('admin/export-timeline/', views.export_timeline_data, name='export_timeline_data'),
    path('admin/live-tracking/', views.live_tracking_view, name='live_tracking'),
    path('export-wip/', views.export_wip, name='export_wip'),
    
    # Admin section routes for direct URL links
    path('machine-management/', views.admin_machine_management, name='machine_management'),
    path('quality-control/', views.admin_quality_control, name='quality_control'),
    path('inventory/', views.admin_inventory, name='inventory'),
    path('user-management/', views.admin_user_management, name='user_management'),
    path('system-health/', views.admin_system_health, name='system_health'),
    path('export-wip/', views.export_wip, name='export_wip'),
]
