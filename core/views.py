from django.shortcuts import render, redirect

def home(request):
    """Home page view"""
    # Redirect logged-in users to their dashboard
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            return redirect('citizen_dashboard')
    
    return render(request, 'core/home.html')


def set_language(request):
    """Set user's language preference"""
    lang = request.GET.get('lang', 'en')
    
    if lang in ['en', 'ne']:
        request.session['language'] = lang
    
    # Redirect back to the previous page
    return redirect(request.META.get('HTTP_REFERER', '/'))