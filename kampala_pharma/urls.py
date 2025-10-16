"""
URL configuration for kampala_pharma project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from dashboards.views import dashboard_home

urlpatterns = [
    path('', dashboard_home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('bmr/', include('bmr.urls', namespace='bmr')),
    path('dashboard/', include('dashboards.urls', namespace='dashboards')),
    path('quarantine/', include('quarantine.urls', namespace='quarantine')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('fgs/', include('fgs_management.urls', namespace='fgs_management')),
    # API URLs
    path('api/bmr/', include('bmr.urls', namespace='bmr_api')),
    path('api/', include('products.urls')),
    # path('api/', include('workflow.urls')),
    # path('api/', include('dashboards.urls')),
    # path('api/', include('products.urls')),
]
