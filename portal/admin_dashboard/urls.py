from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('courses/', views.manage_courses, name='manage_courses'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('courses/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('students/', views.manage_students, name='manage_students'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('students/<int:student_id>/', views.student_details, name='student_details'),
    path('students/<int:student_id>/courses/', views.student_courses, name='student_courses'),
    path('students/<int:student_id>/remove-course/<int:course_id>/', views.remove_student_course, name='remove_student_course'),
    path('faculty/', views.manage_faculty, name='manage_faculty'),
    path('faculty/add/', views.add_faculty, name='add_faculty'),
    path('faculty/edit/<int:faculty_id>/', views.edit_faculty, name='edit_faculty'),
    path('faculty/delete/<int:faculty_id>/', views.delete_faculty, name='delete_faculty'),
    path('faculty/<int:faculty_id>/', views.faculty_details, name='faculty_details'),
    path('faculty/<int:faculty_id>/remove-course/<int:course_id>/', views.remove_faculty_course, name='remove_faculty_course'),
    path('assign-course/', views.assign_course, name='assign_course'),
    path('attendance/<int:course_id>/', views.view_attendance, name='admin_view_attendance'),
    path('report/<int:course_id>/', views.generate_report, name='admin_generate_report'),
]
