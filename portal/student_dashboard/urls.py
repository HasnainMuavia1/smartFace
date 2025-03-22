from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='student_dashboard'),
    path('attendance/', views.view_attendance, name='student_view_attendance'),
    path('attendance/<int:course_id>/', views.view_attendance, name='student_course_attendance'),
    path('timetable/', views.view_timetable, name='student_timetable'),
    path('report/', views.generate_report, name='student_generate_report'),
    path('report/<int:course_id>/', views.generate_report, name='student_course_report'),
]
