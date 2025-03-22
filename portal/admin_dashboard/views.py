from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import User, Course, Faculty, Student, CourseAssignment, Attendance
from django.db.models import Count

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    total_courses = Course.objects.count()
    recent_courses = Course.objects.order_by('-id')[:5]
    
    context = {
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_courses': total_courses,
        'recent_courses': recent_courses,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def manage_courses(request):
    courses = Course.objects.annotate(
        student_count=Count('students'),
        faculty_count=Count('faculty_assignments')
    )
    return render(request, 'admin_dashboard/courses.html', {'courses': courses})

@login_required
@user_passes_test(is_admin)
def manage_students(request):
    students = Student.objects.select_related('user').all()
    return render(request, 'admin_dashboard/students.html', {'students': students})

@login_required
@user_passes_test(is_admin)
def manage_faculty(request):
    faculty = Faculty.objects.select_related('user').all()
    return render(request, 'admin_dashboard/faculty.html', {'faculty': faculty})

@login_required
@user_passes_test(is_admin)
def assign_course(request):
    if request.method == 'POST':
        course_id = request.POST.get('course')
        student_id = request.POST.get('student')
        faculty_id = request.POST.get('faculty')
        
        course = get_object_or_404(Course, id=course_id)
        
        if student_id:
            student = get_object_or_404(Student, id=student_id)
            student.courses.add(course)
            messages.success(request, f'Student assigned to {course.name} successfully.')
        
        if faculty_id:
            faculty = get_object_or_404(Faculty, id=faculty_id)
            CourseAssignment.objects.create(course=course, faculty=faculty)
            messages.success(request, f'Faculty assigned to {course.name} successfully.')
        
        return redirect('manage_courses')
    
    courses = Course.objects.all()
    students = Student.objects.select_related('user').all()
    faculty = Faculty.objects.select_related('user').all()
    
    context = {
        'courses': courses,
        'students': students,
        'faculty': faculty,
    }
    return render(request, 'admin_dashboard/assign_course.html', context)

@login_required
@user_passes_test(is_admin)
def view_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    attendance = Attendance.objects.filter(course=course).select_related('student', 'student__user')
    
    context = {
        'course': course,
        'attendance': attendance,
    }
    return render(request, 'admin_dashboard/attendance.html', context)

@login_required
@user_passes_test(is_admin)
def generate_report(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = Student.objects.filter(courses=course)
    attendance_data = []
    
    for student in students:
        total_classes = Attendance.objects.filter(course=course, student=student).count()
        present_classes = Attendance.objects.filter(course=course, student=student, is_present=True).count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        attendance_data.append({
            'student': student,
            'total_classes': total_classes,
            'present_classes': present_classes,
            'attendance_percentage': round(attendance_percentage, 2)
        })
    
    context = {
        'course': course,
        'attendance_data': attendance_data,
    }
    return render(request, 'admin_dashboard/report.html', context)
