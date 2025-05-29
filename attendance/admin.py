from django.contrib import admin
from .models import Department, Student, FingerPrint, Attendance

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'roll_number', 'department', 'joined_date', 'is_active')
    list_filter = ('department', 'is_active', 'joined_date')
    search_fields = ('name', 'roll_number')
    date_hierarchy = 'joined_date'

@admin.register(FingerPrint)
class FingerPrintAdmin(admin.ModelAdmin):
    list_display = ('student', 'finger_label', 'created_at')
    list_filter = ('finger_label', 'created_at')
    search_fields = ('student__name', 'student__roll_number')
    date_hierarchy = 'created_at'
    
    def has_change_permission(self, request, obj=None):
        # Prevent modifications to fingerprint data for security reasons
        return False

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'time', 'meal_type', 'is_present')
    list_filter = ('date', 'meal_type', 'is_present', 'student__department')
    search_fields = ('student__name', 'student__roll_number')
    date_hierarchy = 'date'
    raw_id_fields = ('student', 'fingerprint_used')