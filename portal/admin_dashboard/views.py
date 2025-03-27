from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from core.models import User, Course, Faculty, Student, CourseAssignment, Attendance
from django.db.models import Count
import os

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
    # Get courses with student and faculty counts
    courses = Course.objects.annotate(
        student_count=Count('students'),
        faculty_count=Count('faculty_assignments')
    ).order_by('name')

    # Get total counts for stats
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()

    # Get all faculty for the filter dropdown
    faculties = Faculty.objects.select_related('user').all()

    context = {
        'courses': courses,
        'total_students': total_students,
        'total_faculty': total_faculty,
        'faculties': faculties,
    }
    return render(request, 'admin_dashboard/courses.html', context)

@login_required
@user_passes_test(is_admin)
def manage_students(request):
    students = Student.objects.select_related('user').all()
    courses = Course.objects.all()
    return render(request, 'admin_dashboard/students.html', {'students': students, 'courses': courses})

@login_required
@user_passes_test(is_admin)
def add_student(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        is_active = 'is_active' in request.POST
        
        # Generate email from username
        email = f"{username}@example.com"
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'A user with this username already exists.')
            return redirect('manage_students')
        
        # Create user
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            role='student'
        )
        
        # Set temporary password
        user.password = make_password('temp123')
        user.save()
        
        # Create student
        student = Student.objects.create(
            user=user,
            phone_number=phone
        )
        
        # Handle profile picture
        if 'profile_picture' in request.FILES:
            student.profile_picture = request.FILES['profile_picture']
            student.save()
        
        # Add courses
        courses = request.POST.getlist('courses[]')
        if courses:
            student.courses.add(*courses)
        
        messages.success(request, f'Student {first_name} {last_name} added successfully.')
        return redirect('manage_students')
    
    return redirect('manage_students')

@login_required
@user_passes_test(is_admin)
def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    user = student.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        phone = request.POST.get('phone')
        is_active = 'is_active' in request.POST
        
        # Check if username already exists (excluding current user)
        if username != user.username and User.objects.filter(username=username).exists():
            messages.error(request, 'A user with this username already exists.')
            return redirect('manage_students')
        
        # Update user
        user.first_name = first_name
        user.last_name = last_name
        user.username = username
        user.email = f"{username}@example.com"  # Update email based on new username
        user.is_active = is_active
        user.save()
        
        # Update student
        student.phone_number = phone
        
        # Handle profile picture
        if 'remove_picture' in request.POST and student.profile_picture:
            # Delete old picture file
            if os.path.isfile(student.profile_picture.path):
                os.remove(student.profile_picture.path)
            student.profile_picture = None
        elif 'profile_picture' in request.FILES:
            # Delete old picture file if it exists
            if student.profile_picture and os.path.isfile(student.profile_picture.path):
                os.remove(student.profile_picture.path)
            # Add new picture
            student.profile_picture = request.FILES['profile_picture']
        
        student.save()
        
        # Update courses
        student.courses.clear()
        courses = request.POST.getlist('courses[]')
        if courses:
            student.courses.add(*courses)
        
        messages.success(request, f'Student {first_name} {last_name} updated successfully.')
        return redirect('manage_students')
    
    return redirect('manage_students')

@login_required
@user_passes_test(is_admin)
def delete_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    user = student.user
    
    if request.method == 'POST':
        # Delete profile picture if exists
        if student.profile_picture:
            if os.path.isfile(student.profile_picture.path):
                os.remove(student.profile_picture.path)
        
        # Get student name before deletion
        student_name = user.get_full_name()
        
        # Delete user (will cascade delete student)
        user.delete()
        
        messages.success(request, f'Student "{student_name}" has been deleted successfully.')
        return redirect('manage_students')
    
    return redirect('manage_students')

