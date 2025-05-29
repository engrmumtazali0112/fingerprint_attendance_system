# Project-level URLs (fingerprint_attendance_system/urls.py)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin-panal/', admin.site.urls),
    path('', include('attendance.urls')),
]