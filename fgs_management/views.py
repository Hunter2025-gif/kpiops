from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import FGSInventory, ProductRelease, FGSAlert
from bmr.models import BMR
from products.models import Product
from workflow.models import BatchPhaseExecution

@login_required
def fgs_dashboard(request):
    """FGS Dashboard with inventory overview and statistics"""
    
    # Get basic inventory statistics
    total_inventory = FGSInventory.objects.count()
    available_inventory = FGSInventory.objects.filter(status='available').count()
    # Recent releases (last 7 days)
    recent_releases = ProductRelease.objects.filter(
        release_date__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Total quantity available by product
    inventory_by_product = FGSInventory.objects.filter(
        status__in=['stored', 'available']
    ).values(
        'product__product_name'
    ).annotate(
        total_quantity=Sum('quantity_available')
    ).order_by('-total_quantity')[:10]
    
    # Recent inventory additions
    recent_inventory = FGSInventory.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).order_by('-created_at')[:10]
    
    # Active alerts
    active_alerts = FGSAlert.objects.filter(is_resolved=False).order_by('-priority', '-created_at')[:10]
    
    # Monthly release trends (last 6 months)
    monthly_releases = []
    for i in range(6):
        month_start = (timezone.now() - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = ProductRelease.objects.filter(
            release_date__range=[month_start, month_end]
        ).aggregate(total=Sum('quantity_released'))['total'] or 0
        
        monthly_releases.append({
            'month': month_start.strftime('%b %Y'),
            'quantity': float(count)
        })
    
    monthly_releases.reverse()
    
    context = {
        'total_inventory': total_inventory,
        'available_inventory': available_inventory,
        'recent_releases': recent_releases,
        'inventory_by_product': inventory_by_product,
        'recent_inventory': recent_inventory,
        'active_alerts': active_alerts,
        'monthly_releases': monthly_releases,
    }
    
    return render(request, 'fgs_management/dashboard.html', context)

@login_required
def inventory_list(request):
    """List all FGS inventory with filtering"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    product_filter = request.GET.get('product', '')
    
    # Base queryset
    inventory = FGSInventory.objects.select_related('product', 'bmr').order_by('-created_at')
    
    # Apply filters
    if status_filter:
        inventory = inventory.filter(status=status_filter)
    
    if product_filter:
        inventory = inventory.filter(product__id=product_filter)
    
    # Get filter options
    products = Product.objects.all().order_by('product_name')
    status_choices = FGSInventory.STATUS_CHOICES
    
    context = {
        'inventory_items': inventory,
        'products': products,
        'status_choices': status_choices,
        'status_filter': status_filter,
        'product_filter': product_filter,
    }
    
    return render(request, 'fgs_management/inventory_list.html', context)

@login_required
def release_list(request):
    """List all product releases with filtering"""
    from django.db.models import Count, Sum
    
    # Get filter parameters
    release_type_filter = request.GET.get('release_type', '')
    date_filter = request.GET.get('date_filter', '')
    product_filter = request.GET.get('product', '')
    batch_filter = request.GET.get('batch', '')
    date_from = request.GET.get('date_from', '')
    
    # Base queryset
    releases = ProductRelease.objects.select_related(
        'inventory__product', 'inventory__bmr', 'authorized_by'
    ).order_by('-release_date')
    
    # Apply filters
    if release_type_filter:
        releases = releases.filter(release_type=release_type_filter)
    
    if product_filter:
        releases = releases.filter(inventory__product__product_name__icontains=product_filter)
    
    if batch_filter:
        releases = releases.filter(inventory__batch_number__icontains=batch_filter)
    
    if date_from:
        releases = releases.filter(release_date__date__gte=date_from)
    
    if date_filter == 'today':
        releases = releases.filter(release_date__date=timezone.now().date())
    elif date_filter == 'week':
        releases = releases.filter(release_date__gte=timezone.now() - timedelta(days=7))
    elif date_filter == 'month':
        releases = releases.filter(release_date__gte=timezone.now() - timedelta(days=30))
    
    # Calculate statistics
    all_releases = ProductRelease.objects.all()
    stats = {
        'total_releases': all_releases.count(),
        'sales_count': all_releases.filter(release_type='sale').count(),
        'transfers_count': all_releases.filter(release_type='transfer').count(),
        'total_value': all_releases.aggregate(total=Sum('total_value'))['total'] or 0,
    }
    
    # Get filter options
    release_type_choices = ProductRelease.RELEASE_TYPE_CHOICES
    
    context = {
        'releases': releases,
        'stats': stats,
        'release_type_choices': release_type_choices,
        'release_type_filter': release_type_filter,
        'date_filter': date_filter,
    }
    
    return render(request, 'fgs_management/release_list.html', context)

@login_required
def create_release(request, inventory_id):
    """Create a new product release"""
    
    inventory = get_object_or_404(FGSInventory, id=inventory_id)
    
    if request.method == 'POST':
        # For debugging
        print("Form data:", request.POST)
        
        # Get form data
        release_type = request.POST.get('release_type')
        quantity_released = float(request.POST.get('quantity_released'))
        
        # Use release_certificate_number as release_reference if it's not provided
        release_reference = request.POST.get('release_reference')
        if not release_reference:
            release_reference = request.POST.get('release_certificate_number')
            
        release_certificate_number = request.POST.get('release_certificate_number')
        customer_name = request.POST.get('customer_name', '')
        customer_contact = request.POST.get('customer_contact', '')
        delivery_address = request.POST.get('delivery_address', '')
        unit_price = request.POST.get('unit_price')
        notes = request.POST.get('notes', '')
        
        # Validate quantity
        if quantity_released > inventory.quantity_available:
            messages.error(request, 'Release quantity cannot exceed available quantity.')
            return redirect('fgs_management:inventory_list')
        
        # Create release
        release = ProductRelease.objects.create(
            inventory=inventory,
            release_type=release_type,
            quantity_released=quantity_released,
            release_reference=release_reference,
            customer_name=customer_name,
            customer_contact=customer_contact,
            delivery_address=delivery_address,
            unit_price=float(unit_price) if unit_price else None,
            authorized_by=request.user,
            created_by=request.user,
            notes=notes
        )
        
        # Update inventory with the release certificate number
        inventory.release_certificate_number = release_certificate_number
        inventory.save()
        
        messages.success(request, f'Product release {release_reference} created successfully.')
        return redirect('fgs_management:release_list')
    
    context = {
        'inventory': inventory,
        'release_type_choices': ProductRelease.RELEASE_TYPE_CHOICES,
    }
    
    return render(request, 'fgs_management/create_release.html', context)

@login_required
def create_inventory_from_fgs(request, phase_id):
    """Create inventory entry from completed FGS phase"""
    
    phase = get_object_or_404(BatchPhaseExecution, id=phase_id)
    
    if phase.phase.phase_name != 'finished_goods_store' or phase.status != 'completed':
        messages.error(request, 'Can only create inventory from completed FGS phases.')
        return redirect('dashboards:finished_goods_dashboard')
    
    # Check if inventory already exists
    existing_inventory = FGSInventory.objects.filter(bmr=phase.bmr).first()
    if existing_inventory:
        messages.warning(request, f'Inventory already exists for batch {phase.bmr.batch_number}.')
        return redirect('dashboards:finished_goods_dashboard')
    
    if request.method == 'POST':
        # Get form data
        release_certificate = request.POST.get('release_certificate', '')
        
        # Create inventory entry - quantity comes automatically from BMR batch_size
        inventory = FGSInventory.objects.create(
            bmr=phase.bmr,
            product=phase.bmr.product,
            batch_number=phase.bmr.batch_number,
            quantity_available=phase.bmr.batch_size,  # Use BMR batch size
            release_certificate_number=release_certificate,
            qa_approved_by=request.user,
            qa_approval_date=timezone.now(),
            status='available',
            created_by=request.user
        )
        
        messages.success(request, f'Inventory created for batch {phase.bmr.batch_number}. Available for release.')
        return redirect('dashboards:finished_goods_dashboard')
    
    context = {
        'phase': phase,
        'bmr': phase.bmr,
    }
    
    return render(request, 'fgs_management/create_inventory.html', context)

@login_required
def quick_release(request, inventory_id):
    """Quick release form for products"""
    from decimal import Decimal
    
    inventory = get_object_or_404(FGSInventory, id=inventory_id)
    
    if request.method == 'POST':
        # Get form data
        release_type = request.POST.get('release_type', 'sale')
        quantity_released = Decimal(request.POST.get('quantity_released'))
        release_reference = request.POST.get('release_reference')
        customer_name = request.POST.get('customer_name', '')
        customer_contact = request.POST.get('customer_contact', '')
        unit_price = request.POST.get('unit_price')
        notes = request.POST.get('notes', '')
        
        # Validate quantity
        if quantity_released > inventory.quantity_available:
            messages.error(request, 'Release quantity cannot exceed available quantity.')
            return redirect('dashboards:finished_goods_dashboard')
        
        # Create release
        release = ProductRelease.objects.create(
            inventory=inventory,
            release_type=release_type,
            quantity_released=quantity_released,
            release_reference=release_reference,
            customer_name=customer_name,
            customer_contact=customer_contact,
            unit_price=Decimal(unit_price) if unit_price else None,
            authorized_by=request.user,
            created_by=request.user,
            notes=notes
        )
        
        # Update inventory status if fully released
        if inventory.quantity_available == 0:
            inventory.status = 'released'
            inventory.save()
        
        messages.success(request, f'Release {release_reference} created successfully. {quantity_released} {inventory.unit_of_measure} released.')
        return redirect('dashboards:finished_goods_dashboard')
    
    context = {
        'inventory': inventory,
        'release_type_choices': ProductRelease.RELEASE_TYPE_CHOICES,
    }
    
    return render(request, 'fgs_management/quick_release.html', context)


@login_required
def inventory_analytics(request):
    """Analytics dashboard for FGS inventory data"""
    
    # Basic statistics
    total_inventory_items = FGSInventory.objects.count()
    total_quantity = FGSInventory.objects.aggregate(
        total=Sum('quantity_available')
    )['total'] or 0
    
    # Status distribution
    status_distribution = FGSInventory.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Product-wise inventory
    product_inventory = FGSInventory.objects.values(
        'product__product_name'
    ).annotate(
        total_quantity=Sum('quantity_available'),
        item_count=Count('id')
    ).order_by('-total_quantity')[:10]
    
    # Monthly release trends (last 6 months)
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_releases = ProductRelease.objects.filter(
        release_date__gte=six_months_ago
    ).extra(
        select={'month': "strftime('%%Y-%%m', release_date)"}
    ).values('month').annotate(
        total_released=Sum('quantity_released'),
        release_count=Count('id')
    ).order_by('month')
    
    context = {
        'total_inventory_items': total_inventory_items,
        'total_quantity': total_quantity,
        'status_distribution': status_distribution,
        'product_inventory': product_inventory,
        'monthly_releases': monthly_releases,
    }
    
    return render(request, 'fgs_management/analytics.html', context)
