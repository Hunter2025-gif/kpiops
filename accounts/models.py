from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """Custom user model for pharmaceutical system with role-based access"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('qa', 'Quality Assurance'),
        ('regulatory', 'Regulatory'),
        ('production_manager', 'Production Manager'),  # New role for BMR requests
        ('store_manager', 'Store Manager'),  # Now handles raw material release to dispensing
        ('dispensing_manager', 'Dispensing Manager'),  # Renamed from store_manager
        ('packaging_store', 'Packaging Store'),
        ('finished_goods_store', 'Finished Goods Store'),
        ('qc', 'Quality Control'),
        ('quarantine', 'Quarantine Manager'),  # Manages batches in quarantine
        # Production Operators - matching your described phases
        ('mixing_operator', 'Mixing Operator'),
        ('tube_filling_operator', 'Tube Filling Operator'),
        ('granulation_operator', 'Granulation Operator'),
        ('blending_operator', 'Blending Operator'),
        ('compression_operator', 'Compression Operator'),
        ('coating_operator', 'Coating Operator'),
        ('drying_operator', 'Drying Operator'),
        ('filling_operator', 'Filling Operator'),
        ('sorting_operator', 'Sorting Operator'),
        # Single packing operator for all packing operations (blister, bulk, secondary)
        ('packing_operator', 'Packing Operator'),
        # Additional operators
        ('dispensing_operator', 'Dispensing Operator'),
        ('equipment_operator', 'Equipment Operator'),
        ('cleaning_operator', 'Cleaning Operator'),
    ]
    
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)
    is_active_operator = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

class UserSession(models.Model):
    """Track user login sessions for audit purposes"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
    
    class Meta:
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
