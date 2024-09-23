from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Student, Faculty, Staff, Department, Course, Section
from .forms import StudentForm, FacultyForm, StaffForm

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

class StudentAdmin(admin.ModelAdmin):
    form = StudentForm
    list_display = ('student_id', 'first_name', 'last_name', 'department', 'cgpa')
    fieldsets = (
        ('Personal Info', {'fields': ('student_id', 'first_name', 'last_name', 'email', 'password')}),
        ('Academic Info', {'fields': ('department', 'credits_completed', 'cgpa')}),
    
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('student_id', 'first_name', 'last_name', 'email', 'password')}
        ),
    )

class FacultyAdmin(admin.ModelAdmin):
    form = FacultyForm
    list_display = ('initial', 'first_name', 'last_name', 'department')
    fieldsets = (
        ('Personal Info', {'fields': ('initial', 'first_name', 'last_name', 'email')}),
        ('Department Info', {'fields': ('department', 'advising_access')}),
        ('Security', {'fields': ('password1', 'password2')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('initial', 'first_name', 'last_name', 'email', 'password1', 'password2')}
        ),
    )

class StaffAdmin(UserAdmin):
    form = StaffForm
    list_display = ('first_name', 'last_name', 'email', 'is_staff', 'is_active', 'is_superuser')
    fieldsets = (
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Security', {'fields': ('password1', 'password2')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Faculty, FacultyAdmin)
admin.site.register(Staff, StaffAdmin)

admin.site.register(Department)
admin.site.register(Course)
admin.site.register(Section)