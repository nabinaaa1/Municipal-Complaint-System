from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from .models import Complaint
from accounts.models import User

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
    """Admin view to list and filter all complaints"""
    
    # Start with all complaints, optimized with select_related
    complaints = Complaint.objects.select_related('user').order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status')
    ward_filter = request.GET.get('ward')
    category_filter = request.GET.get('category')
    search = request.GET.get('search')
    
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    
    if ward_filter:
        complaints = complaints.filter(ward=ward_filter)
    
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    
    if search:
        complaints = complaints.filter(
            Q(description__icontains=search) | 
            Q(user__fullname__icontains=search) |
            Q(user__email__icontains=search)
        )
    
    context = {
        'complaints': complaints,
        'status_filter': status_filter,
        'ward_filter': ward_filter,
        'category_filter': category_filter,
        'search': search,
    }
    
    return render(request, 'complaints/admin_complaint_list.html', context)


@login_required
@user_passes_test(is_admin)
def admin_complaint_detail(request, pk):
    """Admin view to see complaint details and update status"""
    
    complaint = get_object_or_404(Complaint.select_related('user'), pk=pk)
    
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