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
def admin_complaint_detail(request, pk):
    """Admin view to see complaint details, update status, and manage remarks"""
    
    complaint = get_object_or_404(Complaint, pk=pk)
    
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


