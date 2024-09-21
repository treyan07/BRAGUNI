from django.urls import path
from .views import home, add_student, add_faculty, add_staff, AddDepartment, AddCourse, AddSection, student_list, edit_student, delete_student, login_view, logout_view, faculty_list, edit_faculty, delete_faculty
# login_view, advising_panel, createDepartment, createCourse, createFaculty, createStudent, updateStudent, createSection
# from .views import allStudentsList, allCoursesList, allDepartmentList, allFacultiesList, allSectionsList

urlpatterns = [
    path("", home, name = "home"),
    # path('login/', login_view, name='login'),
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

    
    
    path('create-staff/', add_staff, name = 'create-staff'),
    path('create-department/', AddDepartment, name = 'create-department'),
    path('create-course/', AddCourse, name = 'create-course'),
    path('create-section/', AddSection, name = 'create-section'),

    # path('all-faculties/', allFacultiesList, name = 'all-faculties'),
    # path('all-departments/', allDepartmentList, name = 'all-departments'),
    # path('all-courses/', allCoursesList, name = 'all-courses'),
    # path('all-sections/', allSectionsList, name = 'all-sections'),
    
    
    # path('edit-student/<str:stuID>/', updateStudent, name = 'edit-student'),
    
]