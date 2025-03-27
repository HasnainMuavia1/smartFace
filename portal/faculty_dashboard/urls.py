from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='faculty_dashboard'),
    path('mark-attendance/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
    path('face-recognition-attendance/<int:course_id>/', views.mark_attendance_with_face_recognition, name='face_recognition_attendance'),
    path('view-attendance/<int:course_id>/', views.view_attendance, name='faculty_view_attendance'),
    path('report/<int:course_id>/', views.generate_report, name='faculty_generate_report'),
]
