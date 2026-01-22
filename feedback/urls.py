from django.urls import path
from . import views

urlpatterns = [
    path('submit/<int:complaint_id>/', views.submit_feedback, name='submit_feedback'),
    path('my-feedback/', views.my_feedback, name='my_feedback'),
]