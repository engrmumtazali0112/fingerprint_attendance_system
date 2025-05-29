from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
import logging
import base64
import json
from . import views

from .models import Student, Attendance, FingerPrint, Department
from .forms import StudentRegistrationForm, FingerPrintRegistrationForm, AttendanceSearchForm
from .fingerprint_utils import FingerprintProcessor

# Set up logging
logger = logging.getLogger(__name__)

def index(request):
    """Home page view"""
    total_students = Student.objects.filter(is_active=True).count()
    today = timezone.now().date()
    
    # Get today's attendance counts by meal
    breakfast_count = Attendance.objects.filter(date=today, meal_type='breakfast').count()
    lunch_count = Attendance.objects.filter(date=today, meal_type='lunch').count()
    dinner_count = Attendance.objects.filter(date=today, meal_type='dinner').count()
    
    context = {
        'total_students': total_students,
        'breakfast_count': breakfast_count,
        'lunch_count': lunch_count,
        'dinner_count': dinner_count,
        'today': today,
    }
    
    return render(request, 'attendance/index.html', context)

def register_student(request):
    """Register a new student view"""
    if request.method == 'POST':
        student_form = StudentRegistrationForm(request.POST)
        if student_form.is_valid():
            student = student_form.save()
            messages.success(request, f'Student {student.name} registered successfully. Now add fingerprint data.')
            return redirect('register_fingerprint', student_id=student.id)
    else:
        student_form = StudentRegistrationForm()
    
    return render(request, 'attendance/register.html', {
        'form': student_form,
        'title': 'Register New Student'
    })

def register_fingerprint(request, student_id):
    """Register fingerprint for a student"""
    student = get_object_or_404(Student, id=student_id)
    
    if request.method == 'POST':
        form = FingerPrintRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Get fingerprint data from the hidden field in the form
                fingerprint_data = request.POST.get('fingerprint_data')
                
                # Log the data type and first few characters for debugging
                logger.debug(f"Received fingerprint data type: {type(fingerprint_data)}")
                if fingerprint_data:
                    logger.debug(f"First 20 chars: {fingerprint_data[:20]}...")
                else:
                    logger.error("No fingerprint data received")
                    messages.error(request, 'No fingerprint data received. Please try again.')
                    return redirect('register_fingerprint', student_id=student.id)
                
                # Process the fingerprint data
                try:
                    processed_data = FingerprintProcessor.process_fingerprint_image(fingerprint_data)
                    
                    # Save the fingerprint data
                    fingerprint = FingerPrint(
                        student=student,
                        fingerprint_data=processed_data,  # Processed fingerprint data
                        finger_label=form.cleaned_data['finger_label']
                    )
                    fingerprint.save()
                    
                    messages.success(request, f'Fingerprint registered successfully for {student.name}.')
                    
                    # Check if more fingerprints are needed
                    if FingerPrint.objects.filter(student=student).count() < 2:
                        messages.info(request, 'Consider registering another finger as backup.')
                        return redirect('register_fingerprint', student_id=student.id)
                    else:
                        return redirect('student_list')
                        
                except ValueError as e:
                    logger.error(f"Fingerprint processing error: {str(e)}")
                    messages.error(request, f'Error processing fingerprint: {str(e)}')
                    return redirect('register_fingerprint', student_id=student.id)
                    
            except Exception as e:
                logger.exception("Unexpected error during fingerprint registration")
                messages.error(request, f'An unexpected error occurred: {str(e)}')
                return redirect('register_fingerprint', student_id=student.id)
        else:
            logger.warning(f"Form validation errors: {form.errors}")
    else:
        form = FingerPrintRegistrationForm()
    
    # Get already registered fingerprints
    registered_prints = FingerPrint.objects.filter(student=student)
    
    return render(request, 'attendance/register_fingerprint.html', {
        'form': form,
        'student': student,
        'registered_prints': registered_prints,
        'title': f'Register Fingerprint for {student.name}'
    })

