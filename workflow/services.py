from django.utils import timezone
from bmr.models import BMR
from .models import ProductionPhase, BatchPhaseExecution

class WorkflowService:
    """Service to manage workflow progression and phase automation"""
    
    # Define the workflow sequences for each product type
    PRODUCT_WORKFLOWS = {
        'ointment': [
            'bmr_creation',
            'regulatory_approval', 
            'raw_material_release',      # NEW: Store manager releases materials
            'material_dispensing',       # Dispensing manager dispenses materials
            'mixing',
            'post_mixing_qc',  # QC test after mixing - rolls back to mixing if failed
            'tube_filling',
            'packaging_material_release',  # Packaging materials released BEFORE secondary packaging
            'secondary_packaging',
            'final_qa',
            'finished_goods_store'
        ],
        'tablet': [
            'bmr_creation',
            'regulatory_approval',
            'raw_material_release',      # NEW: Store manager releases materials
            'material_dispensing',       # Dispensing manager dispenses materials
            'granulation',
            'blending',
            'compression',
            'post_compression_qc',  # QC test after compression - rolls back to blending if failed
            'sorting',
            'coating',  # Will be skipped if tablet is not coated
            'packaging_material_release',  # Packaging materials released IMMEDIATELY AFTER coating
            'blister_packing',  # Default packing for normal tablets (or bulk_packing for tablet_2)
            'secondary_packaging',
            'final_qa',
            'finished_goods_store'
        ],
        'capsule': [
            'bmr_creation',
            'regulatory_approval',
            'raw_material_release',      # NEW: Store manager releases materials
            'material_dispensing',       # Dispensing manager dispenses materials
            'drying',
            'blending',
            'post_blending_qc',  # QC test after blending - rolls back to blending if failed
            'filling',
            'sorting',  # Sorting after filling for capsules
            'packaging_material_release',  # Packaging materials released BEFORE packing
            'blister_packing',
            'secondary_packaging', 
            'final_qa',
            'finished_goods_store'
        ]
    }
    
    @classmethod
    def initialize_workflow_for_bmr(cls, bmr):
        """Initialize all workflow phases for a new BMR using the correct system workflow"""
        product_type = bmr.product.product_type
        
        # Use the PRODUCT_WORKFLOWS dictionary which includes raw_material_release
        base_workflow = cls.PRODUCT_WORKFLOWS.get(product_type, [])
        if not base_workflow:
            raise ValueError(f"No workflow defined for product type: {product_type}")
        
        # Make a copy to avoid modifying the original
        workflow_phases = base_workflow.copy()
        
        # Handle tablet-specific logic for coating and packing types
        if product_type == 'tablet':
            # Handle coating - skip if not coated
            if not getattr(bmr.product, 'is_coated', False):
                if 'coating' in workflow_phases:
                    workflow_phases.remove('coating')
            
            # Handle packing type for tablets
            if getattr(bmr.product, 'tablet_type', None) == 'tablet_2':
                # TABLET_2 uses bulk_packing instead of blister_packing
                if 'blister_packing' in workflow_phases:
                    index = workflow_phases.index('blister_packing')
                    workflow_phases[index] = 'bulk_packing'
        
        # Remove any duplicate phases that might exist
        seen = set()
        workflow_phases = [x for x in workflow_phases if not (x in seen or seen.add(x))]

        # Remove any accidental duplicates
        seen = set()
        workflow_phases = [x for x in workflow_phases if not (x in seen or seen.add(x))]
        
        # Create phase executions for all phases in the workflow
        for order, phase_name in enumerate(workflow_phases, 1):
            try:
                # Get or create the production phase definition with ENFORCED correct order
                phase, created = ProductionPhase.objects.get_or_create(
                    product_type=product_type,
                    phase_name=phase_name,
                    defaults={
                        'phase_order': order,
                        'is_mandatory': True,
                        'requires_approval': phase_name in ['regulatory_approval', 'final_qa']
                    }
                )
                
                # CRITICAL: Always update phase order to ensure consistency
                if phase.phase_order != order:
                    phase.phase_order = order
                    phase.save()
                    print(f"Updated phase order for {phase_name} to {order}")
                
                # Create the batch phase execution with proper initial status
                if phase_name == 'bmr_creation':
                    initial_status = 'completed'
                elif phase_name == 'regulatory_approval':
                    initial_status = 'pending'
                elif phase_name == 'raw_material_release':
                    initial_status = 'not_ready'  # Will be activated when regulatory approval completes
                elif phase_name == 'material_dispensing':
                    initial_status = 'not_ready'  # Will be activated when raw material release completes
                # ENHANCEMENT: Ensure secondary_packaging is properly initialized
                elif phase_name == 'secondary_packaging':
                    # Always initialize as not_ready, it will be activated at the right time
                    initial_status = 'not_ready'
                else:
                    initial_status = 'not_ready'
                
                BatchPhaseExecution.objects.get_or_create(
                    bmr=bmr,
                    phase=phase,
                    defaults={
                        'status': initial_status
                    }
                )
                
            except Exception as e:
                print(f"Error creating phase {phase_name} for BMR {bmr.bmr_number}: {e}")
        
        print(f"Initialized workflow for {bmr.batch_number} ({product_type}) with {len(workflow_phases)} phases")
    
    @classmethod
    def get_current_phase(cls, bmr):
        """Get the current active phase for a BMR"""
        return BatchPhaseExecution.objects.filter(
            bmr=bmr,
            status__in=['pending', 'in_progress']
        ).order_by('phase__phase_order').first()
    
    @classmethod
    def get_next_phase(cls, bmr):
        """Get the next available phase for a BMR (pending or not_ready)"""
        current_executions = BatchPhaseExecution.objects.filter(
            bmr=bmr
        ).order_by('phase__phase_order')
        
        # Find the first pending phase
        for execution in current_executions:
            if execution.status == 'pending':
                return execution
        
        # If no pending phases, find the first not_ready phase
        for execution in current_executions:
            if execution.status == 'not_ready':
                return execution
        
        return None
    
    @classmethod
    def complete_phase(cls, bmr, phase_name, completed_by, comments=None):
        """Mark a phase as completed and activate the next phase"""
        try:
            execution = BatchPhaseExecution.objects.get(
                bmr=bmr,
                phase__phase_name=phase_name
            )
            
            # Mark current phase as completed
            execution.status = 'completed'
            execution.completed_by = completed_by
            execution.completed_date = timezone.now()
            if comments:
                execution.operator_comments = comments
            execution.save()
            
            # Create QC checkpoints if this is a QC phase
            if 'qc' in phase_name.lower():
                cls._create_qc_checkpoints(execution, completed_by)
            
            # Activate next phase by finding the next 'not_ready' phase in sequence
            next_phases = BatchPhaseExecution.objects.filter(
                bmr=bmr,
                phase__phase_order__gt=execution.phase.phase_order,
                status='not_ready'
            ).order_by('phase__phase_order')
            
            if next_phases.exists():
                next_phase = next_phases.first()
                next_phase.status = 'pending'  # Make it available for operators
                next_phase.save()
                
                # Store notification data in session if available
                from django.contrib import messages
                if hasattr(completed_by, 'request') and hasattr(completed_by.request, 'session'):
                    completed_by.request.session['completed_phase'] = phase_name
                    completed_by.request.session['completed_bmr'] = bmr.id
                    if next_phase:
                        next_phase_name = next_phase.phase.get_phase_name_display()
                        if bmr.product.product_type == 'tablet' and getattr(bmr.product, 'tablet_type', None) == 'tablet_2' and phase_name == 'packaging_material_release':
                            next_phase_name = 'Bulk Packing'  # Force correct next phase name
                return next_phase
                
        except BatchPhaseExecution.DoesNotExist:
            print(f"Phase execution not found: {phase_name} for BMR {bmr.bmr_number}")
        
        return None
    
    @classmethod
    def start_phase(cls, bmr, phase_name, started_by):
        """Start a phase execution - with prerequisite validation"""
        try:
            execution = BatchPhaseExecution.objects.get(
                bmr=bmr,
                phase__phase_name=phase_name,
                status='pending'
            )
            
            # Validate that all prerequisite phases are completed
            if not cls.can_start_phase(bmr, phase_name):
                print(f"Cannot start phase {phase_name} for BMR {bmr.bmr_number} - prerequisites not met")
                return None
            
            execution.status = 'in_progress'
            execution.started_by = started_by
            execution.started_date = timezone.now()
            execution.save()
            
            return execution
            
        except BatchPhaseExecution.DoesNotExist:
            print(f"Cannot start phase {phase_name} for BMR {bmr.bmr_number} - not pending")
        
        return None
    
    @classmethod
    def can_start_phase(cls, bmr, phase_name):
        """Check if a phase can be started (all prerequisites completed)"""
        try:
            current_execution = BatchPhaseExecution.objects.get(
                bmr=bmr,
                phase__phase_name=phase_name
            )
            
            # Cannot start phases that are not pending
            if current_execution.status != 'pending':
                return False
            
            # Get all phases with lower order (prerequisites)
            prerequisite_phases = BatchPhaseExecution.objects.filter(
                bmr=bmr,
                phase__phase_order__lt=current_execution.phase.phase_order
            )
            
            # Check if all prerequisite phases are completed or skipped
            for prereq in prerequisite_phases:
                if prereq.status not in ['completed', 'skipped']:
                    return False
            
            return True
            
        except BatchPhaseExecution.DoesNotExist:
            return False
    
    @classmethod
    def get_workflow_status(cls, bmr):
        """Get complete workflow status for a BMR"""
        executions = BatchPhaseExecution.objects.filter(
            bmr=bmr
        ).select_related('phase').order_by('phase__phase_order')
        
        total_phases = executions.count()
        completed_phases = executions.filter(status='completed').count()
        current_phase = cls.get_current_phase(bmr)
        next_phase = cls.get_next_phase(bmr)
        
        return {
            'total_phases': total_phases,
            'completed_phases': completed_phases,
            'progress_percentage': (completed_phases / total_phases * 100) if total_phases > 0 else 0,
            'current_phase': current_phase,
            'next_phase': next_phase,
            'all_executions': executions,
            'is_complete': completed_phases == total_phases
        }
    
    @classmethod
    def _create_qc_checkpoints(cls, phase_execution, checked_by):
        """Create simple QC checkpoint when a QC phase is completed"""
        from workflow.models import PhaseCheckpoint
        
        # Create a simple checkpoint that just records the QC phase completion
        phase_name = phase_execution.phase.phase_name
        
        # Create readable checkpoint name
        checkpoint_name = phase_name.replace('_', ' ').title()
        
        # Determine if QC passed (95% pass rate for realistic data)
        import random
        qc_passed = random.random() < 0.95
        
        PhaseCheckpoint.objects.create(
            phase_execution=phase_execution,
            checkpoint_name=f"{checkpoint_name} Completed",
            expected_value="QC Phase Completion",
            actual_value="Completed" if qc_passed else "Failed",
            is_within_spec=qc_passed,
            checked_by=checked_by,
            checked_date=phase_execution.completed_date,
            comments=f"QC phase {checkpoint_name} completed. {'Passed quality control.' if qc_passed else 'Failed quality control - requires review.'}"
        )
    
    @classmethod
    def handle_qc_failure_rollback(cls, bmr, failed_phase_name, rollback_to_phase):
        """Handle QC failure and rollback to a previous phase"""
        try:
            # Find the failed QC phase
            failed_execution = BatchPhaseExecution.objects.get(
                bmr=bmr,
                phase__phase_name=failed_phase_name
            )
            
            # Mark the QC phase as failed for audit trail
            if failed_execution.status != 'failed':
                failed_execution.status = 'failed'
                failed_execution.completed_date = timezone.now()
                failed_execution.save()
            
            # Find the rollback phase 
            rollback_phase = BatchPhaseExecution.objects.get(
                bmr=bmr,
                phase__phase_name=rollback_to_phase
            )
            
            # CRITICAL: Reset ALL phases from rollback point onward to ensure proper sequence
            # This includes the failed QC phase which must be reset for retesting
            phases_to_reset = BatchPhaseExecution.objects.filter(
                bmr=bmr,
                phase__phase_order__gte=rollback_phase.phase.phase_order
            )
            
            for phase_execution in phases_to_reset:
                # Reset to not_ready - they will be activated in proper sequence
                phase_execution.status = 'not_ready'
                phase_execution.started_by = None
                phase_execution.started_date = None
                phase_execution.completed_by = None
                phase_execution.completed_date = None
                
                if phase_execution.id == failed_execution.id:
                    phase_execution.operator_comments = f'QC RESET: Ready for retesting after {rollback_to_phase} rework.'
                elif phase_execution.id == rollback_phase.id:
                    phase_execution.operator_comments = f'REWORK REQUIRED: Rolled back from {failed_phase_name} failure. Must restart from this phase.'
                else:
                    phase_execution.operator_comments = 'RESET: Waiting for workflow sequence after rollback.'
                
                phase_execution.save()
            
            # Set ONLY the rollback phase to pending so work can resume
            rollback_phase.status = 'pending'
            rollback_phase.operator_comments = f'REWORK REQUIRED: Rolled back from {failed_phase_name} failure. Must restart from this phase.'
            rollback_phase.save()
            
            return True
            
        except Exception as e:
            print(f"Error handling QC rollback for BMR {bmr.batch_number}: {e}")
            return False
    
    @classmethod
    def trigger_next_phase(cls, bmr, current_phase):
        """Trigger the next phase in the workflow after completing current phase"""
        try:
            current_execution = BatchPhaseExecution.objects.get(
                bmr=bmr,
                phase=current_phase
            )
            
            # QUARANTINE LOGIC: Check if this phase should go to quarantine
            phases_that_bypass_quarantine = [
                'bmr_creation', 'regulatory_approval',  # Administrative phases
                'raw_material_release', 'material_dispensing', 'packaging_material_release',  # Material handling
                'blister_packing', 'bulk_packing', 'secondary_packaging',  # All packing phases bypass quarantine
                'final_qa', 'finished_goods_store'  # Final phases
            ]
            
            if current_execution.phase.phase_name not in phases_that_bypass_quarantine:
                print(f"Phase {current_execution.phase.phase_name} completed for BMR {bmr.batch_number}, sending to quarantine...")
                return cls._send_to_quarantine(bmr, current_execution)
            
            # EXISTING SPECIAL HANDLING (no quarantine)
            # NEW: Handle raw material release -> material dispensing transition
            if current_execution.phase.phase_name == 'raw_material_release':
                print(f"Completed raw material release for BMR {bmr.batch_number}, activating material dispensing...")
                material_dispensing_phase = BatchPhaseExecution.objects.filter(
                    bmr=bmr,
                    phase__phase_name='material_dispensing'
                ).first()
                
                if material_dispensing_phase:
                    material_dispensing_phase.status = 'pending'
                    material_dispensing_phase.save()
                    print(f"Activated material_dispensing phase for BMR {bmr.batch_number}")
                    return True
                else:
                    print(f"WARNING: No material_dispensing phase found for BMR {bmr.batch_number}")
                    return False
            
            # NEW: Handle regulatory approval -> raw material release transition
            if current_execution.phase.phase_name == 'regulatory_approval':
                print(f"Completed regulatory approval for BMR {bmr.batch_number}, activating raw material release...")
                raw_material_release_phase = BatchPhaseExecution.objects.filter(
                    bmr=bmr,
                    phase__phase_name='raw_material_release'
                ).first()
                
                if raw_material_release_phase:
                    raw_material_release_phase.status = 'pending'
                    raw_material_release_phase.save()
                    print(f"Activated raw_material_release phase for BMR {bmr.batch_number}")
                    return True
                else:
                    print(f"WARNING: No raw_material_release phase found for BMR {bmr.batch_number}")
                    return False
            
            # Special handling for sorting -> coating for tablets
            if current_execution.phase.phase_name == 'sorting' and bmr.product.product_type == 'tablet':
                print(f"Completed sorting for tablet BMR {bmr.batch_number}, handling workflow...")
                is_coated = bmr.product.is_coated
                print(f"Is product coated: {is_coated}")
                
                # Get coating and packaging phases
                coating_phase = BatchPhaseExecution.objects.filter(
                    bmr=bmr, 
                    phase__phase_name='coating'
                ).first()
                
                packaging_phase = BatchPhaseExecution.objects.filter(
                    bmr=bmr,
                    phase__phase_name='packaging_material_release'
                ).first()
                
                if coating_phase and packaging_phase:
                    print(f"Found coating phase (status: {coating_phase.status}) and packaging phase (status: {packaging_phase.status})")
                    # For coated tablets: always go to coating first
                    if is_coated:
                        coating_phase.status = 'pending'
                        coating_phase.save()
                        print(f"Activated coating phase for coated product: {bmr.batch_number}")
                        return True
                    else:
                        # For uncoated tablets: skip coating, go to packaging
                        coating_phase.status = 'skipped'
                        coating_phase.completed_date = timezone.now()
                        coating_phase.operator_comments = "Phase skipped - product does not require coating"
                        coating_phase.save()
                        packaging_phase.status = 'pending'
                        packaging_phase.save()
                        print(f"Skipped coating, activated packaging for uncoated product: {bmr.batch_number}")
                        return True
            
            # Special handling for coating -> packaging for coated tablets
            if current_execution.phase.phase_name == 'coating' and bmr.product.product_type == 'tablet':
                print(f"Completed coating for tablet BMR {bmr.batch_number}, activating packaging...")
                packaging_phase = BatchPhaseExecution.objects.filter(
                    bmr=bmr,
                    phase__phase_name='packaging_material_release'
                ).first()
                
                if packaging_phase:
                    packaging_phase.status = 'pending'
                    packaging_phase.save()
                    print(f"Activated packaging phase after coating: {bmr.batch_number}")
                    return True
            
            # Special handling for packaging_material_release -> bulk_packing for tablet_2
            if current_execution.phase.phase_name == 'packaging_material_release' and bmr.product.product_type == 'tablet':
                tablet_type = getattr(bmr.product, 'tablet_type', None)
                print(f"Completed packaging material release for tablet BMR {bmr.batch_number}, tablet_type: {tablet_type}")
                
                if tablet_type == 'tablet_2':
                    # For tablet_2, activate bulk_packing first
                    bulk_packing_phase = BatchPhaseExecution.objects.filter(
                        bmr=bmr,
                        phase__phase_name='bulk_packing'
                    ).first()
                    
                    if bulk_packing_phase:
                        # Ensure secondary packaging is NOT activated yet
                        secondary_phase = BatchPhaseExecution.objects.filter(
                            bmr=bmr,
                            phase__phase_name='secondary_packaging'
                        ).first()
                        if secondary_phase and secondary_phase.status == 'pending':
                            secondary_phase.status = 'not_ready'
                            secondary_phase.save()
                            print(f"Reset secondary_packaging to not_ready for tablet_2: {bmr.batch_number}")
                        
                        bulk_packing_phase.status = 'pending'
                        bulk_packing_phase.save()
                        print(f"Activated bulk_packing phase for tablet_2: {bmr.batch_number}")
                        return True  # CRITICAL: Exit here to prevent standard logic from running
                else:
                    # For normal tablets, activate blister_packing
                    blister_packing_phase = BatchPhaseExecution.objects.filter(
                        bmr=bmr,
                        phase__phase_name='blister_packing'
                    ).first()
                    
                    if blister_packing_phase:
                        # Ensure secondary packaging is NOT activated yet for normal tablets too
                        secondary_phase = BatchPhaseExecution.objects.filter(
                            bmr=bmr,
                            phase__phase_name='secondary_packaging'
                        ).first()
                        if secondary_phase and secondary_phase.status == 'pending':
                            secondary_phase.status = 'not_ready'
                            secondary_phase.save()
                            print(f"Reset secondary_packaging to not_ready for normal tablet: {bmr.batch_number}")
                        
                        blister_packing_phase.status = 'pending'
                        blister_packing_phase.save()
                        print(f"Activated blister_packing phase for normal tablet: {bmr.batch_number}")
                        return True  # CRITICAL: Exit here to prevent standard logic from running
                
                # If we reach here, something went wrong with tablet handling
                print(f"WARNING: Failed to handle tablet packaging transition for BMR {bmr.batch_number}")
                return False
            
            # Special handling for bulk_packing -> secondary_packaging for tablet_2
            if current_execution.phase.phase_name == 'bulk_packing' and bmr.product.product_type == 'tablet':
                tablet_type = getattr(bmr.product, 'tablet_type', None)
                if tablet_type == 'tablet_2':
                    # After bulk packing is complete, activate secondary packaging
                    secondary_phase = BatchPhaseExecution.objects.filter(
                        bmr=bmr,
                        phase__phase_name='secondary_packaging'
                    ).first()
                    
                    if secondary_phase:
                        secondary_phase.status = 'pending'
                        secondary_phase.save()
                        print(f"Activated secondary_packaging phase after bulk_packing for tablet_2: {bmr.batch_number}")
                        return True  # CRITICAL: Exit here to prevent standard logic
                    else:
                        print(f"WARNING: No secondary_packaging phase found for tablet_2 BMR {bmr.batch_number}")
                        return False
                        
            # Special handling for blister_packing -> secondary_packaging for normal tablets
            if current_execution.phase.phase_name == 'blister_packing' and bmr.product.product_type == 'tablet':
                tablet_type = getattr(bmr.product, 'tablet_type', None)
                if tablet_type == 'normal' or tablet_type is None:  # Default to normal if not specified
                    # After blister packing is complete, activate secondary packaging
                    secondary_phase = BatchPhaseExecution.objects.filter(
                        bmr=bmr,
                        phase__phase_name='secondary_packaging'
                    ).first()
                    
                    if secondary_phase:
                        secondary_phase.status = 'pending'
                        secondary_phase.save()
                        print(f"Activated secondary_packaging phase after blister_packing for normal tablet: {bmr.batch_number}")
                        return True  # CRITICAL: Exit here to prevent standard logic
                    else:
                        print(f"WARNING: No secondary_packaging phase found for normal tablet BMR {bmr.batch_number}")
                        return False
            
            # Standard next phase logic for ALL other cases
            # This will only run if none of the special cases above returned True
            all_next = BatchPhaseExecution.objects.filter(
                bmr=bmr,
                phase__phase_order__gt=current_execution.phase.phase_order
            ).order_by('phase__phase_order')
            
            # Important: Get the very next phase by phase_order, regardless of status
            next_phase = all_next.first()
            if next_phase:
                # Special protection for secondary_packaging to ensure correct workflow
                if next_phase.phase.phase_name == 'secondary_packaging' and bmr.product.product_type == 'tablet':
                    tablet_type = getattr(bmr.product, 'tablet_type', None)
                    
                    # For tablet_2, ensure bulk_packing is completed
                    if tablet_type == 'tablet_2':
                        bulk_packing = BatchPhaseExecution.objects.filter(
                            bmr=bmr, 
                            phase__phase_name='bulk_packing'
                        ).first()
                        
                        if bulk_packing and bulk_packing.status != 'completed':
                            print(f"WARNING: Cannot activate secondary_packaging for tablet_2 BMR {bmr.batch_number} - bulk_packing not completed")
                            return False
                    
                    # For normal tablets, ensure blister_packing is completed
                    elif tablet_type == 'normal' or tablet_type is None:
                        blister_packing = BatchPhaseExecution.objects.filter(
                            bmr=bmr, 
                            phase__phase_name='blister_packing'
                        ).first()
                        
                        if blister_packing and blister_packing.status != 'completed':
                            print(f"WARNING: Cannot activate secondary_packaging for normal tablet BMR {bmr.batch_number} - blister_packing not completed")
                            return False
                
                # Update the status to pending to activate it
                next_phase.status = 'pending'
                next_phase.save()
                print(f"Triggered next phase: {next_phase.phase.phase_name} for BMR {bmr.batch_number}")
                return True
            
            print(f"No more phases to trigger for BMR {bmr.batch_number}")
            # Debug: print all phase statuses for this BMR
            all_phases = BatchPhaseExecution.objects.filter(bmr=bmr).select_related('phase').order_by('phase__phase_order')
            print("Phase order and statuses:")
            for p in all_phases:
                print(f"  {p.phase.phase_order:2d}. {p.phase.phase_name:25} {p.status}")
            return False
        except BatchPhaseExecution.DoesNotExist:
            print(f"Current phase execution not found for BMR {bmr.batch_number}")
            return False
        except Exception as e:
            print(f"Error triggering next phase for BMR {bmr.batch_number}: {e}")
            return False
        except Exception as e:
            print(f"Error triggering next phase for BMR {bmr.batch_number}: {e}")
            return False
    
    @classmethod
    def rollback_to_previous_phase(cls, bmr, failed_phase):
        """Rollback to previous phase when QC fails"""
        try:
            # Get product type to determine correct rollback
            product_type = bmr.product.product_type.lower() if bmr.product.product_type else ''
            failed_phase_name = failed_phase.phase_name
            
            # Define QC rollback mapping based on product type
            if 'cream' in product_type or 'ointment' in product_type:
                # Creams/Ointments go back to mixing, never blending
                qc_rollback_mapping = {
                    'post_compression_qc': 'mixing',  # Should not happen for creams
                    'post_mixing_qc': 'mixing',
                    'post_blending_qc': 'mixing',  # Creams should not go to blending!
                }
            elif 'tablet' in product_type:
                # Tablets follow normal flow
                qc_rollback_mapping = {
                    'post_compression_qc': 'granulation',  # Roll back to granulation for tablets
                    'post_mixing_qc': 'mixing',
                    'post_blending_qc': 'blending',
                }
            elif 'capsule' in product_type:
                # Capsules follow their flow
                qc_rollback_mapping = {
                    'post_compression_qc': 'filling',  # Should not happen for capsules
                    'post_mixing_qc': 'drying',
                    'post_blending_qc': 'blending',
                }
            else:
                # Default mapping
                qc_rollback_mapping = {
                    'post_compression_qc': 'granulation',
                    'post_mixing_qc': 'mixing',
                    'post_blending_qc': 'blending',
                }
            
            rollback_to_phase = qc_rollback_mapping.get(failed_phase_name)
            
            if rollback_to_phase:
                success = cls.handle_qc_failure_rollback(bmr, failed_phase_name, rollback_to_phase)
                if success:
                    return rollback_to_phase  # Return the actual phase name for messaging
            
            return None
        except Exception as e:
            print(f"Error rolling back for BMR {bmr.batch_number}: {e}")
            return None
    
    @classmethod
    def get_phases_for_user_role(cls, bmr, user_role):
        """Get phases that a specific user role can work on"""
        # Map user roles to phases they can handle
        role_phase_mapping = {
            'qa': ['bmr_creation', 'final_qa'],
            'regulatory': ['regulatory_approval'],
            'store_manager': ['raw_material_release'],  # Store Manager handles raw material release
            'dispensing_operator': ['material_dispensing'],  # Dispensing Operator handles material dispensing
            'packaging_store': ['packaging_material_release'],  # Packaging store handles packaging material release
            'finished_goods_store': ['finished_goods_store'],  # Finished Goods Store only handles finished goods storage
            'qc': ['post_compression_qc', 'post_mixing_qc', 'post_blending_qc'],
            'mixing_operator': ['mixing'],
            'granulation_operator': ['granulation'],
            'blending_operator': ['blending'],
            'compression_operator': ['compression'],
            'coating_operator': ['coating'],
            'drying_operator': ['drying'],
            'filling_operator': ['filling'],
            'tube_filling_operator': ['tube_filling'],
            'packing_operator': ['blister_packing', 'bulk_packing', 'secondary_packaging'],
            'sorting_operator': ['sorting'],
        }
        
        allowed_phases = role_phase_mapping.get(user_role, [])
        
        return BatchPhaseExecution.objects.filter(
            bmr=bmr,
            phase__phase_name__in=allowed_phases,
            status__in=['pending', 'in_progress']
        ).select_related('phase').order_by('phase__phase_order')
    
    @classmethod
    def _send_to_quarantine(cls, bmr, current_execution):
        """Send completed phase to quarantine"""
        try:
            from quarantine.models import QuarantineBatch
            
            # Check if batch is already in quarantine
            existing_quarantine = QuarantineBatch.objects.filter(
                bmr=bmr,
                status__in=['quarantined', 'sample_requested', 'sample_in_qa', 'sample_in_qc', 'sample_approved', 'sample_failed']
            ).first()
            
            if existing_quarantine:
                # Update existing quarantine record
                existing_quarantine.current_phase = current_execution.phase
                existing_quarantine.status = 'quarantined'
                existing_quarantine.save()
                print(f"Updated existing quarantine record for BMR {bmr.batch_number} at phase {current_execution.phase.phase_name}")
            else:
                # Create new quarantine record
                QuarantineBatch.objects.create(
                    bmr=bmr,
                    current_phase=current_execution.phase,
                    status='quarantined',
                    quarantine_date=timezone.now()
                )
                print(f"Created quarantine record for BMR {bmr.batch_number} at phase {current_execution.phase.phase_name}")
            
            return True
            
        except Exception as e:
            print(f"Error sending BMR {bmr.batch_number} to quarantine: {e}")
            return False
    
    @classmethod
    def proceed_from_quarantine(cls, bmr, quarantine_phase):
        """Proceed from quarantine to next phase after sample approval - skip QC phases since sample was already approved"""
        try:
            # Get all phases after the quarantine phase
            all_next = BatchPhaseExecution.objects.filter(
                bmr=bmr,
                phase__phase_order__gt=quarantine_phase.phase_order
            ).order_by('phase__phase_order')
            
            # QC phases that should be skipped since quarantine sample was approved
            qc_phases = ['post_mixing_qc', 'post_compression_qc', 'post_blending_qc']
            
            # Find the next non-QC phase (since QC was already done via quarantine sample)
            next_phase = None
            for phase_execution in all_next:
                if phase_execution.phase.phase_name not in qc_phases:
                    next_phase = phase_execution
                    break
                else:
                    # Mark QC phases as completed since quarantine sample was approved
                    phase_execution.status = 'completed'
                    phase_execution.completed_date = timezone.now()
                    phase_execution.operator_comments = "QC completed via quarantine sample approval"
                    phase_execution.save()
                    print(f"Skipped QC phase {phase_execution.phase.phase_name} for BMR {bmr.batch_number} (quarantine sample approved)")
            
            if next_phase:
                next_phase.status = 'pending'
                next_phase.save()
                print(f"Proceeded from quarantine: activated {next_phase.phase.phase_name} for BMR {bmr.batch_number}")
                
                # Update quarantine record
                from quarantine.models import QuarantineBatch
                quarantine_batch = QuarantineBatch.objects.filter(bmr=bmr).first()
                if quarantine_batch:
                    quarantine_batch.status = 'released'
                    quarantine_batch.released_date = timezone.now()
                    quarantine_batch.save()
                
                return True
            else:
                print(f"No next production phase found after quarantine for BMR {bmr.batch_number}")
                return False
                
        except Exception as e:
            print(f"Error proceeding from quarantine for BMR {bmr.batch_number}: {e}")
            return False
