from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_student, name='register_student'),
    path('register/fingerprint/<int:student_id>/', views.register_fingerprint, name='register_fingerprint'),
    path('attendance/', views.take_attendance, name='take_attendance'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('report/', views.attendance_report, name='attendance_report'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]