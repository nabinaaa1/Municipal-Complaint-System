from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Feedback
from complaints.models import Complaint

@login_required
def submit_feedback(request, complaint_id):
    """Submit feedback for a resolved complaint"""
    complaint = get_object_or_404(Complaint, pk=complaint_id, user=request.user)
    
    # Check if complaint is resolved
    if complaint.status != 'Resolved':
        messages.error(request, 'You can only give feedback on resolved complaints.')
        return redirect('complaint_detail', pk=complaint_id)
    
    # Check if feedback already exists
    if Feedback.objects.filter(complaint=complaint, user=request.user).exists():
        messages.warning(request, 'You have already submitted feedback for this complaint.')
        return redirect('complaint_detail', pk=complaint_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        message = request.POST.get('message', '').strip()
        
        # Validation
        if not rating:
            messages.error(request, 'Please select a rating.')
            return render(request, 'feedback/submit_feedback.html', {'complaint': complaint})
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                messages.error(request, 'Rating must be between 1 and 5.')
                return render(request, 'feedback/submit_feedback.html', {'complaint': complaint})
        except ValueError:
            messages.error(request, 'Invalid rating value.')
            return render(request, 'feedback/submit_feedback.html', {'complaint': complaint})
        
        if not message:
            messages.error(request, 'Please provide a feedback message.')
            return render(request, 'feedback/submit_feedback.html', {'complaint': complaint})
        
        if len(message) < 10:
            messages.error(request, 'Feedback message must be at least 10 characters.')
            return render(request, 'feedback/submit_feedback.html', {'complaint': complaint})
        
        # Create feedback
        Feedback.objects.create(
            user=request.user,
            complaint=complaint,
            rating=rating,
            message=message
        )
        
        messages.success(request, f'✅ Thank you for your feedback! You rated {rating} stars.')
        return redirect('complaint_detail', pk=complaint_id)
    
    context = {
        'complaint': complaint
    }
    return render(request, 'feedback/submit_feedback.html', context)


@login_required
def my_feedback(request):
    """View all feedback submitted by user"""
    feedbacks = Feedback.objects.filter(user=request.user).select_related('complaint').order_by('-created_at')
    
    context = {
        'feedbacks': feedbacks
    }
    return render(request, 'feedback/my_feedback.html', context)