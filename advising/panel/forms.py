from django import forms
from .models import Student, Faculty, Staff, Department, Course, Section
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate


class CustomLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        user = authenticate(email=email, password=password)

        if not user:
            raise forms.ValidationError("Invalid email or password.")
        
        return self.cleaned_data

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
    password = forms.CharField(
        widget=forms.PasswordInput, 
        required=False
    )

    class Meta:
        model = Faculty
        fields = ['initial', 'first_name', 'last_name', 'email', 'department', 'advising_access']

    def save(self, commit=True):
        faculty = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            faculty.set_password(password)
        if commit:
            faculty.save()
        return faculty

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