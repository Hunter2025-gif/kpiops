from django.db import models
from django.conf import settings
from bmr.models import BMR
from workflow.models import ProductionPhase
from django.utils import timezone

class QuarantineBatch(models.Model):
    """Tracks batches in quarantine after phase completion"""
    
    STATUS_CHOICES = [
        ('quarantined', 'In Quarantine'),
        ('sample_requested', 'Sample Requested'),
        ('sample_in_qa', 'Sample with QA'),
        ('sample_in_qc', 'Sample with QC'),
        ('sample_approved', 'Sample Approved'),
        ('sample_failed', 'Sample Failed'),
        ('released', 'Released to Next Phase'),
    ]
    
    bmr = models.ForeignKey(BMR, on_delete=models.CASCADE, related_name='quarantine_batches')
    current_phase = models.ForeignKey(ProductionPhase, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='quarantined')
    quarantine_date = models.DateTimeField(auto_now_add=True)
    released_date = models.DateTimeField(null=True, blank=True)
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='released_quarantine_batches'
    )
    sample_count = models.PositiveSmallIntegerField(default=0)  # Track number of samples requested
    
    class Meta:
        ordering = ['-quarantine_date']
        unique_together = ['bmr', 'current_phase']  # One quarantine record per BMR-phase
    
    def __str__(self):
        return f"{self.bmr.batch_number} - {self.current_phase.phase_name} (Quarantine)"
    
    @property
    def can_request_sample(self):
        """Check if can request another sample (max 2 samples)"""
        return self.sample_count < 2 and self.status in ['quarantined', 'sample_failed']
    
    @property
    def can_proceed_to_next_phase(self):
        """Check if can proceed to next phase"""
        return self.status in ['quarantined', 'sample_approved']
    
    @property
    def quarantine_duration_hours(self):
        """Calculate time spent in quarantine"""
        end_time = self.released_date or timezone.now()
        duration = end_time - self.quarantine_date
        return round(duration.total_seconds() / 3600, 1)


class SampleRequest(models.Model):
    """Tracks sample requests and their progress through QA and QC"""
    
    QC_STATUS_CHOICES = [
        ('pending', 'Pending QC Review'),
        ('approved', 'Approved'),
        ('failed', 'Failed'),
    ]
    
    quarantine_batch = models.ForeignKey(
        QuarantineBatch, 
        on_delete=models.CASCADE, 
        related_name='sample_requests'
    )
    sample_number = models.PositiveSmallIntegerField()  # 1 or 2
    
    # Request stage
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='requested_samples'
    )
    request_date = models.DateTimeField(auto_now_add=True)
    
    # QA stage
    sampled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sampled_batches'
    )
    sample_date = models.DateTimeField(null=True, blank=True)
    qa_comments = models.TextField(blank=True)
    
    # QC stage
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='received_samples'
    )
    received_date = models.DateTimeField(null=True, blank=True)
    qc_status = models.CharField(max_length=10, choices=QC_STATUS_CHOICES, default='pending')
    qc_comments = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_samples'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-request_date']
        unique_together = ['quarantine_batch', 'sample_number']  # Ensure unique sample numbers per batch
    
    def __str__(self):
        return f"{self.quarantine_batch.bmr.batch_number} - Sample {self.sample_number}"
    
    @property
    def total_turnaround_time_hours(self):
        """Calculate total time from request to QC decision"""
        if self.approved_date:
            duration = self.approved_date - self.request_date
            return round(duration.total_seconds() / 3600, 1)
        return None
    
    @property
    def qa_processing_time_hours(self):
        """Calculate time QA took to process sample"""
        if self.sample_date and self.request_date:
            duration = self.sample_date - self.request_date
            return round(duration.total_seconds() / 3600, 1)
        return None
    
    @property
    def qc_processing_time_hours(self):
        """Calculate time QC took to process sample"""
        if self.approved_date and self.received_date:
            duration = self.approved_date - self.received_date
            return round(duration.total_seconds() / 3600, 1)
        return None
    
    @property
    def wait_time_hours(self):
        """Calculate time waiting for QA processing"""
        if not self.sample_date:
            duration = timezone.now() - self.request_date
            return round(duration.total_seconds() / 3600, 1)
        return None
    
    @property
    def qc_wait_time_hours(self):
        """Calculate time waiting for QC testing"""
        if self.sample_date and not self.received_date:
            duration = timezone.now() - self.sample_date
            return round(duration.total_seconds() / 3600, 1)
        return None
    
    @property
    def is_urgent(self):
        """Check if sample is urgent (waiting > 24 hours)"""
        wait_time = self.wait_time_hours or self.qc_wait_time_hours
        return wait_time and wait_time > 24
    
    def update_qa_stage(self, user, comments=""):
        """Update when QA processes the sample"""
        self.sampled_by = user
        self.sample_date = timezone.now()
        self.qa_comments = comments
        self.save()
        
        # Update quarantine batch status
        self.quarantine_batch.status = 'sample_in_qc'
        self.quarantine_batch.save()
    
    def update_qc_received(self, user):
        """Update when QC receives the sample"""
        self.received_by = user
        self.received_date = timezone.now()
        self.save()
        
        # Update quarantine batch status
        self.quarantine_batch.status = 'sample_in_qc'
        self.quarantine_batch.save()
    
    def update_qc_decision(self, user, status, comments=""):
        """Update QC decision"""
        self.approved_by = user
        self.approved_date = timezone.now()
        self.qc_status = status
        self.qc_comments = comments
        self.save()
        
        # Update quarantine batch status based on decision
        if status == 'approved':
            self.quarantine_batch.status = 'sample_approved'
        elif status == 'failed':
            self.quarantine_batch.status = 'sample_failed'
        
        self.quarantine_batch.save()