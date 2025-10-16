from django.db import models
from django.conf import settings
from bmr.models import BMR

class Machine(models.Model):
    """Machine model for production phases"""
    
    MACHINE_TYPE_CHOICES = [
        ('granulation', 'Granulation'),
        ('blending', 'Blending'),
        ('compression', 'Compression'),
        ('coating', 'Coating'),
        ('blister_packing', 'Blister Packing'),
        ('filling', 'Filling'),  # For capsules
    ]
    
    name = models.CharField(max_length=100)
    machine_type = models.CharField(max_length=20, choices=MACHINE_TYPE_CHOICES)
    is_active = models.BooleanField(default=True, help_text="Active machines are available for selection")
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['machine_type', 'name']
        unique_together = ['name', 'machine_type']
    
    def __str__(self):
        return f"{self.name} ({self.get_machine_type_display()})"

class ProductionPhase(models.Model):
    """Defines the production phases for different product types"""
    
    PHASE_CHOICES = [
        # Common phases
        ('bmr_creation', 'BMR Creation'),
        ('regulatory_approval', 'Regulatory Approval'),
        ('material_dispensing', 'Material Dispensing'),
        ('quality_control', 'Quality Control'),
        ('post_compression_qc', 'Post-Compression QC'),
        ('post_mixing_qc', 'Post-Mixing QC'),
        ('post_blending_qc', 'Post-Blending QC'),
        ('packaging_material_release', 'Packaging Material Release'),
        ('secondary_packaging', 'Secondary Packaging'),
        ('final_qa', 'Final QA'),
        ('finished_goods_store', 'Finished Goods Store'),
        
        # Ointment specific phases
        ('mixing', 'Mixing'),
        ('tube_filling', 'Tube Filling'),
        
        # Tablet specific phases
        ('granulation', 'Granulation'),
        ('blending', 'Blending'),
        ('compression', 'Compression'),
        ('sorting', 'Sorting'),
        ('coating', 'Coating'),
        ('blister_packing', 'Blister Packing'),
        ('bulk_packing', 'Bulk Packing'),
        
        # Capsule specific phases
        ('drying', 'Drying'),
        ('filling', 'Filling'),
    ]
    
    PRODUCT_TYPE_CHOICES = [
        ('ointment', 'Ointment'),
        ('tablet_normal', 'Tablet Normal'),
        ('tablet_2', 'Tablet 2'),
        ('capsule', 'Capsule'),
    ]
    
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    phase_name = models.CharField(max_length=30, choices=PHASE_CHOICES)
    phase_order = models.IntegerField()
    is_mandatory = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    can_rollback_to = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Phase to rollback to if this phase fails"
    )
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['product_type', 'phase_name']
        ordering = ['product_type', 'phase_order']
    
    def __str__(self):
        return f"{self.get_product_type_display()} - {self.get_phase_name_display()}"

