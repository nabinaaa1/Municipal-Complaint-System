from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # Citizen URLs
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('my-complaints/', views.my_complaints, name='my_complaints'),
    path('detail/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    
    # Admin URLs
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/list/', admin_views.admin_complaint_list, name='admin_complaint_list'),
    path('admin/detail/<int:pk>/', admin_views.admin_complaint_detail, name='admin_complaint_detail'),
    path('admin/statistics/', admin_views.admin_statistics, name='admin_statistics'),
    path('admin/export-csv/', admin_views.export_complaints_csv, name='export_complaints_csv'),
]