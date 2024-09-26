from django.urls import path
from .views import home, add_student, add_faculty, add_staff, AddDepartment, AddCourse, AddSection, student_list, edit_student, delete_student, login_view, logout_view, faculty_list, edit_faculty, delete_faculty, all_courses, edit_course, delete_course, all_sections, edit_section, delete_section, enroll_section, all_departments, edit_department, delete_department, enrolled_courses

urlpatterns = [
    path("", home, name = "home"),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    path('create-student/', add_student, name = 'create-student'),
    path('all-students/', student_list, name = 'all-students'),
    path('edit-student/<int:student_id>/', edit_student, name='edit_student'),
    path('delete-student/<int:student_id>/', delete_student, name='delete_student'),
    
    path('faculty/', faculty_list, name='faculty_list'),
    path('faculty/edit/<int:faculty_id>/', edit_faculty, name='edit_faculty'),
    path('faculty/delete/<str:faculty_id>/', delete_faculty, name='delete_faculty'),
    path('create-faculty/', add_faculty, name = 'create-faculty'),
    
    path('courses/', all_courses, name='all-courses'),
    path('courses/edit/<int:course_id>/', edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', delete_course, name='delete_course'),
    path('create-course/', AddCourse, name = 'create-course'),

    
    
    path('create-staff/', add_staff, name = 'create-staff'),
    
    path('create-department/', AddDepartment, name = 'create-department'),
    path('departments/', all_departments, name='all-departments'),
    path('departments/edit/<int:department_id>/', edit_department, name='edit-department'),
    path('departments/delete/<int:department_id>/', delete_department, name='delete-department'),
    
    path('all-sections/', all_sections, name = 'all-sections'),
    path('sections/edit/<int:section_id>/', edit_section, name='edit_section'),
    path('sections/delete/<int:section_id>/', delete_section, name='delete_section'),
    path('create-section/', AddSection, name = 'create-section'),
    
    path('enroll-section/', enroll_section, name='enroll_section'),
    path('enrolled-courses/', enrolled_courses, name='enrolled-courses'),
    
    
]