from django.db import models
from django.contrib.auth import get_user_model
from bmr.models import BMR
from products.models import Product

User = get_user_model()

class FGSInventory(models.Model):
    """Track products in Finished Goods Store"""
    
    STATUS_CHOICES = [
        ('stored', 'Stored'),
        ('available', 'Available for Sale'),
        ('reserved', 'Reserved'),
        ('released', 'Released/Sold'),
        ('recalled', 'Recalled'),
    ]
    
    bmr = models.OneToOneField(BMR, on_delete=models.CASCADE, related_name='fgs_inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    batch_number = models.CharField(max_length=50)
    quantity_available = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Quality details
    release_certificate_number = models.CharField(max_length=50, blank=True)
    qa_approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='qa_approved_inventory'
    )
    qa_approval_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='stored')
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def quantity_produced(self):
        """Get quantity from BMR batch size"""
        return self.bmr.batch_size
    
    @property
    def unit_of_measure(self):
        """Get unit from BMR batch size unit"""
        return self.bmr.batch_size_unit
    
    def __str__(self):
        return f"{self.batch_number} - {self.product.product_name} ({self.quantity_available} {self.unit_of_measure})"
    
    @property
    def quantity_released(self):
        """Calculate total quantity released/sold"""
        return self.releases.aggregate(
            total=models.Sum('quantity_released')
        )['total'] or 0
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'FGS Inventory'
        verbose_name_plural = 'FGS Inventory'

class ProductRelease(models.Model):
    """Track product releases/sales from FGS"""
    
    RELEASE_TYPE_CHOICES = [
        ('sale', 'Sale'),
        ('transfer', 'Transfer'),
        ('donation', 'Donation'),
        ('destruction', 'Destruction'),
        ('return', 'Return'),
    ]
    
    inventory = models.ForeignKey(FGSInventory, on_delete=models.CASCADE, related_name='releases')
    release_type = models.CharField(max_length=20, choices=RELEASE_TYPE_CHOICES, default='sale')
    
    # Release details
    quantity_released = models.DecimalField(max_digits=10, decimal_places=2)
    release_date = models.DateTimeField(auto_now_add=True)
    release_reference = models.CharField(max_length=100)  # Invoice/DO number
    
    # Customer/Recipient details
    customer_name = models.CharField(max_length=200, blank=True)
    customer_contact = models.CharField(max_length=100, blank=True)
    delivery_address = models.TextField(blank=True)
    
    # Financial details (optional)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Authorization
    authorized_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='authorized_releases'
    )
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        from decimal import Decimal
        
        # Calculate total value if unit price is provided
        if self.unit_price:
            self.total_value = self.quantity_released * self.unit_price
        
        # Update inventory available quantity
        if self.pk:
            # If updating existing release, revert old quantity first
            old_release = ProductRelease.objects.get(pk=self.pk)
            self.inventory.quantity_available += old_release.quantity_released
        
        # Subtract new quantity - ensure both are Decimal
        self.inventory.quantity_available -= Decimal(str(self.quantity_released))
        self.inventory.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.release_reference} - {self.inventory.batch_number} ({self.quantity_released} units)"
    
    class Meta:
        ordering = ['-release_date']

class FGSAlert(models.Model):
    """Alerts for FGS management"""
    
    ALERT_TYPE_CHOICES = [
        ('expiry_warning', 'Expiry Warning'),
        ('low_stock', 'Low Stock'),
        ('quality_issue', 'Quality Issue'),
        ('system', 'System Alert'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Related objects
    inventory = models.ForeignKey(FGSInventory, on_delete=models.CASCADE, null=True, blank=True)
    
    # Alert details
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_priority_display()} - {self.title}"
    
    class Meta:
        ordering = ['-created_at', 'priority']
