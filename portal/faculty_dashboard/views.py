from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from core.models import Faculty, Course, Student, Attendance, CourseAssignment
from django.utils import timezone
from datetime import datetime
import sys
import os
import json
from django.http import JsonResponse

# Import the face recognition script
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
from scripts.face import run_face_recognition_attendance

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
def mark_attendance_with_face_recognition(request, course_id):
    faculty = get_object_or_404(Faculty, user=request.user)
    course = get_object_or_404(Course, id=course_id, faculty_assignments__faculty=faculty)
    
    if request.method == 'POST':
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Run face recognition
        results = run_face_recognition_attendance(course_id, request.user)
        
        if is_ajax:
            # Return JSON response for AJAX requests
            return JsonResponse(results)
        else:
            # Handle regular form submission
            if results['success']:
                messages.success(request, f'Face recognition attendance completed for {course.name}')
                
                # Add details about present/absent students
                if results['present_students']:
                    present_msg = f"Present students: {', '.join(results['present_students'])}"
                    messages.info(request, present_msg)
                
                if results['absent_students']:
                    absent_msg = f"Absent students: {', '.join(results['absent_students'])}"
                    messages.warning(request, absent_msg)
                    
                return redirect('faculty_view_attendance', course_id=course_id)
            else:
                messages.error(request, f'Error: {results["error"]}')
                return redirect('faculty_dashboard')
    
    # Show confirmation page before starting face recognition
    students = Student.objects.filter(courses=course)
    students_count = students.count()
    context = {
        'course': course,
        'students': students,
        'students_count': students_count,
    }
    return render(request, 'faculty_dashboard/face_recognition_attendance.html', context)

@login_required
@user_passes_test(is_faculty)
def view_attendance(request, course_id):
    faculty = get_object_or_404(Faculty, user=request.user)
    course = get_object_or_404(Course, id=course_id, faculty_assignments__faculty=faculty)
    
    # Get filter parameters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    student_id = request.GET.get('student_id')
    status = request.GET.get('status')
    sort_by = request.GET.get('sort_by', 'date_desc')
    
    # Base query
    attendance_query = Attendance.objects.filter(course=course).select_related('student', 'student__user')
    
    # Apply filters
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            attendance_query = attendance_query.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            attendance_query = attendance_query.filter(date__lte=date_to_obj)
        except ValueError:
            pass
    
    if student_id:
        attendance_query = attendance_query.filter(student_id=student_id)
    
    if status == 'present':
        attendance_query = attendance_query.filter(is_present=True)
    elif status == 'absent':
        attendance_query = attendance_query.filter(is_present=False)
    
    # Apply sorting
    if sort_by == 'date_asc':
        attendance_query = attendance_query.order_by('date')
    elif sort_by == 'date_desc':
        attendance_query = attendance_query.order_by('-date')
    elif sort_by == 'student_name':
        attendance_query = attendance_query.order_by('student__user__first_name', 'student__user__last_name')
    
    # Calculate attendance statistics
    total_classes = attendance_query.values('date').distinct().count()
    present_count = attendance_query.filter(is_present=True).count()
    absent_count = attendance_query.filter(is_present=False).count()
    
    # Get all students for the filter dropdown
    students = Student.objects.filter(courses=course)
    
    context = {
        'course': course,
        'attendance': attendance_query,
        'students': students,
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'date_from': date_from,
        'date_to': date_to,
        'student_id': student_id,
        'status': status,
        'sort_by': sort_by,
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
