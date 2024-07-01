"""
URL configuration for TSC_Website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from TSC import views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.Home,name='home'),
    path('notice',views.Notices,name='notice'),
    
    path('AdminLogin/',views.AdminLogin,name="AdminLogin"),
    path('AdminLogout/',views.AdminLogout,name="AdminLogout"),
    
    path('register/', views.register, name='register'),
    path('login/', views.LogIn, name='login'),
    path('logout/',views.Logout,name="logout"),

    path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset.html'),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name='password_reset_complete'),


    path('room_list',views.Room_list,name="room_list"),
    
    path('Booking/<int:room_no>/',views.Bookin,name="Booking"),
    
    path('AddNotice/',views.AddNotice,name="AddNotice"),
    path('AddRoom/',views.AddRoom,name="AddRoom"),


    path('Booking_list/',views.Booking_list,name="Booking_list"),
    path('reject_booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('approve_booking/<int:booking_id>/', views.approve_booking, name='approve_booking'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
