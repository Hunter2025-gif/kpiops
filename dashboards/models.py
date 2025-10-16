from django.db import models
from django.conf import settings
from bmr.models import BMR
from workflow.models import BatchPhaseExecution

class DashboardMetrics(models.Model):
    """Dashboard metrics and KPIs for different user roles"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    # General metrics
    active_batches = models.IntegerField(default=0)
    completed_phases_today = models.IntegerField(default=0)
    pending_phases = models.IntegerField(default=0)
    rejected_phases_today = models.IntegerField(default=0)
    
    # Role-specific metrics stored as JSON
    role_specific_data = models.JSONField(default=dict)
    
    class Meta:
        unique_together = ['user', 'date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"

class NotificationAlert(models.Model):
    """System notifications and alerts for users"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('phase_assigned', 'Phase Assigned'),
        ('phase_completed', 'Phase Completed'),
        ('phase_rejected', 'Phase Rejected'),
        ('bmr_approved', 'BMR Approved'),
        ('quality_alert', 'Quality Alert'),
        ('deadline_approaching', 'Deadline Approaching'),
        ('system_maintenance', 'System Maintenance'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    bmr = models.ForeignKey(BMR, on_delete=models.CASCADE, null=True, blank=True)
    phase_execution = models.ForeignKey(
        BatchPhaseExecution, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    
    # Status
    is_read = models.BooleanField(default=False)
    is_acknowledged = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    read_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"

class UserDashboardPreferences(models.Model):
    """User preferences for dashboard customization"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='dashboard_preferences'
    )
    
    # Layout preferences
    show_metrics_summary = models.BooleanField(default=True)
    show_recent_activities = models.BooleanField(default=True)
    show_pending_tasks = models.BooleanField(default=True)
    show_notifications = models.BooleanField(default=True)
    
    # Data refresh preferences
    auto_refresh_enabled = models.BooleanField(default=True)
    refresh_interval_seconds = models.IntegerField(default=30)
    
    # Custom dashboard layout stored as JSON
    layout_config = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Dashboard preferences for {self.user.username}"
