from django.db import models
from django.utils import timezone

# Department Model
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Student Model
class Student(models.Model):
    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    joined_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.roll_number})"


# FingerPrint Model
class FingerPrint(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fingerprints')
    fingerprint_data = models.BinaryField()  # Store fingerprint template as binary data
    finger_label = models.CharField(max_length=20, default="Right Index")  # e.g., "Right Index", "Left Thumb"
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'finger_label')

    def __str__(self):
        return f"Fingerprint of {self.student.name} - {self.finger_label}"


# Attendance Model
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    is_present = models.BooleanField(default=True)
    fingerprint_used = models.ForeignKey(FingerPrint, on_delete=models.SET_NULL, null=True, blank=True)
    meal_type = models.CharField(max_length=20, choices=[('breakfast', 'Breakfast'),
                                                         ('lunch', 'Lunch'),
                                                         ('dinner', 'Dinner')])

    class Meta:
        unique_together = ('student', 'date', 'meal_type')

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.meal_type}"