@login_required
@user_passes_test(is_admin)
def student_details(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    courses = Course.objects.all()
    return render(request, 'admin_dashboard/student_details.html', {'student': student, 'courses': courses})

@login_required
@user_passes_test(is_admin)
def remove_student_course(request, student_id, course_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        course = get_object_or_404(Course, id=course_id)
        
        # Remove the course from the student
        student.courses.remove(course)
        
        messages.success(request, f'Course "{course.name}" has been removed from {student.user.get_full_name()}.')
    
    return redirect('student_details', student_id=student_id)

@login_required
@user_passes_test(is_admin)
def student_courses(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    courses = [course.id for course in student.courses.all()]
    return JsonResponse({'courses': courses})

@login_required
@user_passes_test(is_admin)
def manage_faculty(request):
    faculty_list = Faculty.objects.all().order_by('user__first_name', 'user__last_name')
    courses = Course.objects.all().order_by('name')
    
    # Get faculty course assignments
    for faculty in faculty_list:
        faculty.assigned_courses = Course.objects.filter(faculty_assignments__faculty=faculty)
    
    context = {
        'faculty_list': faculty_list,
        'courses': courses,
    }
    return render(request, 'admin_dashboard/faculty.html', context)

@login_required
@user_passes_test(is_admin)
def add_faculty(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        is_active = 'is_active' in request.POST
        selected_courses = request.POST.getlist('courses')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'A user with this username already exists.')
            return redirect('manage_faculty')
        
        # Create user
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            role='faculty'
        )
        
        # Set default password to faculty123
        user.password = make_password('faculty123')
        user.save()
        
        # Create faculty
        faculty = Faculty.objects.create(
            user=user,
            department=department,
            phone=phone
        )
        
        # Handle profile picture
        if 'profile_picture' in request.FILES:
            faculty.profile_picture = request.FILES['profile_picture']
            faculty.save()
        
        # Assign selected courses
        if selected_courses:
            for course_id in selected_courses:
                try:
                    course = Course.objects.get(id=course_id)
                    CourseAssignment.objects.create(faculty=faculty, course=course)
                except Course.DoesNotExist:
                    continue
        
        messages.success(request, f'Faculty {first_name} {last_name} added successfully with username "{username}" and default password "faculty123".')
        return redirect('manage_faculty')
    
    return redirect('manage_faculty')

@login_required
@user_passes_test(is_admin)
def edit_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    user = faculty.user
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        department = request.POST.get('department')
        is_active = 'is_active' in request.POST
        
        # Check if username already exists (excluding current user)
        if username != user.username and User.objects.filter(username=username).exists():
            messages.error(request, 'A user with this username already exists.')
            return redirect('manage_faculty')
        
        # Update user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.username = username
        user.is_active = is_active
        user.save()
        
        # Update faculty
        faculty.department = department
        faculty.phone = phone
        
        # Handle profile picture
        if 'profile_picture' in request.FILES:
            # Delete old picture if exists
            if faculty.profile_picture:
                try:
                    os.remove(faculty.profile_picture.path)
                except (ValueError, FileNotFoundError):
                    pass
            faculty.profile_picture = request.FILES['profile_picture']
        
        # Handle remove profile picture
        if 'remove_profile_picture' in request.POST and faculty.profile_picture:
            try:
                os.remove(faculty.profile_picture.path)
            except (ValueError, FileNotFoundError):
                pass
            faculty.profile_picture = None
        
        faculty.save()
        
        messages.success(request, f'Faculty {first_name} {last_name} updated successfully.')
        return redirect('faculty_details', faculty_id=faculty_id)
    
    return redirect('manage_faculty')

@login_required
@user_passes_test(is_admin)
def delete_faculty(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    user = faculty.user
    
    if request.method == 'POST':
        # Get faculty name before deletion
        faculty_name = user.get_full_name()
        
        # Check if faculty has course assignments
        if CourseAssignment.objects.filter(faculty=faculty).exists():
            # Delete all course assignments
            CourseAssignment.objects.filter(faculty=faculty).delete()
        
        # Delete user (will cascade delete faculty)
        user.delete()
        
        messages.success(request, f'Faculty "{faculty_name}" has been deleted successfully.')
        return redirect('manage_faculty')
    
    return redirect('manage_faculty')

@login_required
@user_passes_test(is_admin)
def faculty_details(request, faculty_id):
    faculty = get_object_or_404(Faculty, id=faculty_id)
    courses = Course.objects.all()
    
    # Get course assignments
    course_assignments = CourseAssignment.objects.filter(faculty=faculty).select_related('course')
    
    # Calculate total students for each course
    for assignment in course_assignments:
        assignment.student_count = Student.objects.filter(courses=assignment.course).count()
    
    return render(request, 'admin_dashboard/faculty_details.html', {
        'faculty': faculty,
        'courses': courses,
        'course_assignments': course_assignments
    })

@login_required
@user_passes_test(is_admin)
def remove_faculty_course(request, faculty_id, course_id):
    if request.method == 'POST':
        faculty = get_object_or_404(Faculty, id=faculty_id)
        course = get_object_or_404(Course, id=course_id)
        
        # Find and delete the course assignment
        assignment = get_object_or_404(CourseAssignment, faculty=faculty, course=course)
        assignment.delete()
        
        messages.success(request, f'Course "{course.name}" has been removed from {faculty.user.get_full_name()}.')
    
    return redirect('faculty_details', faculty_id=faculty_id)

@login_required
@user_passes_test(is_admin)
def assign_course(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        student_id = request.POST.get('student_id')
        faculty_id = request.POST.get('faculty_id')
        
        course = get_object_or_404(Course, id=course_id)
        
        if student_id:
            student = get_object_or_404(Student, id=student_id)
            student.courses.add(course)
            messages.success(request, f'Student assigned to {course.name} successfully.')
            return redirect('student_details', student_id=student_id)
        
        if faculty_id:
            faculty = get_object_or_404(Faculty, id=faculty_id)
            
            # Check if assignment already exists
            if CourseAssignment.objects.filter(course=course, faculty=faculty).exists():
                messages.warning(request, f'Faculty is already assigned to {course.name}.')
            else:
                CourseAssignment.objects.create(course=course, faculty=faculty)
                messages.success(request, f'Faculty assigned to {course.name} successfully.')
            
            return redirect('faculty_details', faculty_id=faculty_id)
        
        return redirect('manage_courses')
    
    courses = Course.objects.all()
    students = Student.objects.select_related('user').all()
    faculty = Faculty.objects.select_related('user').all()
    
    context = {
        'courses': courses,
        'students': students,
        'faculty': faculty
    }
    
    return render(request, 'admin_dashboard/assign_course.html', context)

@login_required
@user_passes_test(is_admin)
def add_course(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Validate unique code
        if Course.objects.filter(code=code).exists():
            messages.error(request, 'A course with this code already exists.')
            return redirect('manage_courses')

        Course.objects.create(
            code=code,
            name=name,
            description=description
        )
        messages.success(request, f'Course "{name}" has been added successfully.')
        return redirect('manage_courses')
    return redirect('manage_courses')

@login_required
@user_passes_test(is_admin)
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        code = request.POST.get('code')
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Validate unique code
        if Course.objects.filter(code=code).exclude(id=course_id).exists():
            messages.error(request, 'A course with this code already exists.')
            return redirect('manage_courses')

        course.code = code
        course.name = name
        course.description = description
        course.save()
        messages.success(request, f'Course "{name}" has been updated successfully.')
        return redirect('manage_courses')
    return redirect('manage_courses')

@login_required
@user_passes_test(is_admin)
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        course_name = course.name
        course.delete()
        messages.success(request, f'Course "{course_name}" has been deleted successfully.')
        return redirect('manage_courses')
    return redirect('manage_courses')

@login_required
@user_passes_test(is_admin)
def view_attendance(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
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
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            attendance_query = attendance_query.filter(date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            from datetime import datetime
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
