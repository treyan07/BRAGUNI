from django.urls import path
from .views import home, add_student, add_faculty, add_staff, AddDepartment, AddCourse, AddSection, student_list, edit_student, delete_student, login_view, logout_view, faculty_list, edit_faculty, delete_faculty, all_courses, edit_course, delete_course, all_sections, edit_section, delete_section
# login_view, advising_panel, createDepartment, createCourse, createFaculty, createStudent, updateStudent, createSection
# from .views import allStudentsList, allCoursesList, allDepartmentList, allFacultiesList, allSectionsList

urlpatterns = [
    path("", home, name = "home"),
    # path('advising/', advising_panel, name = 'advising'),
    
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
    
    path('all-sections/', all_sections, name = 'all-sections'),
    path('sections/edit/<int:section_id>/', edit_section, name='edit_section'),
    path('sections/delete/<int:section_id>/', delete_section, name='delete_section'),
    path('create-section/', AddSection, name = 'create-section'),

    # path('all-faculties/', allFacultiesList, name = 'all-faculties'),
    # path('all-departments/', allDepartmentList, name = 'all-departments'),
    # path('all-courses/', allCoursesList, name = 'all-courses'),
    
    
]