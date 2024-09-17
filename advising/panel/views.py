from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .forms import StudentForm, FacultyForm, StaffForm, DepartmentForm, CourseForm, SectionForm
from .models import Student, Faculty, Staff, Department, Course, Section
from django.db import connection
# Create your views here.

def home(request):
    return render(request, "home.html")

def is_staff_user(user):
    return user.is_staff

def student_list(request):
    search = request.GET.get('search', '')
    cgpa_min = request.GET.get('cgpa_min', None)
    cgpa_max = request.GET.get('cgpa_max', None)
    credits_min = request.GET.get('credits_min', None)
    credits_max = request.GET.get('credits_max', None)
    advising_access = request.GET.get('advising_access', None)
    department_id = request.GET.get('department', None)

    query = """
        SELECT s.student_id, u.first_name, u.last_name, s.cgpa, s.credits_completed, s.advising_access, d.name as department_name
        FROM panel_student s
        JOIN panel_customuser u ON s.customuser_ptr_id = u.id
        LEFT JOIN panel_department d ON s.department_id = d.id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (s.student_id = %s OR u.first_name LIKE %s OR u.last_name LIKE %s)"
        params.extend([search, f'%{search}%', f'%{search}%'])

    if cgpa_min:
        query += " AND s.cgpa >= %s"
        params.append(cgpa_min)

    if cgpa_max:
        query += " AND s.cgpa <= %s"
        params.append(cgpa_max)

    if credits_min:
        query += " AND s.credits_completed >= %s"
        params.append(credits_min)

    if credits_max:
        query += " AND s.credits_completed <= %s"
        params.append(credits_max)

    if advising_access:
        query += " AND s.advising_access = %s"
        params.append(advising_access)

    if department_id:
        query += " AND s.department_id = %s"
        params.append(department_id)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        students = cursor.fetchall()

    # Debugging: Print the retrieved students
    print("Retrieved Students:", students)

    # Fetch all departments for the dropdown
    departments = Department.objects.all()

    context = {
        'students': students,
        'departments': departments,
    }
    
    return render(request, 'all_students.html', context)

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.set_password(form.cleaned_data['password'])
            student.save()
            return redirect('all-students')
    else:
        form = StudentForm()
    return render(request, 'create_student.html', {'form': form})

def add_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            faculty = form.save(commit=False)
            faculty.set_password(form.cleaned_data['password'])
            faculty.save()
            return redirect('home')
    else:
        form = FacultyForm()
    return render(request, 'create_faculty.html', {'form': form})

def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.set_password(form.cleaned_data['password'])
            staff.save()
            return redirect('home')  # Replace with your success URL
    else:
        form = StaffForm()
    return render(request, 'create_staff.html', {'form': form})

def AddDepartment(request):
    form = DepartmentForm()
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
    
    context = {'form': form}
    return render(request, 'create_department.html', context)

def AddCourse(request):
    form = CourseForm()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
    
    context = {'form': form}
    return render(request, 'create_course.html', context)

def AddSection(request):
    form = SectionForm()
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
    
    context = {'form': form}
    return render(request, 'create_section.html', context)