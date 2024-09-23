from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import user_passes_test, login_required
from .forms import StudentForm, FacultyForm, StaffForm, DepartmentForm, CourseForm, SectionForm, CustomLoginForm
from .models import Student, Faculty, Staff, Department, Course, Section, CustomUser, Section, StudentEnrollment
from django.db import connection

# Choices
class_timings = [
    ("0800_to_0920", "08.00 am - 9.20 am"),
    ("0930_to_1050", "09.30 am - 10.50 am"),
    ("1100_to_1220", "11.00 am - 12.20 pm"),
    ("1230_to_0150", "12.30 pm - 01.50 pm"),
    ("0200_to_0320", "02.00 pm - 03.20 pm"),
    ("0330_to_0450", "03.30 pm - 04.50 pm"),
    ("0500_to_0620", "05.00 pm - 06.20 pm")
]

class_days = [
    ("sat_thu", "Saturday - Thursday"),
    ("sun_tue", "Sunday - Tuesday"),
    ("mon_wed", "Monday - Wednesday")
]

lab_days = [
    ("sat", "Saturday"),
    ("sun", "Sunday"),
    ("mon", "Monday"),
    ("tue", "Tuesday"),
    ("wed", "Wednesday"),
    ("thu", "Thursday")
]

# Create your views here.


def home(request):
    return redirect('home.html')

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

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


def is_staff_user(user):
    return user.is_staff

@login_required
def student_list(request):
    search = request.GET.get('search', '')
    cgpa_min = request.GET.get('cgpa_min', None)
    cgpa_max = request.GET.get('cgpa_max', None)
    credits_min = request.GET.get('credits_min', None)
    credits_max = request.GET.get('credits_max', None)
    department_id = request.GET.get('department', None)

    query = """
        SELECT s.student_id, u.first_name, u.last_name, s.cgpa, s.credits_completed, d.name as department_name
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

@login_required
def edit_student(request, student_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.student_id, u.first_name, u.last_name, u.email, s.department_id, 
                   s.credits_completed, s.cgpa, s.customuser_ptr_id
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
                    SET department_id = %s, credits_completed = %s, cgpa = %s
                    WHERE student_id = %s
                """, [department_instance.id, form.cleaned_data['credits_completed'], form.cleaned_data['cgpa'], student_id])

            return redirect('all-students')
    else:
        form = StudentForm(instance=student_instance)

    return render(request, 'edit_student.html', {'form': form, 'student_id': student_id})

