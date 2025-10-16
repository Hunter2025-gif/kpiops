from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')

urlpatterns = [
    # Product URLs will be added here
] + router.urls
