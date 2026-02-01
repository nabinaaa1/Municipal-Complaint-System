from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Complaint
from accounts.models import User
from datetime import datetime, timedelta
from django.utils import timezone

def is_admin(user):
    """Check if user is staff/admin"""
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    
    # Overall statistics
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='Pending').count()
    in_progress_complaints = Complaint.objects.filter(status='In Progress').count()
    resolved_complaints = Complaint.objects.filter(status='Resolved').count()
    
    # Ward-wise statistics (optimized with single query)
    ward_stats = []
    for i in range(1, 16):
        ward_count = Complaint.objects.filter(ward=str(i)).count()
        ward_stats.append({
            'ward': i,
            'count': ward_count,
            'percentage': (ward_count / total_complaints * 100) if total_complaints > 0 else 0
        })
    
    # Category-wise statistics
    category_stats = Complaint.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent complaints (optimized with select_related)
    recent_complaints = Complaint.objects.select_related('user').order_by('-created_at')[:10]
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'resolved_complaints': resolved_complaints,
        'ward_stats': ward_stats,
        'category_stats': category_stats,
        'recent_complaints': recent_complaints,
    }
    
    return render(request, 'complaints/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_complaint_list(request):
    """Admin view to list and filter all complaints with pagination and date filters"""
    
    # Start with all complaints, optimized with select_related
    complaints_list = Complaint.objects.select_related('user').order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status')
    ward_filter = request.GET.get('ward')
    category_filter = request.GET.get('category')
    search = request.GET.get('search')
    
    if status_filter:
        complaints_list = complaints_list.filter(status=status_filter)
    
    if ward_filter:
        complaints_list = complaints_list.filter(ward=ward_filter)
    
    if category_filter:
        complaints_list = complaints_list.filter(category=category_filter)
    
    if search:
        complaints_list = complaints_list.filter(
            Q(description__icontains=search) | 
            Q(user__fullname__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    # Date range filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            complaints_list = complaints_list.filter(created_at__gte=from_date_obj)
        except ValueError:
            messages.error(request, 'Invalid from date format.')
    
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            # Add one day to include the entire to_date
            to_date_obj = to_date_obj + timedelta(days=1)
            complaints_list = complaints_list.filter(created_at__lt=to_date_obj)
        except ValueError:
            messages.error(request, 'Invalid to date format.')
    
    # Pagination - 10 complaints per page
    paginator = Paginator(complaints_list, 10)
    page = request.GET.get('page')
    
    try:
        complaints = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        complaints = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        complaints = paginator.page(paginator.num_pages)
    
    context = {
        'complaints': complaints,
        'status_filter': status_filter,
        'ward_filter': ward_filter,
        'category_filter': category_filter,
        'search': search,
        'from_date': from_date,
        'to_date': to_date,
        'paginator': paginator,
    }
    
    return render(request, 'complaints/admin_complaint_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_complaint_detail(request, pk):
    """Admin view to see complaint details and update status"""
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status in ['Pending', 'In Progress', 'Resolved']:
            old_status = complaint.status
            complaint.status = new_status
            complaint.save()
            
            messages.success(
                request, 
                f'✅ Complaint #{complaint.id} status updated from "{old_status}" to "{new_status}"'
            )
            return redirect('admin_complaint_detail', pk=pk)
        else:
            messages.error(request, 'Invalid status value.')
    
    context = {
        'complaint': complaint
    }
    
    return render(request, 'complaints/admin_complaint_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_statistics(request):
    """Detailed statistics view for admin"""
    
    # Overall statistics
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='Pending').count()
    in_progress_complaints = Complaint.objects.filter(status='In Progress').count()
    resolved_complaints = Complaint.objects.filter(status='Resolved').count()
    
    # Calculate percentages
    pending_percentage = (pending_complaints / total_complaints * 100) if total_complaints > 0 else 0
    in_progress_percentage = (in_progress_complaints / total_complaints * 100) if total_complaints > 0 else 0
    resolved_percentage = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
    
    # Ward-wise detailed statistics
    ward_statistics = []
    for i in range(1, 16):
        ward_num = str(i)
        ward_total = Complaint.objects.filter(ward=ward_num).count()
        ward_pending = Complaint.objects.filter(ward=ward_num, status='Pending').count()
        ward_in_progress = Complaint.objects.filter(ward=ward_num, status='In Progress').count()
        ward_resolved = Complaint.objects.filter(ward=ward_num, status='Resolved').count()
        
        ward_statistics.append({
            'ward': i,
            'total': ward_total,
            'pending': ward_pending,
            'in_progress': ward_in_progress,
            'resolved': ward_resolved,
            'percentage': (ward_total / total_complaints * 100) if total_complaints > 0 else 0
        })
    
    # Category-wise detailed statistics
    category_statistics = []
    categories = ['Road Maintenance', 'Street Light', 'Water Supply', 'Sanitation', 'Traffic', 'Parks', 'Other']
    
    for category in categories:
        cat_total = Complaint.objects.filter(category=category).count()
        cat_pending = Complaint.objects.filter(category=category, status='Pending').count()
        cat_in_progress = Complaint.objects.filter(category=category, status='In Progress').count()
        cat_resolved = Complaint.objects.filter(category=category, status='Resolved').count()
        
        category_statistics.append({
            'category': category,
            'total': cat_total,
            'pending': cat_pending,
            'in_progress': cat_in_progress,
            'resolved': cat_resolved,
            'percentage': (cat_total / total_complaints * 100) if total_complaints > 0 else 0
        })
    
    # Time-based statistics (last 7 days, 30 days, all time)
    now = timezone.now()
    last_7_days = Complaint.objects.filter(created_at__gte=now - timedelta(days=7)).count()
    last_30_days = Complaint.objects.filter(created_at__gte=now - timedelta(days=30)).count()
    
    # Resolution rate
    resolution_rate = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_percentage': pending_percentage,
        'in_progress_percentage': in_progress_percentage,
        'resolved_percentage': resolved_percentage,
        'ward_statistics': ward_statistics,
        'category_statistics': category_statistics,
        'last_7_days': last_7_days,
        'last_30_days': last_30_days,
        'resolution_rate': resolution_rate,
    }
    
    return render(request, 'complaints/admin_statistics.html', context)