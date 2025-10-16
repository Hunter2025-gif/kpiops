from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, Count, Avg
from .models import QuarantineBatch, SampleRequest
from workflow.services import WorkflowService
from workflow.models import BatchPhaseExecution

@login_required
def quarantine_dashboard(request):
    """Main quarantine dashboard for quarantine managers"""
    # Check permissions - allow quarantine role, admin, and production manager
    if not (request.user.is_staff or request.user.role in ['admin', 'production_manager', 'quarantine']):
        messages.error(request, 'Access denied. Quarantine, Admin or Production Manager privileges required.')
        return redirect('dashboards:dashboard_home')
    
    # Get all batches in quarantine
    quarantine_batches = QuarantineBatch.objects.select_related(
        'bmr__product', 'current_phase', 'released_by'
    ).filter(status__in=['quarantined', 'sample_requested', 'sample_in_qa', 'sample_in_qc', 'sample_approved', 'sample_failed'])
    
    # Get statistics
    total_in_quarantine = quarantine_batches.count()
    awaiting_decision = quarantine_batches.filter(status__in=['quarantined', 'sample_approved']).count()
    samples_in_progress = quarantine_batches.filter(status__in=['sample_requested', 'sample_in_qa', 'sample_in_qc']).count()
    failed_samples = quarantine_batches.filter(status='sample_failed').count()
    
    # Calculate average quarantine time using database fields
    from django.db.models import F, ExpressionWrapper, DurationField
    avg_quarantine_time = 0
    released_batches = QuarantineBatch.objects.filter(released_date__isnull=False)
    if released_batches.exists():
        total_hours = sum(batch.quarantine_duration_hours for batch in released_batches)
        avg_quarantine_time = total_hours / released_batches.count()
    
    # Recent sample requests for tracking
    recent_samples = SampleRequest.objects.select_related(
        'quarantine_batch__bmr__product', 'requested_by', 'sampled_by', 'received_by', 'approved_by'
    ).order_by('-request_date')[:10]
    
    # Group batches by phase for left sidebar
    from django.db.models import Count
    from collections import defaultdict
    from workflow.models import ProductionPhase
    
    # Define phases that can go to quarantine (production phases only)
    quarantine_phases = [
        'mixing', 'post_mixing_qc', 'tube_filling',  # Ointment phases
        'granulation', 'blending', 'post_blending_qc', 'compression', 'post_compression_qc', 'sorting', 'coating',  # Tablet phases  
        'drying', 'filling',  # Capsule phases
    ]
    
    # Get unique phases using Python to avoid SQL distinct issues
    phases_dict = {}
    for phase in ProductionPhase.objects.filter(phase_name__in=quarantine_phases).order_by('phase_order'):
        if phase.phase_name not in phases_dict:
            phases_dict[phase.phase_name] = phase
    
    all_phases = list(phases_dict.values())
    
    # Get current quarantine batch counts per phase
    current_phase_counts = {}
    phase_counts_raw = quarantine_batches.values('current_phase__phase_name').annotate(count=Count('id'))
    for phase_data in phase_counts_raw:
        current_phase_counts[phase_data['current_phase__phase_name']] = phase_data['count']
    
    # Build complete phase list with counts
    phase_counts = []
    for phase in all_phases:
        count = current_phase_counts.get(phase.phase_name, 0)
        display_name = phase.phase_name.replace('_', ' ').title()
        phase_counts.append({
            'phase_name': phase.phase_name,
            'display_name': display_name,
            'count': count,
            'has_batches': count > 0
        })
    
    # Get selected phase filter
    selected_phase = request.GET.get('phase', 'all')
    
    # Filter batches by selected phase if specified
    if selected_phase != 'all':
        filtered_batches = quarantine_batches.filter(current_phase__phase_name=selected_phase)
    else:
        filtered_batches = quarantine_batches
        
    # Get BMR history across all quarantine phases
    # Group quarantine batches by BMR to track complete history
    from django.db.models import Max, Min
    from collections import defaultdict
    
    # Get all unique BMRs that have ever been in quarantine
    bmrs_with_quarantine = QuarantineBatch.objects.values_list('bmr', flat=True).distinct()
    
    # Get comprehensive quarantine history for each BMR (no duplicates)
    bmr_quarantine_history = []
    processed_bmrs = set()  # Track BMRs we've already processed to avoid duplicates
    
    for bmr_id in bmrs_with_quarantine:
        # Skip if we've already processed this BMR
        if bmr_id in processed_bmrs:
            continue
            
        # Mark this BMR as processed
        processed_bmrs.add(bmr_id)
        
        # Get all quarantine batches for this BMR
        bmr_batches = QuarantineBatch.objects.filter(bmr_id=bmr_id).select_related(
            'bmr__product', 'current_phase', 'released_by'
        ).order_by('current_phase__phase_order')
        
        if bmr_batches.exists():
            first_batch = bmr_batches.first()
            # Get total number of quarantine phases this BMR has been through
            phase_count = bmr_batches.count()
            # Get first quarantine date
            first_quarantine = bmr_batches.aggregate(Min('quarantine_date'))['quarantine_date__min']
            # Get last release date if available
            last_release = bmr_batches.filter(released_date__isnull=False).aggregate(Max('released_date'))['released_date__max']
            # Calculate total quarantine time across all phases
            total_time = sum(batch.quarantine_duration_hours for batch in bmr_batches)
            # Check if any phase is still in quarantine
            still_in_quarantine = bmr_batches.filter(released_date__isnull=True).exists()
            
            bmr_history = {
                'bmr': first_batch.bmr,
                'batch_number': first_batch.bmr.batch_number,
                'product_name': first_batch.bmr.product.product_name,
                'phase_count': phase_count,
                'first_quarantine': first_quarantine,
                'last_release': last_release,
                'total_time': round(total_time, 1),
                'still_in_quarantine': still_in_quarantine,
                'phases': list(bmr_batches)
            }
            bmr_quarantine_history.append(bmr_history)
    
    # Sort by most recent first
    bmr_quarantine_history.sort(key=lambda x: x['first_quarantine'], reverse=True)
    
    context = {
        'page_title': 'Quarantine Dashboard',
        'quarantine_batches': filtered_batches,  # Use filtered batches
        'all_quarantine_batches': quarantine_batches,  # Keep all for statistics
        'phase_counts': phase_counts,  # Add phase counts for sidebar
        'selected_phase': selected_phase,  # Add selected phase
        'total_in_quarantine': total_in_quarantine,
        'awaiting_decision': awaiting_decision,
        'samples_in_progress': samples_in_progress,
        'failed_samples': failed_samples,
        'avg_quarantine_time': round(avg_quarantine_time, 1),
        'recent_samples': recent_samples,
        'bmr_quarantine_history': bmr_quarantine_history,  # Add BMR history across phases
    }
    
    return render(request, 'quarantine/dashboard.html', context)