class BatchPhaseExecution(models.Model):
    """Tracks the execution of phases for each batch"""
    
    STATUS_CHOICES = [
        ('not_ready', 'Not Ready'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
        ('rolled_back', 'Rolled Back'),
    ]
    
    bmr = models.ForeignKey(BMR, on_delete=models.CASCADE, related_name='phase_executions')
    phase = models.ForeignKey(ProductionPhase, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Execution tracking
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='started_phases'
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='completed_phases'
    )
    
    # Timestamps
    created_date = models.DateTimeField(auto_now_add=True)
    started_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Phase specific data
    phase_data = models.JSONField(default=dict, blank=True)
    operator_comments = models.TextField(blank=True)
    qa_comments = models.TextField(blank=True)
    
    # Machine tracking
    machine_used = models.ForeignKey('Machine', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Breakdown tracking
    breakdown_occurred = models.BooleanField(default=False)
    breakdown_start_time = models.DateTimeField(null=True, blank=True)
    breakdown_end_time = models.DateTimeField(null=True, blank=True)
    breakdown_reason = models.TextField(blank=True)
    
    # Changeover tracking
    changeover_occurred = models.BooleanField(default=False)
    changeover_start_time = models.DateTimeField(null=True, blank=True)
    changeover_end_time = models.DateTimeField(null=True, blank=True)
    changeover_reason = models.TextField(blank=True)
    
    # Quality control
    qc_approved = models.BooleanField(null=True, blank=True)
    qc_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='qc_approved_phases'
    )
    qc_approval_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['bmr', 'phase']
        ordering = ['bmr', 'phase__phase_order']
    
    def __str__(self):
        return f"{self.bmr.batch_number} - {self.phase.get_phase_name_display()} ({self.status})"
    
    def requires_machine_selection(self):
        """Check if this phase requires machine selection"""
        machine_required_phases = [
            'granulation', 'blending', 'compression', 
            'coating', 'blister_packing', 'filling'
        ]
        return self.phase.phase_name in machine_required_phases
    
    def get_breakdown_duration(self):
        """Calculate breakdown duration in minutes"""
        if self.breakdown_occurred and self.breakdown_start_time and self.breakdown_end_time:
            delta = self.breakdown_end_time - self.breakdown_start_time
            return delta.total_seconds() / 60
        return 0
    
    def get_changeover_duration(self):
        """Calculate changeover duration in minutes"""
        if self.changeover_occurred and self.changeover_start_time and self.changeover_end_time:
            delta = self.changeover_end_time - self.changeover_start_time
            return delta.total_seconds() / 60
        return 0
    
    @property
    def breakdown_duration_minutes(self):
        """Property for template use - breakdown duration in minutes"""
        return round(self.get_breakdown_duration(), 1) if self.get_breakdown_duration() > 0 else None
    
    @property
    def changeover_duration_minutes(self):
        """Property for template use - changeover duration in minutes"""
        return round(self.get_changeover_duration(), 1) if self.get_changeover_duration() > 0 else None
        
    def get_phase_duration_hours(self):
        """Calculate the duration of this phase execution in hours"""
        if self.started_date and self.completed_date:
            duration = self.completed_date - self.started_date
            return round(duration.total_seconds() / 3600, 2)
        return None
        
    @property
    def duration_hours(self):
        """Property for template use - phase duration in hours"""
        return self.get_phase_duration_hours()
        
    @property
    def formatted_duration(self):
        """Return a formatted string representation of the phase duration"""
        hours = self.get_phase_duration_hours()
        if hours is not None:
            h = int(hours)
            m = int((hours - h) * 60)
            if h > 0:
                return f"{h}h {m}m"
            else:
                return f"{m}m"
        return "--"
    
    def get_next_phase(self):
        """Get the next phase in the workflow"""
        product_type = self.bmr.product.product_type
        current_order = self.phase.phase_order
        # Handle special cases for tablet coating
        if (product_type in ['tablet_normal', 'tablet_2'] and 
            self.phase.phase_name == 'sorting'):
            if self.bmr.product.is_coated:
                # Go to coating phase
                next_phase = ProductionPhase.objects.filter(
                    product_type=product_type,
                    phase_name='coating'
                ).first()
            else:
                # Skip coating, go to packaging
                next_phase = ProductionPhase.objects.filter(
                    product_type=product_type,
                    phase_name='packaging_material_release'
                ).first()
        else:
            # Normal sequential flow
            next_phase = ProductionPhase.objects.filter(
                product_type=product_type,
                phase_order__gt=current_order
            ).first()
        return next_phase
    
    def trigger_next_phase(self):
        """Automatically trigger the next phase when current phase completes"""
        if self.status == 'completed':
            next_phase = self.get_next_phase()
            if next_phase:
                BatchPhaseExecution.objects.get_or_create(
                    bmr=self.bmr,
                    phase=next_phase,
                    defaults={'status': 'pending'}
                )

class PhaseOperator(models.Model):
    """Maps operators to specific phases they can handle"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phase = models.ForeignKey(ProductionPhase, on_delete=models.CASCADE)
    is_primary_operator = models.BooleanField(default=False)
    can_approve = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'phase']
    
    def __str__(self):
        return f"{self.user.username} - {self.phase.get_phase_name_display()}"

class PhaseCheckpoint(models.Model):
    """Quality checkpoints within phases"""
    
    phase_execution = models.ForeignKey(
        BatchPhaseExecution, 
        on_delete=models.CASCADE, 
        related_name='checkpoints'
    )
    checkpoint_name = models.CharField(max_length=200)
    expected_value = models.CharField(max_length=200)
    actual_value = models.CharField(max_length=200, blank=True)
    is_within_spec = models.BooleanField(null=True, blank=True)
    checked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    checked_date = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.phase_execution} - {self.checkpoint_name}"
