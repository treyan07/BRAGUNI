from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

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

# Custom User Model
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    USER_TYPE_CHOICES = (
        (1, 'student'),
        (2, 'faculty'),
        (3, 'staff'),
    )
    
    user_type = models.PositiveSmallIntegerField(null = True, choices=USER_TYPE_CHOICES)

    @property
    def is_student(self):
        return self.user_type == 1

    @property
    def is_faculty(self):
        return self.user_type == 2

    @property
    def is_staff_member(self):
        return self.user_type == 3
    
    def __str__(self):
        return self.email

# Department
class Department(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    dept_initial = models.CharField(max_length=5, null=False, unique=True)

    def __str__(self):
        return self.dept_initial

# Course
class Course(models.Model):
    course_name = models.CharField(max_length=70, null=False)
    course_code = models.CharField(max_length=7, null=False, unique = True)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)
    prerequisite_course = models.TextField(max_length=70, null=True, blank=True)

    def __str__(self):
        return self.course_code
    
# Section
class Section(models.Model):
    number = models.IntegerField(null=True, blank=False)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    faculty = models.ForeignKey("Faculty", on_delete=models.CASCADE)
    theory_room = models.CharField(max_length=10, null=True, blank=False)
    lab_room = models.CharField(max_length=10, null=True, blank=True)
    class_time = models.CharField(max_length=20, choices=class_timings)
    exam_time = models.CharField(max_length=20, choices=class_timings)
    class_day = models.CharField(max_length=20, choices=class_days)
    lab_day = models.CharField(max_length=20, choices=lab_days, null=True)
    total_seat = models.IntegerField(default=40, null=False)
    seat_booked = models.IntegerField(default=0, null=False)

    class Meta:
        unique_together = ('number', 'course')
    
    def __str__(self):
        return f"{self.course}: Section - {self.number} - {self.faculty.initial}"

# USER    
class Student(CustomUser):
    student_id = models.PositiveBigIntegerField(unique=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)
    credits_completed = models.IntegerField(default=0)
    cgpa = models.DecimalField(max_digits=3, decimal_places=2, validators=[MaxValueValidator(4), MinValueValidator(0)])
    
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['student_id']
    
    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

class Faculty(CustomUser):
    initial = models.CharField(max_length=3, unique=True)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculty'
        ordering = ['initial']
    
    def __str__(self):
        return f"{self.initial} - {self.first_name} {self.last_name}"

class Staff(CustomUser):
    
    class Meta:
        verbose_name = 'Staff'
        verbose_name_plural = 'Staff'
        ordering = ['first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class StudentEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    class Meta:
        db_table = 'panel_student_enrollment'
        unique_together = ('student', 'section')