@login_required
def request_sample(request, quarantine_id):
    """Request a sample for testing"""
    # Check permissions - allow quarantine role, admin, and production manager
    if not (request.user.is_staff or request.user.role in ['admin', 'production_manager', 'quarantine']):
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    quarantine_batch = get_object_or_404(QuarantineBatch, id=quarantine_id)
    
    if not quarantine_batch.can_request_sample:
        return JsonResponse({
            'success': False, 
            'error': 'Cannot request sample. Maximum 2 samples allowed per batch.'
        })
    
    # Create new sample request
    sample_number = quarantine_batch.sample_count + 1
    sample_request = SampleRequest.objects.create(
        quarantine_batch=quarantine_batch,
        sample_number=sample_number,
        requested_by=request.user
    )
    
    # Update quarantine batch
    quarantine_batch.sample_count = sample_number
    quarantine_batch.status = 'sample_requested'
    quarantine_batch.save()
    
    messages.success(request, f'Sample {sample_number} requested for {quarantine_batch.bmr.batch_number}')
    
    if request.headers.get('Content-Type') == 'application/json':
        return JsonResponse({'success': True, 'message': 'Sample requested successfully'})
    
    return redirect('quarantine:dashboard')

@login_required
def proceed_to_next_phase(request, quarantine_id):
    """Proceed batch to next phase"""
    # Check permissions - allow quarantine role, admin, and production manager
    if not (request.user.is_staff or request.user.role in ['admin', 'production_manager', 'quarantine']):
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    quarantine_batch = get_object_or_404(QuarantineBatch, id=quarantine_id)
    
    if not quarantine_batch.can_proceed_to_next_phase:
        return JsonResponse({
            'success': False, 
            'error': 'Cannot proceed. Sample must be approved first.'
        })
    
    try:
        # Use workflow service to proceed from quarantine
        success = WorkflowService.proceed_from_quarantine(
            quarantine_batch.bmr, 
            quarantine_batch.current_phase
        )
        
        if success:
            return JsonResponse({'success': True, 'message': 'Batch proceeded to next phase'})
        else:
            return JsonResponse({'success': False, 'error': 'Failed to proceed to next phase'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def qa_dashboard(request):
    """QA dashboard for handling sample requests"""
    if request.user.role != 'qa':
        messages.error(request, 'Access denied. QA privileges required.')
        return redirect('dashboards:dashboard_home')
    
    # Get samples awaiting QA processing
    pending_samples = SampleRequest.objects.filter(
        sampled_by__isnull=True
    ).select_related('quarantine_batch__bmr__product', 'requested_by')
    
    # Get samples processed by this QA user
    my_samples = SampleRequest.objects.filter(
        sampled_by=request.user
    ).select_related('quarantine_batch__bmr__product', 'received_by', 'approved_by')
    
    context = {
        'page_title': 'QA Sample Dashboard',
        'pending_samples': pending_samples,
        'my_samples': my_samples,
    }
    
    return render(request, 'quarantine/qa_dashboard.html', context)

@login_required
def process_qa_sample(request, sample_id):
    """QA processes a sample and sends to QC"""
    if request.user.role != 'qa':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    sample = get_object_or_404(SampleRequest, id=sample_id)
    
    if request.method == 'POST':
        comments = request.POST.get('comments', '')
        sample.update_qa_stage(request.user, comments)
        
        messages.success(request, f'Sample processed and sent to QC for {sample.quarantine_batch.bmr.batch_number}')
        return JsonResponse({'success': True, 'message': 'Sample sent to QC'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def qc_dashboard(request):
    """QC dashboard for testing samples"""
    if request.user.role != 'qc':
        messages.error(request, 'Access denied. QC privileges required.')
        return redirect('dashboards:dashboard_home')
    
    # Get samples awaiting QC testing
    pending_samples = SampleRequest.objects.filter(
        sample_date__isnull=False,
        qc_status='pending'
    ).select_related('quarantine_batch__bmr__product', 'sampled_by')
    
    # Get samples tested by this QC user
    my_samples = SampleRequest.objects.filter(
        approved_by=request.user
    ).select_related('quarantine_batch__bmr__product', 'sampled_by')
    
    context = {
        'page_title': 'QC Sample Dashboard',
        'pending_samples': pending_samples,
        'my_samples': my_samples,
    }
    
    return render(request, 'quarantine/qc_dashboard.html', context)

@login_required
def receive_qc_sample(request, sample_id):
    """QC receives a sample"""
    if request.user.role != 'qc':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    sample = get_object_or_404(SampleRequest, id=sample_id)
    sample.update_qc_received(request.user)
    
    messages.success(request, f'Sample received for testing: {sample.quarantine_batch.bmr.batch_number}')
    return JsonResponse({'success': True, 'message': 'Sample received'})

@login_required
def approve_reject_sample(request, sample_id):
    """QC approves or rejects a sample"""
    if request.user.role != 'qc':
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    sample = get_object_or_404(SampleRequest, id=sample_id)
    
    if request.method == 'POST':
        qc_status = request.POST.get('qc_status')  # 'approved' or 'failed'
        comments = request.POST.get('comments', '')
        
        if qc_status not in ['approved', 'failed']:
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
        sample.update_qc_decision(request.user, qc_status, comments)
        
        status_text = 'approved' if qc_status == 'approved' else 'failed'
        messages.success(request, f'Sample {status_text} for {sample.quarantine_batch.bmr.batch_number}')
        return JsonResponse({'success': True, 'message': f'Sample {status_text}'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def approve_qc_sample(request, sample_id):
    """Approve a quarantine sample in QC"""
    if request.user.role != 'qc':
        return JsonResponse({'success': False, 'error': 'Access denied. QC role required.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        sample = get_object_or_404(SampleRequest, id=sample_id)
        
        # Ensure sample is received by QC if not already
        if not sample.received_date:
            sample.update_qc_received(request.user)
        
        # Update sample with QC approval
        sample.update_qc_decision(request.user, 'approved', 'Sample approved by QC')
        
        return JsonResponse({
            'success': True, 
            'message': f'Sample {sample.sample_number} for batch {sample.quarantine_batch.bmr.batch_number} approved'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def fail_qc_sample(request, sample_id):
    """Fail a quarantine sample in QC"""
    if request.user.role != 'qc':
        return JsonResponse({'success': False, 'error': 'Access denied. QC role required.'})
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})
    
    try:
        import json
        sample = get_object_or_404(SampleRequest, id=sample_id)
        
        # Ensure sample is received by QC if not already
        if not sample.received_date:
            sample.update_qc_received(request.user)
        
        # Get failure reason from request body
        body = json.loads(request.body.decode('utf-8'))
        failure_reason = body.get('failure_reason', 'Sample failed QC testing')
        
        # Update sample with QC failure
        sample.update_qc_decision(request.user, 'failed', failure_reason)
        
        return JsonResponse({
            'success': True, 
            'message': f'Sample {sample.sample_number} for batch {sample.quarantine_batch.bmr.batch_number} failed'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def quarantine_details(request, quarantine_id):
    """Detailed view of quarantine batch with full timeline and sample history"""
    # Allow access for admin, qa, qc, quarantine roles, and production managers
    if not (request.user.is_staff or request.user.role in ['admin', 'qa', 'qc', 'quarantine', 'production_manager']):
        messages.error(request, 'Access denied. Authorized personnel only.')
        return redirect('dashboards:dashboard_home')
    
    # Get the quarantine batch with related data
    quarantine_batch = get_object_or_404(
        QuarantineBatch.objects.select_related(
            'bmr__product',
            'bmr__created_by',
            'current_phase',
            'released_by'
        ).prefetch_related(
            'sample_requests__requested_by',
            'sample_requests__sampled_by',      # QA staff who took the sample
            'sample_requests__received_by',     # QC staff who received the sample
            'sample_requests__approved_by'      # QC staff who approved/rejected
        ),
        id=quarantine_id
    )
    
    # Get all sample requests for this batch
    sample_requests = quarantine_batch.sample_requests.all().order_by('-request_date')
    
    # Calculate timeline metrics
    timeline_data = {
        'quarantine_start': quarantine_batch.quarantine_date,
        'phase_before_quarantine': quarantine_batch.current_phase.phase_name if quarantine_batch.current_phase else None,
        'total_samples_requested': sample_requests.count(),
        'approved_samples': sample_requests.filter(qc_status='approved').count(),
        'rejected_samples': sample_requests.filter(qc_status='failed').count(),
        'pending_samples': sample_requests.filter(qc_status='pending').count(),
    }
    
    # Calculate processing times
    if quarantine_batch.released_date:
        timeline_data['total_quarantine_duration'] = quarantine_batch.quarantine_duration_hours
        timeline_data['quarantine_end'] = quarantine_batch.released_date
    
    # Get processing time for each sample
    for sample in sample_requests:
        if sample.sample_date and sample.request_date:
            sample.qa_processing_time = (sample.sample_date - sample.request_date).total_seconds() / 3600
        if sample.approved_date and sample.received_date:
            sample.qc_processing_time = (sample.approved_date - sample.received_date).total_seconds() / 3600
    
    # Get related phase execution details
    phase_executions = BatchPhaseExecution.objects.filter(
        bmr=quarantine_batch.bmr
    ).select_related('phase', 'started_by', 'completed_by').order_by('phase__phase_order')
    
    context = {
        'quarantine_batch': quarantine_batch,
        'sample_requests': sample_requests,
        'timeline_data': timeline_data,
        'phase_executions': phase_executions,
        'user': request.user,
    }
    
    return render(request, 'quarantine/details.html', context)