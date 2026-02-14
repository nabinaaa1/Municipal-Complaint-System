from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
import csv
from .models import Complaint, Remark  
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
    
    # Auto-update priorities for old complaints
    old_complaints = Complaint.objects.filter(
        status__in=['Pending', 'In Progress']
    ).exclude(status='Resolved')
    
    for complaint in old_complaints:
        complaint.update_priority()
    
    # Get statistics
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='Pending').count()
    in_progress_complaints = Complaint.objects.filter(status='In Progress').count()
    resolved_complaints = Complaint.objects.filter(status='Resolved').count()
    
    # Ward-wise statistics
    ward_stats = []
    for i in range(1, 16):
        count = Complaint.objects.filter(ward=str(i)).count()
        percentage = (count / total_complaints * 100) if total_complaints > 0 else 0
        ward_stats.append({
            'ward': i,
            'count': count,
            'percentage': percentage
        })
    
    # Category-wise statistics
    category_stats = Complaint.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent complaints
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
    """Admin view to list and filter all complaints"""
    
    # Auto-update priorities
    old_complaints = Complaint.objects.filter(
        status__in=['Pending', 'In Progress']
    )
    for complaint in old_complaints:
        complaint.update_priority()
    
    # Get all complaints
    complaints_list = Complaint.objects.select_related('user').order_by('-created_at')
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter:
        complaints_list = complaints_list.filter(status=status_filter)
    
    ward_filter = request.GET.get('ward')
    if ward_filter:
        complaints_list = complaints_list.filter(ward=ward_filter)
    
    category_filter = request.GET.get('category')
    if category_filter:
        complaints_list = complaints_list.filter(category=category_filter)
    
    search = request.GET.get('search')
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
            from datetime import timedelta
            to_date_obj = to_date_obj + timedelta(days=1)
            complaints_list = complaints_list.filter(created_at__lt=to_date_obj)
        except ValueError:
            messages.error(request, 'Invalid to date format.')
    
    # Pagination
    paginator = Paginator(complaints_list, 15)  # 15 complaints per page
    page = request.GET.get('page')
    
    try:
        complaints = paginator.page(page)
    except PageNotAnInteger:
        complaints = paginator.page(1)
    except EmptyPage:
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
    """Admin view to see complaint details, update status, and manage remarks"""
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Auto-update priority
    complaint.update_priority()
    
    # Handle status update
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
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
        
        elif action == 'add_remark':
            remark_text = request.POST.get('remark', '').strip()
            
            if remark_text:
                if len(remark_text) < 5:
                    messages.error(request, 'Remark must be at least 5 characters long.')
                else:
                    # Create new remark
                    Remark.objects.create(
                        complaint=complaint,
                        admin_user=request.user,
                        remark=remark_text
                    )
                    messages.success(request, '✅ Internal remark added successfully!')
                    return redirect('admin_complaint_detail', pk=pk)
            else:
                messages.error(request, 'Remark cannot be empty.')
    
    # Get all remarks for this complaint
    remarks = complaint.remarks.select_related('admin_user').all()
    
    context = {
        'complaint': complaint,
        'remarks': remarks,
    }
    
    return render(request, 'complaints/admin_complaint_detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_statistics(request):
    """Detailed statistics page"""
    
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status='Pending').count()
    in_progress_complaints = Complaint.objects.filter(status='In Progress').count()
    resolved_complaints = Complaint.objects.filter(status='Resolved').count()
    
    # Calculate percentages
    pending_percentage = (pending_complaints / total_complaints * 100) if total_complaints > 0 else 0
    in_progress_percentage = (in_progress_complaints / total_complaints * 100) if total_complaints > 0 else 0
    resolved_percentage = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
    
    # Time-based statistics
    now = timezone.now()
    last_7_days = Complaint.objects.filter(created_at__gte=now - timedelta(days=7)).count()
    last_30_days = Complaint.objects.filter(created_at__gte=now - timedelta(days=30)).count()
    
    # Resolution rate
    resolution_rate = (resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0
    
    # Ward-wise detailed statistics
    ward_statistics = []
    for i in range(1, 16):
        ward_complaints = Complaint.objects.filter(ward=str(i))
        total = ward_complaints.count()
        pending = ward_complaints.filter(status='Pending').count()
        in_progress = ward_complaints.filter(status='In Progress').count()
        resolved = ward_complaints.filter(status='Resolved').count()
        percentage = (total / total_complaints * 100) if total_complaints > 0 else 0
        
        ward_statistics.append({
            'ward': i,
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'resolved': resolved,
            'percentage': percentage
        })
    
    # Category-wise detailed statistics
    categories = ['Road Maintenance', 'Street Light', 'Water Supply', 'Sanitation', 'Traffic', 'Parks', 'Other']
    category_statistics = []
    for category in categories:
        category_complaints = Complaint.objects.filter(category=category)
        total = category_complaints.count()
        pending = category_complaints.filter(status='Pending').count()
        in_progress = category_complaints.filter(status='In Progress').count()
        resolved = category_complaints.filter(status='Resolved').count()
        percentage = (total / total_complaints * 100) if total_complaints > 0 else 0
        
        category_statistics.append({
            'category': category,
            'total': total,
            'pending': pending,
            'in_progress': in_progress,
            'resolved': resolved,
            'percentage': percentage
        })
    
    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_percentage': pending_percentage,
        'in_progress_percentage': in_progress_percentage,
        'resolved_percentage': resolved_percentage,
        'last_7_days': last_7_days,
        'last_30_days': last_30_days,
        'resolution_rate': resolution_rate,
        'ward_statistics': ward_statistics,
        'category_statistics': category_statistics,
    }
    
    return render(request, 'complaints/admin_statistics.html', context)


@login_required
@user_passes_test(is_admin)
def export_complaints_csv(request):
    """Export complaints to CSV"""
    
    # Get filtered complaints
    complaints = Complaint.objects.select_related('user').order_by('-created_at')
    
    # Apply same filters as in admin_complaint_list
    status_filter = request.GET.get('status')
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    ward_filter = request.GET.get('ward')
    if ward_filter:
        complaints = complaints.filter(ward=ward_filter)
    
    category_filter = request.GET.get('category')
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    
    search = request.GET.get('search')
    if search:
        complaints = complaints.filter(
            Q(description__icontains=search) |
            Q(user__fullname__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d')
            complaints = complaints.filter(created_at__gte=from_date_obj)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d')
            from datetime import timedelta
            to_date_obj = to_date_obj + timedelta(days=1)
            complaints = complaints.filter(created_at__lt=to_date_obj)
        except ValueError:
            pass
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="complaints_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Citizen Name', 'Email', 'Phone', 'Ward', 'Category', 'Priority', 'Description', 'Status', 'Days Old', 'Created At', 'Updated At'])
    
    for complaint in complaints:
        writer.writerow([
            complaint.id,
            complaint.user.fullname,
            complaint.user.email,
            complaint.user.phone or 'N/A',
            f'Ward {complaint.ward}',
            complaint.category,
            complaint.priority,
            complaint.description,
            complaint.status,
            complaint.days_since_creation(),
            complaint.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            complaint.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    
    return response