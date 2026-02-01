from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from .models import Complaint

@login_required
def submit_complaint(request):
    """Submit new complaint"""
    if request.method == 'POST':
        category = request.POST.get('category', '').strip()
        ward = request.POST.get('ward', '').strip()
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        
        # Validation
        if not category or not ward or not description:
            messages.error(request, 'Category, ward, and description are required.')
            return render(request, 'complaints/submit_complaint.html')
        
        if len(description) < 10:
            messages.error(request, 'Description must be at least 10 characters long.')
            return render(request, 'complaints/submit_complaint.html')
        
        # Image validation
        if image:
            if image.size > 5 * 1024 * 1024:  # 5MB
                messages.error(request, 'Image size must not exceed 5MB.')
                return render(request, 'complaints/submit_complaint.html')
            
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/jpg']
            if image.content_type not in allowed_types:
                messages.error(request, 'Only JPG, JPEG, PNG, and GIF images are allowed.')
                return render(request, 'complaints/submit_complaint.html')
        
        # Create complaint
        complaint = Complaint.objects.create(
            user=request.user,
            category=category,
            ward=ward,
            description=description,
            image=image
        )
        
        messages.success(request, f'✅ Complaint submitted successfully! Your complaint ID is #{complaint.id}')
        return redirect('my_complaints')
    
    return render(request, 'complaints/submit_complaint.html')


@login_required
def my_complaints(request):
    """View user's complaints with pagination and date filters"""
    # Optimized with select_related to prevent N+1 queries
    complaints_list = Complaint.objects.filter(user=request.user).select_related('user').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        complaints_list = complaints_list.filter(status=status_filter)
    
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
            from datetime import timedelta
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
        'from_date': from_date,
        'to_date': to_date,
        'paginator': paginator,
    }
    return render(request, 'complaints/my_complaints.html', context)


@login_required
def complaint_detail(request, pk):
    """View single complaint details"""
    complaint = get_object_or_404(Complaint, pk=pk, user=request.user)
    context = {
        'complaint': complaint
    }
    return render(request, 'complaints/complaint_detail.html', context)