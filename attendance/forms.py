from django import forms
from .models import Student, FingerPrint, Department

# Department Form
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure the department field has the proper widget for styling
        self.fields['name'].widget.attrs.update({'class': 'form-control'})

from django import forms
from .models import Student, FingerPrint

class StudentRegistrationForm(forms.ModelForm):
    finger_label = forms.ChoiceField(
        choices=[
            ('Right Thumb', 'Right Thumb'),
            ('Left Thumb', 'Left Thumb'),
            ('Right Index', 'Right Index'),
            ('Left Index', 'Left Index'),
            ('Right Middle', 'Right Middle'),
            ('Left Middle', 'Left Middle'),
            ('Right Ring', 'Right Ring'),
            ('Left Ring', 'Left Ring'),
            ('Right Little', 'Right Little'),
            ('Left Little', 'Left Little')
        ],
        required=True,
        label='Select Finger for Registration'
    )

    class Meta:
        model = Student
        fields = ['name', 'roll_number', 'department', 'is_active']

# FingerPrint Registration Form
class FingerPrintRegistrationForm(forms.ModelForm):
    finger_label = forms.ChoiceField(
        choices=[('right_thumb', 'Right Thumb'),
                 ('right_index', 'Right Index'),
                 ('right_middle', 'Right Middle'),
                 ('right_ring', 'Right Ring'),
                 ('right_little', 'Right Little'),
                 ('left_thumb', 'Left Thumb'),
                 ('left_index', 'Left Index'),
                 ('left_middle', 'Left Middle'),
                 ('left_ring', 'Left Ring'),
                 ('left_little', 'Left Little')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Remove the fingerprint_data field from the form (not editable by the user)
    class Meta:
        model = FingerPrint
        fields = ['finger_label']  # Only include finger_label, no fingerprint_data

# Attendance Search Form
class AttendanceSearchForm(forms.Form):
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    roll_number = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    meal_type = forms.ChoiceField(
        choices=[('', 'All Meals'), 
                 ('breakfast', 'Breakfast'),
                 ('lunch', 'Lunch'),
                 ('dinner', 'Dinner')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
