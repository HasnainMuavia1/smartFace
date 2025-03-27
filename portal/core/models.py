from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Role choices
class Role(models.TextChoices):
    FACULTY = 'faculty', _('Faculty')
    STUDENT = 'student', _('Student')

class User(AbstractUser):
    """
    Custom User model with role field
    """
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    
    def is_faculty(self):
        return self.role == Role.FACULTY
    
    def is_student(self):
        return self.role == Role.STUDENT
    
    def __str__(self):
        if self.is_superuser:
            return f"{self.username} (Admin)"
        return f"{self.username} ({self.get_role_display()})"

class Course(models.Model):
    """
    Course model representing academic courses
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Faculty(models.Model):
    """
    Faculty model extending the User model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    profile_picture = models.ImageField(upload_to='faculty/', null=True, blank=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_profile.png'

class Student(models.Model):
    """
    Student model extending the User model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    profile_picture = models.ImageField(upload_to='students/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    courses = models.ManyToManyField(Course, related_name='students', blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user.get_full_name()}"

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default_profile.png'

class CourseAssignment(models.Model):
    """
    Model to assign faculties to courses
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='faculty_assignments')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='course_assignments')
    
    class Meta:
        unique_together = ('course', 'faculty')
    
    def __str__(self):
        return f"{self.faculty} - {self.course}"

class Attendance(models.Model):
    """
    Model to track student attendance
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    
    class Meta:
        unique_together = ('student', 'course', 'date')
    
    def __str__(self):
        status = 'Present' if self.is_present else 'Absent'
        return f"{self.student} - {self.course} - {self.date} - {status}"

class Timetable(models.Model):
    """
    Model for student timetables
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='timetable_entries')
    day_of_week = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.course} - {self.day_of_week} - {self.start_time} to {self.end_time}"
