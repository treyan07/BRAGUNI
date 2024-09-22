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

@login_required
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

    print("Retrieved Students:", students)

    departments = Department.objects.all()

    context = {
        'students': students,
        'departments': departments,
    }
    
    return render(request, 'all_students.html', context)

def edit_student(request, student_id):
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
        return redirect('student_list')

    student_instance = Student.objects.get(student_id=student_id)
    custom_user_instance = CustomUser.objects.get(id=student_instance.customuser_ptr_id)

    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student_instance)
        if form.is_valid():
            department_instance = form.cleaned_data['department']

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
        form = StudentForm(instance=student_instance)

    return render(request, 'edit_student.html', {'form': form, 'student_id': student_id})

def delete_student(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == 'POST':
        student.delete()
        return redirect('all-students')

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


def faculty_list(request):
    department_id = request.GET.get('department')
    search_query = request.GET.get('search')

    with connection.cursor() as cursor:
        query = """
            SELECT f.customuser_ptr_id, u.first_name, u.last_name, f.initial, d.name
            FROM panel_faculty f
            JOIN panel_customuser u ON f.customuser_ptr_id = u.id
            JOIN panel_department d ON f.department_id = d.id
        """
        params = []
        
        if department_id:
            query += " WHERE f.department_id = %s"
            params.append(department_id)
        
        if search_query:
            if department_id:
                query += " AND (u.first_name LIKE %s OR u.last_name LIKE %s OR f.initial LIKE %s)"
            else:
                query += " WHERE (u.first_name LIKE %s OR u.last_name LIKE %s OR f.initial LIKE %s)"
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])

        cursor.execute(query, params)
        faculty_list = cursor.fetchall()

    # Fetch all departments for the filter dropdown
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM panel_department")
        departments = cursor.fetchall()

    return render(request, 'faculty_list.html', {
        'faculty_list': faculty_list,
        'departments': departments,
        'selected_department': department_id,
        'search_query': search_query
    })

def edit_faculty(request, faculty_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT f.customuser_ptr_id, u.first_name, u.last_name, u.email, f.department_id
            FROM panel_faculty f
            JOIN panel_customuser u ON f.customuser_ptr_id = u.id
            WHERE f.customuser_ptr_id = %s
        """, [faculty_id])
        row = cursor.fetchone()

    if not row:
        return redirect('faculty_list')

    faculty_instance = Faculty.objects.get(customuser_ptr=faculty_id)
    custom_user_instance = CustomUser.objects.get(id=faculty_instance.customuser_ptr_id)

    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty_instance)
        if form.is_valid():
            department_instance = form.cleaned_data['department']

            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE panel_customuser 
                    SET first_name = %s, last_name = %s, email = %s
                    WHERE id = %s
                """, [form.cleaned_data['first_name'], form.cleaned_data['last_name'], form.cleaned_data['email'], custom_user_instance.id])

                cursor.execute("""
                    UPDATE panel_faculty
                    SET department_id = %s
                    WHERE customuser_ptr_id = %s
                """, [department_instance.id, faculty_id])

            return redirect('faculty_list')
        else:
            print(form.errors)  # Debug line to show form errors
    else:
        form = FacultyForm(instance=faculty_instance)

    return render(request, 'edit_faculty.html', {'form': form, 'faculty_id': faculty_id})

def delete_faculty(request, faculty_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            # First delete any sections that reference this faculty
            cursor.execute("""
                DELETE FROM panel_section
                WHERE faculty_id = %s
            """, [faculty_id])  # Assuming faculty_id is the customuser_ptr_id

            # Now delete the faculty record
            cursor.execute("""
                DELETE FROM panel_faculty
                WHERE customuser_ptr_id = %s
            """, [faculty_id])

            # Finally, delete the custom user record
            cursor.execute("""
                DELETE FROM panel_customuser
                WHERE id = %s
            """, [faculty_id])

        return redirect('faculty_list')

    return render(request, 'delete_faculty.html', {'faculty_id': faculty_id})

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
            return redirect('home')
    else:
        form = StaffForm()
    return render(request, 'create_staff.html', {'form': form})

def all_courses(request):
    
    department_id = request.GET.get('department')
    search_query = request.GET.get('search')

    query = """
        SELECT c.course_code, c.course_name, d.name AS department_name, c.id
        FROM panel_course c
        JOIN panel_department d ON c.department_id = d.id
    """

    params = []
    if department_id:
        query += " WHERE c.department_id = %s"
        params.append(department_id)
    
    if search_query:
        if department_id:
            query += " AND (c.course_name LIKE %s OR c.course_code LIKE %s)"
        else:
            query += " WHERE c.course_name LIKE %s OR c.course_code LIKE %s"
        search_query_like = f"%{search_query}%"
        params.extend([search_query_like, search_query_like])

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        courses = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM panel_department")
        departments = cursor.fetchall()

    return render(request, 'all_courses.html', {
        'courses': courses,
        'departments': departments,
        'selected_department': department_id,
        'search_query': search_query,
    })

def edit_course(request, course_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT c.course_code, c.course_name, c.department_id, c.id
            FROM panel_course c
            WHERE c.id = %s
        """, [course_id])
        course = cursor.fetchone()

    if not course:
        return redirect('all-courses')

    if request.method == 'POST':
        course_code = request.POST.get('course_code')
        course_name = request.POST.get('course_name')
        department_id = request.POST.get('department_id')

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE panel_course
                SET course_code = %s, course_name = %s, department_id = %s
                WHERE id = %s
            """, [course_code, course_name, department_id, course_id])

        return redirect('all-courses')

    # Fetch departments for the dropdown
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM panel_department")
        departments = cursor.fetchall()

    return render(request, 'edit_course.html', {
        'course': course,
        'departments': departments
    })

def delete_course(request, course_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM panel_course WHERE id = %s", [course_id])
        return redirect('all-courses')
    
    # Optional: Render a confirmation page before deletion
    return render(request, 'delete_course.html', {'course_id': course_id})

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
                return redirect('home')
            else:
                form.add_error(None, 'Invalid login credentials')
    else:
        form = CustomLoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')