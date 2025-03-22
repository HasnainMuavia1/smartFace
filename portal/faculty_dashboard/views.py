from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Faculty, Course, Student, Attendance, CourseAssignment
from django.utils import timezone
from datetime import datetime

def is_faculty(user):
    return user.is_authenticated and user.is_faculty()

@login_required
@user_passes_test(is_faculty)
def dashboard(request):
    faculty = get_object_or_404(Faculty, user=request.user)
    assigned_courses = Course.objects.filter(faculty_assignments__faculty=faculty)
    
    context = {
        'faculty': faculty,
        'assigned_courses': assigned_courses,
    }
    return render(request, 'faculty_dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_faculty)
def mark_attendance(request, course_id):
    faculty = get_object_or_404(Faculty, user=request.user)
    course = get_object_or_404(Course, id=course_id, faculty_assignments__faculty=faculty)
    
    if request.method == 'POST':
        date = request.POST.get('date')
        try:
            attendance_date = datetime.strptime(date, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            attendance_date = timezone.now().date()
        
        students = Student.objects.filter(courses=course)
        
        for student in students:
            is_present = request.POST.get(f'student_{student.id}') == 'present'
            Attendance.objects.update_or_create(
                student=student,
                course=course,
                date=attendance_date,
                defaults={'is_present': is_present, 'marked_by': request.user}
            )
        
        messages.success(request, f'Attendance marked for {course.name} on {attendance_date}')
        return redirect('faculty_dashboard')
    
    students = Student.objects.filter(courses=course)
    context = {
        'course': course,
        'students': students,
        'today': timezone.now().date(),
    }
    return render(request, 'faculty_dashboard/mark_attendance.html', context)

@login_required
@user_passes_test(is_faculty)
def view_attendance(request, course_id):
    faculty = get_object_or_404(Faculty, user=request.user)
    course = get_object_or_404(Course, id=course_id, faculty_assignments__faculty=faculty)
    attendance = Attendance.objects.filter(course=course).select_related('student', 'student__user')
    
    context = {
        'course': course,
        'attendance': attendance,
    }
    return render(request, 'faculty_dashboard/view_attendance.html', context)

@login_required
@user_passes_test(is_faculty)
def generate_report(request, course_id):
    faculty = get_object_or_404(Faculty, user=request.user)
    course = get_object_or_404(Course, id=course_id, faculty_assignments__faculty=faculty)
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
    return render(request, 'faculty_dashboard/report.html', context)
