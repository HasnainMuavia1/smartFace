from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from core.models import Student, Course, Attendance, Timetable

def is_student(user):
    return user.is_authenticated and user.is_student()

@login_required
@user_passes_test(is_student)
def dashboard(request):
    student = get_object_or_404(Student, user=request.user)
    courses = student.courses.all()
    
    context = {
        'student': student,
        'courses': courses,
    }
    return render(request, 'student_dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_student)
def view_attendance(request, course_id=None):
    student = get_object_or_404(Student, user=request.user)
    
    if course_id:
        course = get_object_or_404(Course, id=course_id, students=student)
        attendance = Attendance.objects.filter(student=student, course=course)
        context = {
            'course': course,
            'attendance': attendance,
        }
        return render(request, 'student_dashboard/course_attendance.html', context)
    
    # Overview of attendance for all courses
    courses = student.courses.all()
    attendance_data = []
    
    for course in courses:
        total_classes = Attendance.objects.filter(course=course, student=student).count()
        present_classes = Attendance.objects.filter(course=course, student=student, is_present=True).count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        attendance_data.append({
            'course': course,
            'total_classes': total_classes,
            'present_classes': present_classes,
            'attendance_percentage': round(attendance_percentage, 2)
        })
    
    context = {
        'attendance_data': attendance_data,
    }
    return render(request, 'student_dashboard/attendance.html', context)

@login_required
@user_passes_test(is_student)
def view_timetable(request):
    student = get_object_or_404(Student, user=request.user)
    timetable = Timetable.objects.filter(course__in=student.courses.all()).order_by('day_of_week', 'start_time')
    
    # Group timetable by days
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    timetable_by_day = {day: [] for day in days}
    
    for entry in timetable:
        timetable_by_day[entry.day_of_week].append(entry)
    
    context = {
        'timetable_by_day': timetable_by_day,
        'days': days,
    }
    return render(request, 'student_dashboard/timetable.html', context)

@login_required
@user_passes_test(is_student)
def generate_report(request, course_id=None):
    student = get_object_or_404(Student, user=request.user)
    
    if course_id:
        # Generate report for specific course
        course = get_object_or_404(Course, id=course_id, students=student)
        total_classes = Attendance.objects.filter(course=course, student=student).count()
        present_classes = Attendance.objects.filter(course=course, student=student, is_present=True).count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        context = {
            'course': course,
            'total_classes': total_classes,
            'present_classes': present_classes,
            'attendance_percentage': round(attendance_percentage, 2),
            'attendance_records': Attendance.objects.filter(course=course, student=student).order_by('date'),
        }
        return render(request, 'student_dashboard/course_report.html', context)
    
    # Generate report for all courses
    courses = student.courses.all()
    attendance_data = []
    
    for course in courses:
        total_classes = Attendance.objects.filter(course=course, student=student).count()
        present_classes = Attendance.objects.filter(course=course, student=student, is_present=True).count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        attendance_data.append({
            'course': course,
            'total_classes': total_classes,
            'present_classes': present_classes,
            'attendance_percentage': round(attendance_percentage, 2)
        })
    
    context = {
        'attendance_data': attendance_data,
    }
    return render(request, 'student_dashboard/report.html', context)
