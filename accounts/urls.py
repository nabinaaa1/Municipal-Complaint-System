from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.citizen_register, name='citizen_register'),
    path('login/', views.citizen_login, name='citizen_login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
]