from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('detail/<int:pk>/', views.complaint_detail, name='complaint_detail'),
]