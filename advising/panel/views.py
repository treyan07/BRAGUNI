from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import StudentForm, FacultyForm, StaffForm, DepartmentForm, CourseForm, SectionForm, CustomLoginForm
from .models import Student, Faculty, Staff, Department, Course, Section, CustomUser
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

def edit_student(request, student_id):
    # Get student data using a raw SQL query that joins with the panel_customuser table
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.student_id, u.first_name, u.last_name, u.email, s.department_id, 
                   s.credits_completed, s.cgpa, s.advising_access, s.customuser_ptr_id
            FROM panel_student s
            JOIN panel_customuser u ON s.customuser_ptr_id = u.id
            WHERE s.student_id = %s
        """, [student_id])
        row = cursor.fetchone()

    if not row:
        return redirect('student_list')  # If no student is found, redirect to the list

    # Fetch the actual student and custom user instances from the database
    student_instance = Student.objects.get(student_id=student_id)
    custom_user_instance = CustomUser.objects.get(id=student_instance.customuser_ptr_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student_instance)  # Pass instance to avoid uniqueness error
        if form.is_valid():
            # Extract the department instance from the form (Django handles this automatically if it's a ForeignKey)
            department_instance = form.cleaned_data['department']

            # Update the student record using form data
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE panel_customuser 
                    SET first_name = %s, last_name = %s, email = %s
                    WHERE id = %s
                """, [form.cleaned_data['first_name'], form.cleaned_data['last_name'], form.cleaned_data['email'], custom_user_instance.id])

                cursor.execute("""
                    UPDATE panel_student
                    SET department_id = %s, credits_completed = %s, cgpa = %s, advising_access = %s
                    WHERE student_id = %s
                """, [department_instance.id, form.cleaned_data['credits_completed'], form.cleaned_data['cgpa'], form.cleaned_data['advising_access'], student_id])

            return redirect('all-students')
    else:
        form = StudentForm(instance=student_instance)  # Pass instance to pre-populate the form

    return render(request, 'edit_student.html', {'form': form, 'student_id': student_id})


def delete_student(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)  # Fetch the student to be deleted
    
    if request.method == 'POST':  # Confirm deletion after POST request
        student.delete()
        return redirect('all-students')  # Redirect to student list after deletion

    return render(request, 'delete_student.html', {'student': student})

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


def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to homepage or other desired page
            else:
                form.add_error(None, 'Invalid login credentials')
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')