def login_view(request):
    """Custom login view"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('index')  # Redirect to home page after login
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'attendance/login.html', {'form': form})

@csrf_exempt  # For fingerprint submit via AJAX
def take_attendance(request):
    """Handle the fingerprint scan and attendance record"""
    current_time = timezone.now().time()
    meal_type = "breakfast" if current_time.hour < 10 else "lunch" if current_time.hour < 15 else "dinner"

    if request.method == 'POST':
        try:
            # Check if this is a JSON request
            content_type = request.META.get('CONTENT_TYPE', '')
            if 'application/json' in content_type:
                # Parse JSON data
                data = json.loads(request.body)
                fingerprint_data = data.get('fingerprint_data')
            else:
                # Handle form data
                fingerprint_data = request.POST.get('fingerprint_data')
                
            logger.debug(f"Received fingerprint data for attendance (first 20 chars): {fingerprint_data[:20] if fingerprint_data else 'None'}")
            
            if not fingerprint_data:
                logger.error("No fingerprint data received for attendance")
                return JsonResponse({'status': 'error', 'message': 'No fingerprint data received'})
            
            try:
                # Process fingerprint data
                processed_data = FingerprintProcessor.process_fingerprint_image(fingerprint_data)

                # Match the fingerprint
                is_match, student_id, fingerprint_id = FingerprintProcessor.match_fingerprint(processed_data)

                if not is_match:
                    logger.warning("No matching fingerprint found during attendance")
                    return JsonResponse({'status': 'error', 'message': 'No matching fingerprint found. Try again.'})

                student = Student.objects.get(id=student_id)
                fingerprint = FingerPrint.objects.get(id=fingerprint_id)
                
                logger.info(f"Found matching fingerprint for student: {student.name}")

                # Record attendance
                today = timezone.now().date()
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    date=today,
                    meal_type=meal_type,
                    defaults={'time': timezone.now().time(), 'is_present': True, 'fingerprint_used': fingerprint}
                )

                if not created:
                    logger.info(f"Attendance already recorded for {student.name} - {meal_type}")
                    return JsonResponse({
                        'status': 'warning', 
                        'message': f'Attendance for {student.name} already recorded for {meal_type} today.',
                        'student_name': student.name,
                        'roll_number': student.roll_number,
                        'department': student.department.name,
                        'meal_type': meal_type
                    })

                logger.info(f"Attendance recorded for {student.name} - {meal_type}")
                return JsonResponse({
                    'status': 'success',
                    'message': f'Attendance recorded for {student.name}',
                    'student_name': student.name,
                    'roll_number': student.roll_number,
                    'department': student.department.name,
                    'meal_type': meal_type
                })
            except ValueError as e:
                logger.error(f"Error processing attendance fingerprint: {str(e)}")
                return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})
        except Exception as e:
            logger.exception(f"Unexpected error in take_attendance: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Unexpected error: {str(e)}'})

    return render(request, 'attendance/take_attendance.html', {'meal_type': meal_type.capitalize()})

@login_required
def student_list(request):
    """View list of all students"""
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', '')
    
    students = Student.objects.filter(is_active=True)
    
    if query:
        students = students.filter(
            Q(name__icontains=query) | Q(roll_number__icontains=query)
        )
    
    if department_id:
        students = students.filter(department_id=department_id)
    
    departments = Department.objects.all()
    
    return render(request, 'attendance/student_list.html', {
        'students': students,
        'departments': departments,
        'query': query,
        'selected_department': department_id,
        'title': 'Student List'
    })

@login_required
def attendance_report(request):
    """Generate attendance report"""
    form = AttendanceSearchForm(request.GET or None)
    attendances = []
    
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        department = form.cleaned_data['department']
        roll_number = form.cleaned_data['roll_number']
        meal_type = form.cleaned_data['meal_type']
        
        # Base query
        query = Attendance.objects.filter(date__range=[start_date, end_date])
        
        # Apply filters
        if department:
            query = query.filter(student__department=department)
        
        if roll_number:
            query = query.filter(student__roll_number__icontains=roll_number)
        
        if meal_type:
            query = query.filter(meal_type=meal_type)
        
        # Get results
        attendances = query.select_related('student', 'student__department').order_by('-date', 'meal_type')
    
    context = {
        'form': form,
        'attendances': attendances,
        'title': 'Attendance Report'
    }
    
    return render(request, 'attendance/attendance_report.html', context)

@login_required
def student_detail(request, student_id):
    """View student details and fingerprint information"""
    student = get_object_or_404(Student, id=student_id)
    fingerprints = FingerPrint.objects.filter(student=student)
    
    # Get recent attendance
    recent_attendance = Attendance.objects.filter(
        student=student
    ).order_by('-date', '-time')[:10]
    
    context = {
        'student': student,
        'fingerprints': fingerprints,
        'recent_attendance': recent_attendance,
        'title': f'Student: {student.name}'
    }
    
    return render(request, 'attendance/student_details.html', context)