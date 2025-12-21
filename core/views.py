from django.shortcuts import render, redirect

def home(request):
    """Home page view"""
    # Redirect logged-in users to their dashboard
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('/admin/')
        else:
            return redirect('citizen_dashboard')
    
    return render(request, 'core/home.html')