"""
Analytics module for the Pharmaceutical Operations System.
This module provides data processing functions for admin dashboard analytics.
"""
import datetime
from django.db.models import Avg, Count, F, Sum, Q, ExpressionWrapper, DurationField, DateTimeField
from django.utils import timezone
from django.db.models.functions import TruncMonth, TruncWeek, ExtractMonth
from bmr.models import BMR
from workflow.models import BatchPhaseExecution, ProductionPhase


def get_monthly_production_stats(months_lookback=6):
    """Get monthly production statistics for the past X months"""
    end_date = timezone.now()
    start_date = end_date - datetime.timedelta(days=30 * months_lookback)
    
    # Get all BMRs created within the time period
    bmrs = BMR.objects.filter(
        created_date__gte=start_date,
        created_date__lte=end_date
    )
    
    # Annotate by month and count
    monthly_data = (
        bmrs.annotate(month=TruncMonth('created_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Get completed batches by month
    completed_data = (
        bmrs.filter(status='completed')
        .annotate(month=TruncMonth('created_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Get rejected batches by month
    rejected_data = (
        bmrs.filter(status='rejected')
        .annotate(month=TruncMonth('created_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Format data for charts
    months = []
    created_counts = []
    completed_counts = []
    rejected_counts = []
    
    # Ensure we have data for all months in range
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        month_str = current_date.strftime("%b %Y")
        months.append(month_str)
        
        # Find created count for this month
        created_count = next((item['count'] for item in monthly_data if item['month'].month == current_date.month 
                         and item['month'].year == current_date.year), 0)
        created_counts.append(created_count)
        
        # Find completed count for this month
        completed_count = next((item['count'] for item in completed_data if item['month'].month == current_date.month 
                           and item['month'].year == current_date.year), 0)
        completed_counts.append(completed_count)
        
        # Find rejected count for this month
        rejected_count = next((item['count'] for item in rejected_data if item['month'].month == current_date.month 
                          and item['month'].year == current_date.year), 0)
        rejected_counts.append(rejected_count)
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return {
        'labels': months,
        'created': created_counts,
        'completed': completed_counts,
        'rejected': rejected_counts
    }


def get_production_cycle_times():
    """Calculate average production cycle times by product type"""
    # Get all completed BMRs
    completed_bmrs = BMR.objects.filter(status='completed').select_related('product')
    
    # Group by product type
    product_types = {}
    
    for bmr in completed_bmrs:
        # Get first and last phase
        first_phase = BatchPhaseExecution.objects.filter(
            bmr=bmr
        ).order_by('phase__phase_order').first()
        
        last_phase = BatchPhaseExecution.objects.filter(
            bmr=bmr, 
            phase__phase_name='finished_goods_store',
            status='completed'
        ).first()
        
        if first_phase and last_phase and first_phase.started_date and last_phase.completed_date:
            product_type = bmr.product.product_type
            
            if product_type not in product_types:
                product_types[product_type] = []
            
            # Calculate total time in days
            total_time = (last_phase.completed_date - first_phase.started_date).total_seconds() / (3600 * 24)
            product_types[product_type].append(total_time)
    
    # Calculate averages
    result = {
        'labels': [],
        'avg_days': []
    }
    
    for product_type, times in product_types.items():
        if times:  # Check if we have data
            result['labels'].append(product_type.replace('_', ' ').title())
            result['avg_days'].append(round(sum(times) / len(times), 1))
    
    return result


def get_phase_bottleneck_analysis():
    """Identify bottlenecks in the production process by analyzing phase durations"""
    # Get all completed phases
    completed_phases = BatchPhaseExecution.objects.filter(
        status='completed',
        started_date__isnull=False,
        completed_date__isnull=False
    ).select_related('phase', 'bmr__product')
    
    # Calculate duration for each phase
    phase_durations = {}
    
    for phase in completed_phases:
        duration = (phase.completed_date - phase.started_date).total_seconds() / 3600  # hours
        
        phase_name = phase.phase.phase_name
        product_type = phase.bmr.product.product_type
        
        key = f"{product_type}__{phase_name}"
        
        if key not in phase_durations:
            phase_durations[key] = []
        
        phase_durations[key].append(duration)
    
    # Calculate average durations
    avg_durations = []
    
    for key, durations in phase_durations.items():
        product_type, phase_name = key.split('__')
        avg_duration = sum(durations) / len(durations)
        
        avg_durations.append({
            'product_type': product_type.replace('_', ' ').title(),
            'phase_name': phase_name.replace('_', ' ').title(),
            'avg_hours': round(avg_duration, 2),
            'count': len(durations)
        })
    
    # Sort by average duration (descending)
    avg_durations.sort(key=lambda x: x['avg_hours'], reverse=True)
    
    return avg_durations[:10]  # Return top 10 longest phases


def get_quality_metrics():
    """Calculate quality control metrics and rejection rates"""
    # Get all QC phases
    qc_phases = BatchPhaseExecution.objects.filter(
        phase__phase_name__contains='qc_',
        status__in=['completed', 'failed']
    ).select_related('bmr__product')
    
    # Calculate rejection rates by product type
    product_types = {}
    
    for phase in qc_phases:
        product_type = phase.bmr.product.product_type
        
        if product_type not in product_types:
            product_types[product_type] = {
                'total': 0,
                'failed': 0
            }
        
        product_types[product_type]['total'] += 1
        if phase.status == 'failed':
            product_types[product_type]['failed'] += 1
    
    # Calculate rejection percentages
    result = {
        'labels': [],
        'pass_rates': [],
        'fail_rates': []
    }
    
    for product_type, data in product_types.items():
        if data['total'] > 0:
            result['labels'].append(product_type.replace('_', ' ').title())
            
            fail_rate = (data['failed'] / data['total']) * 100
            pass_rate = 100 - fail_rate
            
            result['pass_rates'].append(round(pass_rate, 1))
            result['fail_rates'].append(round(fail_rate, 1))
    
    return result


def get_productivity_metrics():
    """Calculate productivity metrics for operators and phases"""
    # Get phases from the last 30 days
    thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
    
    recent_phases = BatchPhaseExecution.objects.filter(
        completed_date__gte=thirty_days_ago,
        status='completed'
    ).select_related('phase', 'completed_by')
    
    # Group by operator
    operators = {}
    
    for phase in recent_phases:
        if not phase.completed_by:
            continue
        
        operator_name = phase.completed_by.get_full_name() or phase.completed_by.username
        
        if operator_name not in operators:
            operators[operator_name] = {
                'count': 0,
                'phases': {}
            }
        
        operators[operator_name]['count'] += 1
        
        phase_name = phase.phase.phase_name
        if phase_name not in operators[operator_name]['phases']:
            operators[operator_name]['phases'][phase_name] = 0
        
        operators[operator_name]['phases'][phase_name] += 1
    
    # Sort operators by completion count
    sorted_operators = sorted(operators.items(), key=lambda x: x[1]['count'], reverse=True)
    
    return {
        'top_operators': sorted_operators[:10],  # Top 10 operators
        'total_operators': len(operators),
        'total_completions': sum(op[1]['count'] for op in sorted_operators)
    }
