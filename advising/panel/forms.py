from django import forms
from .models import Student, Faculty, Staff, Department, Course, Section

class StudentForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput, 
        required=False
    )

    class Meta:
        model = Student
        fields = ['student_id', 'first_name', 'last_name', 'email', 'department', 'credits_completed', 'cgpa', 'advising_access']

    def save(self, commit=True):
        student = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            student.set_password(password)
        if commit:
            student.save()
        return student

class FacultyForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Faculty
        fields = ['initial', 'first_name', 'last_name', 'email', 'department', 'advising_access', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class StaffForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions', 'password', 'password_confirm']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = '__all__'