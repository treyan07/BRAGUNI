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

def manage_students(request):
    search_query = request.GET.get('search', '')
    filter_department = request.GET.get('department', '')
    filter_advising_status = request.GET.get('advising_access', '')
    filter_cgpa_min = request.GET.get('cgpa_min', '')
    filter_cgpa_max = request.GET.get('cgpa_max', '')
    filter_credits_completed_min = request.GET.get('credits_completed_min', '')
    filter_credits_completed_max = request.GET.get('credits_completed_max', '')

    # Base SQL query
    query = """
        SELECT s.student_id, c.first_name, c.last_name, s.cgpa, s.credits_completed, s.advising_access, d.name as department_name
        FROM panel_student s
        JOIN panel_customuser c ON s.customuser_ptr_id = c.id
        LEFT JOIN panel_department d ON s.department_id = d.id
        WHERE 1=1
    """
    params = []

    # Search by first name, last name, or student ID
    if search_query:
        query += " AND (c.first_name LIKE %s OR c.last_name LIKE %s OR s.student_id = %s)"
        params.extend(['%' + search_query + '%', '%' + search_query + '%', search_query])

    # Filter by department
    if filter_department:
        query += " AND s.department_id = %s"
        params.append(filter_department)

    # Filter by advising status
    if filter_advising_status:
        query += " AND s.advising_access = %s"
        params.append(filter_advising_status == 'True')

    # Filter by CGPA range
    if filter_cgpa_min:
        query += " AND s.cgpa >= %s"
        params.append(filter_cgpa_min)
    if filter_cgpa_max:
        query += " AND s.cgpa <= %s"
        params.append(filter_cgpa_max)

    # Filter by credits completed range
    if filter_credits_completed_min:
        query += " AND s.credits_completed >= %s"
        params.append(filter_credits_completed_min)
    if filter_credits_completed_max:
        query += " AND s.credits_completed <= %s"
        params.append(filter_credits_completed_max)

    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        students = cursor.fetchall()

    # Fetch departments for filtering
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM panel_department")
        departments = cursor.fetchall()

    context = {
        'students': students,
        'departments': departments,
        'search_query': search_query,
        'filter_department': filter_department,
        'filter_advising_status': filter_advising_status,
        'filter_cgpa_min': filter_cgpa_min,
        'filter_cgpa_max': filter_cgpa_max,
        'filter_credits_completed_min': filter_credits_completed_min,
        'filter_credits_completed_max': filter_credits_completed_max,
    }
    
    return render(request, 'manage_students.html', context)

@user_passes_test(is_staff_user)
def edit_student(request, student_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM panel_student WHERE student_id = %s", [student_id])
        student_data = cursor.fetchone()

    # Fetching departments
    departments = Department.objects.raw("SELECT * FROM panel_department")  # Replace with your department table name

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        cgpa = request.POST.get('cgpa')
        credits_completed = request.POST.get('credits_completed')
        advising_access = request.POST.get('advising_access') == 'True'
        department_id = request.POST.get('department')  # Get selected department

        # Update panel_customuser
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE panel_customuser 
                SET first_name = %s, last_name = %s 
                WHERE id = (SELECT customuser_ptr_id FROM panel_student WHERE student_id = %s)
            """, [first_name, last_name, student_id])

            # Update panel_student
            cursor.execute("""
                UPDATE panel_student 
                SET cgpa = %s, credits_completed = %s, advising_access = %s, department_id = %s 
                WHERE student_id = %s
            """, [cgpa, credits_completed, advising_access, department_id, student_id])

        return redirect('manage_students')

    context = {
        'student': student_data,
        'departments': departments,  # Pass departments to the template
    }
    return render(request, 'edit_student.html', context)

@user_passes_test(is_staff_user)
def delete_student(request, student_id):
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM panel_student WHERE student_id = %s", [student_id])
        cursor.execute("DELETE FROM panel_customuser WHERE id = (SELECT customuser_ptr_id FROM panel_student WHERE student_id = %s)", [student_id])
    return redirect('manage_students')

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.set_password(form.cleaned_data['password'])
            student.save()
            return redirect('manage_students')
    else:
        form = StudentForm()
    return render(request, 'create_student.html', {'form': form})

@user_passes_test(is_staff_user)
def add_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            faculty = form.save(commit=False)
            faculty.set_password(form.cleaned_data['password'])
            faculty.save()
            return redirect('home')  # Replace with your success URL
    else:
        form = FacultyForm()
    return render(request, 'create_faculty.html', {'form': form})

@user_passes_test(is_staff_user)
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