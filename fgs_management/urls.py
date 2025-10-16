from django.urls import path
from . import views

app_name = 'fgs_management'

urlpatterns = [
    path('dashboard/', views.fgs_dashboard, name='dashboard'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('releases/', views.release_list, name='release_list'),
    path('inventory/<int:inventory_id>/release/', views.create_release, name='create_release'),
    path('analytics/', views.inventory_analytics, name='analytics'),
    
    # New release functionality
    path('create-inventory/<int:phase_id>/', views.create_inventory_from_fgs, name='create_inventory'),
    path('quick-release/<int:inventory_id>/', views.quick_release, name='quick_release'),
]
