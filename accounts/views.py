from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import User

def citizen_register(request):
    """Citizen registration view"""
    if request.user.is_authenticated:
        return redirect('citizen_dashboard')
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip()
        ward = request.POST.get('ward', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        if not all([fullname, email, password, confirm_password]):
            messages.error(request, 'All required fields must be filled.')
            return render(request, 'accounts/register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'accounts/register.html')
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            fullname=fullname,
            ward=ward,
            phone=phone,
            password=password
        )
        
        login(request, user)
        messages.success(request, f'Welcome {fullname}! Your account has been created.')
        return redirect('citizen_dashboard')
    
    return render(request, 'accounts/register.html')


def citizen_login(request):
    """Citizen login view"""
    if request.user.is_authenticated:
        return redirect('citizen_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not email or not password:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'accounts/login.html')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.fullname}!')
            return redirect('citizen_dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html')


def user_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def citizen_dashboard(request):
    """Citizen dashboard"""
    if not request.user.is_authenticated:
        return redirect('citizen_login')
    
    # Get user's complaints statistics
    from complaints.models import Complaint
    from django.db.models import Count, Q
    
    stats = Complaint.objects.filter(user=request.user).aggregate(
        pending=Count('id', filter=Q(status='Pending')),
        in_progress=Count('id', filter=Q(status='In Progress')),
        resolved=Count('id', filter=Q(status='Resolved'))
    )
    
    # Optimized with select_related to prevent N+1 queries
    recent_complaints = Complaint.objects.filter(user=request.user).select_related('user').order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'recent_complaints': recent_complaints
    }
    return render(request, 'accounts/dashboard.html', context)