from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('courses/', views.manage_courses, name='manage_courses'),
    path('students/', views.manage_students, name='manage_students'),
    path('faculty/', views.manage_faculty, name='manage_faculty'),
    path('assign-course/', views.assign_course, name='assign_course'),
    path('attendance/<int:course_id>/', views.view_attendance, name='admin_view_attendance'),
    path('report/<int:course_id>/', views.generate_report, name='admin_generate_report'),
]