@login_required
def delete_student(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    
    if request.method == 'POST':
        student.delete()
        return redirect('all-students')

    return render(request, 'delete_student.html', {'student': student})

@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.set_password(form.cleaned_data['password'])
            student.user_type = 1
            student.save()
            return redirect('all-students')
    else:
        form = StudentForm()
    return render(request, 'create_student.html', {'form': form})

@login_required
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

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM panel_department")
        departments = cursor.fetchall()

    return render(request, 'faculty_list.html', {
        'faculty_list': faculty_list,
        'departments': departments,
        'selected_department': department_id,
        'search_query': search_query
    })

@login_required
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
            print(form.errors)
    else:
        form = FacultyForm(instance=faculty_instance)

    return render(request, 'edit_faculty.html', {'form': form, 'faculty_id': faculty_id})

@login_required
def delete_faculty(request, faculty_id):
    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute("""
                DELETE FROM panel_section
                WHERE faculty_id = %s
            """, [faculty_id])

            cursor.execute("""
                DELETE FROM panel_faculty
                WHERE customuser_ptr_id = %s
            """, [faculty_id])

        return redirect('faculty_list')

    return render(request, 'delete_faculty.html', {'faculty_id': faculty_id})

@login_required
def add_faculty(request):
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            faculty = form.save(commit=False)
            faculty.set_password(form.cleaned_data['password'])
            faculty.user_type = 2
            faculty.save()
            return redirect('home')
    else:
        form = FacultyForm()
    return render(request, 'create_faculty.html', {'form': form})

@login_required
def add_staff(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            staff = form.save(commit=False)
            staff.set_password(form.cleaned_data['password'])
            staff.user_type = 3
            staff.save()
            return redirect('home')
    else:
        form = StaffForm()
    return render(request, 'create_staff.html', {'form': form})

@login_required
def all_courses(request):
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')

    query = """
        SELECT c.id, c.course_code, c.course_name, d.name AS department_name
        FROM panel_course c
        JOIN panel_department d ON c.department_id = d.id
        WHERE c.course_name LIKE %s OR c.course_code LIKE %s
    """

    params = ['%' + search_query + '%', '%' + search_query + '%']

    if department_filter:
        query += " AND c.department_id = %s"
        params.append(department_filter)

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        courses = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM panel_department")
        departments = cursor.fetchall()

    return render(request, 'all_courses.html', {
        'courses': courses,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter
    })

@login_required
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

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM panel_department")
        departments = cursor.fetchall()

    return render(request, 'edit_course.html', {
        'course': course,
        'departments': departments
    })

@login_required
def delete_course(request, course_id):
    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM panel_course WHERE id = %s", [course_id])
        return redirect('all-courses')
    
    # Optional: Render a confirmation page before deletion
    return render(request, 'delete_course.html', {'course_id': course_id})

@login_required
def AddDepartment(request):
    form = DepartmentForm()
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
    
    context = {'form': form}
    return render(request, 'create_department.html', context)

@login_required
def AddCourse(request):
    form = CourseForm()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
    
    context = {'form': form}
    return render(request, 'create_course.html', context)

@login_required
def all_sections(request):
    sections = []
    course_filter = request.GET.get('course_code', '')
    class_time_filter = request.GET.get('class_time', '')
    class_day_filter = request.GET.get('class_day', '')

    with connection.cursor() as cursor:
        query = """
            SELECT s.id, s.number, d.name AS department_name, c.course_code, 
                   c.course_name, f.initial AS faculty_initial, 
                   s.theory_room, s.lab_room, s.class_time, 
                   s.exam_time, s.class_day, s.lab_day, 
                   s.total_seat, s.seat_booked 
            FROM panel_section s
            JOIN panel_department d ON s.department_id = d.id
            JOIN panel_course c ON s.course_id = c.id
            JOIN panel_faculty f ON s.faculty_id = f.customuser_ptr_id
        """
        filters = []
        if course_filter:
            query += " WHERE c.course_code LIKE %s"
            filters.append(f"%{course_filter}%")
        if class_time_filter:
            query += " AND s.class_time = %s"
            filters.append(class_time_filter)
        if class_day_filter:
            query += " AND s.class_day = %s"
            filters.append(class_day_filter)

        cursor.execute(query, filters)
        sections = cursor.fetchall()

    return render(request, 'all_sections.html', {
        'sections': sections,
        'course_filter': course_filter,
        'class_time_filter': class_time_filter,
        'class_day_filter': class_day_filter,
        'class_timings': dict(class_timings),
        'class_days': dict(class_days),
    })

@login_required
def edit_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)  # Change based on your ID field

    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            return redirect('all-sections')  # Redirect to the sections list
    else:
        form = SectionForm(instance=section)  # Pre-fill the form with existing data

    return render(request, 'edit_section.html', {'form': form, 'section': section})

@login_required
def delete_section(request, section_id):
    section = get_object_or_404(Section, id=section_id)

    if request.method == 'POST':
        section.delete()
        return redirect('all-sections')

    return render(request, 'delete_section.html', {'section': section})

@login_required
def AddSection(request):
    form = SectionForm()
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
    
    context = {'form': form}
    return render(request, 'create_section.html', context)


@login_required
def enroll_section(request):
    student_id = request.user.id  # Assuming user is logged in as a student

    if request.method == "POST":
        selected_sections = request.POST.getlist('sections')

        # Ensure student selects between 2 and 4 sections
        if len(selected_sections) < 2 or len(selected_sections) > 4:
            return render(request, 'enroll_section.html', {'error': 'You must select between 2 and 4 sections.'})

        # Check if the student has already enrolled in any section
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM panel_student_enrollment
                WHERE student_id = %s
            """, [student_id])
            already_enrolled = cursor.fetchone()[0]

            if already_enrolled > 0:
                return render(request, 'enroll_section.html', {'error': 'You have already enrolled in sections. You cannot enroll again.'})

            enrolled_courses = set()
            for section_id in selected_sections:
                cursor.execute("""
                    SELECT c.course_code FROM panel_section s
                    JOIN panel_course c ON s.course_id = c.id
                    WHERE s.id = %s
                """, [section_id])
                course_code = cursor.fetchone()

                if course_code is None:
                    continue  # Skip if the section does not exist
                
                course_code = course_code[0]

                if course_code in enrolled_courses:
                    return render(request, 'enroll_section.html', {'error': 'You cannot enroll in multiple sections of the same course.'})

                enrolled_courses.add(course_code)

                cursor.execute("""
                    INSERT INTO panel_student_enrollment (student_id, section_id)
                    VALUES (%s, %s)
                """, [student_id, section_id])

                cursor.execute("""
                    UPDATE panel_section
                    SET seat_booked = seat_booked + 1
                    WHERE id = %s
                """, [section_id])

        return redirect('home')

    course_code_filter = request.GET.get('course_code', '')
    
    with connection.cursor() as cursor:
        query = """
            SELECT s.id, s.number, c.course_code, c.course_name, 
                   f.initial, s.theory_room, s.lab_room, 
                   s.class_time, s.class_day, s.lab_day, s.exam_time, 
                   s.total_seat, s.seat_booked,
                   (s.total_seat - s.seat_booked) AS remaining_seats
            FROM panel_section s
            JOIN panel_course c ON s.course_id = c.id
            JOIN panel_faculty f ON s.faculty_id = f.customuser_ptr_id
        """
        
        if course_code_filter:
            query += " WHERE c.course_code LIKE %s"
            cursor.execute(query, ['%' + course_code_filter + '%'])
        else:
            cursor.execute(query)

        sections = cursor.fetchall()

    return render(request, 'enroll_section.html', {'sections': sections, 'course_code_filter': course_code_filter})
