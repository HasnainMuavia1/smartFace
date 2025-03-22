from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Course, Faculty, Student, CourseAssignment, Attendance, Timetable

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')
    ordering = ('code',)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'department')
    raw_id_fields = ('user',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'roll_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'roll_number')
    raw_id_fields = ('user',)
    filter_horizontal = ('courses',)

@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'faculty')
    search_fields = ('course__name', 'faculty__user__username')
    raw_id_fields = ('course', 'faculty')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date', 'is_present', 'marked_by')
    list_filter = ('is_present', 'date', 'course')
    search_fields = ('student__user__username', 'course__name')
    raw_id_fields = ('student', 'course', 'marked_by')
    date_hierarchy = 'date'

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('course', 'day_of_week', 'start_time', 'end_time', 'room')
    list_filter = ('day_of_week',)
    search_fields = ('course__name', 'room')
    raw_id_fields = ('course',)
